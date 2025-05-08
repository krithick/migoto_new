from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.user_models import UserDB, UserRole
from models.course_assignment_models import CourseAssignmentCreate, CourseAssignmentDB, CourseAssignmentUpdate

# Create an assignment
async def create_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> CourseAssignmentDB:
    """Assign a course to a user and record the assignment"""
    
    # Check if assignment already exists
    existing = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if existing:
        return CourseAssignmentDB(**existing)
    
    # Create assignment record
    assignment = CourseAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        assigned_date=datetime.now(),
        completed=False,
        completed_date=None
    )
    
    # Convert to DB model
    assignment_db = CourseAssignmentDB(**assignment.dict())
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    
    # Insert into database
    result = await db.user_course_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_course_assignments.find_one({"_id": str(result.inserted_id)})
    
    return CourseAssignmentDB(**created_assignment)

# Get all course assignments for a user
async def get_user_course_assignments(
    db: Any,
    user_id: UUID
) -> List[CourseAssignmentDB]:
    """Get all course assignments for a user"""
    
    assignments = []
    cursor = db.user_course_assignments.find({"user_id": str(user_id)})
    async for document in cursor:
        assignments.append(CourseAssignmentDB(**document))
    
    return assignments

# Get a specific course assignment
async def get_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> Optional[CourseAssignmentDB]:
    """Get a specific course assignment"""
    
    assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if assignment:
        return CourseAssignmentDB(**assignment)
    
    return None

# Update a course assignment
async def update_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    update_data: CourseAssignmentUpdate
) -> Optional[CourseAssignmentDB]:
    """Update a course assignment"""
    
    # Find the assignment
    assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
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
        await db.user_course_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_course_assignments.find_one({"_id": assignment["_id"]})
        if updated_assignment:
            return CourseAssignmentDB(**updated_assignment)
    
    return CourseAssignmentDB(**assignment)

# Delete a course assignment
async def delete_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> bool:
    """Delete a course assignment"""
    
    result = await db.user_course_assignments.delete_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    return result.deleted_count > 0

