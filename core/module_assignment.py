from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.module_assignment_models import (
    ModuleAssignmentCreate, ModuleAssignmentDB, ModuleAssignmentUpdate,
    BulkModuleAssignmentCreate, AssignmentContext
)
from models.user_models import UserDB, UserRole
from models.company_models import CompanyType, CompanyDB

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

# async def determine_assignment_context(
#     db: Any, 
#     assigning_admin_company: UUID, 
#     module_company: UUID
# ) -> str:
#     """
#     Determine assignment context based on company hierarchy:
    
#     INTERNAL: Admin assigns module from their own company
#     CROSS_COMPANY: Admin assigns MOTHER company module to their users
#     """
#     if assigning_admin_company == module_company:
#         return AssignmentContext.INTERNAL
    
#     # Check if module is from MOTHER company
#     module_company_type = await get_company_hierarchy_type(db, module_company)
#     if module_company_type == CompanyType.MOTHER:
#         return AssignmentContext.CROSS_COMPANY
    
#     # This shouldn't happen if access control is working properly
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Invalid assignment: Cannot assign module from different non-mother company"
#     )
async def determine_assignment_context(db, assigning_admin_company, content_company):
    # CRITICAL FIX: Convert to strings for consistent comparison
    admin_company_str = str(assigning_admin_company)
    content_company_str = str(content_company)
    
    if admin_company_str == content_company_str:
        return AssignmentContext.INTERNAL
    
    # Check if content is from MOTHER company
    content_company_doc = await db.companies.find_one({"_id": content_company_str})
    if content_company_doc and content_company_doc.get("company_type") == CompanyType.MOTHER:
        return AssignmentContext.CROSS_COMPANY
    
    # CRITICAL FIX: Add proper error handling
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid assignment: Cannot assign content from different non-mother company"
    )
# Create a module assignment with company context
async def create_module_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    module_id: UUID,
    assigned_by: Optional[UUID] = None
) -> ModuleAssignmentDB:
    """Assign a module to a user with full company context tracking"""
    
    # If no assigned_by provided, this is a system assignment (fallback)
    if not assigned_by:
        # This might happen during automated assignments
        assigned_by = user_id  # Fallback to user themselves
    
    # Get assigning admin info
    admin = await db.users.find_one({"_id": str(assigned_by)})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid assigning user"
        )
    
    admin_user = UserDB(**admin)
    
    # Check if assignment already exists (including archived ones)
    existing = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id),
        "module_id": str(module_id)
    })
    
    if existing:
        existing_assignment = ModuleAssignmentDB(**existing)
        if existing_assignment.is_archived:
            # Reactivate archived assignment with new context
            await db.user_module_assignments.update_one(
                {"_id": str(existing_assignment.id)},
                {"$set": {
                    "is_archived": False,
                    "archived_at": None,
                    "archived_by": None,
                    "archived_reason": None,
                    "assigned_by": str(assigned_by),
                    "assigned_by_company": str(admin_user.company_id),
                    "assigned_date": datetime.now()
                }}
            )
            reactivated = await db.user_module_assignments.find_one({"_id": str(existing_assignment.id)})
            return ModuleAssignmentDB(**reactivated)
        else:
            # Assignment already exists and is active
            return existing_assignment
    
    # Verify that the user has access to the course
    course_assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id),
        "is_archived": False
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
    
    # Check if module is archived
    if module.get("is_archived", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign archived module"
        )
    
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course or str(module_id) not in course.get("modules", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with ID {module_id} does not belong to course with ID {course_id}"
        )
    
    # Validate assignment permissions
    from core.module import can_user_assign_module, ModuleDB
    module_obj = ModuleDB(**module)
    
    if admin_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and not await can_user_assign_module(db, admin_user, module_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to assign this module"
        )
    
    # Determine assignment context
    module_company_id = UUID(module["company_id"])
    assignment_context = await determine_assignment_context(
        db, admin_user.company_id, module_company_id
    )
    
    # Create assignment record with full company context
    assignment = ModuleAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        module_id=module_id,
        assigned_date=datetime.now(),
        completed=False,
        completed_date=None
    )
    
    # Convert to DB model with company context
    assignment_db = ModuleAssignmentDB(
        **assignment.dict(),
        assigned_by=assigned_by,
        assigned_by_company=admin_user.company_id,
        source_company=module_company_id,
        assignment_context=assignment_context
    )
    
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    assignment_dict["module_id"] = str(assignment_dict["module_id"])
    assignment_dict["assigned_by"] = str(assignment_dict["assigned_by"])
    assignment_dict["assigned_by_company"] = str(assignment_dict["assigned_by_company"])
    assignment_dict["source_company"] = str(assignment_dict["source_company"])
    
    # Insert into database
    result = await db.user_module_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_module_assignments.find_one({"_id": str(result.inserted_id)})
    
    return ModuleAssignmentDB(**created_assignment)

