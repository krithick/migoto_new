from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timedelta
import os
from models.company_models import (
    CompanyDB, CompanyResponse, CompanyCreate, CompanyUpdate, 
    CompanyAnalytics, CompanyStatus, CompanyType
)
from models.user_models import UserDB, UserRole, AccountType
from core.user import get_current_user, get_boss_admin_user, get_superadmin_user, get_admin_user
from core.course_transfer import transfer_course_complete

# Create router
router = APIRouter(prefix="/companies", tags=["Company Management"])

async def get_database():
    from database import get_db
    return await get_db()

# Company Operations
async def get_company_by_id(db: Any, company_id: UUID) -> Optional[CompanyDB]:
    """Get company by ID"""
    company = await db.companies.find_one({"_id": str(company_id)})
    if company:
        return CompanyDB(**company)
    return None

async def get_companies_by_type(db: Any, company_type: CompanyType) -> List[CompanyDB]:
    """Get companies by type"""
    companies = []
    cursor = db.companies.find({"company_type": company_type})
    async for document in cursor:
        companies.append(CompanyDB(**document))
    return companies

async def get_companies_by_parent(db: Any, parent_company_id: UUID) -> List[CompanyDB]:
    """Get subsidiary companies by parent company ID"""
    companies = []
    cursor = db.companies.find({"parent_company_id": str(parent_company_id)})
    async for document in cursor:
        companies.append(CompanyDB(**document))
    return companies

async def get_all_companies(db: Any, skip: int = 0, limit: int = 100, 
                           status_filter: Optional[CompanyStatus] = None) -> List[CompanyDB]:
    """Get all companies with optional filtering"""
    companies = []
    query = {}
    
    if status_filter:
        query["status"] = status_filter
    
    cursor = db.companies.find(query).skip(skip).limit(limit)
    async for document in cursor:
        companies.append(CompanyDB(**document))
    return companies

async def create_company(db: Any, company: CompanyCreate, created_by: UUID) -> CompanyDB:
    """Create a new company (boss admin only)"""
    # Check if creator is boss admin
    creator = await db.users.find_one({"_id": str(created_by)})
    if not creator or creator.get("role") != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only boss admins can create companies"
        )
    
    # Validate parent company if this is a subsidiary
    if company.company_type == CompanyType.SUBSIDIARY:
        if not company.parent_company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subsidiary companies must have a parent company"
            )
        
        parent_company = await get_company_by_id(db, company.parent_company_id)
        if not parent_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent company not found"
            )
        
        if parent_company.company_type not in [CompanyType.MOTHER, CompanyType.CLIENT]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent company must be mother or client type"
            )
    
    # Check if company name already exists
    existing_company = await db.companies.find_one({"name": company.name})
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name already exists"
        )
    
    # Create CompanyDB model
    company_dict = company.dict()
    
    company_db = CompanyDB(
        **company_dict,
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    company_dict = company_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in company_dict:
        company_dict["_id"] = str(company_dict["_id"])
    
    # Convert UUID fields to strings for MongoDB
    if "parent_company_id" in company_dict and company_dict["parent_company_id"]:
        company_dict["parent_company_id"] = str(company_dict["parent_company_id"])
    
    if "created_by" in company_dict:
        company_dict["created_by"] = str(company_dict["created_by"])
    
    result = await db.companies.insert_one(company_dict)
    created_company = await db.companies.find_one({"_id": str(result.inserted_id)})
    
    return CompanyDB(**created_company)

async def update_company(db: Any, company_id: UUID, update_data: CompanyUpdate, 
                        updated_by: UUID) -> Optional[CompanyDB]:
    """Update a company"""
    # Get the company
    company = await get_company_by_id(db, company_id)
    if not company:
        return None
    
    # Get the user making the update
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized update attempt"
        )
    
    # Check authorization
    updater_role = updater.get("role")
    updater_company_id = updater.get("company_id")
    
    if updater_role == UserRole.BOSS_ADMIN:
        # Boss admin can update any company
        pass
    elif updater_role == UserRole.SUPERADMIN and str(updater_company_id) == str(company_id):
        # Superadmin can only update their own company
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this company"
        )
    
    # Prepare update data
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now()
    
    # Update in database
    await db.companies.update_one(
        {"_id": str(company_id)},
        {"$set": update_dict}
    )
    
    updated_company = await db.companies.find_one({"_id": str(company_id)})
    if updated_company:
        return CompanyDB(**updated_company)
    return None

