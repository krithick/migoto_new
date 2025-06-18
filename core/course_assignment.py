from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.user_models import UserDB, UserRole
from models.course_assignment_models import (
    CourseAssignmentCreate, CourseAssignmentDB, CourseAssignmentUpdate, 
    AssignmentContext
)
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
#     course_company: UUID
# ) -> str:
#     """Fixed version with proper validation"""
    
#     # Convert to strings for MongoDB comparison
#     admin_company_str = str(assigning_admin_company)
#     course_company_str = str(course_company)
    
#     if admin_company_str == course_company_str:
#         return AssignmentContext.INTERNAL
    
#     # Check if course is from MOTHER company
#     course_company_doc = await db.companies.find_one({"_id": course_company_str})
#     if not course_company_doc:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Course company not found"
#         )
    
#     if course_company_doc.get("company_type") == CompanyType.MOTHER:
#         return AssignmentContext.CROSS_COMPANY
    
#     # FIXED: This was missing - should block invalid cross-company assignments
#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Cannot assign content from different non-mother company"
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
# Create an assignment with company context
async def create_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    assigned_by: UUID
) -> CourseAssignmentDB:
    """Fixed version with proper error handling"""
    
    # Get assigning admin info
    admin = await db.users.find_one({"_id": str(assigned_by)})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # FIXED: was 403
            detail="Assigning user not found"
        )
    
    admin_user = UserDB(**admin)
    
    # Get course info
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if course is archived
    if course.get("is_archived", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign archived course"
        )
    
    # Get target user info
    target_user = await db.users.find_one({"_id": str(user_id)})
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # FIXED: was 400
            detail="Target user not found"
        )
    
    target_user_obj = UserDB(**target_user)
    
    # Validate assignment permissions with FIXED context determination
    try:
        assignment_context = await determine_assignment_context(
            db, admin_user.company_id, UUID(course["company_id"])
        )
    except HTTPException as e:
        # Re-raise permission errors as-is
        raise e
    
    # Validate assignment permissions
    from core.course import can_user_assign_course, CourseDB
    course_obj = CourseDB(**course)
    
    if not await can_user_assign_course(db, admin_user, course_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to assign this course"
        )
    
    # Check if assignment already exists (including archived ones)
    existing = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if existing:
        existing_assignment = CourseAssignmentDB(**existing)
        if existing_assignment.is_archived:
            # Reactivate archived assignment with new context
            await db.user_course_assignments.update_one(
                {"_id": str(existing_assignment.id)},
                {"$set": {
                    "is_archived": False,
                    "archived_at": None,
                    "archived_by": None,
                    "archived_reason": None,
                    "assigned_by": str(assigned_by),
                    "assigned_by_company": str(admin_user.company_id),
                    "assignment_context": await determine_assignment_context(
                        db, admin_user.company_id, UUID(course["company_id"])
                    ),
                    "assigned_date": datetime.now()
                }}
            )
            reactivated = await db.user_course_assignments.find_one({"_id": str(existing_assignment.id)})
            return CourseAssignmentDB(**reactivated)
        else:
            # Assignment already exists and is active
            return existing_assignment
    
    # Determine assignment context
    course_company_id = UUID(course["company_id"])
    assignment_context = await determine_assignment_context(
        db, admin_user.company_id, course_company_id
    )
    
    # Create assignment record with full company context
    assignment = CourseAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        assigned_date=datetime.now(),
        completed=False,
        completed_date=None
    )
    
    # Convert to DB model with company context
    assignment_db = CourseAssignmentDB(
        **assignment.dict(),
        assigned_by=assigned_by,
        assigned_by_company=admin_user.company_id,
        source_company=course_company_id,
        assignment_context=assignment_context
    )
    
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    assignment_dict["assigned_by"] = str(assignment_dict["assigned_by"])
    assignment_dict["assigned_by_company"] = str(assignment_dict["assigned_by_company"])
    assignment_dict["source_company"] = str(assignment_dict["source_company"])
    
    # Insert into database
    result = await db.user_course_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_course_assignments.find_one({"_id": str(result.inserted_id)})
    
    return CourseAssignmentDB(**created_assignment)