# Bulk create module assignments with company context
async def bulk_create_module_assignments(
    db: Any,
    bulk_assignment: BulkModuleAssignmentCreate,
    assigned_by: Optional[UUID] = None
) -> List[ModuleAssignmentDB]:
    """Create multiple module assignments at once with company context tracking"""
    
    # If no assigned_by provided, get from context or use user_id as fallback
    if not assigned_by:
        assigned_by = bulk_assignment.user_id  # Fallback
    
    # Get assigning admin info
    admin = await db.users.find_one({"_id": str(assigned_by)})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid assigning user"
        )
    
    admin_user = UserDB(**admin)
    
    # Verify that the user has access to the course
    course_assignment = await db.user_course_assignments.find_one({
        "user_id": str(bulk_assignment.user_id),
        "course_id": str(bulk_assignment.course_id),
        "is_archived": False
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
    
    # Verify all modules belong to the course and get module info
    course_module_ids = course.get("modules", [])
    invalid_modules = [m_id for m_id in module_ids_str if m_id not in course_module_ids]
    
    if invalid_modules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following modules do not belong to the course: {', '.join(invalid_modules)}"
        )
    
    # Get modules info for permission checking and company context
    modules_info = {}
    for module_id in module_ids_str:
        module = await db.modules.find_one({"_id": module_id})
        if module and not module.get("is_archived", False):
            modules_info[module_id] = module
    
    # Validate assignment permissions for each module
    from core.module import can_user_assign_module, ModuleDB
    for module_id, module_doc in modules_info.items():
        module_obj = ModuleDB(**module_doc)
        if admin_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and not await can_user_assign_module(db, admin_user, module_obj):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not authorized to assign module {module_id}"
            )
    
    if bulk_assignment.operation == "add":
        # Find existing assignments for these modules
        existing_assignments = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str}
        }).to_list(length=None)
        
        existing_module_ids = [assignment["module_id"] for assignment in existing_assignments]
        
        # Reactivate archived assignments
        archived_assignments = [a for a in existing_assignments if a.get("is_archived", False)]
        for archived in archived_assignments:
            module_company_id = UUID(modules_info[archived["module_id"]]["company_id"])
            assignment_context = await determine_assignment_context(
                db, admin_user.company_id, module_company_id
            )
            
            await db.user_module_assignments.update_one(
                {"_id": archived["_id"]},
                {"$set": {
                    "is_archived": False,
                    "archived_at": None,
                    "archived_by": None,
                    "archived_reason": None,
                    "assigned_by": str(assigned_by),
                    "assigned_by_company": str(admin_user.company_id),
                    "assignment_context": assignment_context,
                    "assigned_date": datetime.now()
                }}
            )
        
        # Filter out modules that are already assigned (active)
        active_existing = [a["module_id"] for a in existing_assignments if not a.get("is_archived", False)]
        new_module_ids = [m_id for m_id in module_ids_str if m_id not in active_existing]
        
        # Create new assignments
        assignments = []
        for module_id in new_module_ids:
            if module_id in modules_info:
                module_company_id = UUID(modules_info[module_id]["company_id"])
                assignment_context = await determine_assignment_context(
                    db, admin_user.company_id, module_company_id
                )
                
                assignment = ModuleAssignmentCreate(
                    user_id=bulk_assignment.user_id,
                    course_id=bulk_assignment.course_id,
                    module_id=UUID(module_id),
                    assigned_date=datetime.now(),
                    completed=False,
                    completed_date=None
                )
                
                assignment_db = ModuleAssignmentDB(
                    **assignment.dict(),
                    assigned_by=assigned_by,
                    assigned_by_company=admin_user.company_id,
                    source_company=module_company_id,
                    assignment_context=assignment_context
                )
                assignment_dict = assignment_db.dict(by_alias=True)
                
                # Convert UUIDs to strings
                assignment_dict["_id"] = str(assignment_dict["_id"])
                assignment_dict["user_id"] = str(assignment_dict["user_id"])
                assignment_dict["course_id"] = str(assignment_dict["course_id"])
                assignment_dict["module_id"] = str(assignment_dict["module_id"])
                assignment_dict["assigned_by"] = str(assignment_dict["assigned_by"])
                assignment_dict["assigned_by_company"] = str(assignment_dict["assigned_by_company"])
                assignment_dict["source_company"] = str(assignment_dict["source_company"])
                
                assignments.append(assignment_dict)
        
        # Insert all new assignments
        if assignments:
            await db.user_module_assignments.insert_many(assignments)
        
        # Return all assignments (existing + new)
        all_assignments = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "module_id": {"$in": module_ids_str},
            "is_archived": False
        }).to_list(length=None)
        
        return [ModuleAssignmentDB(**assignment) for assignment in all_assignments]
            
    elif bulk_assignment.operation == "remove":
        # Archive the assignments instead of deleting
        result = await db.user_module_assignments.update_many(
            {
                "user_id": str(bulk_assignment.user_id),
                "course_id": str(bulk_assignment.course_id),
                "module_id": {"$in": module_ids_str},
                "is_archived": False
            },
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(assigned_by),
                "archived_reason": "Bulk removal"
            }}
        )
        
        # Also archive any scenario assignments for these modules
        await db.user_scenario_assignments.update_many(
            {
                "user_id": str(bulk_assignment.user_id),
                "course_id": str(bulk_assignment.course_id),
                "module_id": {"$in": module_ids_str},
                "is_archived": False
            },
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(assigned_by),
                "archived_reason": "Module assignment archived"
            }}
        )
        
        # Return remaining active assignments
        remaining = await db.user_module_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "course_id": str(bulk_assignment.course_id),
            "is_archived": False
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
    user_id: UUID,
    include_archived: bool = False
) -> List[ModuleAssignmentDB]:
    """Get all module assignments for a user"""
    
    query = {"user_id": str(user_id)}
    if not include_archived:
        query["is_archived"] = False
    
    assignments = []
    cursor = db.user_module_assignments.find(query)
    async for document in cursor:
        assignments.append(ModuleAssignmentDB(**document))
    
    return assignments

