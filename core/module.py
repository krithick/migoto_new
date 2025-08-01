from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime


from models.user_models import UserDB , UserRole
from models.modules_models import ModuleCreate, ModuleResponse,ModuleWithAssignmentResponse, ModuleWithScenariosResponse, ModuleDB, ModuleBase, ScenarioResponse
# from main import get_db
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.course import get_course  # Import from course CRUD to check permissions
from core.scenario_assignment import get_user_module_scenario_assignments

from models.company_models import CompanyType, CompanyDB
from models.modules_models import ContentVisibility, ModuleUpdate  
# Create router
router = APIRouter(tags=["Modules"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

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
# Module Any Operations
# async def get_modules(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[ModuleDB]:
#     """
#     Get a list of all modules with permission checks.
#     - Admins/Superadmins: all modules
#     - Regular users: only modules from assigned courses
#     """
#     if not current_user:
#         return []
    
#     modules = []
    
#     # For admins and superadmins, return all modules
#     if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
#         cursor = db.modules.find().skip(skip).limit(limit)
#         async for document in cursor:
#             modules.append(ModuleDB(**document))
#     else:
#         # For regular users, get only modules from assigned courses
#         user_data = current_user.dict()
#         assigned_course_ids = user_data.get("assigned_courses", [])
        
#         # Convert UUIDs to strings for MongoDB
#         assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
        
#         if assigned_course_ids_str:
#             # Get all courses assigned to user
#             courses = []
#             for course_id in assigned_course_ids_str:
#                 course = await db.courses.find_one({"_id": course_id})
#                 if course:
#                     courses.append(course)
            
#             # Extract module IDs from all assigned courses
#             module_ids = []
#             for course in courses:
#                 module_ids.extend(course.get("modules", []))
            
#             # Get modules by these IDs
#             if module_ids:
#                 cursor = db.modules.find({"_id": {"$in": module_ids}}).skip(skip).limit(limit)
#                 async for document in cursor:
#                     modules.append(ModuleDB(**document))
    
#     return modules

async def get_modules(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[ModuleDB]:
    """Get modules based on user's company hierarchy access"""
    if not current_user:
        return []
    
    modules = []
    
    if current_user.role == UserRole.USER:
        # Users only see assigned modules through module assignments
        assignments_cursor = db.user_module_assignments.find({
            "user_id": str(current_user.id),
            "is_archived": False  # Don't show archived assignments
        })
        
        assigned_module_ids = []
        async for assignment in assignments_cursor:
            assigned_module_ids.append(assignment["module_id"])
        
        if assigned_module_ids:
            cursor = db.modules.find({
                "_id": {"$in": assigned_module_ids},
                "is_archived": False  # Don't show archived modules
            }).skip(skip).limit(limit)
            async for document in cursor:
                modules.append(ModuleDB(**document))
    
    elif current_user.role == UserRole.BOSS_ADMIN:
        # Boss admin sees ALL modules from ALL companies
        cursor = db.modules.find({"is_archived": False}).skip(skip).limit(limit)
        async for document in cursor:
            modules.append(ModuleDB(**document))
    
    else:  # ADMIN or SUPERADMIN
        # Get user's company type
        user_company_type = await get_company_hierarchy_type(db, current_user.company_id)
        
        if user_company_type == CompanyType.MOTHER:
            # MOTHER company admins see all modules
            cursor = db.modules.find({"is_archived": False}).skip(skip).limit(limit)
            async for document in cursor:
                modules.append(ModuleDB(**document))
        else:
            # CLIENT/SUBSIDIARY company admins see:
            # 1. Their own company modules
            # 2. MOTHER company modules
            
            # Get all MOTHER companies
            mother_companies = []
            mother_cursor = db.companies.find({"company_type": CompanyType.MOTHER})
            async for company_doc in mother_cursor:
                mother_companies.append(company_doc["_id"])
            
            # Build query for accessible modules
            accessible_companies = [str(current_user.company_id)] + mother_companies
            
            cursor = db.modules.find({
                "company_id": {"$in": accessible_companies},
                "is_archived": False
            }).skip(skip).limit(limit)
            async for document in cursor:
                modules.append(ModuleDB(**document))
    
    return modules
async def get_module(
    db: Any, 
    module_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[ModuleDB]:
    """
    Get a module by ID with permission checks:
    - Admins/Superadmins: can access all modules
    - Regular users: can only access modules from assigned courses
    """
    # Always use string representation for MongoDB query
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        return None
    
    # If admin or superadmin, allow access
    # if current_user and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
    #     return ModuleDB(**module)
    # Replace with:
    if current_user and current_user.role == UserRole.BOSS_ADMIN:
        return ModuleDB(**module)
    elif current_user and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        # Check company hierarchy access
        module_company_id = UUID(module["company_id"])
        user_company_type = await get_company_hierarchy_type(db, current_user.company_id)
    
        # Same company or MOTHER company access
        if (current_user.company_id == module_company_id or 
            await get_company_hierarchy_type(db, module_company_id) == CompanyType.MOTHER):
            return ModuleDB(**module)
    # For regular users, check if module belongs to an assigned course
    if current_user:
        user_data = current_user.dict()
        assigned_course_ids = user_data.get("assigned_courses", [])
        
        # Convert assigned courses to strings for comparison
        assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
        
        # Find courses that contain this module
        courses_with_module = await db.courses.find(
            {"modules": str(module_id), "_id": {"$in": assigned_course_ids_str}}
        ).to_list(None)
        
        if courses_with_module:
            return ModuleDB(**module)
    
    return None

async def get_modules_by_course(
    db: Any, 
    course_id: UUID, 
    current_user: Optional[UserDB] = None
) -> List[ModuleDB]:
    """
    Get all modules belonging to a specific course, with permission checks
    """
    # First check if user can access the course
    course = await get_course(db, course_id, current_user)
    if not course:
        return []
    
    modules = []
    module_ids = course.dict().get("modules", [])
    
    # Convert module_ids to strings for MongoDB
    module_ids_str = [str(module_id) for module_id in module_ids]
    
    # If user is regular user, filter modules by assignment
    if current_user and current_user.role == UserRole.USER:
        # Get assigned modules for this course
        assignments_cursor = db.user_module_assignments.find({
            "user_id": str(current_user.id),
            "course_id": str(course_id)
        })
        
        # Get assigned module IDs
        assigned_module_ids = []
        assigned_module_data = {}
        
        async for assignment in assignments_cursor:
            module_id = assignment["module_id"]
            assigned_module_ids.append(module_id)
            assigned_module_data[module_id] = {
                "completed": assignment.get("completed", False),
                "completed_date": assignment.get("completed_date"),
                "assigned_date": assignment.get("assigned_date")
            }
        
        # Filter module_ids to only show assigned ones
        module_ids_str = [m_id for m_id in module_ids_str if m_id in assigned_module_ids]
        
        # Fetch modules with assignment data
        for module_id in module_ids_str:
            module = await db.modules.find_one({"_id": module_id})
            if module:
                module_obj = ModuleDB(**module)
                module_obj_dict=module_obj.model_dump()
                print(module_obj)
                
                # Add assignment data
                if module_id in assigned_module_data:
                    module_obj_dict["assigned_date"] = assigned_module_data[module_id]["assigned_date"]
                    module_obj_dict["completed"] = assigned_module_data[module_id]["completed"]
                    module_obj_dict["completed_date"] = assigned_module_data[module_id]["completed_date"]
                print(module_obj_dict)
                modules.append(module_obj_dict)
    else:
        # For admins/superadmins, show all modules
        for module_id in module_ids_str:
            module = await db.modules.find_one({"_id": module_id})
            if module:
                modules.append(ModuleDB(**module))
    
    return modules

# Modify the get_module_with_scenarios function to filter by assignment
# async def get_module_with_scenarios(
#     db: Any, 
#     module_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[Dict[str, Any]]:
#     """
#     Get a module with all its scenarios expanded
#     """
#     # First check if user can access this module
#     module = await get_module(db, module_id, current_user)
#     if not module:
#         return None
    
#     # Get module with expanded scenarios
#     module_dict = module.dict()
    
#     # Get scenarios for this module
#     scenario_ids = module_dict.get("scenarios", [])
    
#     # Convert scenario_ids to strings for MongoDB
#     scenario_ids_str = [str(scenario_id) for scenario_id in scenario_ids]
    
#     # If user is regular user, only show assigned scenarios
#     if current_user.role == UserRole.USER:
#         # Get scenario assignments for this user and module
#         scenario_assignments = await get_user_module_scenario_assignments(db, current_user.id, module_id)
#         assigned_scenario_ids = [str(assignment.scenario_id) for assignment in scenario_assignments]
        
#         # Filter scenarios to only show assigned ones
#         scenario_ids_str = [s_id for s_id in scenario_ids_str if s_id in assigned_scenario_ids]
    
#     scenarios = []
    
#     for scenario_id in scenario_ids_str:
#         scenario = await db.scenarios.find_one({"_id": scenario_id})
#         if scenario:
#             scenario["id"] = scenario.pop("_id")
            
#             # If user is regular user, add assignment info to scenario
#             if current_user.role == UserRole.USER:
#                 # Find assignment for this scenario
#                 assignment = await db.user_scenario_assignments.find_one({
#                     "user_id": str(current_user.id),
#                     "scenario_id": scenario_id
#                 })
                
#                 if assignment:
#                     scenario["assigned"] = True
#                     scenario["assigned_modes"] = assignment.get("assigned_modes", [])
#                     scenario["completed"] = assignment.get("completed", False)
#                     scenario["mode_progress"] = assignment.get("mode_progress", {})
            
#             scenarios.append(scenario)
    
#     # Replace scenario IDs with scenario data
#     module_dict["scenarios"] = scenarios
    
#     return module_dict

async def get_module_with_scenarios(
    db: Any, 
    module_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a module with all its scenarios expanded
    """
    # First check if user can access this module
    module = await get_module(db, module_id, current_user)
    if not module:
        return None
    
    # Get module with expanded scenarios
    module_dict = module.dict()
    
    # Get scenarios for this module
    scenario_ids = module_dict.get("scenarios", [])
    
    # Convert scenario_ids to strings for MongoDB
    scenario_ids_str = [str(scenario_id) for scenario_id in scenario_ids]
    
    scenarios = []
    
    # If user is regular user, filter scenarios to only show assigned ones
    if current_user and current_user.role == UserRole.USER:
        # Get scenario assignments for this user and module
        assignments_cursor = db.user_scenario_assignments.find({
            "user_id": str(current_user.id),
            "module_id": str(module_id)
        })
        
        # Get assigned scenario IDs
        assigned_scenario_ids = []
        assigned_scenario_data = {}
        
        async for assignment in assignments_cursor:
            scenario_id = assignment["scenario_id"]
            assigned_scenario_ids.append(scenario_id)
            assigned_scenario_data[scenario_id] = {
                "assigned_modes": assignment.get("assigned_modes", []),
                "completed": assignment.get("completed", False),
                "completed_date": assignment.get("completed_date"),
                "mode_progress": assignment.get("mode_progress", {})
            }
        
        # Filter scenario_ids to only show assigned ones
        scenario_ids_str = [s_id for s_id in scenario_ids_str if s_id in assigned_scenario_ids]
    
    # Fetch scenarios
    for scenario_id in scenario_ids_str:
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if scenario:
            scenario["id"] = scenario.pop("_id")
            
            # Add assignment info for regular users
            if current_user and current_user.role == UserRole.USER:
                if scenario_id in assigned_scenario_data:
                    data = assigned_scenario_data[scenario_id]
                    scenario["assigned"] = True
                    scenario["assigned_modes"] = data["assigned_modes"]
                    scenario["completed"] = data["completed"]
                    scenario["completed_date"] = data["completed_date"]
                    scenario["mode_progress"] = data["mode_progress"]
            
            scenarios.append(scenario)
    
    # Replace scenario IDs with scenario data
    module_dict["scenarios"] = scenarios
    
    print(module_dict, "/full")
    return module_dict
async def create_module(
    db: Any, 
    course_id: UUID, 
    module: ModuleCreate, 
    created_by: UUID,
    role:UserRole
) -> ModuleDB:
    """
    Create a new module within a course
    """
    # First check if course exists - use string representation
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check if creator has permission to modify the course - use string representation
    creator = await db.users.find_one({"_id": str(created_by)})
    if not creator:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    creator = UserDB(**creator)
    if isinstance(creator.company_id, UUID):
        creator_company_id = creator.company_id
    else:
        creator_company_id = UUID(creator.company_id)
    # creator_company_id = UUID(creator.company_id)
    # If creator is admin (not superadmin), check if they created the course
    if creator.role == UserRole.ADMIN and course.get("created_by") != str(created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins can only add modules to courses they created"
        )
    
    # Create ModuleDB model
    module_dict = module.dict()
    module_db = ModuleDB(
    **module_dict,
    creater_role=role,
    created_by=created_by,
    company_id=creator_company_id,  # ADD THIS LINE
    visibility=ContentVisibility.CREATOR_ONLY,  # ADD THIS LINE
    created_at=datetime.now(),
    updated_at=datetime.now()
)    
    # module_db = ModuleDB(
    #     **module_dict,
    #     creater_role=role,
    #     created_by=created_by,  # Set the creator
    #     created_at=datetime.now(),
    #     updated_at=datetime.now()
    # )
    
    # Insert into database
    module_dict = module_db.dict(by_alias=True)
    module_dict["company_id"] = str(module_dict["company_id"])
    
    # Always use string for _id in MongoDB
    if "_id" in module_dict:
        module_dict["_id"] = str(module_dict["_id"])
    
    # Convert all UUIDs to strings for MongoDB
    if "scenarios" in module_dict and module_dict["scenarios"]:
        module_dict["scenarios"] = [str(scenario_id) for scenario_id in module_dict["scenarios"]]
    
    # Store created_by as string
    if "created_by" in module_dict:
        module_dict["created_by"] = str(module_dict["created_by"])
    
    result = await db.modules.insert_one(module_dict)
    
    # Update the course to include this module - use string representation
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$push": {"modules": str(result.inserted_id)}}
    )
    
    created_module = await db.modules.find_one({"_id": str(result.inserted_id)})
    print(created_module,"created_Module",ModuleDB(**created_module))    
    return ModuleDB(**created_module)

async def update_module(
    db: Any, 
    module_id: UUID, 
    module_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[ModuleDB]:
    """
    Update a module with permission checks
    """
    # Get the module to update - use string representation
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update modules they created
        if module.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update modules they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update modules
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update modules"
        )
    
    # Add updated timestamp
    module_updates["updated_at"] = datetime.now()
    
    # Convert scenario UUIDs to strings if present
    if "scenarios" in module_updates and module_updates["scenarios"]:
        module_updates["scenarios"] = [str(scenario_id) for scenario_id in module_updates["scenarios"]]
    
    # Update in database - use string representation
    await db.modules.update_one(
        {"_id": str(module_id)},
        {"$set": module_updates}
    )
    
    updated_module = await db.modules.find_one({"_id": str(module_id)})
    if updated_module:
        return ModuleDB(**updated_module)
    return None

# async def delete_module(db: Any, module_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete a module with permission checks
#     """
#     # Get the module to delete - use string representation
#     module = await db.modules.find_one({"_id": str(module_id)})
#     if not module:
#         return False
    
#     # Get the user making the deletion - use string representation
#     deleter = await db.users.find_one({"_id": str(deleted_by)})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions - compare string representations
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete modules they created
#         if module.get("created_by") != str(deleted_by):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete modules they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete modules
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete modules"
#         )
    
#     # Remove module from any courses - use string representation
#     await db.courses.update_many(
#         {"modules": str(module_id)},
#         {"$pull": {"modules": str(module_id)}}
#     )
    
#     # Delete the module - use string representation
#     result = await db.modules.delete_one({"_id": str(module_id)})
    
#     return result.deleted_count > 0

async def archive_module(db: Any, module_id: UUID, archived_by: UUID, reason: str = "Manual archive") -> bool:
    """Archive a module (soft delete) instead of hard deletion"""
    # Get the module
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        return False
    
    # Get the user making the archive
    deleter = await db.users.find_one({"_id": str(archived_by)})
    if not deleter:
        return False
    
    deleter = UserDB(**deleter)
    
    # Check permissions (same as your existing logic)
    if deleter.role == UserRole.ADMIN:
        if module.get("created_by") != str(archived_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only archive modules they created"
            )
    elif deleter.role != UserRole.SUPERADMIN and deleter.role != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive modules"
        )
    
    # Archive the module
    await db.modules.update_one(
        {"_id": str(module_id)},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": reason,
            "updated_at": datetime.now()
        }}
    )
    
    # Archive all assignments for this module
    await db.user_module_assignments.update_many(
        {"module_id": str(module_id), "is_archived": False},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": f"Module archived: {reason}"
        }}
    )
    
    return True

