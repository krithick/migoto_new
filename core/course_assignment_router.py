# Add to core/course_assignment_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from models.scenario_assignment_models import ScenarioModeType , ModeProgressUpdate
from models.course_assignment_models import CourseAssignmentCreate, CourseAssignmentResponse
from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.course_assignment import (
    update_course_completion,
    assign_course_with_content
)
from core.scenario_assignment import (
update_mode_progress
)
# Create router
router = APIRouter(prefix="/course-assignments", tags=["Course Assignments"])

# Dependency to get database
async def get_database():
    from database import get_db  # Import your existing function
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
    - Superadmins can update any assignment
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
    
    # Update course completion
    completed = await update_course_completion(db, target_user_id, course_id)
    
    return {"success": True, "completed": completed}

# @router.post("/course/{course_id}/assign-with-content", response_model=Dict[str, Any])
# async def assign_course_with_content_endpoint(
#     course_id: UUID,
#     user_id: UUID = Body(..., description="User to assign the course to"),
#     include_all_modules: bool = Body(True, description="Whether to include all modules"),
#     include_all_scenarios: bool = Body(True, description="Whether to include all scenarios"),
#     module_ids: Optional[List[UUID]] = Body(None, description="Specific module IDs to include"),
#     scenario_mapping: Optional[Dict[str, List[UUID]]] = Body(None, description="Module ID to scenario IDs mapping"),
#     mode_mapping: Optional[Dict[str, List[str]]] = Body(None, description="Scenario ID to modes mapping"),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign
# ):
#     """
#     Assign a course to a user with specified modules, scenarios and modes
#     """
#     # Check if admin is allowed to manage this user
#     if admin_user.role == UserRole.ADMIN:
#         admin_data = await db.users.find_one({"_id": str(admin_user.id)})
#         if admin_data and "managed_users" in admin_data:
#             managed_users = admin_data["managed_users"]
#             if str(user_id) not in managed_users:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Access denied: you can only assign courses to users you manage"
#                 )
    
#     # Convert string keys to UUIDs in mappings
#     scenario_mapping_uuid = {}
#     if scenario_mapping:
#         for module_id_str, scenarios in scenario_mapping.items():
#             scenario_mapping_uuid[UUID(module_id_str)] = scenarios
    
#     mode_mapping_uuid = {}
#     if mode_mapping:
#         for scenario_id_str, modes in mode_mapping.items():
#             mode_mapping_uuid[UUID(scenario_id_str)] = modes
    
#     # Assign course with content
#     result = await assign_course_with_content(
#         db,
#         user_id,
#         course_id,
#         include_all_modules,
#         include_all_scenarios,
#         module_ids,
#         scenario_mapping_uuid,
#         mode_mapping_uuid
#     )
    
#     return result

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
    Assign a course to a user with specified modules, scenarios and modes
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
    
    # Convert string keys to UUIDs in mappings
    scenario_mapping_uuid = {}
    if scenario_mapping:
        for module_id_str, scenarios in scenario_mapping.items():
            scenario_mapping_uuid[UUID(module_id_str)] = scenarios
    
    mode_mapping_uuid = {}
    if mode_mapping:
        for scenario_id_str, modes in mode_mapping.items():
            mode_mapping_uuid[UUID(scenario_id_str)] = modes
    
     # Assign course for each user
    assignment_results = {}
    print("include_all_modules",include_all_modules)
    print("include_all_scenarios",include_all_scenarios)
    for user_id in user_ids:
        result = await assign_course_with_content(
            db,
            user_id,
            course_id,
            admin_user,
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
        "scenario_id": str(scenario_id)
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