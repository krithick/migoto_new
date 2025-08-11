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
    update_mode_progress, archive_scenario_assignment,
    is_scenario_assigned, is_mode_assigned,
    get_user_scenario_completion_stats
)

# Create router
router = APIRouter(prefix="/scenario-assignments", tags=["Scenario Assignments"])

# Dependency to get database
async def get_database():
    from database import get_db
    return await get_db()

# Scenario Assignment API Endpoints with Company Context
@router.post("/", response_model=ScenarioAssignmentResponse)
async def assign_scenario(
    assignment: ScenarioAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign scenarios
):
    """
    Assign a scenario to a user with company context tracking
    """
    # Check if admin can manage the target user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(assignment.user_id) not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign scenarios to users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(assignment.user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign scenarios to users in your company"
            )
    
    return await create_scenario_assignment(
        db, 
        assignment.user_id, 
        assignment.course_id, 
        assignment.module_id, 
        assignment.scenario_id,
        assignment.assigned_modes,
        admin_user.id  # Pass admin_user.id for company context
    )

@router.post("/bulk", response_model=List[ScenarioAssignmentResponse])
async def bulk_assign_scenarios(
    bulk_assignment: BulkScenarioAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign scenarios
):
    """
    Assign multiple scenarios to a user in bulk with company context tracking
    """
    # Check if admin can manage the target user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if str(bulk_assignment.user_id) not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign scenarios to users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(bulk_assignment.user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only assign scenarios to users in your company"
            )
    
    return await bulk_create_scenario_assignments(db, bulk_assignment, admin_user.id)

@router.get("/user/{user_id}", response_model=List[ScenarioAssignmentResponse])
async def get_user_scenarios(
    user_id: UUID,
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to a specific user.
    - Regular users can only view their own assignments
    - Admins can view assignments for users they manage
    - Superadmins can view assignments for users in their company
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own assignments"
        )
    elif current_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
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
    
    return await get_user_scenario_assignments(db, user_id, include_archived)

@router.get("/user/{user_id}/module/{module_id}", response_model=List[ScenarioAssignmentDB])
async def get_user_module_scenarios(
    user_id: UUID,
    module_id: UUID,
    include_archived: bool = Query(False, description="Include archived assignments"),
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
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
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
    
    return await get_user_module_scenario_assignments(db, user_id, module_id, include_archived)

@router.get("/me", response_model=List[ScenarioAssignmentResponse])
async def get_my_scenarios(
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to the current user
    """
    return await get_user_scenario_assignments(db, current_user.id, include_archived)

@router.get("/me/module/{module_id}", response_model=List[ScenarioAssignmentResponse])
async def get_my_module_scenarios(
    module_id: UUID,
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios assigned to the current user for a specific module
    """
    return await get_user_module_scenario_assignments(db, current_user.id, module_id, include_archived)

@router.get("/me/stats", response_model=Dict[str, Any])
async def get_my_scenario_stats(
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get completion statistics for the current user's assigned scenarios with company context
    """
    return await get_user_scenario_completion_stats(db, current_user.id, include_archived)

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
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if assignment.user_id not in managed_users and str(current_user.id) != assignment.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view assignments for users you manage"
                )
    elif current_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": assignment.user_id})
        if not target_user or target_user.get("company_id") != str(current_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view assignments for users in your company"
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
    Update a scenario assignment with company permission checks
    """
    # Get the assignment first to check permissions
    assignment = await get_scenario_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    # Check if admin can manage the user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        if assignment.user_id not in managed_users and admin_user.id != UUID(assignment.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only update assignments for users you manage"
            )
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": assignment.user_id})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only update assignments for users in your company"
            )
    
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
    Update a scenario assignment by user and scenario ID with company permission checks
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
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only update assignments for users in your company"
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
    Update progress for a specific mode in a scenario assignment with company permission checks
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
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only update assignments for users in your company"
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
    archive_reason: str = Body("Manual removal", embed=True),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Archive a scenario assignment with company permission checks
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
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": assignment.user_id})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only delete assignments for users in your company"
            )
    
    # Archive the assignment
    success = await archive_scenario_assignment(
        db, 
        UUID(assignment.user_id), 
        UUID(assignment.scenario_id), 
        admin_user.id,
        archive_reason
    )
    
    return {"success": success}

