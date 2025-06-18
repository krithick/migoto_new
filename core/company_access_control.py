# core/company_access_control.py - Company-Aware Access Control

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from fastapi import HTTPException, status
from models.user_models import UserDB, UserRole
from models.company_models import CompanyDB, CompanyType
from models.course_models import CourseDB, ContentVisibility, ContentStatus
from models.modules_models import ModuleDB
from models.scenario_models import ScenarioDB
from datetime import datetime
async def get_user_accessible_courses(
    db: Any, 
    user: UserDB,
    skip: int = 0,
    limit: int = 100,
    include_archived: bool = False
) -> List[CourseDB]:
    """
    Get courses that user can access based on company hierarchy and role
    """
    # Get user's company
    user_company = await db.companies.find_one({"_id": str(user.company_id)})
    if not user_company:
        return []
    
    # Build query based on user role and company hierarchy
    query = {"status": {"$ne": ContentStatus.ARCHIVED}} if not include_archived else {}
    
    if user.role == UserRole.BOSS_ADMIN:
        # Boss admin can see all courses
        pass
    elif user.role in [UserRole.SUPERADMIN, UserRole.ADMIN]:
        # Can see:
        # 1. Mother company courses (available to all)
        # 2. Their own company's courses (based on visibility)
        
        accessible_conditions = []
        
        # Mother company courses
        mother_companies = await db.companies.find({"company_type": CompanyType.MOTHER}).to_list(length=None)
        mother_company_ids = [str(company["_id"]) for company in mother_companies]
        
        if mother_company_ids:
            accessible_conditions.append({
                "company_id": {"$in": mother_company_ids},
                "visibility": ContentVisibility.MOTHER_COMPANY
            })
        
        # Own company courses
        if user.role == UserRole.SUPERADMIN:
            # Superadmin can see all courses in their company
            accessible_conditions.append({
                "company_id": str(user.company_id)
            })
        elif user.role == UserRole.ADMIN:
            # Admin can see:
            # - Their own courses
            # - Company-wide visible courses in their company
            accessible_conditions.extend([
                {
                    "company_id": str(user.company_id),
                    "created_by": str(user.id)
                },
                {
                    "company_id": str(user.company_id),
                    "visibility": ContentVisibility.COMPANY_WIDE
                }
            ])
        
        if accessible_conditions:
            query["$or"] = accessible_conditions
        else:
            # No accessible courses
            return []
    
    elif user.role == UserRole.USER:
        # Regular users only see assigned courses
        user_data = user.dict()
        assigned_course_ids = [str(course_id) for course_id in user_data.get("assigned_courses", [])]
        if not assigned_course_ids:
            return []
        query["_id"] = {"$in": assigned_course_ids}
    
    # Execute query
    courses = []
    cursor = db.courses.find(query).skip(skip).limit(limit)
    async for document in cursor:
        courses.append(CourseDB(**document))
    
    return courses

async def can_user_access_course(
    db: Any,
    user: UserDB, 
    course: CourseDB
) -> bool:
    """Check if user can access a specific course"""
    
    if user.role == UserRole.BOSS_ADMIN:
        return True
    
    # Check if course is archived
    if course.status == ContentStatus.ARCHIVED:
        return user.role in [UserRole.BOSS_ADMIN, UserRole.SUPERADMIN]
    
    # Get course owner company
    course_company = await db.companies.find_one({"_id": str(course.company_id)})
    if not course_company:
        return False
    
    # Mother company courses available to all
    if course_company.get("company_type") == CompanyType.MOTHER and course.visibility == ContentVisibility.MOTHER_COMPANY:
        return user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    
    # Same company access
    if str(course.company_id) == str(user.company_id):
        if user.role == UserRole.SUPERADMIN:
            return True
        elif user.role == UserRole.ADMIN:
            return (
                str(course.created_by) == str(user.id) or 
                course.visibility == ContentVisibility.COMPANY_WIDE
            )
        elif user.role == UserRole.USER:
            # Check if course is assigned to user
            user_data = user.dict()
            assigned_courses = [str(c_id) for c_id in user_data.get("assigned_courses", [])]
            return str(course.id) in assigned_courses
    
    return False

async def can_user_assign_course(
    db: Any,
    user: UserDB, 
    course: CourseDB
) -> bool:
    """Check if user can assign a specific course"""
    
    # Users cannot assign courses
    if user.role == UserRole.USER:
        return False
    
    # Boss admin can assign any course
    if user.role == UserRole.BOSS_ADMIN:
        return True
    
    # Check if course is archived
    if course.is_archived:
        return False
    
    # Get course owner company
    course_company = await db.companies.find_one({"_id": str(course.company_id)})
    if not course_company:
        return False
    
    # Mother company courses available to all
    if course_company.get("company_type") == CompanyType.MOTHER:
        return True  # Any admin can assign MOTHER company content
    
    # Same company access
    if str(course.company_id) == str(user.company_id):
        if user.role == UserRole.SUPERADMIN:
            return True
        elif user.role == UserRole.ADMIN:
            return (
                str(course.created_by) == str(user.id) or 
                course.visibility == ContentVisibility.COMPANY_WIDE
            )
    
    return False

