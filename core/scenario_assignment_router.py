from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models.scenario_assignment_models import (
    ScenarioAssignmentCreate, ScenarioAssignmentDB, ScenarioAssignmentUpdate,
    ScenarioAssignmentResponse, BulkScenarioAssignmentCreate,
    ScenarioModeType, ModeProgressUpdate
)
from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.scenario_assignment import (
    create_scenario_assignment, bulk_create_scenario_assignments,
    get_user_scenario_assignments, get_user_module_scenario_assignments,
    get_scenario_assignment, get_scenario_assignment_by_id,
    update_scenario_assignment, update_scenario_assignment_by_id,
    update_mode_progress, delete_scenario_assignment,
    is_scenario_assigned, is_mode_assigned,
    get_user_scenario_completion_stats
)

# Create router
router = APIRouter(prefix="/scenario-assignments", tags=["Scenario Assignments"])

# Dependency to get database
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Scenario Assignment API Endpoints
@router.post("/", response_model=ScenarioAssignmentResponse)
async def assign_scenario(
    assignment: ScenarioAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign scenarios
):
    """
    Assign a scenario to a user
    """
    return await create_scenario_assignment(
        db, 
        assignment.user_id, 
        assignment.course_id, 
        assignment.module_id, 
        assignment.scenario_id,
        assignment.assigned_modes
    )

@router.post("/bulk", response_model=List[ScenarioAssignmentResponse])
async def bulk_assign_scenarios(
    bulk_assignment: BulkScenarioAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign scenarios
):
    """
    Assign multiple scenarios to a user in bulk
    """
    return await bulk_create_scenario_assignments(db, bulk_assignment)

@router.get("/user/{user_id}", response_model=List[ScenarioAssignmentResponse])
async def get_user_scenarios(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to a specific user.
    - Regular users can only view their own assignments
    - Admins can view assignments for users they manage
    - Superadmins can view all assignments
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own assignments"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view assignments for users you manage"
                )
    
    return await get_user_scenario_assignments(db, user_id)

@router.get("/user/{user_id}/module/{module_id}", response_model=List[ScenarioAssignmentResponse])
async def get_user_module_scenarios(
    user_id: UUID,
    module_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to a user for a specific module
    """
    # Check permissions (same as get_user_scenarios)
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own assignments"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view assignments for users you manage"
                )
    
    return await get_user_module_scenario_assignments(db, user_id, module_id)

@router.get("/me", response_model=List[ScenarioAssignmentResponse])
async def get_my_scenarios(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to the current user
    """
    return await get_user_scenario_assignments(db, current_user.id)

@router.get("/me/module/{module_id}", response_model=List[ScenarioAssignmentResponse])
async def get_my_module_scenarios(
    module_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to the current user for a specific module
    """
    return await get_user_module_scenario_assignments(db, current_user.id, module_id)

@router.get("/me/stats", response_model=Dict[str, Any])
async def get_my_scenario_stats(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get completion statistics for the current user's assigned scenarios
    """
    return await get_user_scenario_completion_stats(db, current_user.id)

@router.get("/{assignment_id}", response_model=ScenarioAssignmentResponse)
async def get_scenario_assignment_by_id_endpoint(
    assignment_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific scenario assignment by ID
    """
    assignment = await get_scenario_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.USER and str(current_user.id) != assignment.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own assignments"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if assignment.user_id not in managed_users and str(current_user.id) != assignment.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view assignments for users you manage"
                )
    
    return assignment

@router.put("/{assignment_id}", response_model=ScenarioAssignmentResponse)
async def update_scenario_assignment_endpoint(
    assignment_id: UUID,
    update_data: ScenarioAssignmentUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update assignments
):
    """
    Update a scenario assignment
    """
    updated_assignment = await update_scenario_assignment_by_id(db, assignment_id, update_data)
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    return updated_assignment

@router.put("/user/{user_id}/scenario/{scenario_id}", response_model=ScenarioAssignmentResponse)
async def update_user_scenario_assignment(
    user_id: UUID,
    scenario_id: UUID,
    update_data: ScenarioAssignmentUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update assignments
):
    """
    Update a scenario assignment by user and scenario ID
    """
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and admin_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only update assignments for users you manage"
                )
    
    updated_assignment = await update_scenario_assignment(db, user_id, scenario_id, update_data)
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    return updated_assignment

@router.put("/user/{user_id}/scenario/{scenario_id}/mode/{mode}", response_model=ScenarioAssignmentResponse)
async def update_user_scenario_mode_progress(
    user_id: UUID,
    scenario_id: UUID,
    mode: ScenarioModeType,
    progress: ModeProgressUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update mode progress
):
    """
    Update progress for a specific mode in a scenario assignment
    """
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and admin_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only update assignments for users you manage"
                )
    
    updated_assignment = await update_mode_progress(db, user_id, scenario_id, mode, progress)
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    return updated_assignment

@router.put("/me/scenario/{scenario_id}/completion", response_model=ScenarioAssignmentResponse)
async def update_my_scenario_completion(
    scenario_id: UUID,
    completed: bool = Body(..., embed=True),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update completion status for one of the current user's assigned scenarios
    """
    # Create update model
    update_data = ScenarioAssignmentUpdate(completed=completed)
    
    # Check if scenario is assigned to user
    is_assigned = await is_scenario_assigned(db, current_user.id, scenario_id)
    if not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This scenario is not assigned to you"
        )
    
    # Update the assignment
    updated_assignment = await update_scenario_assignment(db, current_user.id, scenario_id, update_data)
    
    return updated_assignment

@router.put("/me/scenario/{scenario_id}/mode/{mode}", response_model=ScenarioAssignmentResponse)
async def update_my_scenario_mode_progress(
    scenario_id: UUID,
    mode: ScenarioModeType,
    progress: ModeProgressUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update progress for a specific mode in one of the current user's assigned scenarios
    """
    # Check if scenario and mode are assigned to user
    is_assigned = await is_scenario_assigned(db, current_user.id, scenario_id)
    if not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This scenario is not assigned to you"
        )
    
    mode_assigned = await is_mode_assigned(db, current_user.id, scenario_id, mode)
    if not mode_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The {mode.value} is not assigned to you for this scenario"
        )
    
    # Update the mode progress
    updated_assignment = await update_mode_progress(db, current_user.id, scenario_id, mode, progress)
    
    return updated_assignment

@router.delete("/{assignment_id}", response_model=Dict[str, bool])
async def delete_scenario_assignment_endpoint(
    assignment_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Delete a scenario assignment
    """
    # Get the assignment first to check permissions
    assignment = await get_scenario_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if assignment.user_id not in managed_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only delete assignments for users you manage"
                )
    
    # Delete the assignment
    success = await delete_scenario_assignment(db, UUID(assignment.user_id), UUID(assignment.scenario_id))
    
    return {"success": success}

@router.delete("/user/{user_id}/scenario/{scenario_id}", response_model=Dict[str, bool])
async def delete_user_scenario_assignment(
    user_id: UUID,
    scenario_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Delete a scenario assignment by user and scenario ID
    """
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only delete assignments for users you manage"
                )
    
    # Delete the assignment
    success = await delete_scenario_assignment(db, user_id, scenario_id)
    
    return {"success": success}