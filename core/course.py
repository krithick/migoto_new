from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from models.course_models import CourseCreate, CourseResponse, CourseWithModulesResponse, CourseDB, CourseBase, ContentVisibility, CourseUpdate
from models.modules_models import ModuleResponse
from models.user_models import UserDB, UserRole
from models.company_models import CompanyType, CompanyDB

from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.module_assignment import get_user_course_module_assignments
from core.tier_utils import (
    enforce_content_creation_limit,
    enforce_chat_session_limit, 
    enforce_analysis_limit,
    check_feature_permission,
    enforce_feature_access
)
# Create router
router = APIRouter(prefix="/courses", tags=["Courses"])

# Database dependency
async def get_database():
    from database import get_db
    return await get_db()

# Company hierarchy helper functions
async def get_company_by_id(db: Any, company_id: UUID) -> Optional[CompanyDB]:
    """Get company by ID"""
    company = await db.companies.find_one({"_id": str(company_id)})
    if company:
        return CompanyDB(**company)
    return None

async def get_company_hierarchy_type(db: Any, company_id: UUID) -> CompanyType:
    """Get company type for hierarchy rules"""
    company = await get_company_by_id(db, company_id)
    return company.company_type if company else CompanyType.CLIENT

async def is_mother_company_content(db: Any, content_company_id: UUID) -> bool:
    """Check if content belongs to MOTHER company"""
    company_type = await get_company_hierarchy_type(db, content_company_id)
    return company_type == CompanyType.MOTHER

# Company hierarchy access control functions
async def get_accessible_courses_for_user(db: Any, user: UserDB) -> List[CourseDB]:
    """
    Get courses user can ACCESS based on company hierarchy:
    
    BOSS_ADMIN: All courses from all companies
    SUPERADMIN/ADMIN: 
    - Their own company courses (all visibility levels)
    - MOTHER company courses (regardless of visibility)
    USER: Only assigned courses
    """
    courses = []
    
    if user.role == UserRole.USER:
        # Users only see assigned courses - use existing logic
        user_data = user.dict()
        assigned_course_ids = user_data.get("assigned_courses", [])
        print(f"Raw assigned_courses: {assigned_course_ids}")
        print(f"Types: {[type(x) for x in assigned_course_ids]}")
        assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
        
        if assigned_course_ids_str:
            cursor = db.courses.find({
                "_id": {"$in": assigned_course_ids_str},
                "is_archived": False  # Don't show archived courses
            })
            async for document in cursor:
                courses.append(CourseDB(**document))
    
    elif user.role == UserRole.BOSS_ADMIN:
        # Boss admin sees ALL courses from ALL companies
        cursor = db.courses.find({"is_archived": False})
        async for document in cursor:
            courses.append(CourseDB(**document))
    
    else:  # ADMIN or SUPERADMIN
        # Get user's company type
        user_company_type = await get_company_hierarchy_type(db, user.company_id)
        
        if user_company_type == CompanyType.MOTHER:
            # MOTHER company admins see all courses
            cursor = db.courses.find({"is_archived": False})
            async for document in cursor:
                courses.append(CourseDB(**document))
        else:
            # CLIENT/SUBSIDIARY company admins see:
            # 1. Their own company courses
            # 2. MOTHER company courses
            
            # Get all MOTHER companies
            mother_companies = []
            mother_cursor = db.companies.find({"company_type": CompanyType.MOTHER})
            async for company_doc in mother_cursor:
                mother_companies.append(company_doc["_id"])
            
            # Build query for accessible courses
            accessible_companies = [str(user.company_id)] + mother_companies
            print(f"Accessible companies for user {user.id}: {accessible_companies}")
            cursor = db.courses.find({
                "company_id": {"$in": accessible_companies},
                "is_archived": False
            })
            async for document in cursor:
                print(document["_id"],"courses")
                courses.append(CourseDB(**document))
    
    return courses

