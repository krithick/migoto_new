from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime


from models.scenario_models import (
    ScenarioCreate, ScenarioResponse, ScenarioDB,
    LearnModeCreate, TryModeCreate, AssessModeCreate,
     
)
from models.user_models import UserDB ,UserRole

# from main import get_db
from core.user import get_current_user, get_admin_user, get_superadmin_user
from core.module import get_module  # Import from module CRUD to check permissions
from core.scenario_assignment import get_scenario_assignment

from models.company_models import CompanyType, CompanyDB
from models.scenario_models import ContentVisibility, ScenarioUpdate  # Add these to your imports
from core.tier_utils import (
    enforce_content_creation_limit,
    enforce_chat_session_limit, 
    enforce_analysis_limit,
    check_feature_permission,
    enforce_feature_access
)

# Create router
router = APIRouter(tags=["Scenarios"])

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

# async def can_user_assign_scenario(db: Any, user: UserDB, scenario: ScenarioDB) -> bool:
#     """Check if user can ASSIGN a specific scenario based on company hierarchy"""
#     if user.role == UserRole.USER:
#         return False
#     if user.role == UserRole.BOSS_ADMIN:
#         return True
#     if scenario.is_archived:
#         return False
    
#     # Check company hierarchy access
#     scenario_company_type = await get_company_hierarchy_type(db, scenario.company_id)
    
#     # Same company assignment
#     if user.company_id == scenario.company_id:
#         if scenario.visibility == ContentVisibility.CREATOR_ONLY:
#             return scenario.created_by == user.id
#         elif scenario.visibility == ContentVisibility.COMPANY_WIDE:
#             return True
    
#     # Cross-company assignment (MOTHER → CLIENT/SUBSIDIARY)
#     elif scenario_company_type == CompanyType.MOTHER:
#         return True
    
#     return False
async def can_user_assign_scenario(db: Any, user: UserDB, scenario: ScenarioDB) -> bool:
    if user.role == UserRole.USER:
        return False
    if user.role == UserRole.BOSS_ADMIN:
        return True
    if scenario.is_archived:
        return False
    
    # CRITICAL FIX: Convert all UUIDs to strings
    user_company_str = str(user.company_id)
    scenario_company_str = str(scenario.company_id)
    user_id_str = str(user.id)
    created_by_str = str(scenario.created_by)
    
    if user_company_str == scenario_company_str:
        if scenario.visibility == ContentVisibility.CREATOR_ONLY:
            return user_id_str == created_by_str  # FIXED
        elif scenario.visibility == ContentVisibility.COMPANY_WIDE:
            return True
    
    scenario_company_type = await get_company_hierarchy_type(db, scenario.company_id)
    if scenario_company_type == CompanyType.MOTHER:
        return True
    
    return False

async def get_assignable_scenarios_for_user(db: Any, user: UserDB) -> List[ScenarioDB]:
    """Get scenarios that user can ASSIGN to others"""
    if user.role == UserRole.USER:
        return []
    
    # Get all scenarios user can access
    scenarios = []
    
    if user.role == UserRole.BOSS_ADMIN:
        cursor = db.scenarios.find({"is_archived": False})
        async for document in cursor:
            scenarios.append(ScenarioDB(**document))
    else:
        user_company_type = await get_company_hierarchy_type(db, user.company_id)
        
        if user_company_type == CompanyType.MOTHER:
            cursor = db.scenarios.find({"is_archived": False})
            async for document in cursor:
                scenarios.append(ScenarioDB(**document))
        else:
            # Get MOTHER companies
            mother_companies = []
            mother_cursor = db.companies.find({"company_type": CompanyType.MOTHER})
            async for company_doc in mother_cursor:
                mother_companies.append(company_doc["_id"])
            
            accessible_companies = [str(user.company_id)] + mother_companies
            cursor = db.scenarios.find({
                "company_id": {"$in": accessible_companies},
                "is_archived": False
            })
            async for document in cursor:
                scenarios.append(ScenarioDB(**document))
    
    # Filter to only assignable ones
    assignable_scenarios = []
    for scenario in scenarios:
        if await can_user_assign_scenario(db, user, scenario):
            assignable_scenarios.append(scenario)
    
    return assignable_scenarios

