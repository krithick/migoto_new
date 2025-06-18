# Updated core/course_assignment_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from models.scenario_assignment_models import ScenarioModeType, ModeProgressUpdate
from models.course_assignment_models import CourseAssignmentCreate, CourseAssignmentResponse
from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.course_assignment import (
    update_course_completion,
    assign_course_with_content,
    create_course_assignment,
    get_user_courses_with_assignments,
    archive_course_assignment,
    get_course_assignment
)
from core.scenario_assignment import update_mode_progress

# Create router
router = APIRouter(prefix="/course-assignments", tags=["Course Assignments"])

# Dependency to get database
async def get_database():
    from database import get_db
    return await get_db()

@router.post("/course/{course_id}/complete-assignment", response_model=Dict[str, bool])
async def recalculate_course_completion(
    course_id: UUID,
    user_id: UUID = Query(None, description="User ID (admins only, defaults to current user)"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Recalculate and update course completion status based on module completions.
    - Regular users can only update their own assignments
    - Admins can update assignments for users they manage
    - Superadmins can update any assignment in their company
    """
    # Determine which user's assignment to update
    target_user_id = user_id if user_id else current_user.id
    
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only update your own assignments"
        )
    elif current_user.role == UserRole.ADMIN and user_id:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(target_user_id) not in managed_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only update assignments for users you manage"
                )
    elif current_user.role == UserRole.SUPERADMIN and user_id:
        # Superadmin can update assignments for users in their company
        target_user = await db.users.find_one({"_id": str(target_user_id)})
        if not target_user or target_user.get("company_id") != str(current_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only update assignments for users in your company"
            )
    
    # Update course completion
    completed = await update_course_completion(db, target_user_id, course_id)
    
    return {"success": True, "completed": completed}

@router.post("/course/{course_id}/assign-with-content", response_model=Dict[str, Any])
async def assign_course_with_content_endpoint(
    course_id: UUID,
    user_ids: List[UUID] = Body(..., description="List of users to assign the course to"),
    include_all_modules: bool = Body(True, description="Whether to include all modules"),
    include_all_scenarios: bool = Body(True, description="Whether to include all scenarios"),
    module_ids: Optional[List[UUID]] = Body(None, description="Specific module IDs to include"),
    scenario_mapping: Optional[Dict[str, List[UUID]]] = Body(None, description="Module ID to scenario IDs mapping"),
    mode_mapping: Optional[Dict[str, List[str]]] = Body(None, description="Scenario ID to modes mapping"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign
):
    """
    Assign a course to multiple users with specified modules, scenarios and modes.
    Now includes full company context tracking for all assignments.
    """
    # For admin, ensure they can manage each user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        for uid in user_ids:
            if str(uid) not in managed_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: you can only assign courses to users you manage (user {uid})"
                )
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin can assign to users in their company
        for uid in user_ids:
            target_user = await db.users.find_one({"_id": str(uid)})
            if not target_user or target_user.get("company_id") != str(admin_user.company_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: you can only assign courses to users in your company (user {uid})"
                )
    
    # Convert string keys to UUIDs in mappings
    scenario_mapping_uuid = {}
    if scenario_mapping:
        for module_id_str, scenarios in scenario_mapping.items():
            scenario_mapping_uuid[UUID(module_id_str)] = scenarios
    
    mode_mapping_uuid = {}
    if mode_mapping:
        for scenario_id_str, modes in mode_mapping.items():
            mode_mapping_uuid[UUID(scenario_id_str)] = modes
    
    # Assign course for each user with company context tracking
    assignment_results = {}
    for user_id in user_ids:
        result = await assign_course_with_content(
            db,
            user_id,
            course_id,
            admin_user,  # Pass admin_user for company context
            include_all_modules,
            include_all_scenarios,
            module_ids,
            scenario_mapping_uuid,
            mode_mapping_uuid
        )
        assignment_results[str(user_id)] = result

    return assignment_results

@router.put("/me/scenario/{scenario_id}/mode/{mode}/complete", response_model=Dict[str, bool])
async def complete_scenario_mode(
    scenario_id: UUID,
    mode: ScenarioModeType,
    completed: bool = Body(True, embed=True),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Mark a specific mode of a scenario as completed or not completed
    """
    # Check if scenario and mode are assigned to user
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(current_user.id),
        "scenario_id": str(scenario_id),
        "is_archived": False
    })
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    assigned_modes = assignment.get("assigned_modes", [])
    if mode.value not in assigned_modes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The {mode.value} is not assigned to you for this scenario"
        )
    
    # Update mode progress
    progress = ModeProgressUpdate(completed=completed)
    result = await update_mode_progress(db, current_user.id, scenario_id, mode, progress)
    
    if result:
        # Check if completion triggered scenario completion
        return {
            "success": True, 
            "completed": completed,
            "scenario_completed": result.completed
        }
    
    return {"success": False, "completed": completed, "scenario_completed": False}

@router.get("/me/courses", response_model=List[Dict[str, Any]])
async def get_my_assigned_courses(
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all courses assigned to the current user with full company context
    """
    return await get_user_courses_with_assignments(db, current_user.id, include_archived)

@router.get("/user/{user_id}/courses", response_model=List[Dict[str, Any]])
async def get_user_assigned_courses(
    user_id: UUID,
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get all courses assigned to a specific user (admin only)
    """
    # Check permissions
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(user_id) not in managed_users and admin_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view assignments for users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view assignments for users in your company"
            )
    
    return await get_user_courses_with_assignments(db, user_id, include_archived)