async def can_user_assign_course(db: Any, user: UserDB, course: CourseDB) -> bool:
    """
    Check if user can ASSIGN a specific course based on:
    1. Company hierarchy rules
    2. Content visibility settings
    3. User role permissions
    """
    # Users cannot assign courses
    if user.role == UserRole.USER:
        return False
    
    # Boss admin can assign any course
    if user.role == UserRole.BOSS_ADMIN:
        return True
    
    # Check if course is archived
    if course.is_archived:
        return False
    user_company_str = str(user.company_id)
    course_company_str = str(course.company_id)
    user_id_str = str(user.id)
    created_by_str = str(course.created_by)    
    # Check company hierarchy access
    user_company_type = await get_company_hierarchy_type(db, user.company_id)
    course_company_type = await get_company_hierarchy_type(db, course.company_id)
    
    # Same company assignment
    # if user.company_id == course_company_str:
    #     # Check visibility rules
    #     if course.visibility == ContentVisibility.CREATOR_ONLY:
    #         return course.created_by == user.id
    #     elif course.visibility == ContentVisibility.COMPANY_WIDE:
    #         return True  # Any admin/superadmin in same company can assign
    if user_company_str == course_company_str:
        if course.visibility == ContentVisibility.CREATOR_ONLY:
            return user_id_str == created_by_str  # FIXED: string comparison
        elif course.visibility == ContentVisibility.COMPANY_WIDE:
            return True    
    
    # Cross-company assignment (MOTHER → CLIENT/SUBSIDIARY)
    if course_company_type == CompanyType.MOTHER:
        # MOTHER company courses can be assigned by any admin/superadmin
        # regardless of visibility setting
        return True
    
    # All other cases: no access
    return False

async def get_assignable_courses_for_user(db: Any, user: UserDB) -> List[CourseDB]:
    """Get courses that user can ASSIGN to others"""
    if user.role == UserRole.USER:
        return []
    
    accessible_courses = await get_accessible_courses_for_user(db, user)
    assignable_courses = []
    
    for course in accessible_courses:
        if await can_user_assign_course(db, user, course):
            print(f"User {user.id} can assign course {course.id}")
            assignable_courses.append(course)
    
    return assignable_courses

# Updated course operations with company context
async def get_courses(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[CourseDB]:
    """Get courses based on user's company hierarchy access"""
    if not current_user:
        return []
    
    accessible_courses = await get_accessible_courses_for_user(db, current_user)
    
    # Apply pagination
    start_idx = skip
    end_idx = skip + limit
    return accessible_courses[start_idx:end_idx]

async def get_course(db: Any, course_id: UUID, current_user: Optional[UserDB] = None) -> Optional[CourseDB]:
    """Get a course by ID with company hierarchy permission checks"""
    # Find the course
    course_doc = await db.courses.find_one({"_id": str(course_id)})
    if not course_doc:
        return None
    
    course = CourseDB(**course_doc)
    
    # Check if archived
    if course.is_archived:
        # Only boss admin can see archived courses
        if not current_user or current_user.role != UserRole.BOSS_ADMIN:
            return None
    
    # Check access permissions
    if current_user:
        accessible_courses = await get_accessible_courses_for_user(db, current_user)
        accessible_course_ids = [str(c.id) for c in accessible_courses]
        
        if str(course_id) not in accessible_course_ids:
            return None
    
    return course

async def get_course_with_modules(
    db: Any, 
    course_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """Get a course with modules expanded, respecting company hierarchy"""
    # First check if user can access this course
    course = await get_course(db, course_id, current_user)
    if not course:
        return None
    
    # Get course with expanded modules
    course_dict = course.dict()
    
    # Get modules for this course
    module_ids = course_dict.get("modules", [])
    module_ids_str = [str(module_id) for module_id in module_ids]
    
    modules = []
    
    # For regular users, filter modules to only show assigned ones
    if current_user and current_user.role == UserRole.USER:
        # Get module assignments for this user and course
        assignments_cursor = db.user_module_assignments.find({
            "user_id": str(current_user.id),
            "course_id": str(course_id),
            "is_archived": False  # Don't show archived assignments
        })
        
        # Get assigned module IDs
        assigned_module_ids = []
        async for assignment in assignments_cursor:
            assigned_module_ids.append(assignment["module_id"])
        
        # Filter module_ids to only show assigned ones
        module_ids_str = [m_id for m_id in module_ids_str if m_id in assigned_module_ids]
    
    # Fetch modules
    for module_id in module_ids_str:
        module = await db.modules.find_one({
            "_id": module_id,
            "is_archived": False  # Don't show archived modules
        })
        if module:
            module["id"] = module.pop("_id")
            
            # Add assignment info for regular users
            if current_user and current_user.role == UserRole.USER:
                assignment = await db.user_module_assignments.find_one({
                    "user_id": str(current_user.id),
                    "module_id": module_id,
                    "is_archived": False
                })
                
                if assignment:
                    module["assigned"] = True
                    module["completed"] = assignment.get("completed", False)
                    module["completed_date"] = assignment.get("completed_date")
            
            modules.append(module)
    
    # Replace module IDs with module data
    course_dict["modules"] = modules
    
    return CourseWithModulesResponse(**course_dict)

async def create_course(db: Any, course: CourseCreate, created_by: UUID, role: UserRole) -> CourseDB:
    """Create a new course with company context"""
    # Get creator info
    creator = await db.users.find_one({"_id": str(created_by)})
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid creator"
        )
    
    creator_company_id = creator["company_id"]
    
    # Validate creator permissions
    if role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and superadmins can create courses"
        )
    # await enforce_content_creation_limit(db, creator_company_id, "course")
    # Create CourseDB model with company context
    course_dict = course.dict()
    
    course_db = CourseDB(
        **course_dict,
        creater_role=role,
        created_by=created_by,
        company_id=creator_company_id,  # Auto-fill company from creator
        visibility=ContentVisibility.CREATOR_ONLY,  # DEFAULT
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    course_dict = course_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in course_dict:
        course_dict["_id"] = str(course_dict["_id"])
    
    if "modules" in course_dict and course_dict["modules"]:
        course_dict["modules"] = [str(module_id) for module_id in course_dict["modules"]]
    
    course_dict["created_by"] = str(course_dict["created_by"])
    course_dict["company_id"] = str(course_dict["company_id"])
    
    result = await db.courses.insert_one(course_dict)
    created_course = await db.courses.find_one({"_id": str(result.inserted_id)})
    
    return CourseDB(**created_course)

async def update_course(
    db: Any, 
    course_id: UUID, 
    course_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[CourseDB]:
    """Update a course with company hierarchy permission checks"""
    # Get the course to update
    course_doc = await db.courses.find_one({"_id": str(course_id)})
    if not course_doc:
        return None
    
    course = CourseDB(**course_doc)
    
    # Get the user making the update
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    updater_user = UserDB(**updater)
    
    # Check permissions
    if updater_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can update any course
        pass
    elif updater_user.role in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        # Check if user can assign this course (same permission logic)
        if not await can_user_assign_course(db, updater_user, course):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this course"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update courses"
        )
    
    # Add updated timestamp
    course_updates["updated_at"] = datetime.now()
    
    # Convert module UUIDs to strings if present
    if "modules" in course_updates and course_updates["modules"]:
        course_updates["modules"] = [str(module_id) for module_id in course_updates["modules"]]
    
    # Update in database
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$set": course_updates}
    )
    
    updated_course = await db.courses.find_one({"_id": str(course_id)})
    if updated_course:
        return CourseDB(**updated_course)
    return None