# Get module assignments for a user and course
async def get_user_course_module_assignments(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    include_archived: bool = False
) -> List[ModuleAssignmentDB]:
    """Get all module assignments for a user within a specific course"""
    
    query = {
        "user_id": str(user_id),
        "course_id": str(course_id)
    }
    if not include_archived:
        query["is_archived"] = False
    
    assignments = []
    cursor = db.user_module_assignments.find(query)
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
    
    # Don't allow updates to archived assignments
    if assignment.get("is_archived", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update archived assignment"
        )
    
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
    
    # Don't allow updates to archived assignments
    if assignment.get("is_archived", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update archived assignment"
        )
    
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

# Archive a module assignment (soft delete)
async def archive_module_assignment(
    db: Any,
    user_id: UUID,
    module_id: UUID,
    archived_by: UUID,
    reason: str = "Manual removal"
) -> bool:
    """Archive a module assignment instead of deleting it"""
    
    assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id)
    })
    
    if not assignment:
        return False
    
    # Archive the assignment
    result = await db.user_module_assignments.update_one(
        {"_id": assignment["_id"]},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": reason
        }}
    )
    
    # Also archive any scenario assignments for this module
    await db.user_scenario_assignments.update_many(
        {
            "user_id": str(user_id),
            "module_id": str(module_id),
            "is_archived": False
        },
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": f"Module assignment archived: {reason}"
        }}
    )
    
    return result.modified_count > 0

# Delete a module assignment (now just calls archive)
async def delete_module_assignment(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> bool:
    """Delete a module assignment - now archives instead"""
    return await archive_module_assignment(db, user_id, module_id, user_id, "Direct deletion")

# Check if a module is assigned to a user
async def is_module_assigned(
    db: Any,
    user_id: UUID,
    module_id: UUID
) -> bool:
    """Check if a module is assigned to a user (active assignment only)"""
    
    assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id),
        "is_archived": False
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
        "module_id": str(module_id),
        "is_archived": False
    })
    
    if not module_assignment:
        return None
    
    # Get all scenario assignments for this module
    scenario_assignments = await db.user_scenario_assignments.find({
        "user_id": str(user_id),
        "module_id": str(module_id),
        "is_archived": False
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
    
    # Also update course completion status
    if all_completed:
        from core.course_assignment import update_course_completion
        await update_course_completion(db, user_id, UUID(module_assignment["course_id"]))
    
    return ModuleAssignmentDB(**updated_assignment)