# Keep delete_module as a wrapper
async def delete_module(db: Any, module_id: UUID, deleted_by: UUID) -> bool:
    """Delete a module - now just calls archive_module"""
    return await archive_module(db, module_id, deleted_by, "Module deleted")
async def reorder_module_scenarios(
    db: Any, 
    module_id: UUID, 
    scenario_ids: List[UUID], 
    updated_by: UUID
) -> Optional[ModuleDB]:
    """
    Reorder scenarios in a module
    """
    # Get the module to update - use string representation
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update modules they created
        if module.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only reorder scenarios in modules they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update modules
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reorder scenarios"
        )
    
    # Verify that all scenario IDs exist in the module
    existing_scenarios = set(str(s_id) for s_id in module.get("scenarios", []))
    new_scenarios = set(str(s_id) for s_id in scenario_ids)
    
    if existing_scenarios != new_scenarios:
        # The sets of scenarios don't match
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided scenario IDs don't match the module's scenarios"
        )
    
    # Convert scenario IDs to strings for MongoDB
    scenario_ids_str = [str(s_id) for s_id in scenario_ids]
    
    # Update the module with the new scenario order - use string representation
    await db.modules.update_one(
        {"_id": str(module_id)},
        {
            "$set": {
                "scenarios": scenario_ids_str,
                "updated_at": datetime.now()
            }
        }
    )
    
    updated_module = await db.modules.find_one({"_id": str(module_id)})
    if updated_module:
        return ModuleDB(**updated_module)
    return None