async def archive_course(db: Any, course_id: UUID, archived_by: UUID, reason: str = "Manual archive") -> bool:
    """Archive a course (soft delete) instead of hard deletion"""
    # Get the course
    course_doc = await db.courses.find_one({"_id": str(course_id)})
    if not course_doc:
        return False
    
    course = CourseDB(**course_doc)
    
    # Get the user making the archive
    archiver = await db.users.find_one({"_id": str(archived_by)})
    if not archiver:
        return False
    
    archiver_user = UserDB(**archiver)
    
    # Check permissions (same as update permissions)
    if archiver_user.role == UserRole.BOSS_ADMIN:
        pass
    elif archiver_user.role in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        if not await can_user_assign_course(db, archiver_user, course):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to archive this course"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive courses"
        )
    
    # Archive the course
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": reason,
            "updated_at": datetime.now()
        }}
    )
    
    # Archive all assignments for this course (but keep for history)
    await db.user_course_assignments.update_many(
        {"course_id": str(course_id), "is_archived": False},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": f"Course archived: {reason}"
        }}
    )
    
    return True

async def delete_course(db: Any, course_id: UUID, deleted_by: UUID) -> bool:
    """Delete a course with permission checks - now just calls archive_course"""
    return await archive_course(db, course_id, deleted_by, "Course deleted")

async def publish_course(db: Any, course_id: UUID, publish_status: bool, updated_by: UUID) -> Optional[CourseDB]:
    """Publish or unpublish a course with company hierarchy permission checks"""
    course_doc = await db.courses.find_one({"_id": str(course_id)})
    if not course_doc:
        return None
    
    course = CourseDB(**course_doc)
    
    # Get the user making the update
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    updater_user = UserDB(**updater)
    
    # Check permissions (same as update permissions)
    if updater_user.role == UserRole.BOSS_ADMIN:
        pass
    elif updater_user.role in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        if not await can_user_assign_course(db, updater_user, course):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish/unpublish this course"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish/unpublish courses"
        )
    
    # Update the course
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$set": {"is_published": publish_status, "updated_at": datetime.now()}}
    )
    
    updated_course = await db.courses.find_one({"_id": str(course_id)})
    if updated_course:
        return CourseDB(**updated_course)
    return None