# Get all course assignments for a user
async def get_user_course_assignments(
    db: Any,
    user_id: UUID,
    include_archived: bool = False
) -> List[CourseAssignmentDB]:
    """Get all course assignments for a user"""
    
    query = {"user_id": str(user_id)}
    if not include_archived:
        query["is_archived"] = False
    
    assignments = []
    cursor = db.user_course_assignments.find(query)
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
        await db.user_course_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_course_assignments.find_one({"_id": assignment["_id"]})
        if updated_assignment:
            return CourseAssignmentDB(**updated_assignment)
    
    return CourseAssignmentDB(**assignment)

# Archive a course assignment (soft delete)
# async def archive_course_assignment(
#     db: Any,
#     user_id: UUID,
#     course_id: UUID,
#     archived_by: UUID,
#     reason: str = "Manual removal"
# ) -> bool:
#     """Archive a course assignment instead of deleting it"""
    
#     assignment = await db.user_course_assignments.find_one({
#         "user_id": str(user_id),
#         "course_id": str(course_id)
#     })
    
#     if not assignment:
#         return False
    
#     # Archive the assignment
#     result = await db.user_course_assignments.update_one(
#         {"_id": assignment["_id"]},
#         {"$set": {
#             "is_archived": True,
#             "archived_at": datetime.now(),
#             "archived_by": str(archived_by),
#             "archived_reason": reason
#         }}
#     )
    
#     # Also archive related module and scenario assignments
#     await db.user_module_assignments.update_many(
#         {
#             "user_id": str(user_id),
#             "course_id": str(course_id),
#             "is_archived": False
#         },
#         {"$set": {
#             "is_archived": True,
#             "archived_at": datetime.now(),
#             "archived_by": str(archived_by),
#             "archived_reason": f"Course assignment archived: {reason}"
#         }}
#     )
    
#     await db.user_scenario_assignments.update_many(
#         {
#             "user_id": str(user_id),
#             "course_id": str(course_id),
#             "is_archived": False
#         },
#         {"$set": {
#             "is_archived": True,
#             "archived_at": datetime.now(),
#             "archived_by": str(archived_by),
#             "archived_reason": f"Course assignment archived: {reason}"
#         }}
#     )
    
#     # Remove course from user's assigned_courses array
#     await db.users.update_one(
#         {"_id": str(user_id)},
#         {"$pull": {"assigned_courses": str(course_id)}}
#     )
    
#     return result.modified_count > 0


async def archive_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    archived_by: UUID,
    reason: str = "Manual removal"
) -> bool:
    """Archive a course assignment instead of deleting it"""
    
    try:  # Optional: Add try-catch for robustness
        assignment = await db.user_course_assignments.find_one({
            "user_id": str(user_id),
            "course_id": str(course_id)
        })
        
        if not assignment:
            return False
        
        # Archive the assignment
        result = await db.user_course_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(archived_by),
                "archived_reason": reason
            }}
        )
        
        # Also archive related module and scenario assignments
        await db.user_module_assignments.update_many(
            {
                "user_id": str(user_id),
                "course_id": str(course_id),
                "is_archived": False
            },
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(archived_by),
                "archived_reason": f"Course assignment archived: {reason}"
            }}
        )
        
        await db.user_scenario_assignments.update_many(
            {
                "user_id": str(user_id),
                "course_id": str(course_id),
                "is_archived": False
            },
            {"$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(archived_by),
                "archived_reason": f"Course assignment archived: {reason}"
            }}
        )
        
        # Remove course from user's assigned_courses array
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$pull": {"assigned_courses": str(course_id)}}
        )
        
        return result.modified_count > 0
        
    except Exception as e:  # Optional: Add error handling
        print(f"Error archiving course assignment: {str(e)}")
        return False
# Delete a course assignment (now just calls archive)
async def delete_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> bool:
    """Delete a course assignment - now archives instead"""
    return await archive_course_assignment(db, user_id, course_id, user_id, "Direct deletion")