# Module API Endpoints
@router.get("/modules", response_model=List[ModuleResponse])
async def get_modules_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all modules (filtered by user role)
    """
    return await get_modules(db, skip, limit, current_user)

@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module_endpoint(
    module_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific module by ID (with permission checks)
    """
    module = await get_module(db, module_id, current_user)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Module not found or access denied")
    return module

@router.get("/courses/{course_id}/modules", response_model=List[ModuleWithAssignmentResponse])
# @router.get("/courses/{course_id}/modules", response_model=List[ModuleResponse])response_model=Dict[str, Any]
async def get_modules_by_course_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all modules belonging to a specific course
    """
    modules = await get_modules_by_course(db, course_id, current_user)
    return modules

@router.get("/modules/{module_id}/full", response_model=ModuleWithScenariosResponse)
async def get_module_with_scenarios_endpoint(
    module_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a module with all its scenarios expanded
    """
    module = await get_module_with_scenarios(db, module_id, current_user)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Module not found or access denied")
    return module

@router.post("/courses/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module_endpoint(
    course_id: UUID,
    module: ModuleCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create modules
):
    """
    Create a new module in a course (admin/superadmin only)
    """
    return await create_module(db, course_id, module, admin_user.id,admin_user.role)

@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module_endpoint(
    module_id: UUID,
    module_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update modules
):
    """
    Update a module by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_module = await update_module(db, module_id, module_updates, admin_user.id)
    if not updated_module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return updated_module

# @router.delete("/modules/{module_id}", response_model=Dict[str, bool])
# async def delete_module_endpoint(
#     module_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete modules
# ):
#     """
#     Delete a module by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_module(db, module_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
#     return {"success": True}

