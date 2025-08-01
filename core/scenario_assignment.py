from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.scenario_assignment_models import (
    ScenarioAssignmentCreate, ScenarioAssignmentDB, ScenarioAssignmentUpdate,
    BulkScenarioAssignmentCreate, ScenarioModeType, ModeProgressUpdate,
    AssignmentContext
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
#     scenario_company: UUID
# ) -> str:
#     """
#     Determine assignment context based on company hierarchy:
    
#     INTERNAL: Admin assigns scenario from their own company
#     CROSS_COMPANY: Admin assigns MOTHER company scenario to their users
#     """
#     if assigning_admin_company == scenario_company:
#         return AssignmentContext.INTERNAL
    
#     # Check if scenario is from MOTHER company
#     scenario_company_type = await get_company_hierarchy_type(db, scenario_company)
#     if scenario_company_type == CompanyType.MOTHER:
#         return AssignmentContext.CROSS_COMPANY
    
#     # This shouldn't happen if access control is working properly
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Invalid assignment: Cannot assign scenario from different non-mother company"
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
# Create a scenario assignment with company context
async def create_scenario_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    module_id: UUID,
    scenario_id: UUID,
    assigned_modes: List[ScenarioModeType] = None,
    assigned_by: Optional[UUID] = None
) -> ScenarioAssignmentDB:
    """Assign a scenario to a user with full company context tracking"""
    
    if assigned_modes is None:
        assigned_modes = [
            ScenarioModeType.LEARN_MODE, 
            ScenarioModeType.TRY_MODE, 
            ScenarioModeType.ASSESS_MODE
        ]
    
    # If no assigned_by provided, this is a system assignment (fallback)
    if not assigned_by:
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
    existing = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id)
    })
    
    if existing:
        existing_assignment = ScenarioAssignmentDB(**existing)
        if existing_assignment.is_archived:
            # Reactivate archived assignment with new context
            # Initialize mode progress for new modes
            mode_progress = {}
            for mode in assigned_modes:
                mode_progress[mode.value] = {"completed": False, "completed_date": None}
            
            await db.user_scenario_assignments.update_one(
                {"_id": str(existing_assignment.id)},
                {"$set": {
                    "is_archived": False,
                    "archived_at": None,
                    "archived_by": None,
                    "archived_reason": None,
                    "assigned_by": str(assigned_by),
                    "assigned_by_company": str(admin_user.company_id),
                    "assigned_modes": [mode.value for mode in assigned_modes],
                    "mode_progress": mode_progress,
                    "assigned_date": datetime.now(),
                    "completed": False,
                    "completed_date": None
                }}
            )
            reactivated = await db.user_scenario_assignments.find_one({"_id": str(existing_assignment.id)})
            return ScenarioAssignmentDB(**reactivated)
        else:
            # Assignment already exists - update modes if they've changed
            current_modes = set(existing.get("assigned_modes", []))
            new_modes = set(mode.value for mode in assigned_modes)
            
            if current_modes != new_modes:
                # Update the mode_progress to include any new modes
                mode_progress = existing.get("mode_progress", {})
                for mode in assigned_modes:
                    if mode.value not in mode_progress:
                        if not mode_progress:
                            mode_progress = {}
                        mode_progress[mode.value] = {"completed": False, "completed_date": None}
                
                # Update assignment
                await db.user_scenario_assignments.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "assigned_modes": [mode.value for mode in assigned_modes],
                        "mode_progress": mode_progress,
                        "assigned_by": str(assigned_by),
                        "assigned_by_company": str(admin_user.company_id)
                    }}
                )
                
                updated = await db.user_scenario_assignments.find_one({"_id": existing["_id"]})
                return ScenarioAssignmentDB(**updated)
            
            return existing_assignment
    
    # Verify that the user has access to the module
    module_assignment = await db.user_module_assignments.find_one({
        "user_id": str(user_id),
        "module_id": str(module_id),
        "is_archived": False
    })
    
    if not module_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must be assigned to the module before assigning scenarios"
        )
    
    # Verify that the scenario belongs to the module
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module or str(scenario_id) not in module.get("scenarios", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario with ID {scenario_id} does not belong to module with ID {module_id}"
        )
    
    # Get scenario info
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID {scenario_id} not found"
        )
    
    # Check if scenario is archived
    if scenario.get("is_archived", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign archived scenario"
        )
    
    # Validate assignment permissions
    from core.scenario import can_user_assign_scenario, ScenarioDB
    scenario_obj = ScenarioDB(**scenario)
    
    if admin_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and not await can_user_assign_scenario(db, admin_user, scenario_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to assign this scenario"
        )
    
    # Determine assignment context
    scenario_company_id = UUID(scenario["company_id"])
    assignment_context = await determine_assignment_context(
        db, admin_user.company_id, scenario_company_id
    )
    
    # Initialize mode progress
    mode_progress = {}
    for mode in assigned_modes:
        mode_progress[mode.value] = {"completed": False, "completed_date": None}
    
    # Create assignment record with full company context
    assignment = ScenarioAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        module_id=module_id,
        scenario_id=scenario_id,
        assigned_date=datetime.now(),
        assigned_modes=assigned_modes,
        completed=False,
        completed_date=None,
        mode_progress=mode_progress
    )
    
    # Convert to DB model with company context
    assignment_db = ScenarioAssignmentDB(
        **assignment.dict(),
        assigned_by=assigned_by,
        assigned_by_company=admin_user.company_id,
        source_company=scenario_company_id,
        assignment_context=assignment_context
    )
    
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    assignment_dict["module_id"] = str(assignment_dict["module_id"])
    assignment_dict["scenario_id"] = str(assignment_dict["scenario_id"])
    assignment_dict["assigned_by"] = str(assignment_dict["assigned_by"])
    assignment_dict["assigned_by_company"] = str(assignment_dict["assigned_by_company"])
    assignment_dict["source_company"] = str(assignment_dict["source_company"])
    
    # Convert ScenarioModeType enum values to strings
    assignment_dict["assigned_modes"] = [mode.value for mode in assignment_dict["assigned_modes"]]
    
    # Insert into database
    result = await db.user_scenario_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_scenario_assignments.find_one({"_id": str(result.inserted_id)})
    
    return ScenarioAssignmentDB(**created_assignment)