# Get courses with assignment data and company context
async def get_user_courses_with_assignments(
    db: Any,
    user_id: UUID,
    include_archived: bool = False
) -> List[Dict[str, Any]]:
    """Get all courses assigned to a user with assignment data and company context"""
    
    user = await db.users.find_one({"_id": str(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all assignments for this user
    assignment_query = {"user_id": str(user_id)}
    if not include_archived:
        assignment_query["is_archived"] = False
    
    assignments = {}
    cursor = db.user_course_assignments.find(assignment_query)
    async for assignment in cursor:
        course_id = assignment["course_id"]
        assignments[course_id] = {
            "assigned_date": assignment["assigned_date"],
            "completed": assignment.get("completed", False),
            "completed_date": assignment.get("completed_date"),
            "assigned_by_company": assignment.get("assigned_by_company"),
            "source_company": assignment.get("source_company"),
            "assignment_context": assignment.get("assignment_context", "internal"),
            "assigned_by": assignment.get("assigned_by"),
            "is_archived": assignment.get("is_archived", False)
        }
    
    # Get course data for assigned courses
    assigned_course_ids = list(assignments.keys())
    courses = []
    
    if assigned_course_ids:
        course_query = {"_id": {"$in": assigned_course_ids}}
        if not include_archived:
            course_query["is_archived"] = False
        
        cursor = db.courses.find(course_query)
        async for course in cursor:
            # Convert _id to id
            course["id"] = course.pop("_id")
            course_id = course["id"]
            
            # Add assignment data
            if course_id in assignments:
                assignment_data = assignments[course_id]
                course.update(assignment_data)
                
                # Add company information for transparency
                try:
                    if assignment_data.get("assigned_by_company"):
                        assigning_company = await get_company_by_id(db, UUID(assignment_data["assigned_by_company"]))
                        course["assigned_by_company_name"] = assigning_company.name if assigning_company else "Unknown"
                    
                    if assignment_data.get("source_company"):
                        source_company = await get_company_by_id(db, UUID(assignment_data["source_company"]))
                        course["source_company_name"] = source_company.name if source_company else "Unknown"
                        
                except Exception as e:
                    print(f"Error fetching company names: {e}")
                    course["assigned_by_company_name"] = "Unknown"
                    course["source_company_name"] = "Unknown"
            else:
                # Default values for courses without assignment data
                course["assigned_date"] = user.get("created_at", datetime.now())
                course["completed"] = False
                course["completed_date"] = None
                course["assignment_context"] = "internal"
                course["is_archived"] = False
            
            courses.append(course)
    
    return courses

# Update course completion based on module completions
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
            "course_id": str(course_id),
            "is_archived": False
        })
        
        if not course_assignment:
            return False
        
        # Get all module assignments for this course
        module_assignments = await db.user_module_assignments.find({
            "user_id": str(user_id),
            "course_id": str(course_id),
            "is_archived": False
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
        await db.user_course_assignments.update_one(
            {
                "user_id": str(user_id),
                "course_id": str(course_id),
                "is_archived": False
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

# Assign course with content and company context tracking
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
    Assign a course to a user with company context tracking,
    optionally with its modules and scenarios
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required"
        )
    
    # Import functions to avoid circular imports
    from core.module_assignment import bulk_create_module_assignments
    from core.scenario_assignment import bulk_create_scenario_assignments
    from models.module_assignment_models import BulkModuleAssignmentCreate
    from models.scenario_assignment_models import BulkScenarioAssignmentCreate, ScenarioModeType
    from core.user import get_user_by_id
    
    # Create course assignment with company context
    course_assignment = await create_course_assignment(db, user_id, course_id, current_user.id)
    
    # Validate target user
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
            "scenarios_assigned": 0,
            "assignment_context": course_assignment.assignment_context if course_assignment else "unknown"
        }
    
    # Add course to user's assigned_courses array
    await db.users.update_one(
        {"_id": str(user_id)},
        {"$addToSet": {"assigned_courses": str(course_id)}}
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
        
        # Execute bulk assignment (this will handle company context internally)
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
            
            # Execute bulk assignment (this will handle company context internally)
            scenario_assignments = await bulk_create_scenario_assignments(db, bulk_scenario_assignment)
            scenarios_assigned += len(scenario_assignments)
    
    return {
        "course_assigned": course_assignment is not None,
        "modules_assigned": modules_assigned,
        "scenarios_assigned": scenarios_assigned,
        "assignment_context": course_assignment.assignment_context if course_assignment else "unknown",
        "assigned_by_company": str(course_assignment.assigned_by_company) if course_assignment else None,
        "source_company": str(course_assignment.source_company) if course_assignment else None
    }