# Get courses with assignment data
async def get_user_courses_with_assignments(
    db: Any,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """Get all courses assigned to a user with assignment data"""
    
    user = await db.users.find_one({"_id": str(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    assigned_course_ids = [str(course_id) for course_id in user.get("assigned_courses", [])]
    
    # Get all assignments for this user
    assignments = {}
    cursor = db.user_course_assignments.find({"user_id": str(user_id)})
    async for assignment in cursor:
        assignments[assignment["course_id"]] = {
            "assigned_date": assignment["assigned_date"],
            "completed": assignment.get("completed", False),
            "completed_date": assignment.get("completed_date")
        }
    
    # Get course data
    courses = []
    if assigned_course_ids:
        cursor = db.courses.find({"_id": {"$in": assigned_course_ids}})
        async for course in cursor:
            # CRITICAL FIX: Convert _id to id
            course["id"] = course.pop("_id")
            
            # Add assignment data
            course_id = course["id"]  # Now using "id" instead of "_id"
            if course_id in assignments:
                data = assignments[course_id]
                course["assigned_date"] = data["assigned_date"]
                course["completed"] = data["completed"]
                course["completed_date"] = data["completed_date"]
            else:
                # Default values
                course["assigned_date"] = user.get("created_at", datetime.now())
                course["completed"] = False
                course["completed_date"] = None
            
            courses.append(course)
    
    return courses


async def update_course_completion(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> bool:
    """
    Update course completion status based on module completions
    Returns True if the course was completed, False otherwise
    """
    try:
        # Find course assignment
        course_assignment = await db.user_course_assignments.find_one({
            "user_id": str(user_id),
            "course_id": str(course_id)
        })
        
        if not course_assignment:
            return False
        
        # Get all module assignments for this course
        module_assignments = await db.user_module_assignments.find({
            "user_id": str(user_id),
            "course_id": str(course_id)
        }).to_list(length=None)
        
        # If there are no module assignments, don't update course status
        if not module_assignments:
            return False
        
        # Check if all modules are completed
        all_modules_completed = all(
            assignment.get("completed", False) 
            for assignment in module_assignments
        )
        
        # Update course completion status
        completion_date = datetime.now() if all_modules_completed else None
        update_result = await db.user_course_assignments.update_one(
            {
                "user_id": str(user_id),
                "course_id": str(course_id)
            },
            {
                "$set": {
                    "completed": all_modules_completed,
                    "completed_date": completion_date
                }
            }
        )
        
        return all_modules_completed
    except Exception as e:
        print(f"Error updating course completion: {e}")
        return False


async def assign_course_with_content(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    current_user: Optional[UserDB],
    include_all_modules: bool = True,
    include_all_scenarios: bool = True,
    module_ids: List[UUID] = None,
    scenario_mapping: Dict[UUID, List[UUID]] = None,
    mode_mapping: Dict[UUID, List[str]] = None,
    
) -> Dict[str, Any]:
    """
    Assign a course to a user, optionally with its modules and scenarios
    
    Parameters:
    - user_id: UUID of the user
    - course_id: UUID of the course
    - include_all_modules: Whether to include all modules in the course
    - include_all_scenarios: Whether to include all scenarios in modules
    - module_ids: List of specific module IDs to include (if not all)
    - scenario_mapping: Dict mapping module IDs to lists of scenario IDs
    - mode_mapping: Dict mapping scenario IDs to lists of modes
    
    Returns:
    - Dict with course, module, and scenario assignment counts
    """
    # Import functions to avoid circular imports
    from core.module_assignment import bulk_create_module_assignments
    from core.scenario_assignment import bulk_create_scenario_assignments
    from models.module_assignment_models import BulkModuleAssignmentCreate
    from models.scenario_assignment_models import BulkScenarioAssignmentCreate, ScenarioModeType
    from core.user import get_user_by_id
    # Create course assignment
    course_assignment = await create_course_assignment(db, user_id, course_id)
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified user does not exist"
        )
    # Get course to find modules
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        return {
            "course_assigned": course_assignment is not None,
            "modules_assigned": 0,
            "scenarios_assigned": 0
        }
    await db.users.update_one(
    {"_id": str(user_id)},
    {"$addToSet": {"assigned_courses": str(user_id)}}
)
    # Determine which modules to assign
    modules_to_assign = []
    if include_all_modules:
        modules_to_assign = course.get("modules", [])
    elif module_ids:
        modules_to_assign = [str(m_id) for m_id in module_ids]
    
    # Create module assignments if needed
    modules_assigned = 0
    if modules_to_assign:
        # Convert string IDs to UUIDs
        module_ids_uuid = [UUID(m_id) for m_id in modules_to_assign]
        
        # Create bulk assignment
        bulk_module_assignment = BulkModuleAssignmentCreate(
            user_id=user_id,
            course_id=course_id,
            module_ids=module_ids_uuid,
            operation="add"
        )
        
        # Execute bulk assignment
        module_assignments = await bulk_create_module_assignments(db, bulk_module_assignment)
        modules_assigned = len(module_assignments)
    
    # Create scenario assignments if needed
    scenarios_assigned = 0
    if include_all_scenarios or scenario_mapping:
        for module_id in modules_to_assign:
            # Get module to find scenarios
            module = await db.modules.find_one({"_id": module_id})
            if not module:
                continue
            
            # Determine which scenarios to assign
            scenarios_to_assign = []
            if include_all_scenarios:
                scenarios_to_assign = module.get("scenarios", [])
            elif scenario_mapping and UUID(module_id) in scenario_mapping:
                scenarios_to_assign = [str(s_id) for s_id in scenario_mapping[UUID(module_id)]]
            
            if not scenarios_to_assign:
                continue
            
            # Convert string IDs to UUIDs
            scenario_ids_uuid = [UUID(s_id) for s_id in scenarios_to_assign]
            
            # Determine modes for each scenario
            assigned_modes = {}
            if mode_mapping:
                for s_id in scenario_ids_uuid:
                    if s_id in mode_mapping:
                        assigned_modes[s_id] = [
                            ScenarioModeType(mode) for mode in mode_mapping[s_id]
                        ]
            
            # Create bulk assignment
            bulk_scenario_assignment = BulkScenarioAssignmentCreate(
                user_id=user_id,
                course_id=course_id,
                module_id=UUID(module_id),
                scenario_ids=scenario_ids_uuid,
                assigned_modes=assigned_modes if assigned_modes else None,
                operation="add"
            )
            
            # Execute bulk assignment
            scenario_assignments = await bulk_create_scenario_assignments(db, bulk_scenario_assignment)
            scenarios_assigned += len(scenario_assignments)
    
    return {
        "course_assigned": course_assignment is not None,
        "modules_assigned": modules_assigned,
        "scenarios_assigned": scenarios_assigned
    }