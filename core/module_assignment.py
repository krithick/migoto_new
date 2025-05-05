from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.module_assignment_models import (
    ModuleAssignmentCreate, ModuleAssignmentDB, ModuleAssignmentUpdate,
    BulkModuleAssignmentCreate
)
from models.user_models import UserDB, UserRole

# Create a module assignment
async def create_module_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    module_id: UUID
) -> ModuleAssignmentDB:
    """Assign a module to a user and record the assignment"""
    
    # Check if assignment already exists
    existing = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id),
        "module_id": str(module_id)
    })
    
    if existing:
        return ModuleAssignmentDB(**existing)
    
    # Verify that the user has access to the course
    course_assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if not course_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must be assigned to the course before assigning modules"
        )
    
    # Verify that the module belongs to the course
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course or str(module_id) not in course.get("modules", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with ID {module_id} does not belong to course with ID {course_id}"
        )
    
    # Create assignment record
    assignment = ModuleAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        module_id=module_id,
        assigned_date=datetime.now(),
        completed=False,
        completed_date=None
    )
    
    # Convert to DB model
    assignment_db = ModuleAssignmentDB(**assignment.dict())
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    assignment_dict["module_id"] = str(assignment_dict["module_id"])
    
    # Insert into database
    result = await db.user_module_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_module_assignments.find_one({"_id": str(result.inserted_id)})
    
    return ModuleAssignmentDB(**created_assignment)

# Bulk create module assignments
async def bulk_create_module_assignments(
    db: Any,
    bulk_assignment: BulkModuleAssignmentCreate
) -> List[ModuleAssignmentDB]:
    """Create multiple module assignments at once"""
    
    # Verify that the user has access to the course
    course_assignment = await db.user_course_assignments.find_one({
        "user_id": str(bulk_assignment.user_id),
        "course_id": str(bulk_assignment.course_id)
    })
    
    if not course_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must be assigned to the course before assigning modules"
        )
    
    # Get course to verify modules
    course = await db.courses.find_one({"_id": str(bulk_assignment.course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {bulk_assignment.course_id} not found"
        )
    
    # Convert module IDs to strings
    module_ids_str = [str(module_id) for module_id in bulk_assignment.module_ids]
    
    # Verify all modules belong to the course
    course_module_ids = course.get("modules", [])
    invalid_modules = [m_id for m_id in module_ids_str if m_id not in course_module_ids]
    
    if invalid_modules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following modules do not belong to the course: {', '.join(invalid_modules)}"
        )
    
    if bulk_assignment.operation == "add":
        # Find existing assignments for these modules
        existing_assignments = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str}
        }).to_list(length=None)
        
        existing_module_ids = [assignment["module_id"] for assignment in existing_assignments]
        
        # Filter out modules that are already assigned
        new_module_ids = [m_id for m_id in module_ids_str if m_id not in existing_module_ids]
        
        # Create new assignments
        assignments = []
        for module_id in new_module_ids:
            assignment = ModuleAssignmentCreate(
                user_id=bulk_assignment.user_id,
                course_id=bulk_assignment.course_id,
                module_id=UUID(module_id),
                assigned_date=datetime.now(),
                completed=False,
                completed_date=None
            )
            
            assignment_db = ModuleAssignmentDB(**assignment.dict())
            assignment_dict = assignment_db.dict(by_alias=True)
            
            # Convert UUIDs to strings
            assignment_dict["_id"] = str(assignment_dict["_id"])
            assignment_dict["user_id"] = str(assignment_dict["user_id"])
            assignment_dict["course_id"] = str(assignment_dict["course_id"])
            assignment_dict["module_id"] = str(assignment_dict["module_id"])
            
            assignments.append(assignment_dict)
        
        # Insert all new assignments
        if assignments:
            await db.user_module_assignments.insert_many(assignments)
        
        # Return all assignments (existing + new)
        all_assignments = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str}
        }).to_list(length=None)
        
        return [ModuleAssignmentDB(**assignment) for assignment in all_assignments]
            
    elif bulk_assignment.operation == "remove":
        # Delete the assignments
        result = await db.user_module_assignments.delete_many({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str}
        })
        
        # Also delete any scenario assignments for these modules
        await db.user_scenario_assignments.delete_many({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str}
        })
        
        # Return remaining assignments
        remaining = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id)
        }).to_list(length=None)
        
        return [ModuleAssignmentDB(**assignment) for assignment in remaining]
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {bulk_assignment.operation}. Must be 'add' or 'remove'."
        )

# Get all module assignments for a user
async def get_user_module_assignments(
    db: Any,
    user_id: UUID
) -> List[ModuleAssignmentDB]:
    """Get all module assignments for a user"""
    
    assignments = []
    cursor = db.user_module_assignments.find({"user_id": str(user_id)})
    async for document in cursor:
        assignments.append(ModuleAssignmentDB(**document))
    
    return assignments