# Scenario Any Operations
# async def get_scenarios(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[ScenarioDB]:
#     """
#     Get a list of all scenarios with permission checks.
#     - Admins/Superadmins: all scenarios
#     - Regular users: only scenarios from modules in assigned courses
#     """
#     if not current_user:
#         return []
    
#     scenarios = []
    
#     # For admins and superadmins, return all scenarios
#     if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
#         cursor = db.scenarios.find().skip(skip).limit(limit)
#         async for document in cursor:
#             scenarios.append(ScenarioDB(**document))
#     else:
#         # For regular users, get only scenarios from modules in assigned courses
#         user_data = current_user.dict()
#         assigned_course_ids = user_data.get("assigned_courses", [])
#         assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
#         if assigned_course_ids_str:
#             # Get all courses assigned to user
#             courses = []
#             for course_id in assigned_course_ids_str:
#                 course = await db.courses.find_one({"_id": str(course_id)})
#                 if course:
#                     courses.append(course)
            
#             # Extract module IDs from all assigned courses
#             module_ids = []
#             for course in courses:
#                 module_ids.extend(course.get("modules", []))
            
#             # Get modules by these IDs
#             print(module_ids,"module_ids")
#             modules = []
#             for module_id in module_ids:
#                 module = await db.modules.find_one({"_id": str(module_id)})
#                 if module:
#                     modules.append(module)
#             print(modules,"modules")
            
#             # Extract scenario IDs from all modules
#             scenario_ids = []
#             for module in modules:
#                 scenario_ids.extend(module.get("scenarios", []))
#             print(scenario_ids,"scenario_ids",type(scenario_ids[0]))
#             # Get scenarios by these IDs - convert UUIDs to strings for MongoDB
#             if scenario_ids:
#                 # Convert all UUIDs to strings
#                 scenario_ids_str = [str(s_id) for s_id in scenario_ids]
#                 cursor = db.scenarios.find({"_id": {"$in": scenario_ids_str}}).skip(skip).limit(limit)
#                 async for document in cursor:
#                     scenarios.append(ScenarioDB(**document))
    
#     return scenarios