# Bulk create scenario assignments with company context
async def bulk_create_scenario_assignments(
    db: Any,
    bulk_assignment: BulkScenarioAssignmentCreate,
    assigned_by: Optional[UUID] = None
) -> List[ScenarioAssignmentDB]:
    """Create multiple scenario assignments at once with company context tracking"""
    
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
    
    # Verify that the user has access to the module
    module_assignment = await db.user_module_assignments.find_one({
        "user_id": str(bulk_assignment.user_id),
        "module_id": str(bulk_assignment.module_id),
        "is_archived": False
    })
    
    if not module_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must be assigned to the module before assigning scenarios"
        )
    
    # Get module to verify scenarios
    module = await db.modules.find_one({"_id": str(bulk_assignment.module_id)})
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {bulk_assignment.module_id} not found"
        )
    
    # Convert scenario IDs to strings
    scenario_ids_str = [str(scenario_id) for scenario_id in bulk_assignment.scenario_ids]
    
    # Verify all scenarios belong to the module and get scenario info
    module_scenario_ids = module.get("scenarios", [])
    invalid_scenarios = [s_id for s_id in scenario_ids_str if s_id not in module_scenario_ids]
    
    if invalid_scenarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following scenarios do not belong to the module: {', '.join(invalid_scenarios)}"
        )
    
    # Get scenarios info for permission checking and company context
    scenarios_info = {}
    for scenario_id in scenario_ids_str:
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if scenario and not scenario.get("is_archived", False):
            scenarios_info[scenario_id] = scenario
    
    # Validate assignment permissions for each scenario
    from core.scenario import can_user_assign_scenario, ScenarioDB
    for scenario_id, scenario_doc in scenarios_info.items():
        scenario_obj = ScenarioDB(**scenario_doc)
        if admin_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and not await can_user_assign_scenario(db, admin_user, scenario_obj):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not authorized to assign scenario {scenario_id}"
            )
    
    if bulk_assignment.operation == "add":
        # Find existing assignments for these scenarios
        existing_assignments = await db.user_scenario_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "scenario_id": {"$in": scenario_ids_str}
        }).to_list(length=None)
        
        existing_scenario_ids = [assignment["scenario_id"] for assignment in existing_assignments]
        
        results = []
        
        # Reactivate archived assignments and update existing ones if modes have changed
        for assignment in existing_assignments:
            scenario_id = assignment["scenario_id"]
            scenario_uuid = UUID(scenario_id)
            
            # Determine assigned modes for this scenario
            if bulk_assignment.assigned_modes and scenario_uuid in bulk_assignment.assigned_modes:
                assigned_modes = bulk_assignment.assigned_modes[scenario_uuid]
            else:
                assigned_modes = [
                    ScenarioModeType.LEARN_MODE,
                    ScenarioModeType.TRY_MODE,
                    ScenarioModeType.ASSESS_MODE
                ]
            
            if assignment.get("is_archived", False):
                # Reactivate archived assignment
                mode_progress = {}
                for mode in assigned_modes:
                    mode_progress[mode.value] = {"completed": False, "completed_date": None}
                
                scenario_company_id = UUID(scenarios_info[scenario_id]["company_id"])
                assignment_context = await determine_assignment_context(
                    db, admin_user.company_id, scenario_company_id
                )
                
                await db.user_scenario_assignments.update_one(
                    {"_id": assignment["_id"]},
                    {"$set": {
                        "is_archived": False,
                        "archived_at": None,
                        "archived_by": None,
                        "archived_reason": None,
                        "assigned_by": str(assigned_by),
                        "assigned_by_company": str(admin_user.company_id),
                        "assignment_context": assignment_context,
                        "assigned_modes": [mode.value for mode in assigned_modes],
                        "mode_progress": mode_progress,
                        "assigned_date": datetime.now()
                    }}
                )
                
                updated = await db.user_scenario_assignments.find_one({"_id": assignment["_id"]})
                results.append(ScenarioAssignmentDB(**updated))
            else:
                # Update existing active assignment if modes have changed
                existing_modes = set(assignment.get("assigned_modes", []))
                new_modes = set(mode.value for mode in assigned_modes)
                
                if existing_modes != new_modes:
                    # Initialize mode progress for new modes
                    mode_progress = assignment.get("mode_progress", {})
                    for mode in assigned_modes:
                        if mode.value not in mode_progress:
                            if not mode_progress:
                                mode_progress = {}
                            mode_progress[mode.value] = {"completed": False, "completed_date": None}
                    
                    scenario_company_id = UUID(scenarios_info[scenario_id]["company_id"])
                    assignment_context = await determine_assignment_context(
                        db, admin_user.company_id, scenario_company_id
                    )
                    
                    # Update assignment
                    await db.user_scenario_assignments.update_one(
                        {"_id": assignment["_id"]},
                        {"$set": {
                            "assigned_modes": [mode.value for mode in assigned_modes],
                            "mode_progress": mode_progress,
                            "assigned_by": str(assigned_by),
                            "assigned_by_company": str(admin_user.company_id),
                            "assignment_context": assignment_context
                        }}
                    )
                    
                    updated = await db.user_scenario_assignments.find_one({"_id": assignment["_id"]})
                    results.append(ScenarioAssignmentDB(**updated))
                else:
                    results.append(ScenarioAssignmentDB(**assignment))
        
        # Filter out scenarios that are already assigned (active)
        active_existing = [a["scenario_id"] for a in existing_assignments if not a.get("is_archived", False)]
        new_scenario_ids = [s_id for s_id in scenario_ids_str if s_id not in active_existing]
        
        # Create new assignments
        for scenario_id_str in new_scenario_ids:
            if scenario_id_str in scenarios_info:
                scenario_id = UUID(scenario_id_str)
                scenario_company_id = scenarios_info[scenario_id_str]["company_id"]
                assignment_context = await determine_assignment_context(
                    db, admin_user.company_id, scenario_company_id
                )
                
                # Default to all modes unless specifically set
                assigned_modes = bulk_assignment.assigned_modes.get(scenario_id, [
                    ScenarioModeType.LEARN_MODE,
                    ScenarioModeType.TRY_MODE,
                    ScenarioModeType.ASSESS_MODE
                ]) if bulk_assignment.assigned_modes else [
                    ScenarioModeType.LEARN_MODE,
                    ScenarioModeType.TRY_MODE,
                    ScenarioModeType.ASSESS_MODE
                ]
                
                # Initialize mode progress
                mode_progress = {}
                for mode in assigned_modes:
                    mode_progress[mode.value] = {"completed": False, "completed_date": None}
                
                assignment = ScenarioAssignmentCreate(
                    user_id=bulk_assignment.user_id,
                    course_id=bulk_assignment.course_id,
                    module_id=bulk_assignment.module_id,
                    scenario_id=scenario_id,
                    assigned_date=datetime.now(),
                    assigned_modes=assigned_modes,
                    completed=False,
                    completed_date=None,
                    mode_progress=mode_progress
                )
                
                # Convert to DB model with company context
                assignment_db = ScenarioAssignmentDB(
                    **assignment.dict(),
                    assigned_by=assigned_by,
                    assigned_by_company=admin_user.company_id,
                    source_company=scenario_company_id,
                    assignment_context=assignment_context
                )
                assignment_dict = assignment_db.dict(by_alias=True)
                
                # Convert UUIDs to strings for MongoDB
                assignment_dict["_id"] = str(uuid4())
                assignment_dict["user_id"] = str(assignment_dict["user_id"])
                assignment_dict["course_id"] = str(assignment_dict["course_id"])
                assignment_dict["module_id"] = str(assignment_dict["module_id"])
                assignment_dict["scenario_id"] = str(assignment_dict["scenario_id"])
                assignment_dict["assigned_by"] = str(assignment_dict["assigned_by"])
                assignment_dict["assigned_by_company"] = str(assignment_dict["assigned_by_company"])
                assignment_dict["source_company"] = str(assignment_dict["source_company"])
                
                # Convert ScenarioModeType enum values to strings
                assignment_dict["assigned_modes"] = [mode.value for mode in assignment_dict["assigned_modes"]]
                
                # Insert into database
                result = await db.user_scenario_assignments.insert_one(assignment_dict)
                created_assignment = await db.user_scenario_assignments.find_one({"_id": str(result.inserted_id)})
                
                results.append(ScenarioAssignmentDB(**created_assignment))
        
        return results
            
    elif bulk_assignment.operation == "remove":
        # Archive the assignments instead of deleting
        result = await db.user_scenario_assignments.update_many(
            {
                "user_id": str(bulk_assignment.user_id),
                "scenario_id": {"$in": scenario_ids_str},
                "is_archived": False
            },
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(assigned_by),
                "archived_reason": "Bulk removal"
            }}
        )
        
        # Return remaining active assignments for this module
        remaining = await db.user_scenario_assignments.find({
            "user_id": str(bulk_assignment.user_id),
            "module_id": str(bulk_assignment.module_id),
            "is_archived": False
        }).to_list(length=None)
        
        return [ScenarioAssignmentDB(**assignment) for assignment in remaining]
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {bulk_assignment.operation}. Must be 'add' or 'remove'."
        )