# Get module assignments for a user and course
async def get_user_course_module_assignments(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> List[ModuleAssignmentDB]:
    """Get all module assignments for a user within a specific course"""
    
    assignments = []
    cursor = db.user_module_assignments.find({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    async for document in cursor:
        assignments.append(ModuleAssignmentDB(**document))
    
    return assignments

# Get a specific module assignment
async def get_module_assignment(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> Optional[ModuleAssignmentDB]:
    """Get a specific module assignment"""
    
    assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    if assignment:
        return ModuleAssignmentDB(**assignment)
    
    return None

# Get a specific module assignment by ID
async def get_module_assignment_by_id(
    db: Any,
    assignment_id: UUID
) -> Optional[ModuleAssignmentDB]:
    """Get a module assignment by its ID"""
    
    assignment = await db.user_module_assignments.find_one({
        "_id": str(assignment_id)
    })
    
    if assignment:
        return ModuleAssignmentDB(**assignment)
    
    return None

# Update a module assignment
async def update_module_assignment(
    db: Any,
    user_id: UUID,
    module_id: UUID,
    update_data: ModuleAssignmentUpdate
) -> Optional[ModuleAssignmentDB]:
    """Update a module assignment"""
    
    # Find the assignment
    assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    if not assignment:
        return None
    
    # Prepare update data
    update_dict = {}
    for key, value in update_data.dict(exclude_unset=True).items():
        if value is not None:
            update_dict[key] = value
    
    # Special case for completion status
    if "completed" in update_dict:
        if update_dict["completed"]:
            # When marking as completed, set the completion date
            update_dict["completed_date"] = datetime.now()
        else:
            # When marking as incomplete, clear the completion date
            update_dict["completed_date"] = None
    
    # Update in database
    if update_dict:
        await db.user_module_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_module_assignments.find_one({"_id": assignment["_id"]})
        if updated_assignment:
            return ModuleAssignmentDB(**updated_assignment)
    
    return ModuleAssignmentDB(**assignment)

# Update a module assignment by ID
async def update_module_assignment_by_id(
    db: Any,
    assignment_id: UUID,
    update_data: ModuleAssignmentUpdate
) -> Optional[ModuleAssignmentDB]:
    """Update a module assignment by its ID"""
    
    # Find the assignment
    assignment = await db.user_module_assignments.find_one({
        "_id": str(assignment_id)
    })
    
    if not assignment:
        return None
    
    # Prepare update data
    update_dict = {}
    for key, value in update_data.dict(exclude_unset=True).items():
        if value is not None:
            update_dict[key] = value
    
    # Special case for completion status
    if "completed" in update_dict:
        if update_dict["completed"]:
            # When marking as completed, set the completion date
            update_dict["completed_date"] = datetime.now()
        else:
            # When marking as incomplete, clear the completion date
            update_dict["completed_date"] = None
    
    # Update in database
    if update_dict:
        await db.user_module_assignments.update_one(
            {"_id": str(assignment_id)},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_module_assignments.find_one({"_id": str(assignment_id)})
        if updated_assignment:
            return ModuleAssignmentDB(**updated_assignment)
    
    return ModuleAssignmentDB(**assignment)

# Delete a module assignment
async def delete_module_assignment(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> bool:
    """Delete a module assignment"""
    
    # Also delete any scenario assignments for this module
    await db.user_scenario_assignments.delete_many({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    # Delete the module assignment
    result = await db.user_module_assignments.delete_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    return result.deleted_count > 0

# Check if a module is assigned to a user
async def is_module_assigned(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> bool:
    """Check if a module is assigned to a user"""
    
    assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    return assignment is not None

# Update module completion based on scenario completions
async def update_module_completion_status(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> Optional[ModuleAssignmentDB]:
    """
    Update module completion status based on scenario completions.
    If all assigned scenarios are completed, mark the module as completed.
    """
    # Find the module assignment
    module_assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    if not module_assignment:
        return None
    
    # Get all scenario assignments for this module
    scenario_assignments = await db.user_scenario_assignments.find({
        "user_id": str(user_id),
        "module_id": str(module_id)
    }).to_list(length=None)
    
    # If there are no scenario assignments, don't update module status
    if not scenario_assignments:
        return ModuleAssignmentDB(**module_assignment)
    
    # Check if all scenarios are completed
    all_completed = all(assignment.get("completed", False) for assignment in scenario_assignments)
    
    # Update module assignment status
    update_data = {}
    if all_completed:
        update_data["completed"] = True
        update_data["completed_date"] = datetime.now()
    else:
        update_data["completed"] = False
        update_data["completed_date"] = None
    
    await db.user_module_assignments.update_one(
        {"_id": module_assignment["_id"]},
        {"$set": update_data}
    )
    
    updated_assignment = await db.user_module_assignments.find_one({"_id": module_assignment["_id"]})
    return ModuleAssignmentDB(**updated_assignment)