@router.delete("/user/{user_id}/scenario/{scenario_id}", response_model=Dict[str, bool])
async def delete_user_scenario_assignment(
    user_id: UUID,
    scenario_id: UUID,
    archive_reason: str = Body("Manual removal", embed=True),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Archive a scenario assignment by user and scenario ID with company permission checks
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
    elif admin_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(admin_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only delete assignments for users in your company"
            )
    
    # Archive the assignment
    success = await archive_scenario_assignment(db, user_id, scenario_id, admin_user.id, archive_reason)
    
    return {"success": success}

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

@router.get("/company/{company_id}/assignments", response_model=List[ScenarioAssignmentResponse])
async def get_company_scenario_assignments(
    company_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get all scenario assignments for a specific company (for analytics)
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
    
    # Build query
    query = {"assigned_by_company": str(company_id)}
    if not include_archived:
        query["is_archived"] = False
    
    # Get assignments with pagination
    assignments = []
    cursor = db.user_scenario_assignments.find(query).skip(skip).limit(limit)
    async for assignment_doc in cursor:
        assignments.append(ScenarioAssignmentResponse(**assignment_doc))
    
    return assignments

@router.get("/analytics/company/{company_id}", response_model=Dict[str, Any])
async def get_company_scenario_assignment_analytics(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get scenario assignment analytics for a specific company with mode breakdown
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
    total_assignments = await db.user_scenario_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": False
    })
    
    completed_assignments = await db.user_scenario_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": False,
        "completed": True
    })
    
    internal_assignments = await db.user_scenario_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "assignment_context": "internal",
        "is_archived": False
    })
    
    cross_company_assignments = await db.user_scenario_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "assignment_context": "cross_company",
        "is_archived": False
    })
    
    archived_assignments = await db.user_scenario_assignments.count_documents({
        "assigned_by_company": str(company_id),
        "is_archived": True
    })
    
    # Get mode-specific statistics
    mode_stats = {}
    for mode in ["learn_mode", "try_mode", "assess_mode"]:
        mode_assignments = await db.user_scenario_assignments.count_documents({
            "assigned_by_company": str(company_id),
            "is_archived": False,
            "assigned_modes": mode
        })
        
        # Count completed modes by checking mode_progress
        mode_completed = 0
        cursor = db.user_scenario_assignments.find({
            "assigned_by_company": str(company_id),
            "is_archived": False,
            "assigned_modes": mode
        })
        
        async for assignment in cursor:
            mode_progress = assignment.get("mode_progress", {})
            if mode in mode_progress and mode_progress[mode].get("completed", False):
                mode_completed += 1
        
        mode_stats[mode] = {
            "assigned": mode_assignments,
            "completed": mode_completed,
            "completion_rate": (mode_completed / mode_assignments * 100) if mode_assignments > 0 else 0
        }
    
    return {
        "company_id": str(company_id),
        "total_scenario_assignments": total_assignments,
        "completed_scenario_assignments": completed_assignments,
        "completion_rate": (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0,
        "internal_assignments": internal_assignments,
        "cross_company_assignments": cross_company_assignments,
        "archived_assignments": archived_assignments,
        "mode_statistics": mode_stats,
        "generated_at": datetime.now()
    }

@router.get("/user/{user_id}/analytics", response_model=Dict[str, Any])
async def get_user_scenario_assignment_analytics(
    user_id: UUID,
    include_archived: bool = Query(False, description="Include archived assignments"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get detailed scenario assignment analytics for a specific user
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own analytics"
        )
    elif current_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view analytics for users you manage"
                )
    elif current_user.role == UserRole.SUPERADMIN:
        target_user = await db.users.find_one({"_id": str(user_id)})
        if not target_user or target_user.get("company_id") != str(current_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: you can only view analytics for users in your company"
            )
    
    # Get detailed analytics using the existing function
    analytics = await get_user_scenario_completion_stats(db, user_id, include_archived)
    
    # Add user information
    user = await db.users.find_one({"_id": str(user_id)})
    if user:
        analytics["user_info"] = {
            "email": user.get("email"),
            "username": user.get("username"),
            "company_id": user.get("company_id")
        }
    
    return analytics