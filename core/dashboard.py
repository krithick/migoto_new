# core/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user

# Create router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Database dependency
async def get_database():
    from database import get_db
    return await get_db()

# User Stats Endpoint
@router.get("/user-stats", response_model=Dict[str, int])
async def get_user_stats(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get user statistics:
    - Total users
    - Active users
    - Assigned users (to current admin)
    - Unassigned users (not assigned to any admin)
    
    Admin users see stats for users they manage.
    Superadmin users see stats for all users.
    """
    stats = {
        "total_users": 0,
        "active_users": 0,
        "assigned_users": 0,
        "unassigned_users": 0
    }
    
    # Set up base query for user filters
    base_query = {"role": UserRole.USER.value}
    
    # For admin, only show managed users
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        
        # Get total users managed by this admin
        stats["total_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "_id": {"$in": managed_users}
        })
        
        # Get active users managed by this admin
        stats["active_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "is_active": True,
            "_id": {"$in": managed_users}
        })
        
        # All managed users are "assigned" (to this admin)
        stats["assigned_users"] = stats["total_users"]
        stats["unassigned_users"] = 0
    else:
        # Superadmin sees all users
        stats["total_users"] = await db.users.count_documents({"role": UserRole.USER.value})
        stats["active_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "is_active": True
        })
        
        # Count users assigned to any admin
        all_admins = await db.users.find({"role": UserRole.ADMIN.value}).to_list(length=None)
        assigned_user_ids = set()
        
        for admin in all_admins:
            managed_users = admin.get("managed_users", [])
            assigned_user_ids.update(managed_users)
        
        stats["assigned_users"] = len(assigned_user_ids)
        stats["unassigned_users"] = stats["total_users"] - stats["assigned_users"]
    
    return stats

# Course Stats Endpoint
@router.get("/course-stats", response_model=Dict[str, int])
async def get_course_stats(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get course statistics:
    - Total courses
    - Created by current user
    - Created by other admins
    - Created by superadmin
    - Pre-feeded courses
    """
    stats = {
        "total_courses": 0,
        "created_by_me": 0,
        "created_by_other_admins": 0,
        "created_by_superadmin": 0,
        "pre_feeded": 0  # Assuming pre-feeded courses have a special flag or creator
    }
    
    # Get total courses
    stats["total_courses"] = await db.courses.count_documents({})
    
    # Get courses created by current user
    stats["created_by_me"] = await db.courses.count_documents({
        "created_by": str(admin_user.id)
    })
    
    # Get superadmin users
    superadmins = await db.users.find({"role": UserRole.SUPERADMIN.value}).to_list(length=None)
    superadmin_ids = [str(admin["_id"]) for admin in superadmins]
    
    # Get courses created by superadmins
    stats["created_by_superadmin"] = await db.courses.count_documents({
        "created_by": {"$in": superadmin_ids}
    })
    
    # Get other admin users (excluding current user if they're an admin)
    admin_query = {"role": UserRole.ADMIN.value}
    if admin_user.role == UserRole.ADMIN:
        admin_query["_id"] = {"$ne": str(admin_user.id)}
    
    other_admins = await db.users.find(admin_query).to_list(length=None)
    other_admin_ids = [str(admin["_id"]) for admin in other_admins]
    
    # Get courses created by other admins
    stats["created_by_other_admins"] = await db.courses.count_documents({
        "created_by": {"$in": other_admin_ids}
    })
    
    # Determine pre-feeded courses (assuming system user or null creator)
    # This may need adjustment based on how pre-feeded courses are marked
    stats["pre_feeded"] = stats["total_courses"] - (
        stats["created_by_me"] + 
        stats["created_by_other_admins"] + 
        stats["created_by_superadmin"]
    )
    
    return stats

# User Analysis Reports Endpoint
@router.get("/user-analysis", response_model=List[Dict[str, Any]])
async def get_user_analysis_reports(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    time_period: Optional[int] = Query(None, description="Time period in days"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get analysis reports for users assigned to the current admin.
    Filter by score range and time period if specified.
    """
    # For admin users, get managed user IDs
    user_ids = []
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            user_ids = admin_data["managed_users"]
    
    # Build query
    query = {}
    
    # Filter by user IDs for admin
    if admin_user.role == UserRole.ADMIN and user_ids:
        query["user_id"] = {"$in": user_ids}
    
    # Add score filters if specified
    if min_score is not None or max_score is not None:
        query["overall_evaluation.total_score"] = {}
        if min_score is not None:
            query["overall_evaluation.total_score"]["$gte"] = min_score
        if max_score is not None:
            query["overall_evaluation.total_score"]["$lte"] = max_score
    
    # Add time period filter if specified
    if time_period is not None:
        start_date = datetime.now() - timedelta(days=time_period)
        query["timestamp"] = {"$gte": start_date}
    
    # Execute query with pagination
    cursor = db.analysis.find(query).sort("overall_evaluation.total_score", -1).skip(offset).limit(limit)
    reports = await cursor.to_list(length=limit)
    
    # Process results to include user and scenario information
    result = []
    for report in reports:
        # Convert MongoDB _id to id
        report["id"] = str(report.pop("_id"))
        
        # Get user information
        user = await db.users.find_one({"_id": report["user_id"]})
        user_info = {
            "id": report["user_id"],
            "name": f"{user['username']}" if user else "Unknown User",
            "email": user.get("email", "No email") if user else "No email"
        }
        
        # Get session information
        session = await db.sessions.find_one({"_id": report["session_id"]})
        scenario_name = session.get("scenario_name", "Unknown Scenario") if session else "Unknown Scenario"
        
        # Format data for response
        result.append({
            "id": report["id"],
            "user": user_info,
            "scenario_name": scenario_name,
            "overall_score": report.get("overall_evaluation", {}).get("total_score", 0),
            "performance_category": report.get("overall_evaluation", {}).get("user_performance_category", "Unknown"),
            "timestamp": report.get("timestamp", datetime.now()),
            # Include other relevant fields as needed
        })
    
    return result