# API Endpoints with company hierarchy
@router.get("/", response_model=List[CourseResponse])
async def get_courses_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get courses based on company hierarchy access rules"""
    return await get_courses(db, skip, limit, current_user)

@router.get("/assignable", response_model=List[CourseResponse])
async def get_assignable_courses_endpoint(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get courses that current admin can assign to users"""
    return await get_assignable_courses_for_user(db, admin_user)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a specific course by ID with company hierarchy access checks"""
    course = await get_course(db, course_id, current_user)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or access denied")
    return course

@router.get("/{course_id}/full", response_model=CourseWithModulesResponse)
async def get_course_with_modules_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a course with all its modules expanded"""
    course = await get_course_with_modules(db, course_id, current_user)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or access denied")
    return course

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    course: CourseCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Create a new course with company context"""
    limit=await enforce_content_creation_limit(db, admin_user.company_id, "course")
    print("limit",limit)
    return await create_course(db, course, admin_user.id, admin_user.role)

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course_endpoint(
    course_id: UUID,
    course_updates: CourseUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Update a course by ID with company hierarchy permission checks"""
    course_updates_dict = course_updates.dict(exclude_unset=True)
    updated_course = await update_course(db, course_id, course_updates_dict, admin_user.id)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", response_model=Dict[str, bool])
async def delete_course_endpoint(
    course_id: UUID,
    archive_reason: str = Body("Manual deletion", embed=True),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Archive a course (soft delete) with company hierarchy permission checks"""
    archived = await archive_course(db, course_id, admin_user.id, archive_reason)
    if not archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return {"success": True, "archived": True}

@router.put("/{course_id}/publish", response_model=CourseResponse)
async def publish_course_endpoint(
    course_id: UUID,
    publish_data: Dict[str, bool] = Body(..., example={"publish": True}),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Publish or unpublish a course with company hierarchy permission checks"""
    publish_status = publish_data.get("publish", True)
    updated_course = await publish_course(db, course_id, publish_status, admin_user.id)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.put("/{course_id}/visibility", response_model=CourseResponse)
async def update_course_visibility_endpoint(
    course_id: UUID,
    visibility_data: Dict[str, str] = Body(..., example={"visibility": "company_wide"}),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Update course visibility (creator_only vs company_wide)"""
    new_visibility = visibility_data.get("visibility")
    
    if new_visibility not in [ContentVisibility.CREATOR_ONLY, ContentVisibility.COMPANY_WIDE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visibility. Must be 'creator_only' or 'company_wide'"
        )
    
    course_updates = {"visibility": new_visibility}
    updated_course = await update_course(db, course_id, course_updates, admin_user.id)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.get("/admin/assignable-content", response_model=Dict[str, Any])
async def get_assignable_content(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get all content that current admin can assign"""
    
    # Get assignable courses
    from core.company_access_control import get_user_accessible_courses
    accessible_courses = await get_user_accessible_courses(db, admin_user)
    
    assignable_courses = []
    for course in accessible_courses:
        if await can_user_assign_course(db, admin_user, course):
            # Get course with modules and scenarios
            course_dict = course.dict()
            
            # Get modules for this course
            modules = []
            for module_id in course_dict.get("modules", []):
                module = await db.modules.find_one({"_id": str(module_id)})
                if module and not module.get("is_archived", False):
                    module_dict = dict(module)
                    module_dict["id"] = module_dict.pop("_id")
                    
                    # Get scenarios for this module
                    scenarios = []
                    for scenario_id in module.get("scenarios", []):
                        scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
                        if scenario and not scenario.get("is_archived", False):
                            scenario_dict = dict(scenario)
                            scenario_dict["id"] = scenario_dict.pop("_id")
                            scenarios.append(scenario_dict)
                    
                    module_dict["scenarios"] = scenarios
                    modules.append(module_dict)
            
            course_dict["modules"] = modules
            assignable_courses.append(course_dict)
    
    # Get manageable users
    manageable_users = []
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_user_ids = admin_data.get("managed_users", []) if admin_data else []
        
        for user_id in managed_user_ids:
            user = await db.users.find_one({"_id": user_id})
            if user:
                user_dict = dict(user)
                user_dict["id"] = user_dict.pop("_id")
                manageable_users.append(user_dict)
    
    elif admin_user.role == UserRole.SUPERADMIN:
        cursor = db.users.find({
            "company_id": str(admin_user.company_id),
            "role": UserRole.USER
        })
        async for user_doc in cursor:
            user_dict = dict(user_doc)
            user_dict["id"] = user_dict.pop("_id")
            manageable_users.append(user_dict)
    
    return {
        "assignable_courses": assignable_courses,
        "manageable_users": manageable_users,
        "admin_info": {
            "role": admin_user.role,
            "company_id": str(admin_user.company_id),
            "can_assign": len(assignable_courses) > 0
        }
    }