# Get all scenario assignments for a user
async def get_user_scenario_assignments(
    db: Any,
    user_id: UUID,
    include_archived: bool = False
) -> List[ScenarioAssignmentDB]:
    """Get all scenario assignments for a user"""
    
    query = {"user_id": str(user_id)}
    if not include_archived:
        query["is_archived"] = False
    
    assignments = []
    cursor = db.user_scenario_assignments.find(query)
    async for document in cursor:
        assignments.append(ScenarioAssignmentDB(**document))
    
    return assignments

# Get scenario assignments for a user and module
async def get_user_module_scenario_assignments(
    db: Any,
    user_id: UUID,
    module_id: UUID,
    include_archived: bool = False
) -> List[ScenarioAssignmentDB]:
    """Get all scenario assignments for a user within a specific module"""
    
    query = {
        "user_id": str(user_id),
        "module_id": str(module_id)
    }
    if not include_archived:
        query["is_archived"] = False
    
    assignments = []
    cursor = db.user_scenario_assignments.find(query)
    async for document in cursor:
        assignments.append(ScenarioAssignmentDB(**document))
    
    return assignments

# Get a specific scenario assignment
async def get_scenario_assignment(
    db: Any,
    user_id: UUID,
    scenario_id: UUID
) -> Optional[ScenarioAssignmentDB]:
    """Get a specific scenario assignment"""
    
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id)
    })
    
    if assignment:
        return ScenarioAssignmentDB(**assignment)
    
    return None