async def delete_module_endpoint(
    module_id: UUID,
    archive_reason: str = Body("Manual deletion", embed=True),  # ADD THIS
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Archive a module (soft delete) with company hierarchy permission checks"""
    archived = await archive_module(db, module_id, admin_user.id, archive_reason)  # CHANGE THIS
    if not archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return {"success": True, "archived": True}  # UPDATE RESPONSE
@router.put("/modules/{module_id}/reorder", response_model=ModuleResponse)
async def reorder_module_scenarios_endpoint(
    module_id: UUID,
    scenario_ids: List[UUID] = Body(..., embed=True),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can reorder scenarios
):
    """
    Reorder scenarios in a module (admin/superadmin only, with ownership checks for admins)
    """
    updated_module = await reorder_module_scenarios(db, module_id, scenario_ids, admin_user.id)
    if not updated_module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return updated_module


@router.get("/modules/assignable", response_model=List[ModuleResponse])
async def get_assignable_modules_endpoint(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get modules that current admin can assign to users"""
    # This would use the new company hierarchy logic
    modules = await get_modules(db, 0, 1000, admin_user)  # Get all accessible modules
    return modules

@router.put("/modules/{module_id}/visibility", response_model=ModuleResponse)
async def update_module_visibility_endpoint(
    module_id: UUID,
    visibility_data: Dict[str, str] = Body(..., example={"visibility": "company_wide"}),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Update module visibility (creator_only vs company_wide)"""
    new_visibility = visibility_data.get("visibility")
    
    if new_visibility not in [ContentVisibility.CREATOR_ONLY, ContentVisibility.COMPANY_WIDE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visibility. Must be 'creator_only' or 'company_wide'"
        )
    
    module_updates = {"visibility": new_visibility}
    updated_module = await update_module(db, module_id, module_updates, admin_user.id)
    if not updated_module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return updated_module

# async def can_user_assign_module(db: Any, user: UserDB, module: ModuleDB) -> bool:
#     """
#     Check if user can ASSIGN a specific module based on:
#     1. Company hierarchy rules
#     2. Content visibility settings
#     3. User role permissions
#     """
#     # Users cannot assign modules
#     if user.role == UserRole.USER:
#         return False
    
#     # Boss admin can assign any module
#     if user.role == UserRole.BOSS_ADMIN:
#         return True
    
#     # Check if module is archived
#     if module.is_archived:
#         return False
    
#     # Check company hierarchy access
#     user_company_type = await get_company_hierarchy_type(db, user.company_id)
#     module_company_type = await get_company_hierarchy_type(db, module.company_id)
    
#     # Same company assignment
#     if user.company_id == module.company_id:
#         # Check visibility rules
#         if module.visibility == ContentVisibility.CREATOR_ONLY:
#             return module.created_by == user.id
#         elif module.visibility == ContentVisibility.COMPANY_WIDE:
#             return True  # Any admin/superadmin in same company can assign
    
#     # Cross-company assignment (MOTHER → CLIENT/SUBSIDIARY)
#     elif module_company_type == CompanyType.MOTHER:
#         # MOTHER company modules can be assigned by any admin/superadmin
#         # regardless of visibility setting
#         return True
    
#     # All other cases: no access
#     return False

# REPLACE this function:
async def can_user_assign_module(db: Any, user: UserDB, module: ModuleDB) -> bool:
    if user.role == UserRole.USER:
        return False
    if user.role == UserRole.BOSS_ADMIN:
        return True
    if module.is_archived:
        return False
    
    # CRITICAL FIX: Convert all UUIDs to strings
    user_company_str = str(user.company_id)
    module_company_str = str(module.company_id)
    user_id_str = str(user.id)
    created_by_str = str(module.created_by)
    
    if user_company_str == module_company_str:
        if module.visibility == ContentVisibility.CREATOR_ONLY:
            return user_id_str == created_by_str  # FIXED
        elif module.visibility == ContentVisibility.COMPANY_WIDE:
            return True
    
    module_company_type = await get_company_hierarchy_type(db, module.company_id)
    if module_company_type == CompanyType.MOTHER:
        return True
    
    return False