# 
async def get_scenarios(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[ScenarioDB]:
    """Get scenarios based on user's company hierarchy access"""
    if not current_user:
        return []
    
    scenarios = []
    
    if current_user.role == UserRole.USER:
        # Users only see assigned scenarios
        assignments_cursor = db.user_scenario_assignments.find({
            "user_id": str(current_user.id),
            "is_archived": False
        })
        
        assigned_scenario_ids = []
        async for assignment in assignments_cursor:
            assigned_scenario_ids.append(assignment["scenario_id"])
        
        if assigned_scenario_ids:
            cursor = db.scenarios.find({
                "_id": {"$in": assigned_scenario_ids},
                "is_archived": False
            }).skip(skip).limit(limit)
            async for document in cursor:
                scenarios.append(ScenarioDB(**document))
    
    elif current_user.role == UserRole.BOSS_ADMIN:
        cursor = db.scenarios.find({"is_archived": False}).skip(skip).limit(limit)
        async for document in cursor:
            scenarios.append(ScenarioDB(**document))
    
    else:  # ADMIN or SUPERADMIN
        user_company_type = await get_company_hierarchy_type(db, current_user.company_id)
        
        if user_company_type == CompanyType.MOTHER:
            cursor = db.scenarios.find({"is_archived": False}).skip(skip).limit(limit)
            async for document in cursor:
                scenarios.append(ScenarioDB(**document))
        else:
            # Get MOTHER companies
            mother_companies = []
            mother_cursor = db.companies.find({"company_type": CompanyType.MOTHER})
            async for company_doc in mother_cursor:
                mother_companies.append(company_doc["_id"])
            
            accessible_companies = [str(current_user.company_id)] + mother_companies
            
            cursor = db.scenarios.find({
                "company_id": {"$in": accessible_companies},
                "is_archived": False
            }).skip(skip).limit(limit)
            async for document in cursor:
                scenarios.append(ScenarioDB(**document))
    
    return scenarios
# 
# async def get_scenario(
#     db: Any, 
#     scenario_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[ScenarioDB]:
#     """
#     Get a scenario by ID with permission checks:
#     - Admins/Superadmins: can access all scenarios
#     - Regular users: can only access scenarios from modules in assigned courses
#     """
#     scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
#     print(scenario)
#     if not scenario:
#         return None
# async def get_scenario(
#     db: Any, 
#     scenario_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[ScenarioDB]:
#     """Get a scenario by ID with permission checks"""
#     scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
#     if not scenario:
#         return None
    
#     # ADD THIS: Check if archived
#     if scenario.get("is_archived", False):
#         if not current_user or current_user.role != UserRole.BOSS_ADMIN:
#             return None    
#     # If admin or superadmin, allow access
#     if current_user and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
#         return ScenarioDB(**scenario)
    
#     # For regular users, check if scenario is assigned
#     if current_user and current_user.role == UserRole.USER:
#         # Check if scenario is assigned to user
#         assignment = await db.user_scenario_assignments.find_one({
#             "user_id": str(current_user.id),
#             "scenario_id": str(scenario_id)
#         })
        
#         if assignment:
#             scenario_obj = ScenarioDB(**scenario)
#             scenario_obj_dict = scenario_obj.model_dump()
            
#             # Add assignment data
#             scenario_obj_dict["assigned_modes"] = assignment.get("assigned_modes", [])
#             scenario_obj_dict["completed"] = assignment.get("completed", False)
#             scenario_obj_dict["completed_date"] = assignment.get("completed_date")
#             scenario_obj_dict["assigned_date"] = assignment.get("assigned_date")
#             print(scenario_obj_dict)
#             return scenario_obj_dict
    
#     return None


async def get_scenario(
    db: Any, 
    scenario_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[ScenarioDB]:
    """Get a scenario by ID with permission checks"""
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        return None
    
    # ADD THIS: Check if archived
    if scenario.get("is_archived", False):
        if not current_user or current_user.role != UserRole.BOSS_ADMIN:
            return None    
    # If admin or superadmin, allow access
    if current_user and current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        scenario_obj = ScenarioDB(**scenario)
        scenario_dict = scenario_obj.model_dump()
        
        # Add expanded creator info
        creator = await db.users.find_one({"_id": scenario.get("created_by")})
        if creator:
            scenario_dict["created_by_info"] = {
                "id": str(creator["_id"]),
                "username": creator.get("username", "Unknown"),
                "role": creator.get("role", "USER"),
                "company_id": str(creator.get("company_id", ""))
            }
        
        return scenario_dict
    
    # For regular users, check if scenario is assigned
    if current_user and current_user.role == UserRole.USER:
        # Check if scenario is assigned to user
        assignment = await db.user_scenario_assignments.find_one({
            "user_id": str(current_user.id),
            "scenario_id": str(scenario_id)
        })
        
        if assignment:
            scenario_obj = ScenarioDB(**scenario)
            scenario_obj_dict = scenario_obj.model_dump()
            
            # Add assignment data
            scenario_obj_dict["assigned_modes"] = assignment.get("assigned_modes", [])
            scenario_obj_dict["completed"] = assignment.get("completed", False)
            scenario_obj_dict["completed_date"] = assignment.get("completed_date")
            scenario_obj_dict["assigned_date"] = assignment.get("assigned_date")
            
            # Add expanded creator info
            creator = await db.users.find_one({"_id": scenario.get("created_by")})
            if creator:
                scenario_obj_dict["created_by_info"] = {
                    "id": str(creator["_id"]),
                    "username": creator.get("username", "Unknown"),
                    "role": creator.get("role", "USER"),
                    "company_id": str(creator.get("company_id", ""))
                }
            
            return scenario_obj_dict
    
    return None

# async def get_scenarios_by_module(
#     db: Any, 
#     module_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> List[ScenarioDB]:
#     """
#     Get all scenarios belonging to a specific module, with permission checks
#     """
#     # First check if user can access this module
#     module = await get_module(db, module_id, current_user)
#     if not module:
#         return []
    
#     scenarios = []
#     scenario_ids = module.dict().get("scenarios", [])
    
#     # Convert scenario_ids to strings for MongoDB
#     scenario_ids_str = [str(scenario_id) for scenario_id in scenario_ids]
    
#     # If user is regular user, filter scenarios by assignment
#     if current_user and current_user.role == UserRole.USER:
#         # Check if module is assigned to user
#         module_assigned = await db.user_module_assignments.find_one({
#             "user_id": str(current_user.id),
#             "module_id": str(module_id)
#         })
        
#         if not module_assigned:
#             return []  # Not assigned to this module
        
#         # Get assigned scenarios for this module
#         assignments_cursor = db.user_scenario_assignments.find({
#             "user_id": str(current_user.id),
#             "module_id": str(module_id)
#         })
        
#         # Get assigned scenario IDs and data
#         assigned_scenario_ids = []
#         assigned_scenario_data = {}
        
#         async for assignment in assignments_cursor:
#             scenario_id = assignment["scenario_id"]
#             assigned_scenario_ids.append(scenario_id)
#             assigned_scenario_data[scenario_id] = {
#                 "assigned_modes": assignment.get("assigned_modes", []),
#                 "completed": assignment.get("completed", False),
#                 "completed_date": assignment.get("completed_date"),
#                 "assigned_date": assignment.get("assigned_date")
#             }
        
#         # Filter scenario_ids to only show assigned ones
#         scenario_ids_str = [s_id for s_id in scenario_ids_str if s_id in assigned_scenario_ids]
        
#         # Fetch scenarios with assignment data
#         for scenario_id in scenario_ids_str:
#             scenario = await db.scenarios.find_one({"_id": scenario_id})
#             if scenario:
#                 scenario_obj = ScenarioDB(**scenario)
#                 scenario_obj_dict= scenario_obj.model_dump()
#                 # Add assignment data
#                 if scenario_id in assigned_scenario_data:
#                     data = assigned_scenario_data[scenario_id]
#                     scenario_obj_dict["assigned_modes"] = data["assigned_modes"]
#                     scenario_obj_dict["completed"] = data["completed"]
#                     scenario_obj_dict["completed_date"] = data["completed_date"]
#                     scenario_obj_dict["assigned_date"] = data["assigned_date"]
                
#                 scenarios.append(scenario_obj_dict)
#     else:
#         # For admins/superadmins, show all scenarios
#         for scenario_id in scenario_ids_str:
#             scenario = await db.scenarios.find_one({"_id": scenario_id})
#             if scenario:
#                 scenario_dict = ScenarioDB(**scenario)
#                 scenarios.append(scenario_dict.model_dump())
                
    
#     return scenarios

async def get_scenarios_by_module(
    db: Any, 
    module_id: UUID, 
    current_user: Optional[UserDB] = None
) -> List[ScenarioDB]:
    """
    Get all scenarios belonging to a specific module, with permission checks
    """
    # First check if user can access this module
    module = await get_module(db, module_id, current_user)
    if not module:
        return []
    
    scenarios = []
    scenario_ids = module.dict().get("scenarios", [])
    
    # Convert scenario_ids to strings for MongoDB
    scenario_ids_str = [str(scenario_id) for scenario_id in scenario_ids]
    
    # If user is regular user, filter scenarios by assignment
    if current_user and current_user.role == UserRole.USER:
        # Check if module is assigned to user
        module_assigned = await db.user_module_assignments.find_one({
            "user_id": str(current_user.id),
            "module_id": str(module_id)
        })
        
        if not module_assigned:
            return []  # Not assigned to this module
        
        # Get assigned scenarios for this module
        assignments_cursor = db.user_scenario_assignments.find({
            "user_id": str(current_user.id),
            "module_id": str(module_id)
        })
        
        # Get assigned scenario IDs and data
        assigned_scenario_ids = []
        assigned_scenario_data = {}
        
        async for assignment in assignments_cursor:
            scenario_id = assignment["scenario_id"]
            assigned_scenario_ids.append(scenario_id)
            assigned_scenario_data[scenario_id] = {
                "assigned_modes": assignment.get("assigned_modes", []),
                "completed": assignment.get("completed", False),
                "completed_date": assignment.get("completed_date"),
                "assigned_date": assignment.get("assigned_date")
            }
        
        # Filter scenario_ids to only show assigned ones
        scenario_ids_str = [s_id for s_id in scenario_ids_str if s_id in assigned_scenario_ids]
        
        # Fetch scenarios with assignment data
        for scenario_id in scenario_ids_str:
            scenario = await db.scenarios.find_one({"_id": scenario_id})
            if scenario:
                scenario_obj = ScenarioDB(**scenario)
                scenario_obj_dict= scenario_obj.model_dump()
                # Add assignment data
                if scenario_id in assigned_scenario_data:
                    data = assigned_scenario_data[scenario_id]
                    scenario_obj_dict["assigned_modes"] = data["assigned_modes"]
                    scenario_obj_dict["completed"] = data["completed"]
                    scenario_obj_dict["completed_date"] = data["completed_date"]
                    scenario_obj_dict["assigned_date"] = data["assigned_date"]
                
                # Add expanded creator info
                creator = await db.users.find_one({"_id": scenario.get("created_by")})
                if creator:
                    scenario_obj_dict["created_by_info"] = {
                        "id": str(creator["_id"]),
                        "username": creator.get("username", "Unknown"),
                        "role": creator.get("role", "USER"),
                        "company_id": str(creator.get("company_id", ""))
                    }
                
                scenarios.append(scenario_obj_dict)
    else:
        # For admins/superadmins, show all scenarios
        for scenario_id in scenario_ids_str:
            scenario = await db.scenarios.find_one({"_id": scenario_id})
            if scenario:
                scenario_obj = ScenarioDB(**scenario)
                scenario_dict = scenario_obj.model_dump()
                
                # Add expanded creator info
                creator = await db.users.find_one({"_id": scenario.get("created_by")})
                if creator:
                    scenario_dict["created_by_info"] = {
                        "id": str(creator["_id"]),
                        "username": creator.get("username", "Unknown"),
                        "role": creator.get("role", "USER"),
                        "company_id": str(creator.get("company_id", ""))
                    }
                
                scenarios.append(scenario_dict)
                
    
    return scenarios

# Modify the get_full_scenario function to respect mode assignments
# async def get_full_scenario(
#     db: Any, 
#     scenario_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[Dict[str, Any]]:
#     """
#     Get a scenario with all references expanded
#     """
#     # First check if user can access this scenario
#     scenario = await get_scenario(db, scenario_id, current_user)
#     if not scenario:
#         return None
    
#     # Get scenario with expanded references
#     scenario_dict = scenario.dict()
    
#     # If user is regular user, check scenario assignment to determine which modes to show
#     assignment = None
#     if current_user and current_user.role == UserRole.USER:
#         assignment = await get_scenario_assignment(db, current_user.id, scenario_id)
    
#     # Process learn mode if present and (admin user or mode is assigned to regular user)
#     if "learn_mode" in scenario_dict and scenario_dict["learn_mode"]:
#         # For regular user, check if mode is assigned
#         if current_user.role == UserRole.USER and assignment:
#             assigned_modes = assignment.assigned_modes
#             # If learn_mode is not assigned, remove it
#             if "learn_mode" not in [mode.value for mode in assigned_modes]:
#                 scenario_dict.pop("learn_mode", None)
#             else:
#                 # Add progress information
#                 mode_progress = assignment.mode_progress ["learn_mode"]
#                 if "learn_mode" in scenario_dict:
#                     scenario_dict["learn_mode"]["completed"] = mode_progress.completed
#                     scenario_dict["learn_mode"]["completed_date"] = mode_progress.completed_date
        
#         # If learn_mode is still present, expand its references
#         if "learn_mode" in scenario_dict:
#             if "avatar_interaction" in scenario_dict["learn_mode"]:
#                 avatar_id = scenario_dict["learn_mode"]["avatar_interaction"]
#                 avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
#                 if avatar_interaction:
#                     scenario_dict["learn_mode"]["avatar_interaction"] = avatar_interaction
    
#     # Process try mode if present
#     if "try_mode" in scenario_dict and scenario_dict["try_mode"]:
#         # For regular user, check if mode is assigned
#         if current_user.role == UserRole.USER and assignment:
#             assigned_modes = assignment.assigned_modes
#             # If try_mode is not assigned, remove it
#             if "try_mode" not in [mode.value for mode in assigned_modes]:
#                 scenario_dict.pop("try_mode", None)
#             else:
#                 # Add progress information
#                 mode_progress = assignment.mode_progress["try_mode"]
#                 if "try_mode" in scenario_dict:
#                     scenario_dict["try_mode"]["completed"] = mode_progress.completed
#                     scenario_dict["try_mode"]["completed_date"] = mode_progress.completed_date
        
#         # If try_mode is still present, expand its references
#         if "try_mode" in scenario_dict:
#             if "avatar_interaction" in scenario_dict["try_mode"]:
#                 avatar_id = scenario_dict["try_mode"]["avatar_interaction"]
#                 avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
#                 if avatar_interaction:
#                     scenario_dict["try_mode"]["avatar_interaction"] = avatar_interaction
    
#     # Process assess mode if present
#     if "assess_mode" in scenario_dict and scenario_dict["assess_mode"]:
#         # For regular user, check if mode is assigned
#         if current_user.role == UserRole.USER and assignment:
#             assigned_modes = assignment.assigned_modes
#             # If assess_mode is not assigned, remove it
#             if "assess_mode" not in [mode.value for mode in assigned_modes]:
#                 scenario_dict.pop("assess_mode", None)
#             else:
#                 # Add progress information
#                 mode_progress = assignment.mode_progress["assess_mode"]
#                 if "assess_mode" in scenario_dict:
#                     scenario_dict["assess_mode"]["completed"] = mode_progress.completed
#                     scenario_dict["assess_mode"]["completed_date"] = mode_progress.completed_date
        
#         # If assess_mode is still present, expand its references
#         if "assess_mode" in scenario_dict:
#             if "avatar_interaction" in scenario_dict["assess_mode"]:
#                 avatar_id = scenario_dict["assess_mode"]["avatar_interaction"]
#                 avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
#                 if avatar_interaction:
#                     scenario_dict["assess_mode"]["avatar_interaction"] = avatar_interaction
    
#     # Add assignment data to the scenario
#     if current_user and current_user.role == UserRole.USER and assignment:
#         scenario_dict["assigned"] = True
#         scenario_dict["assigned_modes"] = [mode.value for mode in assignment.assigned_modes]
#         scenario_dict["completed"] = assignment.completed
#         scenario_dict["completed_date"] = assignment.completed_date
    
#     return scenario_dict
async def get_full_scenario(
    db: Any, 
    scenario_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a scenario with all references expanded and respect assigned modes
    """
    # First check if user can access this scenario
    scenario = await get_scenario(db, scenario_id, current_user)
    if not scenario:
        return None
    
    # Get scenario with expanded references
    scenario_dict = scenario.dict()
    
    # Get assignment data for regular users
    assigned_modes = []
    mode_progress = {}
    
    if current_user and current_user.role == UserRole.USER:
        # Get assignment for this scenario
        assignment = await db.user_scenario_assignments.find_one({
            "user_id": str(current_user.id),
            "scenario_id": str(scenario_id)
        })
        
        if assignment:
            assigned_modes = assignment.get("assigned_modes", [])
            mode_progress = assignment.get("mode_progress", {})
            
            # Add assignment data to scenario
            scenario_dict["assigned"] = True
            scenario_dict["assigned_modes"] = assigned_modes
            scenario_dict["completed"] = assignment.get("completed", False)
            scenario_dict["completed_date"] = assignment.get("completed_date")
    
    # If user is regular user, filter modes based on assignments
    # For admins, show all modes
    filter_modes = current_user and current_user.role == UserRole.USER
    
    # Process learn mode if present
    if "learn_mode" in scenario_dict and scenario_dict["learn_mode"]:
        # For regular users, check if mode is assigned
        if filter_modes and "learn_mode" not in assigned_modes:
            # Remove this mode
            scenario_dict.pop("learn_mode", None)
        else:
            # Add mode progress if available
            if "learn_mode" in mode_progress:
                if "learn_mode" not in scenario_dict:
                    scenario_dict["learn_mode"] = {}
                scenario_dict["learn_mode"]["completed"] = mode_progress["learn_mode"].get("completed", False)
                scenario_dict["learn_mode"]["completed_date"] = mode_progress["learn_mode"].get("completed_date")
            
            # Expand avatar interaction reference
            if "learn_mode" in scenario_dict and "avatar_interaction" in scenario_dict["learn_mode"]:
                avatar_id = scenario_dict["learn_mode"]["avatar_interaction"]
                avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
                if avatar_interaction:
                    scenario_dict["learn_mode"]["avatar_interaction"] = avatar_interaction
    
    # Process try mode if present
    if "try_mode" in scenario_dict and scenario_dict["try_mode"]:
        # For regular users, check if mode is assigned
        if filter_modes and "try_mode" not in assigned_modes:
            # Remove this mode
            scenario_dict.pop("try_mode", None)
        else:
            # Add mode progress if available
            if "try_mode" in mode_progress:
                if "try_mode" not in scenario_dict:
                    scenario_dict["try_mode"] = {}
                scenario_dict["try_mode"]["completed"] = mode_progress["try_mode"].get("completed", False)
                scenario_dict["try_mode"]["completed_date"] = mode_progress["try_mode"].get("completed_date")
            
            # Expand avatar interaction reference
            if "try_mode" in scenario_dict and "avatar_interaction" in scenario_dict["try_mode"]:
                avatar_id = scenario_dict["try_mode"]["avatar_interaction"]
                avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
                if avatar_interaction:
                    scenario_dict["try_mode"]["avatar_interaction"] = avatar_interaction
    
    # Process assess mode if present
    if "assess_mode" in scenario_dict and scenario_dict["assess_mode"]:
        # For regular users, check if mode is assigned
        if filter_modes and "assess_mode" not in assigned_modes:
            # Remove this mode
            scenario_dict.pop("assess_mode", None)
        else:
            # Add mode progress if available
            if "assess_mode" in mode_progress:
                if "assess_mode" not in scenario_dict:
                    scenario_dict["assess_mode"] = {}
                scenario_dict["assess_mode"]["completed"] = mode_progress["assess_mode"].get("completed", False)
                scenario_dict["assess_mode"]["completed_date"] = mode_progress["assess_mode"].get("completed_date")
            
            # Expand avatar interaction reference
            if "assess_mode" in scenario_dict and "avatar_interaction" in scenario_dict["assess_mode"]:
                avatar_id = scenario_dict["assess_mode"]["avatar_interaction"]
                avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_id)})
                if avatar_interaction:
                    scenario_dict["assess_mode"]["avatar_interaction"] = avatar_interaction
    
    print(scenario_dict)
    return scenario_dict

async def create_scenario(
    db: Any, 
    module_id: UUID, 
    scenario: ScenarioCreate, 
    created_by: UUID,
    template_id: Optional[str] = None 
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
    # ADD THIS: Get creator's company
    try:
        creator_company_id = UUID(str(creator.company_id))
    except (ValueError, TypeError):
        creator_company_id = creator.company_id
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
    # scenario_db = ScenarioDB(
    #     **scenario_dict,
    #     created_by=created_by,
    #     created_at=datetime.now(),
    #     updated_at=datetime.now()
    # )
    template_data = None
    knowledge_base_id = None
    if template_id:
        template = await db.templates.find_one({"id": template_id})
        if template:
            template_data = template.get("template_data")
            knowledge_base_id = template.get("knowledge_base_id")
    
    scenario_db = ScenarioDB(
        **scenario_dict,
        created_by=created_by,
        company_id=creator_company_id,  # ADD THIS
        visibility=ContentVisibility.CREATOR_ONLY,  # ADD THIS
        knowledge_base_id=knowledge_base_id,
        template_data=template_data,
        fact_checking_enabled=knowledge_base_id is not None,        
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
        if scenario.get("created_by") != str(updated_by):
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
    
    updated_scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
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
async def archive_scenario(db: Any, scenario_id: UUID, archived_by: UUID, reason: str = "Manual archive") -> bool:
    """Archive a scenario (soft delete) instead of hard deletion"""
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        return False
    
    # Check permissions (same as your delete_scenario logic)
    deleter = await db.users.find_one({"_id": str(archived_by)})
    if not deleter:
        return False
    
    deleter = UserDB(**deleter)
    
    if deleter.role == UserRole.ADMIN:
        if scenario.get("created_by") != str(archived_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only archive scenarios they created"
            )
    elif deleter.role != UserRole.SUPERADMIN and deleter.role != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive scenarios"
        )
    
    # Archive the scenario
    await db.scenarios.update_one(
        {"_id": str(scenario_id)},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": reason,
            "updated_at": datetime.now()
        }}
    )
    
    # Archive all assignments for this scenario
    await db.user_scenario_assignments.update_many(
        {"scenario_id": str(scenario_id), "is_archived": False},
        {"$set": {
            "is_archived": True,
            "archived_at": datetime.now(),
            "archived_by": str(archived_by),
            "archived_reason": f"Scenario archived: {reason}"
        }}
    )
    
    return True
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

@router.get("/scenarios/{scenario_id}", response_model=Dict[str, Any])
# @router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)response_model=Dict[str, Any]
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

@router.get("/modules/{module_id}/scenarios", response_model=List[Dict[str, Any]])
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
    await enforce_content_creation_limit(db, admin_user.company_id, "scenario", module_id=module_id)
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

# @router.delete("/scenarios/{scenario_id}", response_model=Dict[str, bool])
# async def delete_scenario_endpoint(
#     scenario_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete scenarios
# ):
#     """
#     Delete a scenario by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_scenario(db, scenario_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
#     return {"success": True}
@router.delete("/scenarios/{scenario_id}", response_model=Dict[str, bool])
async def delete_scenario_endpoint(
    scenario_id: UUID,
    archive_reason: str = Body("Manual deletion", embed=True),  # ADD THIS
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Archive a scenario by ID (admin/superadmin only, with ownership checks for admins)"""
    archived = await archive_scenario(db, scenario_id, admin_user.id, archive_reason)  # CHANGE THIS
    if not archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return {"success": True, "archived": True}  # CHANGE THIS
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


@router.get("/assignable", response_model=List[ScenarioResponse])
async def get_assignable_scenarios_endpoint(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get scenarios that current admin can assign to users"""
    return await get_assignable_scenarios_for_user(db, admin_user)

@router.put("/scenarios/{scenario_id}/visibility", response_model=ScenarioResponse)
async def update_scenario_visibility_endpoint(
    scenario_id: UUID,
    visibility_data: Dict[str, str] = Body(..., example={"visibility": "company_wide"}),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Update scenario visibility (creator_only vs company_wide)"""
    new_visibility = visibility_data.get("visibility")
    
    if new_visibility not in [ContentVisibility.CREATOR_ONLY, ContentVisibility.COMPANY_WIDE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visibility. Must be 'creator_only' or 'company_wide'"
        )
    
    scenario_updates = {"visibility": new_visibility}
    updated_scenario = await update_scenario(db, scenario_id, scenario_updates, admin_user.id)
    if not updated_scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return updated_scenario

@router.get("/scenarios/{scenario_id}/with-assignment", response_model=Dict[str, Any])
async def get_scenario_with_assignment_endpoint(
    scenario_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a scenario with assignment data for current user"""
    scenario = await get_full_scenario(db, scenario_id, current_user)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found or access denied")
    return scenario