# Get a specific scenario assignment by ID
async def get_scenario_assignment_by_id(
    db: Any,
    assignment_id: UUID
) -> Optional[ScenarioAssignmentDB]:
    """Get a scenario assignment by its ID"""
    
    assignment = await db.user_scenario_assignments.find_one({
        "_id": str(assignment_id)
    })
    
    if assignment:
        return ScenarioAssignmentDB(**assignment)
    
    return None

# Update a scenario assignment
async def update_scenario_assignment(
    db: Any,
    user_id: UUID,
    scenario_id: UUID,
    update_data: ScenarioAssignmentUpdate
) -> Optional[ScenarioAssignmentDB]:
    """Update a scenario assignment"""
    
    # Find the assignment
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id)
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
            if key == "assigned_modes":
                update_dict[key] = [mode.value for mode in value]
            elif key == "mode_progress":
                # Convert mode_progress values for MongoDB
                mode_progress_dict = {}
                for mode, progress in value.items():
                    mode_progress_dict[mode.value] = progress.dict()
                update_dict[key] = mode_progress_dict
            else:
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
        await db.user_scenario_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_scenario_assignments.find_one({"_id": assignment["_id"]})
        if updated_assignment:
            assignment_db = ScenarioAssignmentDB(**updated_assignment)
            
            # If the scenario was marked as completed, update module completion
            if update_dict.get("completed", False):
                from core.module_assignment import update_module_completion_status
                await update_module_completion_status(db, user_id, UUID(assignment["module_id"]))
            
            return assignment_db
    
    return ScenarioAssignmentDB(**assignment)

