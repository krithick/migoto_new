from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models.module_assignment_models import (
    ModuleAssignmentCreate, ModuleAssignmentDB, ModuleAssignmentUpdate, 
    ModuleAssignmentResponse, BulkModuleAssignmentCreate
)
from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.module_assignment import (
    create_module_assignment, bulk_create_module_assignments,
    get_user_module_assignments, get_user_course_module_assignments,
    get_module_assignment, get_module_assignment_by_id,
    update_module_assignment, update_module_assignment_by_id,
    delete_module_assignment, is_module_assigned,
    update_module_completion_status
)

# Create router
router = APIRouter(prefix="/module-assignments", tags=["Module Assignments"])

# Dependency to get database
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Module Assignment API Endpoints
@router.post("/", response_model=ModuleAssignmentResponse)
async def assign_module(
    assignment: ModuleAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign modules
):
    """
    Assign a module to a user
    """
    return await create_module_assignment(
        db, 
        assignment.user_id, 
        assignment.course_id, 
        assignment.module_id
    )

@router.post("/bulk", response_model=List[ModuleAssignmentResponse])
async def bulk_assign_modules(
    bulk_assignment: BulkModuleAssignmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can assign modules
):
    """
    Assign multiple modules to a user in bulk
    """
    return await bulk_create_module_assignments(db, bulk_assignment)

@router.get("/user/{user_id}", response_model=List[ModuleAssignmentResponse])
async def get_user_modules(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all modules assigned to a specific user.
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
    
    return await get_user_module_assignments(db, user_id)

@router.get("/user/{user_id}/course/{course_id}", response_model=List[ModuleAssignmentResponse])
async def get_user_course_modules(
    user_id: UUID,
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all modules assigned to a user for a specific course
    """
    # Check permissions (same as get_user_modules)
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
    
    return await get_user_course_module_assignments(db, user_id, course_id)

@router.get("/me", response_model=List[ModuleAssignmentResponse])
async def get_my_modules(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all modules assigned to the current user
    """
    return await get_user_module_assignments(db, current_user.id)

@router.get("/me/course/{course_id}", response_model=List[ModuleAssignmentResponse])
async def get_my_course_modules(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all modules assigned to the current user for a specific course
    """
    return await get_user_course_module_assignments(db, current_user.id, course_id)

@router.get("/{assignment_id}", response_model=ModuleAssignmentResponse)
async def get_module_assignment_by_id_endpoint(
    assignment_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific module assignment by ID
    """
    assignment = await get_module_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module assignment not found"
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

@router.put("/{assignment_id}", response_model=ModuleAssignmentResponse)
async def update_module_assignment_endpoint(
    assignment_id: UUID,
    update_data: ModuleAssignmentUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update assignments
):
    """
    Update a module assignment
    """
    updated_assignment = await update_module_assignment_by_id(db, assignment_id, update_data)
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module assignment not found"
        )
    
    return updated_assignment

@router.put("/user/{user_id}/module/{module_id}", response_model=ModuleAssignmentResponse)
async def update_user_module_assignment(
    user_id: UUID,
    module_id: UUID,
    update_data: ModuleAssignmentUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update assignments
):
    """
    Update a module assignment by user and module ID
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
    
    updated_assignment = await update_module_assignment(db, user_id, module_id, update_data)
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module assignment not found"
        )
    
    return updated_assignment

@router.put("/me/module/{module_id}/completion", response_model=ModuleAssignmentResponse)
async def update_my_module_completion(
    module_id: UUID,
    completed: bool = Body(..., embed=True),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update completion status for one of the current user's assigned modules
    """
    # Create update model
    update_data = ModuleAssignmentUpdate(completed=completed)
    
    # Check if module is assigned to user
    is_assigned = await is_module_assigned(db, current_user.id, module_id)
    if not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This module is not assigned to you"
        )
    
    # Update the assignment
    updated_assignment = await update_module_assignment(db, current_user.id, module_id, update_data)
    
    return updated_assignment

@router.delete("/{assignment_id}", response_model=Dict[str, bool])
async def delete_module_assignment_endpoint(
    assignment_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Delete a module assignment
    """
    # Get the assignment first to check permissions
    assignment = await get_module_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module assignment not found"
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
    success = await delete_module_assignment(db, UUID(assignment.user_id), UUID(assignment.module_id))
    
    return {"success": success}

@router.delete("/user/{user_id}/module/{module_id}", response_model=Dict[str, bool])
async def delete_user_module_assignment(
    user_id: UUID,
    module_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete assignments
):
    """
    Delete a module assignment by user and module ID
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
    success = await delete_module_assignment(db, user_id, module_id)
    
    return {"success": success}

@router.post("/recalculate-completion/{assignment_id}", response_model=ModuleAssignmentResponse)
async def recalculate_module_completion(
    assignment_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can trigger recalculation
):
    """
    Recalculate module completion status based on scenario completions
    """
    # Get the assignment first to check permissions
    assignment = await get_module_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module assignment not found"
        )
    
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if assignment.user_id not in managed_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only recalculate assignments for users you manage"
                )
    
    # Recalculate completion status
    updated_assignment = await update_module_completion_status(
        db, 
        UUID(assignment.user_id), 
        UUID(assignment.module_id)
    )
    
    if not updated_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to recalculate module completion"
        )
    
    return updated_assignment