async def get_assignable_users_for_course(
    db: Any,
    admin_user: UserDB,
    course: CourseDB
) -> List[UserDB]:
    """Get list of users that admin can assign the course to"""
    
    if not await can_user_access_course(db, admin_user, course):
        return []
    
    users = []
    
    if admin_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can assign to any user in any company
        cursor = db.users.find({"role": UserRole.USER})
        async for user_doc in cursor:
            users.append(UserDB(**user_doc))
    
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin can assign to all users in their company
        cursor = db.users.find({
            "company_id": str(admin_user.company_id),
            "role": UserRole.USER
        })
        async for user_doc in cursor:
            users.append(UserDB(**user_doc))
    
    elif admin_user.role == UserRole.ADMIN:
        # Admin can assign to their managed users
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_user_ids = admin_data.get("managed_users", []) if admin_data else []
        
        if managed_user_ids:
            cursor = db.users.find({
                "_id": {"$in": managed_user_ids},
                "role": UserRole.USER
            })
            async for user_doc in cursor:
                users.append(UserDB(**user_doc))
    
    return users

async def archive_course_with_assignments(
    db: Any,
    course_id: UUID,
    archived_by: UUID,
    reason: Optional[str] = None
) -> bool:
    """Archive a course and handle its assignments"""
    from datetime import datetime
    
    try:
        # Archive the course
        await db.courses.update_one(
            {"_id": str(course_id)},
            {
                "$set": {
                    "status": ContentStatus.ARCHIVED,
                    "archived_at": datetime.now(),
                    "archived_by": str(archived_by),
                    "archive_reason": reason
                }
            }
        )
        
        # Archive related assignments (keep for history)
        await db.user_course_assignments.update_many(
            {"course_id": str(course_id)},
            {
                "$set": {
                    "status": "archived",
                    "archived_at": datetime.now(),
                    "archived_by": str(archived_by)
                }
            }
        )
        
        # Archive module assignments
        await db.user_module_assignments.update_many(
            {"course_id": str(course_id)},
            {
                "$set": {
                    "status": "archived", 
                    "archived_at": datetime.now(),
                    "archived_by": str(archived_by)
                }
            }
        )
        
        # Archive scenario assignments
        await db.user_scenario_assignments.update_many(
            {"course_id": str(course_id)},
            {
                "$set": {
                    "status": "archived",
                    "archived_at": datetime.now(), 
                    "archived_by": str(archived_by)
                }
            }
        )
        
        # Remove course from users' assigned_courses (but keep assignment records)
        await db.users.update_many(
            {"assigned_courses": str(course_id)},
            {"$pull": {"assigned_courses": str(course_id)}}
        )
        
        print(f"Successfully archived course {course_id} and related assignments")
        return True
        
    except Exception as e:
        print(f"Error archiving course {course_id}: {str(e)}")
        return False

async def restore_archived_course(
    db: Any,
    course_id: UUID,
    restored_by: UUID
) -> bool:
    """Restore an archived course"""
    from datetime import datetime
    
    try:
        # Restore the course
        await db.courses.update_one(
            {"_id": str(course_id)},
            {
                "$set": {
                    "status": ContentStatus.ACTIVE,
                    "updated_at": datetime.now()
                },
                "$unset": {
                    "archived_at": "",
                    "archived_by": "",
                    "archive_reason": ""
                }
            }
        )
        
        # Restore active assignments (not removed ones)
        await db.user_course_assignments.update_many(
            {
                "course_id": str(course_id),
                "status": "archived"
            },
            {
                "$set": {
                    "status": "active",
                    "updated_at": datetime.now()
                },
                "$unset": {
                    "archived_at": "",
                    "archived_by": ""
                }
            }
        )
        
        print(f"Successfully restored course {course_id}")
        return True
        
    except Exception as e:
        print(f"Error restoring course {course_id}: {str(e)}")
        return False

async def get_course_usage_analytics(
    db: Any,
    course_id: UUID,
    requesting_user: UserDB
) -> Dict[str, Any]:
    """Get usage analytics for a course"""
    
    # Check if user can view analytics for this course
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course_obj = CourseDB(**course)
    
    if not await can_user_access_course(db, requesting_user, course_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view analytics for this course"
        )
    
    # Calculate analytics
    total_assignments = await db.user_course_assignments.count_documents({
        "course_id": str(course_id),
        "status": {"$ne": "removed"}
    })
    
    completed_assignments = await db.user_course_assignments.count_documents({
        "course_id": str(course_id),
        "completed": True,
        "status": {"$ne": "removed"}
    })
    
    active_assignments = await db.user_course_assignments.count_documents({
        "course_id": str(course_id),
        "status": "active"
    })
    
    # Get assignments by company
    assignments_by_company = {}
    cursor = db.user_course_assignments.aggregate([
        {"$match": {"course_id": str(course_id), "status": {"$ne": "removed"}}},
        {"$group": {"_id": "$assigned_by_company", "count": {"$sum": 1}}}
    ])
    
    async for doc in cursor:
        company_id = doc["_id"]
        company = await db.companies.find_one({"_id": company_id})
        company_name = company["name"] if company else "Unknown"
        assignments_by_company[company_name] = doc["count"]
    
    return {
        "course_id": str(course_id),
        "course_title": course_obj.title,
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "active_assignments": active_assignments,
        "completion_rate": (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0,
        "assignments_by_company": assignments_by_company,
        "course_status": course_obj.status,
        "visibility": course_obj.visibility,
        "generated_at": datetime.now()
    }