# Update a scenario assignment by ID
async def update_scenario_assignment_by_id(
    db: Any,
    assignment_id: UUID,
    update_data: ScenarioAssignmentUpdate
) -> Optional[ScenarioAssignmentDB]:
    """Update a scenario assignment by its ID"""
    
    # Find the assignment
    assignment = await db.user_scenario_assignments.find_one({
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
            if key == "assigned_modes":
                update_dict[key] = [mode.value for mode in value]
            elif key == "mode_progress":
                # Convert mode_progress values for MongoDB
                mode_progress_dict = {}
                for mode, progress in value.items():
                    mode_progress_dict[mode.value] = progress.dict()
                update_dict[key] = mode_progress_dict
            else:
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
        await db.user_scenario_assignments.update_one(
            {"_id": str(assignment_id)},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_scenario_assignments.find_one({"_id": str(assignment_id)})
        if updated_assignment:
            assignment_db = ScenarioAssignmentDB(**updated_assignment)
            
            # If the scenario was marked as completed, update module completion
            if update_dict.get("completed", False):
                from core.module_assignment import update_module_completion_status
                await update_module_completion_status(
                    db, 
                    UUID(assignment["user_id"]), 
                    UUID(assignment["module_id"])
                )
            
            return assignment_db
    
    return ScenarioAssignmentDB(**assignment)

# Update a specific mode's progress
async def update_mode_progress(
    db: Any,
    user_id: UUID,
    scenario_id: UUID,
    mode: ScenarioModeType,
    progress: ModeProgressUpdate
) -> Optional[ScenarioAssignmentDB]:
    """Update the progress for a specific mode in a scenario assignment"""
    
    # Find the assignment
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id),
        "is_archived": False
    })
    
    if not assignment:
        return None
    
    # Check if mode is assigned
    assigned_modes = assignment.get("assigned_modes", [])
    if mode.value not in assigned_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mode {mode.value} is not assigned to this scenario"
        )
    
    # Update mode progress
    mode_progress = assignment.get("mode_progress", {})
    if not mode_progress:
        mode_progress = {}
    
    mode_progress[mode.value] = progress.dict()
    
    # If marking completed, set completed_date
    if progress.completed and not progress.completed_date:
        mode_progress[mode.value]["completed_date"] = datetime.now()
    
    await db.user_scenario_assignments.update_one(
        {"_id": assignment["_id"]},
        {"$set": {"mode_progress": mode_progress}}
    )
    
    # Check if all assigned modes are completed, and update completion status
    updated_assignment = await db.user_scenario_assignments.find_one({"_id": assignment["_id"]})
    if updated_assignment:
        updated_mode_progress = updated_assignment.get("mode_progress", {})
        all_modes_completed = True
        
        for assigned_mode in assigned_modes:
            if assigned_mode not in updated_mode_progress or not updated_mode_progress[assigned_mode].get("completed", False):
                all_modes_completed = False
                break
        
        # If all modes are completed, mark scenario as completed
        if all_modes_completed:
            await db.user_scenario_assignments.update_one(
                {"_id": assignment["_id"]},
                {"$set": {
                    "completed": True,
                    "completed_date": datetime.now()
                }}
            )
            
            # Update module completion status
            from core.module_assignment import update_module_completion_status
            await update_module_completion_status(db, user_id, UUID(assignment["module_id"]))
        
        # Get final updated assignment
        final_assignment = await db.user_scenario_assignments.find_one({"_id": assignment["_id"]})
        return ScenarioAssignmentDB(**final_assignment)
    
    return ScenarioAssignmentDB(**assignment)