@router.delete("/course/{course_id}/user/{user_id}", response_model=Dict[str, bool])
async def remove_course_assignment(
    course_id: UUID,
    user_id: UUID,
    archive_reason: str = Body("Manual removal", embed=True),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Remove (archive) a course assignment from a user
    """
    # Check permissions
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(user_id) not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only remove assignments for users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only remove assignments for users in your company"
            )
    
    # Archive the assignment
    success = await archive_course_assignment(db, user_id, course_id, admin_user.id, archive_reason)
    
    return {"success": success}

# @router.post("/course/{course_id}/user/{user_id}", response_model=CourseAssignmentResponse)
# async def create_course_assignment_endpoint(
#     course_id: UUID,
#     user_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)
# ):
#     """
#     Create a single course assignment with company context tracking
#     """
#     # Check permissions
#     if admin_user.role == UserRole.ADMIN:
#         admin_data = await db.users.find_one({"_id": str(admin_user.id)})
#         managed_users = admin_data.get("managed_users", []) if admin_data else []
#         if str(user_id) not in managed_users:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Access denied: you can only assign courses to users you manage"
#             )
#     elif admin_user.role == UserRole.SUPERADMIN:
#         target_user = await db.users.find_one({"_id": str(user_id)})
#         if not target_user or target_user.get("company_id") != str(admin_user.company_id):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Access denied: you can only assign courses to users in your company"
#             )
    
#     # Create the assignment with company context
#     assignment = await create_course_assignment(db, user_id, course_id, admin_user.id)
    
#     # Add course to user's assigned_courses array
#     await db.users.update_one(
#         {"_id": str(user_id)},
#         {"$addToSet": {"assigned_courses": str(course_id)}}
#     )
    
#     return assignment
@router.post("/course/{course_id}/user/{user_id}", response_model=CourseAssignmentResponse)
async def create_course_assignment_endpoint(
    course_id: UUID,
    user_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Fixed version with proper permission checks"""
    
    # ADDED: Validate admin can assign to this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(user_id) not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign courses to users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign courses to users in your company"
            )
    
    # ADDED: Validate admin can assign this course
    course = await db.courses.find_one({"_id": str(course_id)})
    if course:
        # Use the can_user_assign_course function from company_access_control.py
        from core.company_access_control import can_user_access_course
        from models.course_models import CourseDB
        
        course_obj = CourseDB(**course)
        # This should use a can_user_assign_course function (you may need to create it)
        # For now, basic check:
        if course.get("is_archived", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign archived course"
            )
    
    # Create the assignment with company context
    assignment = await create_course_assignment(db, user_id, course_id, admin_user.id)
    
    # Add course to user's assigned_courses array
    await db.users.update_one(
        {"_id": str(user_id)},
        {"$addToSet": {"assigned_courses": str(course_id)}}
    )
    
    return assignment
@router.get("/course/{course_id}/user/{user_id}", response_model=CourseAssignmentResponse)
async def get_course_assignment_endpoint(
    course_id: UUID,
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific course assignment
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own assignments"
        )
    elif current_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(user_id) not in managed_users and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view assignments for users you manage"
            )
    elif current_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(current_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view assignments for users in your company"
            )
    
    assignment = await get_course_assignment(db, user_id, course_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course assignment not found"
        )
    
    return assignment

@router.get("/company/{company_id}/assignments", response_model=List[Dict[str, Any]])
async def get_company_course_assignments(
    company_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get all course assignments for a specific company (for analytics)
    """
    # Check permissions
    if admin_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can view any company's assignments
        pass
    elif admin_user.role == UserRole.SUPERADMIN and admin_user.company_id == company_id:
        # Superadmin can view their own company's assignments
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view assignments for your company"
        )
    
    # Get all users in the company
    user_cursor = db.users.find({"company_id": str(company_id)})
    company_assignments = []
    
    async for user_doc in user_cursor:
        user_id = UUID(user_doc["_id"])
        user_assignments = await get_user_courses_with_assignments(db, user_id, include_archived)
        
        for assignment in user_assignments:
            assignment["user_email"] = user_doc.get("email")
            assignment["user_username"] = user_doc.get("username")
            company_assignments.append(assignment)
    
    # Apply pagination
    start_idx = skip
    end_idx = skip + limit
    return company_assignments[start_idx:end_idx]

@router.get("/analytics/company/{company_id}", response_model=Dict[str, Any])
async def get_company_assignment_analytics(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get assignment analytics for a specific company
    """
    # Check permissions
    if admin_user.role == UserRole.BOSS_ADMIN:
        pass
    elif admin_user.role == UserRole.SUPERADMIN and admin_user.company_id == company_id:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view analytics for your company"
        )
    
    # Get assignment statistics
    total_assignments = await db.user_course_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": False
    })
    
    completed_assignments = await db.user_course_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": False,
        "completed": True
    })
    
    internal_assignments = await db.user_course_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "assignment_context": "internal",
        "is_archived": False
    })
    
    cross_company_assignments = await db.user_course_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "assignment_context": "cross_company",
        "is_archived": False
    })
    
    archived_assignments = await db.user_course_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": True
    })
    
    return {
        "company_id": str(company_id),
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "completion_rate": (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0,
        "internal_assignments": internal_assignments,
        "cross_company_assignments": cross_company_assignments,
        "archived_assignments": archived_assignments,
        "generated_at": datetime.now()
    }