async def delete_company(db: Any, company_id: UUID, deleted_by: UUID) -> bool:
    """Delete a company (boss admin only)"""
    # Get the company
    company = await get_company_by_id(db, company_id)
    if not company:
        return False
    
    # Get the user making the deletion
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter or deleter.get("role") != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only boss admins can delete companies"
        )
    
    # Check if company has users
    user_count = await db.users.count_documents({"company_id": str(company_id)})
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company with {user_count} users. Please reassign or delete users first."
        )
    
    # Check if company has subsidiaries
    subsidiaries = await get_companies_by_parent(db, company_id)
    if subsidiaries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company with {len(subsidiaries)} subsidiaries. Please reassign subsidiaries first."
        )
    
    # Delete from database
    result = await db.companies.delete_one({"_id": str(company_id)})
    return result.deleted_count > 0

async def update_company_statistics(db: Any, company_id: UUID) -> bool:
    """Update company statistics (user counts, etc.)"""
    try:
        # Count users by role
        total_users = await db.users.count_documents({"company_id": str(company_id)})
        total_admins = await db.users.count_documents({
            "company_id": str(company_id),
            "role": {"$in": [UserRole.ADMIN, UserRole.SUPERADMIN]}
        })
        total_superadmins = await db.users.count_documents({
            "company_id": str(company_id),
            "role": UserRole.SUPERADMIN
        })
        
        # Count content (these would need to be implemented when content models are available)
        # For now, setting to 0
        total_courses = 0  # await db.courses.count_documents({"owner_company_id": str(company_id)})
        total_modules = 0  # await db.modules.count_documents({"owner_company_id": str(company_id)})
        total_scenarios = 0  # await db.scenarios.count_documents({"owner_company_id": str(company_id)})
        
        # Update company statistics
        await db.companies.update_one(
            {"_id": str(company_id)},
            {
                "$set": {
                    "total_users": total_users,
                    "total_admins": total_admins,
                    "total_superadmins": total_superadmins,
                    "total_courses": total_courses,
                    "total_modules": total_modules,
                    "total_scenarios": total_scenarios,
                    "updated_at": datetime.now()
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error updating company statistics: {str(e)}")
        return False

async def get_company_analytics(db: Any, company_id: UUID, requesting_user_id: UUID) -> CompanyAnalytics:
    """Get comprehensive analytics for a company"""
    # Get the requesting user
    user = await db.users.find_one({"_id": str(requesting_user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_role = user.get("role")
    user_company_id = user.get("company_id")
    
    # Check permissions
    if user_role == UserRole.BOSS_ADMIN:
        # Boss admin can see any company's analytics
        pass
    elif user_role == UserRole.SUPERADMIN and str(user_company_id) == str(company_id):
        # Superadmin can see their own company's analytics
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's analytics"
        )
    
    # Get company info
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Calculate user statistics
    total_users = await db.users.count_documents({"company_id": str(company_id)})
    
    user_stats = {}
    for role in [UserRole.USER, UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
        count = await db.users.count_documents({
            "company_id": str(company_id),
            "role": role
        })
        user_stats[role] = count
    
    # Demo user statistics
    demo_users = await db.users.count_documents({
        "company_id": str(company_id),
        "account_type": AccountType.DEMO
    })
    
    expired_demos = await db.users.count_documents({
        "company_id": str(company_id),
        "account_type": AccountType.DEMO,
        "demo_expires_at": {"$lt": datetime.now()}
    })
    
    expiring_soon = await db.users.count_documents({
        "company_id": str(company_id),
        "account_type": AccountType.DEMO,
        "demo_expires_at": {
            "$gte": datetime.now(),
            "$lte": datetime.now() + timedelta(days=7)
        }
    })
    
    user_stats.update({
        "total_users": total_users,
        "demo_users": demo_users,
        "expired_demo_users": expired_demos,
        "expiring_demo_users": expiring_soon
    })
    
    # Course completion stats (mock data for now)
    course_completion_stats = {
        "total_courses": 0,
        "completed_courses": 0,
        "in_progress_courses": 0,
        "average_completion_rate": 0.0
    }
    
    # Usage statistics (mock data for now)
    usage_stats = {
        "active_sessions": 0,
        "total_logins_today": 0,
        "total_logins_week": 0,
        "average_session_duration": 0
    }
    
    # Performance metrics (mock data for now)
    performance_metrics = {
        "user_engagement_score": 75.0,
        "course_completion_rate": 68.5,
        "demo_conversion_rate": 23.4,
        "user_satisfaction_score": 4.2
    }
    
    # Create analytics period
    analytics_period = {
        "start_date": datetime.now() - timedelta(days=30),
        "end_date": datetime.now()
    }
    
    return CompanyAnalytics(
        company_id=company_id,
        company_name=company.name,
        user_stats=user_stats,
        course_completion_stats=course_completion_stats,
        usage_stats=usage_stats,
        performance_metrics=performance_metrics,
        analytics_period=analytics_period,
        last_updated=datetime.now()
    )

async def get_all_companies_analytics(db: Any, requesting_user_id: UUID) -> List[Dict[str, Any]]:
    """Get analytics for all companies (boss admin only)"""
    # Get the requesting user
    user = await db.users.find_one({"_id": str(requesting_user_id)})
    if not user or user.get("role") != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only boss admins can view all companies analytics"
        )
    
    # Get all companies
    companies = await get_all_companies(db)
    
    analytics_list = []
    for company in companies:
        try:
            # Calculate basic analytics for each company
            total_users = await db.users.count_documents({"company_id": str(company.id)})
            total_admins = await db.users.count_documents({
                "company_id": str(company.id),
                "role": {"$in": [UserRole.ADMIN, UserRole.SUPERADMIN]}
            })
            demo_users = await db.users.count_documents({
                "company_id": str(company.id),
                "account_type": AccountType.DEMO
            })
            expired_demos = await db.users.count_documents({
                "company_id": str(company.id),
                "account_type": AccountType.DEMO,
                "demo_expires_at": {"$lt": datetime.now()}
            })
            
            analytics_list.append({
                "company_id": str(company.id),
                "company_name": company.name,
                "company_type": company.company_type,
                "status": company.status,
                "total_users": total_users,
                "total_admins": total_admins,
                "demo_users": demo_users,
                "expired_demo_users": expired_demos,
                "generated_at": datetime.now()
            })
            
        except Exception as e:
            print(f"Error getting analytics for company {company.id}: {str(e)}")
            continue
    
    return analytics_list

async def toggle_company_status(db: Any, company_id: UUID, new_status: CompanyStatus, 
                               updated_by: UUID) -> CompanyDB:
    """Toggle company status (active/inactive/suspended/demo)"""
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check permissions
    user = await db.users.find_one({"_id": str(updated_by)})
    if not user or user.get("role") != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only boss admins can change company status"
        )
    
    # Update status
    await db.companies.update_one(
        {"_id": str(company_id)},
        {
            "$set": {
                "status": new_status,
                "updated_at": datetime.now()
            }
        }
    )
    
    # If suspending company, deactivate all users
    if new_status == CompanyStatus.SUSPENDED:
        await db.users.update_many(
            {"company_id": str(company_id)},
            {"$set": {"is_active": False, "updated_at": datetime.now()}}
        )
    elif new_status == CompanyStatus.ACTIVE:
        # Reactivate users when company becomes active
        await db.users.update_many(
            {"company_id": str(company_id)},
            {"$set": {"is_active": True, "updated_at": datetime.now()}}
        )
    
    updated_company = await db.companies.find_one({"_id": str(company_id)})
    return CompanyDB(**updated_company)

async def calculate_company_statistics(db: Any, company_id: UUID) -> Dict[str, int]:
    """Calculate company statistics dynamically"""
    try:
        # Count users by role
        total_users = await db.users.count_documents({"company_id": str(company_id)})
        total_admins = await db.users.count_documents({
            "company_id": str(company_id),
            "role": UserRole.ADMIN
        })
        total_superadmins = await db.users.count_documents({
            "company_id": str(company_id),
            "role": UserRole.SUPERADMIN
        })
        
        # Count content (implement when you have these collections)
        total_courses =0 #await db.courses.count_documents({"owner_company_id": str(company_id)}) if "courses" in await db.list_collection_names() else 0
        total_modules =0 #await db.modules.count_documents({"owner_company_id": str(company_id)}) if "modules" in await db.list_collection_names() else 0
        total_scenarios =0 #await db.scenarios.count_documents({"owner_company_id": str(company_id)}) if "scenarios" in await db.list_collection_names() else 0
        
        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_superadmins": total_superadmins,
            "total_courses": total_courses,
            "total_modules": total_modules,
            "total_scenarios": total_scenarios
        }
    except Exception as e:
        print(f"Error calculating company statistics: {str(e)}")
        return {
            "total_users": 0,
            "total_admins": 0,
            "total_superadmins": 0,
            "total_courses": 0,
            "total_modules": 0,
            "total_scenarios": 0
        }

# API Endpoints

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(
    company: CompanyCreate,
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Create a new company (boss admin only)"""
    created_company = await create_company(db, company, boss_admin.id)
    
    # Calculate stats dynamically for response
    stats = await calculate_company_statistics(db, created_company.id)
    company_dict = created_company.dict()
    company_dict.update(stats)
    
    return CompanyResponse(**company_dict)


@router.get("/", response_model=List[CompanyResponse])
async def read_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[CompanyStatus] = Query(None, description="Filter by company status"),
    company_type_filter: Optional[CompanyType] = Query(None, description="Filter by company type"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get companies (boss admin: all, others: their own)"""
    companies = []
    
    if current_user.role == UserRole.BOSS_ADMIN:
        companies = await get_all_companies(db, skip, limit, status_filter)
        if company_type_filter:
            companies = [c for c in companies if c.company_type == company_type_filter]
    else:
        company = await get_company_by_id(db, current_user.company_id)
        if company:
            companies = [company]
    
    # Calculate stats for each company and return response
    response_companies = []
    for company in companies:
        stats = await calculate_company_statistics(db, company.id)
        company_dict = company.dict()
        company_dict.update(stats)
        response_companies.append(CompanyResponse(**company_dict))
    
    return response_companies

@router.get("/{company_id}", response_model=CompanyResponse)
async def read_company(
    company_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get specific company by ID"""
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    # Check permissions
    if current_user.role != UserRole.BOSS_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company"
        )
    
    # Calculate statistics dynamically
    stats = await calculate_company_statistics(db, company_id)
    company_dict = company.dict()
    company_dict.update(stats)
    
    return CompanyResponse(**company_dict)

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company_endpoint(
    company_id: UUID,
    company_update: CompanyUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Update a company"""
    updated_company = await update_company(db, company_id, company_update, current_user.id)
    if not updated_company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    # Calculate stats dynamically for response
    stats = await calculate_company_statistics(db, updated_company.id)
    company_dict = updated_company.dict()
    company_dict.update(stats)
    
    return CompanyResponse(**company_dict)
@router.delete("/{company_id}", response_model=Dict[str, bool])
async def delete_company_endpoint(
    company_id: UUID,
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Delete a company (boss admin only)"""
    deleted = await delete_company(db, company_id, boss_admin.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    return {"success": True}

@router.post("/{company_id}/status", response_model=CompanyResponse)
async def toggle_company_status_endpoint(
    company_id: UUID,
    new_status: CompanyStatus = Body(..., embed=True),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Toggle company status (active/inactive/suspended/demo)"""
    updated_company = await toggle_company_status(db, company_id, new_status, boss_admin.id)
    return CompanyResponse(**updated_company.dict())

@router.get("/{company_id}/analytics", response_model=CompanyAnalytics)
async def get_company_analytics_endpoint(
    company_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get analytics for a specific company"""
    return await get_company_analytics(db, company_id, current_user.id)

@router.get("/{company_id}/subsidiaries", response_model=List[CompanyResponse])
async def get_company_subsidiaries(
    company_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get subsidiary companies"""
    # Check permissions
    if current_user.role != UserRole.BOSS_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's subsidiaries"
        )
    
    subsidiaries = await get_companies_by_parent(db, company_id)
    return [CompanyResponse(**company.dict()) for company in subsidiaries]

@router.get("/{company_id}/users", response_model=List[Dict[str, Any]])
async def get_company_users(
    company_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role_filter: Optional[UserRole] = Query(None, description="Filter by user role"),
    account_type_filter: Optional[AccountType] = Query(None, description="Filter by account type"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get users in a specific company"""
    # Check permissions
    if current_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can view users in any company
        pass
    elif current_user.role == UserRole.SUPERADMIN and current_user.company_id == company_id:
        # Superadmin can view users in their company
        pass
    elif current_user.role == UserRole.ADMIN and current_user.company_id == company_id:
        # Admin can view users in their company (but will be filtered by managed users)
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's users"
        )
    
    # Build query
    query = {"company_id": str(company_id)}
    
    if role_filter:
        query["role"] = role_filter
    
    if account_type_filter:
        query["account_type"] = account_type_filter
    
    # For admins, only show their managed users
    if current_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        managed_users = admin_data.get("managed_users", [])
        if managed_users:
            query["_id"] = {"$in": managed_users}
        else:
            # Admin has no managed users
            return []
    
    users = []
    cursor = db.users.find(query).skip(skip).limit(limit)
    async for user_doc in cursor:
        # Convert MongoDB document to dict and clean up
        user_dict = dict(user_doc)
        user_dict["id"] = user_dict.pop("_id")
        
        # Add demo expiry status
        if user_dict.get("account_type") == AccountType.DEMO and user_dict.get("demo_expires_at"):
            user_dict["is_demo_expired"] = datetime.now() > user_dict["demo_expires_at"]
        else:
            user_dict["is_demo_expired"] = False
        
        users.append(user_dict)
    
    return users



@router.post("/transfer-course", response_model=Dict[str, Any])
async def transfer_course_endpoint(
    course_id: UUID = Body(..., description="Unique identifier of the course to transfer"),
    to_company_id: UUID = Body(..., description="Unique identifier of the target company"),
    new_admin_id: UUID = Body(..., description="Unique identifier of the new admin owner"),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
) -> Dict[str, Any]:
    """
    Transfer a course to a new company and admin (BOSS_ADMIN only).
    
    This endpoint transfers:
    - Course ownership
    - All associated modules
    - All scenarios within modules
    - Archives existing user assignments
    
    Args:
        course_id: UUID of the course to transfer
        to_company_id: UUID of the target company
        new_admin_id: UUID of the new admin owner
        db: Database dependency
        boss_admin: Authenticated BOSS_ADMIN user
    
    Returns:
        Dictionary containing the transfer result
    
    Raises:
        HTTPException: If target company or new admin is invalid
    """
    # Validate target company exists
    target_company = await db.companies.find_one({"_id": str(to_company_id)})
    if not target_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target company not found"
        )

    # Validate new admin exists in target company with proper role
    new_admin = await db.users.find_one({
        "_id": str(new_admin_id),
        "company_id": str(to_company_id),
        "role": {"$in": ["admin", "superadmin"]},
        "is_active": True
    })
    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New admin must be an active admin or superadmin in the target company"
        )

    # Execute course transfer
    result = await transfer_course_complete(
        db=db,
        course_id=course_id,
        to_company_id=to_company_id,
        new_admin_id=new_admin_id,
        boss_admin_id=boss_admin.id
    )

    return result

@router.get("/transfer-history", response_model=List[Dict[str, Any]])
async def get_transfer_history(
    company_id: Optional[UUID] = Query(None, description="Filter by company ID (from or to)"),
    course_id: Optional[UUID] = Query(None, description="Filter by specific course ID"),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
) -> List[Dict[str, Any]]:
    """
    Retrieve course transfer history (BOSS_ADMIN only).
    
    Returns a list of transfer records, optionally filtered by company or course.
    
    Args:
        company_id: Optional UUID to filter by source or destination company
        course_id: Optional UUID to filter by specific course
        db: Database dependency
        boss_admin: Authenticated BOSS_ADMIN user
    
    Returns:
        List of dictionaries containing transfer history details
    """
    query = {"transfer_history": {"$exists": True, "$ne": []}}

    # Apply filters if provided
    if company_id:
        query["$or"] = [
            {"transfer_history.from_company": str(company_id)},
            {"transfer_history.to_company": str(company_id)}
        ]
    
    if course_id:
        query["_id"] = str(course_id)

    transfers = []
    async for course in db.courses.find(query):
        for transfer in course.get("transfer_history", []):
            transfers.append({
                "course_id": course["_id"],
                "course_title": course.get("title", "Unknown"),
                "from_company": transfer["from_company"],
                "to_company": transfer["to_company"],
                "transferred_by": transfer["transferred_by"],
                "transferred_at": transfer["transferred_at"]
            })

    # Sort transfers by date (newest first)
    transfers.sort(key=lambda x: x["transferred_at"], reverse=True)

    return transfers