# Archive a scenario assignment (soft delete)
async def archive_scenario_assignment(
    db: Any,
    user_id: UUID,
    scenario_id: UUID,
    archived_by: UUID,
    reason: str = "Manual removal"
) -> bool:
    """Archive a scenario assignment instead of deleting it"""
    
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id)
    })
    
    if not assignment:
        return False
    
    # Archive the assignment
    result = await db.user_scenario_assignments.update_one(
        {"_id": assignment["_id"]},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": reason
        }}
    )
    
    return result.modified_count > 0

# Delete a scenario assignment (now just calls archive)
async def delete_scenario_assignment(
    db: Any,
    user_id: UUID,
    scenario_id: UUID
) -> bool:
    """Delete a scenario assignment - now archives instead"""
    return await archive_scenario_assignment(db, user_id, scenario_id, user_id, "Direct deletion")

# Check if a scenario is assigned to a user
async def is_scenario_assigned(
    db: Any,
    user_id: UUID,
    scenario_id: UUID
) -> bool:
    """Check if a scenario is assigned to a user (active assignment only)"""
    
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id),
        "is_archived": False
    })
    
    return assignment is not None

# Check if a specific mode is assigned to a user for a scenario
async def is_mode_assigned(
    db: Any,
    user_id: UUID,
    scenario_id: UUID,
    mode: ScenarioModeType
) -> bool:
    """Check if a specific mode of a scenario is assigned to a user"""
    
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(user_id),
        "scenario_id": str(scenario_id),
        "is_archived": False
    })
    
    if not assignment:
        return False
    
    assigned_modes = assignment.get("assigned_modes", [])
    return mode.value in assigned_modes

# Get completion stats for a user's scenarios
async def get_user_scenario_completion_stats(
    db: Any,
    user_id: UUID,
    include_archived: bool = False
) -> Dict[str, Any]:
    """Get completion statistics for a user's assigned scenarios"""
    
    query = {"user_id": str(user_id)}
    if not include_archived:
        query["is_archived"] = False
    
    assignments = await db.user_scenario_assignments.find(query).to_list(length=None)
    
    total_scenarios = len(assignments)
    completed_scenarios = sum(1 for a in assignments if a.get("completed", False))
    
    # Mode statistics
    mode_stats = {
        "learn_mode": {"assigned": 0, "completed": 0},
        "try_mode": {"assigned": 0, "completed": 0},
        "assess_mode": {"assigned": 0, "completed": 0}
    }
    
    for assignment in assignments:
        assigned_modes = assignment.get("assigned_modes", [])
        mode_progress = assignment.get("mode_progress", {})
        
        for mode in assigned_modes:
            if mode in mode_stats:
                mode_stats[mode]["assigned"] += 1
                if mode in mode_progress and mode_progress[mode].get("completed", False):
                    mode_stats[mode]["completed"] += 1
    
    # Company context statistics
    internal_assignments = sum(1 for a in assignments if a.get("assignment_context") == "internal")
    cross_company_assignments = sum(1 for a in assignments if a.get("assignment_context") == "cross_company")
    
    return {
        "total_scenarios": total_scenarios,
        "completed_scenarios": completed_scenarios,
        "completion_percentage": (completed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
        "mode_stats": mode_stats,
        "assignment_context_stats": {
            "internal": internal_assignments,
            "cross_company": cross_company_assignments
        }
    }