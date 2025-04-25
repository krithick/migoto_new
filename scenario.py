from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from models_new import (
    ScenarioCreate, ScenarioResponse, ScenarioDB,
    LearnModeCreate, TryModeCreate, AssessModeCreate,
     UserRole
)
from user_models import UserDB

# from main import get_db
from user import get_current_user, get_admin_user, get_superadmin_user
from module import get_module  # Import from module CRUD to check permissions

# Create router
router = APIRouter(tags=["Scenarios"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Scenario Any Operations
async def get_scenarios(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[ScenarioDB]:
    """
    Get a list of all scenarios with permission checks.
    - Admins/Superadmins: all scenarios
    - Regular users: only scenarios from modules in assigned courses
    """
    if not current_user:
        return []
    
    scenarios = []
    
    # For admins and superadmins, return all scenarios
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        cursor = db.scenarios.find().skip(skip).limit(limit)
        async for document in cursor:
            scenarios.append(ScenarioDB(**document))
    else:
        # For regular users, get only scenarios from modules in assigned courses
        user_data = current_user.dict()
        assigned_course_ids = user_data.get("assigned_courses", [])
        assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
        if assigned_course_ids_str:
            # Get all courses assigned to user
            courses = []
            for course_id in assigned_course_ids_str:
                course = await db.courses.find_one({"_id": str(course_id)})
                if course:
                    courses.append(course)
            
            # Extract module IDs from all assigned courses
            module_ids = []
            for course in courses:
                module_ids.extend(course.get("modules", []))
            
            # Get modules by these IDs
            print(module_ids,"module_ids")
            modules = []
            for module_id in module_ids:
                module = await db.modules.find_one({"_id": str(module_id)})
                if module:
                    modules.append(module)
            print(modules,"modules")
            
            # Extract scenario IDs from all modules
            scenario_ids = []
            for module in modules:
                scenario_ids.extend(module.get("scenarios", []))
            print(scenario_ids,"scenario_ids",type(scenario_ids[0]))
            # Get scenarios by these IDs - convert UUIDs to strings for MongoDB
            if scenario_ids:
                # Convert all UUIDs to strings
                scenario_ids_str = [str(s_id) for s_id in scenario_ids]
                cursor = db.scenarios.find({"_id": {"$in": scenario_ids_str}}).skip(skip).limit(limit)
                async for document in cursor:
                    scenarios.append(ScenarioDB(**document))
    
    return scenarios

async def get_scenario(
    db: Any, 
    scenario_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[ScenarioDB]:
    """
    Get a scenario by ID with permission checks:
    - Admins/Superadmins: can access all scenarios
    - Regular users: can only access scenarios from modules in assigned courses
    """
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    print(scenario)
    if not scenario:
        return None
    
    # If admin or superadmin, allow access
    if current_user and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return ScenarioDB(**scenario)
    
    # For regular users, check if scenario belongs to a module in an assigned course
    if current_user:
        # Find modules that contain this scenario - convert UUID to string for MongoDB
        modules_with_scenario = await db.modules.find({"scenarios": str(scenario_id)}).to_list(None)
        module_ids = [module["_id"] for module in modules_with_scenario]
        
        # Find courses that contain these modules
        if module_ids:
            user_data = current_user.dict()
            assigned_course_ids = user_data.get("assigned_courses", [])
            
            for course_id in assigned_course_ids:
                course = await db.courses.find_one({"_id": str(course_id)})
                if course and any(module_id in course.get("modules", []) for module_id in module_ids):
                    return ScenarioDB(**scenario)
    
    return None

async def get_scenarios_by_module(
    db: Any, 
    module_id: UUID, 
    current_user: Optional[UserDB] = None
) -> List[ScenarioDB]:
    """
    Get all scenarios belonging to a specific module, with permission checks
    """
    # First check if user can access the module
    module = await get_module(db, module_id, current_user)
    if not module:
        return []
    
    scenarios = []
    scenario_ids = module.dict().get("scenarios", [])
    
    for scenario_id in scenario_ids:
        # Convert UUID to string for MongoDB
        scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
        if scenario:
            scenarios.append(ScenarioDB(**scenario))
    
    return scenarios

async def get_full_scenario(
    db: Any, 
    scenario_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a scenario with all references expanded
    """
    # First check if user can access this scenario
    scenario = await get_scenario(db, scenario_id, current_user)
    if not scenario:
        return None
    
    # Get scenario with expanded references
    scenario_dict = scenario.dict()
    
    # Process learn mode if present
    if "learn_mode" in scenario_dict and scenario_dict["learn_mode"]:
        if "avatar_interaction" in scenario_dict["learn_mode"]:
            avatar_id = scenario_dict["learn_mode"]["avatar_interaction"]
            avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
            if avatar_interaction:
                scenario_dict["learn_mode"]["avatar_interaction"] = avatar_interaction
        
        # Expand videos - NOW IN LEARN MODE
        if "videos" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["videos"]:
            video_ids = scenario_dict["learn_mode"]["videos"]
            videos = []
            for video_id in video_ids:
                video = await db.videos.find_one({"_id": str(video_id)})
                if video:
                    videos.append(video)
            scenario_dict["learn_mode"]["videos"] = videos
        
        # Expand documents - NOW IN LEARN MODE
        if "documents" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["documents"]:
            doc_ids = scenario_dict["learn_mode"]["documents"]
            documents = []
            for doc_id in doc_ids:
                document = await db.documents.find_one({"_id": str(doc_id)})
                if document:
                    documents.append(document)
            scenario_dict["learn_mode"]["documents"] = documents
    
    # Process try mode if present
    if "try_mode" in scenario_dict and scenario_dict["try_mode"]:
        if "avatar_interaction" in scenario_dict["try_mode"]:
            avatar_id = scenario_dict["try_mode"]["avatar_interaction"]
            avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
            if avatar_interaction:
                scenario_dict["try_mode"]["avatar_interaction"] = avatar_interaction
        
        # No need to expand videos or documents in try_mode anymore
    
    # Process assess mode if present
    if "assess_mode" in scenario_dict and scenario_dict["assess_mode"]:
        if "avatar_interaction" in scenario_dict["assess_mode"]:
            avatar_id = scenario_dict["assess_mode"]["avatar_interaction"]
            avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
            if avatar_interaction:
                scenario_dict["assess_mode"]["avatar_interaction"] = avatar_interaction
    
    return scenario_dict

# async def create_scenario(
#     db: Any, 
#     module_id: UUID, 
#     scenario: ScenarioCreate, 
#     created_by: UUID
# ) -> ScenarioDB:
#     """
#     Create a new scenario within a module
#     """
#     # First check if module exists - convert UUID to string for MongoDB
#     module = await db.modules.find_one({"_id": str(module_id)})
#     if not module:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
#     # Check if creator has permission to modify the module - convert UUID to string for MongoDB
#     creator = await db.users.find_one({"_id": str(created_by)})
#     if not creator:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
#     creator = UserDB(**creator)
    
#     # If creator is admin (not superadmin), check if they created the module
#     if creator.role == UserRole.ADMIN and module.get("created_by") != created_by:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admins can only add scenarios to modules they created"
#         )
    
#     # Validate that at least one mode is provided
#     if not any([scenario.learn_mode, scenario.try_mode, scenario.assess_mode]):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="At least one mode (learn, try, or assess) must be provided"
#         )
    
#     # Create ScenarioDB model
#     scenario_dict = scenario.dict()
    
#     # Add creator and timestamps
#     scenario_db = ScenarioDB(
#         **scenario_dict,
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Process the scenario for database insertion
#     scenario_dict = scenario_db.dict(by_alias=True)
#     if scenario_dict.get("_id") is None:
#         scenario_dict.pop("_id", None)
#     else:
#         scenario_dict["_id"] = UUID(str(scenario_dict["_id"]))
    
#     # Process learn mode if present
#     if "learn_mode" in scenario_dict and scenario_dict["learn_mode"]:
#         if "avatar_interaction" in scenario_dict["learn_mode"]:
#             avatar_id = scenario_dict["learn_mode"]["avatar_interaction"]
#             scenario_dict["learn_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
        
#         # Convert video and document UUIDs - NOW IN LEARN MODE
#         if "videos" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["videos"]:
#             scenario_dict["learn_mode"]["videos"] = [UUID(str(video_id)) if not isinstance(video_id, UUID) else video_id 
#                                                 for video_id in scenario_dict["learn_mode"]["videos"]]
        
#         if "documents" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["documents"]:
#             scenario_dict["learn_mode"]["documents"] = [UUID(str(doc_id)) if not isinstance(doc_id, UUID) else doc_id 
#                                                     for doc_id in scenario_dict["learn_mode"]["documents"]]
    
#     # Process try mode if present
#     if "try_mode" in scenario_dict and scenario_dict["try_mode"]:
#         if "avatar_interaction" in scenario_dict["try_mode"]:
#             avatar_id = scenario_dict["try_mode"]["avatar_interaction"]
#             scenario_dict["try_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
        
#         # No need to convert video and document UUIDs in try_mode anymore
    
#     # Process assess mode if present
#     if "assess_mode" in scenario_dict and scenario_dict["assess_mode"]:
#         if "avatar_interaction" in scenario_dict["assess_mode"]:
#             avatar_id = scenario_dict["assess_mode"]["avatar_interaction"]
#             scenario_dict["assess_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
    
#     # Insert scenario into database
#     result = await db.scenarios.insert_one(scenario_dict)
    
#     # Update the module to include this scenario - convert UUIDs to strings for MongoDB
#     await db.modules.update_one(
#         {"_id": str(module_id)},
#         {"$push": {"scenarios": str(result.inserted_id)}}
#     )
    
#     created_scenario = await db.scenarios.find_one({"_id": result.inserted_id})
#     print(created_scenario,"created_scenario",ScenarioDB(**created_scenario))
#     return ScenarioDB(**created_scenario)
#     # return ScenarioDB(**created_scenario)

async def create_scenario(
    db: Any, 
    module_id: UUID, 
    scenario: ScenarioCreate, 
    created_by: UUID
) -> ScenarioDB:
    """
    Create a new scenario within a module
    """
    # First check if module exists - convert UUID to string for MongoDB
    module = await db.modules.find_one({"_id": str(module_id)})
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    
    # Check if creator has permission to modify the module - convert UUID to string for MongoDB
    creator = await db.users.find_one({"_id": str(created_by)})
    if not creator:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    creator = UserDB(**creator)
    
    # If creator is admin (not superadmin), check if they created the module
    if creator.role == UserRole.ADMIN and module.get("created_by") != str(created_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins can only add scenarios to modules they created"
        )
    
    # Validate that at least one mode is provided
    if not any([scenario.learn_mode, scenario.try_mode, scenario.assess_mode]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one mode (learn, try, or assess) must be provided"
        )
    
    # Create ScenarioDB model
    scenario_dict = scenario.dict()
    
    # Add creator and timestamps
    scenario_db = ScenarioDB(
        **scenario_dict,
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Process the scenario for database insertion
    scenario_dict = scenario_db.dict(by_alias=True)
    
    # Always use string for _id in MongoDB
    if "_id" in scenario_dict:
        scenario_dict["_id"] = str(scenario_dict["_id"])
    
    # Store created_by as string
    if "created_by" in scenario_dict:
        scenario_dict["created_by"] = str(scenario_dict["created_by"])
    
    # Process learn mode if present
    if "learn_mode" in scenario_dict and scenario_dict["learn_mode"]:
        if "avatar_interaction" in scenario_dict["learn_mode"]:
            scenario_dict["learn_mode"]["avatar_interaction"] = str(scenario_dict["learn_mode"]["avatar_interaction"])
        
        # Convert video and document UUIDs to strings
        if "videos" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["videos"]:
            scenario_dict["learn_mode"]["videos"] = [str(video_id) for video_id in scenario_dict["learn_mode"]["videos"]]
        
        if "documents" in scenario_dict["learn_mode"] and scenario_dict["learn_mode"]["documents"]:
            scenario_dict["learn_mode"]["documents"] = [str(doc_id) for doc_id in scenario_dict["learn_mode"]["documents"]]
    
    # Process try mode if present
    if "try_mode" in scenario_dict and scenario_dict["try_mode"]:
        if "avatar_interaction" in scenario_dict["try_mode"]:
            scenario_dict["try_mode"]["avatar_interaction"] = str(scenario_dict["try_mode"]["avatar_interaction"])
        
        # Convert any additional UUIDs in try_mode to strings if needed
        if "videos" in scenario_dict["try_mode"] and scenario_dict["try_mode"]["videos"]:
            scenario_dict["try_mode"]["videos"] = [str(video_id) for video_id in scenario_dict["try_mode"]["videos"]]
        
        if "documents" in scenario_dict["try_mode"] and scenario_dict["try_mode"]["documents"]:
            scenario_dict["try_mode"]["documents"] = [str(doc_id) for doc_id in scenario_dict["try_mode"]["documents"]]
    
    # Process assess mode if present
    if "assess_mode" in scenario_dict and scenario_dict["assess_mode"]:
        if "avatar_interaction" in scenario_dict["assess_mode"]:
            scenario_dict["assess_mode"]["avatar_interaction"] = str(scenario_dict["assess_mode"]["avatar_interaction"])
        
        # Convert any additional UUIDs in assess_mode to strings if needed
        if "videos" in scenario_dict["assess_mode"] and scenario_dict["assess_mode"]["videos"]:
            scenario_dict["assess_mode"]["videos"] = [str(video_id) for video_id in scenario_dict["assess_mode"]["videos"]]
        
        if "documents" in scenario_dict["assess_mode"] and scenario_dict["assess_mode"]["documents"]:
            scenario_dict["assess_mode"]["documents"] = [str(doc_id) for doc_id in scenario_dict["assess_mode"]["documents"]]
    
    # Insert scenario into database
    result = await db.scenarios.insert_one(scenario_dict)
    
    # Update the module to include this scenario - convert UUIDs to strings for MongoDB
    await db.modules.update_one(
        {"_id": str(module_id)},
        {"$push": {"scenarios": str(result.inserted_id)}}
    )
    
    # Retrieve the created scenario with string ID
    created_scenario = await db.scenarios.find_one({"_id": str(result.inserted_id)})
    return ScenarioDB(**created_scenario)

async def update_scenario(
    db: Any, 
    scenario_id: UUID, 
    scenario_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[ScenarioDB]:
    """
    Update a scenario with permission checks
    """
    # Get the scenario to update - convert UUID to string for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        return None
    
    # Get the user making the update - convert UUID to string for MongoDB
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions
    if updater.role == UserRole.ADMIN:
        # Admin can only update scenarios they created
        if scenario.get("created_by") != updated_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update scenarios they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update scenarios
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update scenarios"
        )
    
    # Add updated timestamp
    scenario_updates["updated_at"] = datetime.now()
    
    # Process learn mode if present
    if "learn_mode" in scenario_updates and scenario_updates["learn_mode"]:
        if "avatar_interaction" in scenario_updates["learn_mode"]:
            avatar_id = scenario_updates["learn_mode"]["avatar_interaction"]
            scenario_updates["learn_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
        
        # Convert video and document UUIDs - NOW IN LEARN MODE
        if "videos" in scenario_updates["learn_mode"] and scenario_updates["learn_mode"]["videos"]:
            scenario_updates["learn_mode"]["videos"] = [UUID(str(video_id)) if not isinstance(video_id, UUID) else video_id 
                                                   for video_id in scenario_updates["learn_mode"]["videos"]]
        
        if "documents" in scenario_updates["learn_mode"] and scenario_updates["learn_mode"]["documents"]:
            scenario_updates["learn_mode"]["documents"] = [UUID(str(doc_id)) if not isinstance(doc_id, UUID) else doc_id 
                                                       for doc_id in scenario_updates["learn_mode"]["documents"]]
    
    # Process try mode if present
    if "try_mode" in scenario_updates and scenario_updates["try_mode"]:
        if "avatar_interaction" in scenario_updates["try_mode"]:
            avatar_id = scenario_updates["try_mode"]["avatar_interaction"]
            scenario_updates["try_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
        
        # No need to convert video and document UUIDs in try_mode anymore
    
    # Process assess mode if present
    if "assess_mode" in scenario_updates and scenario_updates["assess_mode"]:
        if "avatar_interaction" in scenario_updates["assess_mode"]:
            avatar_id = scenario_updates["assess_mode"]["avatar_interaction"]
            scenario_updates["assess_mode"]["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
    
    # Update in database - convert UUID to string for MongoDB
    await db.scenarios.update_one(
        {"_id": str(scenario_id)},
        {"$set": scenario_updates}
    )
    
    updated_scenario = await db.scenarios.find_one({"_id": scenario_id})
    if updated_scenario:
        return ScenarioDB(**updated_scenario)
    return None

async def delete_scenario(db: Any, scenario_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a scenario with permission checks
    """
    # Get the scenario to delete - convert UUID to string for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        return False
    
    # Get the user making the deletion - convert UUID to string for MongoDB
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete scenarios they created
        if scenario.get("created_by") != deleted_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete scenarios they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete scenarios
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete scenarios"
        )
    
    # Remove scenario from any modules - convert UUID to string for MongoDB
    await db.modules.update_many(
        {"scenarios": str(scenario_id)},
        {"$pull": {"scenarios": str(scenario_id)}}
    )
    
    # Delete the scenario - convert UUID to string for MongoDB
    result = await db.scenarios.delete_one({"_id": str(scenario_id)})
    
    return result.deleted_count > 0

async def update_scenario_mode(
    db: Any, 
    scenario_id: UUID, 
    mode_type: str,
    mode_data: Union[LearnModeCreate, TryModeCreate, AssessModeCreate, None],
    updated_by: UUID
) -> Optional[ScenarioDB]:
    """
    Update a specific mode (learn, try, assess) of a scenario
    """
    # Validate mode type
    if mode_type not in ["learn_mode", "try_mode", "assess_mode"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode type. Must be 'learn_mode', 'try_mode', or 'assess_mode'"
        )
    
    # Get the scenario to update - convert UUID to string for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        return None
    
    # Get the user making the update - convert UUID to string for MongoDB
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions
    if updater.role == UserRole.ADMIN:
        # Admin can only update scenarios they created
        if scenario.get("created_by") != updated_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update scenarios they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update scenarios
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update scenarios"
        )
    
    # If mode_data is None, remove the mode
    if mode_data is None:
        # Check if there will be at least one mode left
        other_modes = [m for m in ["learn_mode", "try_mode", "assess_mode"] if m != mode_type]
        if not any(scenario.get(m) for m in other_modes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the only mode. At least one mode must remain"
            )
        
        # Update in database - remove the mode - convert UUID to string for MongoDB
        await db.scenarios.update_one(
            {"_id": str(scenario_id)},
            {
                "$unset": {mode_type: ""},
                "$set": {"updated_at": datetime.now()}
            }
        )
    else:
        # Process mode data based on type
        mode_dict = mode_data.dict()
        
        if mode_type in ["learn_mode", "try_mode", "assess_mode"]:
            if "avatar_interaction" in mode_dict:
                avatar_id = mode_dict["avatar_interaction"]
                mode_dict["avatar_interaction"] = UUID(str(avatar_id)) if not isinstance(avatar_id, UUID) else avatar_id
        
        # Additional processing for learn mode - CHANGED FROM TRY MODE TO LEARN MODE
        if mode_type == "learn_mode":
            # Convert video and document UUIDs
            if "videos" in mode_dict and mode_dict["videos"]:
                mode_dict["videos"] = [UUID(str(video_id)) if not isinstance(video_id, UUID) else video_id 
                                     for video_id in mode_dict["videos"]]
            
            if "documents" in mode_dict and mode_dict["documents"]:
                mode_dict["documents"] = [UUID(str(doc_id)) if not isinstance(doc_id, UUID) else doc_id 
                                        for doc_id in mode_dict["documents"]]
        
        # Update in database - set the mode - convert UUID to string for MongoDB
        await db.scenarios.update_one(
            {"_id": str(scenario_id)},
            {
                "$set": {
                    mode_type: mode_dict,
                    "updated_at": datetime.now()
                }
            }
        )
    
    updated_scenario = await db.scenarios.find_one({"_id": scenario_id})
    if updated_scenario:
        return ScenarioDB(**updated_scenario)
    return None

# Scenario API Endpoints
@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all scenarios (filtered by user role)
    """
    return await get_scenarios(db, skip, limit, current_user)

@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_endpoint(
    scenario_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific scenario by ID (with permission checks)
    """
    scenario = await get_scenario(db, scenario_id, current_user)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Scenario not found or access denied")
    return scenario

@router.get("/modules/{module_id}/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios_by_module_endpoint(
    module_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all scenarios belonging to a specific module
    """
    scenarios = await get_scenarios_by_module(db, module_id, current_user)
    return scenarios

@router.get("/scenarios/{scenario_id}/full", response_model=Dict[str, Any])
async def get_full_scenario_endpoint(
    scenario_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a scenario with all references expanded
    """
    scenario = await get_full_scenario(db, scenario_id, current_user)
    print(scenario)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Scenario not found or access denied")
    return scenario

@router.post("/modules/{module_id}/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario_endpoint(
    module_id: UUID,
    scenario: ScenarioCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create scenarios
):
    """
    Create a new scenario in a module (admin/superadmin only)
    """
    return await create_scenario(db, module_id, scenario, admin_user.id)

@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario_endpoint(
    scenario_id: UUID,
    scenario_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update scenarios
):
    """
    Update a scenario by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_scenario = await update_scenario(db, scenario_id, scenario_updates, admin_user.id)
    if not updated_scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return updated_scenario

@router.delete("/scenarios/{scenario_id}", response_model=Dict[str, bool])
async def delete_scenario_endpoint(
    scenario_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete scenarios
):
    """
    Delete a scenario by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_scenario(db, scenario_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return {"success": True}

@router.put("/scenarios/{scenario_id}/{mode_type}", response_model=ScenarioResponse)
async def update_scenario_mode_endpoint(
    scenario_id: UUID,
    mode_type: str = Path(..., description="Mode type: learn_mode, try_mode, or assess_mode"),
    mode_data: Optional[Union[LearnModeCreate, TryModeCreate, AssessModeCreate]] = Body(None),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update scenario modes
):
    """
    Update or remove a specific mode of a scenario (admin/superadmin only, with ownership checks for admins)
    """
    updated_scenario = await update_scenario_mode(db, scenario_id, mode_type, mode_data, admin_user.id)
    if not updated_scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return updated_scenario