"""
Hierarchical API Endpoints for Learning Platform

This file defines additional API endpoints to support the hierarchical nature
of courses, modules, scenarios, modes, and their related components.

The structure follows a logical progression:
- Scenario selection
- Mode selection (learn, try, assess)
- Component selection (avatars, personas, languages, bot voices, environments)

Each endpoint respects the parent-child relationships and applies appropriate
filtering based on previous selections.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from models_new import (
    UserRole, ScenarioResponse, ScenarioDB,
    AvatarResponse, AvatarDB,
    PersonaResponse, PersonaDB,
    LanguageResponse, LanguageDB,
    BotVoiceResponse, BotVoiceDB,
    EnvironmentResponse, EnvironmentDB,
    VideoResponse, VideoDB,
    DocumentResponse, DocumentDB
)
from models.user_models import UserDB
from core.user import get_current_user, get_admin_user

# Create router - you might want to organize these into separate files
# or use different routers based on entity type
router = APIRouter(tags=["Hierarchical Relationships"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db
    return await get_db()

#############################################
# SCENARIO MODE NAVIGATION
#############################################

async def get_scenario_available_modes(
    db: Any,
    scenario_id: UUID,
    current_user: Optional[UserDB] = None
) -> Dict[str, bool]:
    """
    Get the available modes for a specific scenario
    """
    if not current_user:
        return {}
    
    # Get scenario with string ID for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check which modes are available
    available_modes = {
        "learn_mode": "learn_mode" in scenario and scenario["learn_mode"] is not None,
        "try_mode": "try_mode" in scenario and scenario["try_mode"] is not None,
        "assess_mode": "assess_mode" in scenario and scenario["assess_mode"] is not None
    }
    
    return available_modes

@router.get("/scenarios/{scenario_id}/modes", response_model=Dict[str, bool])
async def get_scenario_modes_endpoint(
    scenario_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the available modes for a specific scenario.
    Returns a dictionary with mode names as keys and booleans as values.
    """
    return await get_scenario_available_modes(db, scenario_id, current_user)

#############################################
# AVATAR INTERACTIONS BY SCENARIO MODE
#############################################

async def get_avatar_interaction_by_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """
    Get the avatar interaction for a specific scenario mode
    """
    if not current_user:
        return None
    
    # Validate mode name
    if mode_name not in ["learn_mode", "try_mode", "assess_mode"]:
        raise HTTPException(status_code=400, detail="Invalid mode name")
    
    # Get scenario with string ID for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if the mode exists
    if mode_name not in scenario or not scenario[mode_name]:
        raise HTTPException(status_code=404, detail=f"Mode {mode_name} not found in this scenario")
    
    # Get the avatar interaction ID
    mode_data = scenario[mode_name]
    if "avatar_interaction" not in mode_data:
        return None
    
    avatar_interaction_id = mode_data["avatar_interaction"]
    
    # Get the avatar interaction
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        return None
    
    return avatar_interaction

@router.get("/scenarios/{scenario_id}/{mode_name}/avatar-interaction", response_model=Dict[str, Any])
async def get_mode_avatar_interaction_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the avatar interaction for a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    """
    avatar_interaction = await get_avatar_interaction_by_mode(db, scenario_id, mode_name, current_user)
    if not avatar_interaction:
        raise HTTPException(status_code=404, detail="Avatar interaction not found for this mode")
    return avatar_interaction

#############################################
# AVATARS BY SCENARIO MODE
#############################################

async def get_avatars_by_scenario_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> List[AvatarDB]:
    """
    Get avatars available for a specific scenario mode
    """
    if not current_user:
        return []
    
    # Get the avatar interaction for this mode
    avatar_interaction = await get_avatar_interaction_by_mode(db, scenario_id, mode_name, current_user)
    if not avatar_interaction:
        return []
    
    # Get avatar IDs from the interaction
    avatar_ids = avatar_interaction.get("avatars", [])
    if not avatar_ids:
        return []
    
    # Get the actual avatars
    avatars = []
    for avatar_id in avatar_ids:
        avatar = await db.avatars.find_one({"_id": avatar_id})
        if avatar:
            avatars.append(AvatarDB(**avatar))
    
    return avatars

@router.get("/scenarios/{scenario_id}/{mode_name}/avatars", response_model=List[AvatarResponse])
async def get_mode_avatars_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the avatars available for a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    """
    return await get_avatars_by_scenario_mode(db, scenario_id, mode_name, current_user)

#############################################
# PERSONAS BY AVATAR
#############################################

async def get_personas_by_avatar(
    db: Any,
    avatar_id: UUID,
    current_user: Optional[UserDB] = None
) -> List[PersonaDB]:
    """
    Get personas that are used with a specific avatar in any avatar interaction
    """
    if not current_user:
        return []
    
    # Find avatar interactions that include this avatar
    interactions_cursor = db.avatar_interactions.find({"avatars": str(avatar_id)})
    
    # Collect all persona IDs from these interactions
    persona_ids = set()
    async for interaction in interactions_cursor:
        persona_ids.update(interaction.get("personas", []))
    
    # Get the actual personas
    personas = []
    for persona_id in persona_ids:
        persona = await db.personas.find_one({"_id": persona_id})
        if persona:
            personas.append(PersonaDB(**persona))
    
    return personas

@router.get("/avatars/{avatar_id}/personas", response_model=List[PersonaResponse])
async def get_avatar_personas_endpoint(
    avatar_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get personas that are used with a specific avatar in any avatar interaction.
    """
    return await get_personas_by_avatar(db, avatar_id, current_user)

#############################################
# LANGUAGES BY SCENARIO MODE
#############################################

async def get_languages_by_scenario_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> List[LanguageDB]:
    """
    Get languages available for a specific scenario mode
    """
    if not current_user:
        return []
    
    # Get the avatar interaction for this mode
    avatar_interaction = await get_avatar_interaction_by_mode(db, scenario_id, mode_name, current_user)
    if not avatar_interaction:
        return []
    
    # Get language IDs from the interaction
    language_ids = avatar_interaction.get("languages", [])
    if not language_ids:
        return []
    
    # Get the actual languages
    languages = []
    for language_id in language_ids:
        language = await db.languages.find_one({"_id": language_id})
        if language:
            languages.append(LanguageDB(**language))
    
    return languages

@router.get("/scenarios/{scenario_id}/{mode_name}/languages", response_model=List[LanguageResponse])
async def get_mode_languages_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the languages available for a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    """
    return await get_languages_by_scenario_mode(db, scenario_id, mode_name, current_user)

#############################################
# BOT VOICES BY LANGUAGE AND AVATAR GENDER
#############################################

async def get_bot_voices_by_language_and_gender(
    db: Any,
    language_id: UUID,
    gender: Optional[str] = None,
    current_user: Optional[UserDB] = None
) -> List[BotVoiceDB]:
    """
    Get bot voices filtered by language and optionally by gender
    """
    if not current_user:
        return []
    
    # Get the language to get its code
    language = await db.languages.find_one({"_id": str(language_id)})
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    language_code = language.get("code")
    
    # Build the query
    query = {"language_code": language_code}
    
    # Add gender filter if provided
    # Note: This assumes bot voices have a gender field or naming convention
    # You'll need to adjust this based on your actual data model
    if gender:
        # This is just an example - adjust based on your actual schema
        query["gender"] = gender  # or query["name"] = {"$regex": f".*{gender}.*", "$options": "i"}
    
    # Get the bot voices
    bot_voices = []
    cursor = db.bot_voices.find(query)
    async for voice in cursor:
        bot_voices.append(BotVoiceDB(**voice))
    
    return bot_voices

@router.get("/languages/{language_id}/bot-voices", response_model=List[BotVoiceResponse])
async def get_language_bot_voices_endpoint(
    language_id: UUID,
    gender: Optional[str] = Query(None, description="Filter by voice gender (male/female)"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get bot voices for a specific language, optionally filtered by gender.
    """
    return await get_bot_voices_by_language_and_gender(db, language_id, gender, current_user)

#############################################
# ENVIRONMENTS BY SCENARIO MODE
#############################################

async def get_environments_by_scenario_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> List[EnvironmentDB]:
    """
    Get environments available for a specific scenario mode
    """
    if not current_user:
        return []
    
    # Get the avatar interaction for this mode
    avatar_interaction = await get_avatar_interaction_by_mode(db, scenario_id, mode_name, current_user)
    if not avatar_interaction:
        return []
    
    # Get environment IDs from the interaction
    environment_ids = avatar_interaction.get("environments", [])
    if not environment_ids:
        return []
    
    # Get the actual environments
    environments = []
    for environment_id in environment_ids:
        environment = await db.environments.find_one({"_id": environment_id})
        if environment:
            environments.append(EnvironmentDB(**environment))
    
    return environments

@router.get("/scenarios/{scenario_id}/{mode_name}/environments", response_model=List[EnvironmentResponse])
async def get_mode_environments_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the environments available for a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    """
    return await get_environments_by_scenario_mode(db, scenario_id, mode_name, current_user)

#############################################
# VIDEOS BY SCENARIO MODE
#############################################

async def get_videos_by_scenario_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> List[VideoDB]:
    """
    Get videos associated with a specific scenario mode
    """
    if not current_user:
        return []
    
    # Get scenario with string ID for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if the mode exists and has videos
    if mode_name not in scenario or not scenario[mode_name]:
        return []
    
    mode_data = scenario[mode_name]
    if "videos" not in mode_data or not mode_data["videos"]:
        return []
    
    # Get the videos
    videos = []
    for video_id in mode_data["videos"]:
        video = await db.videos.find_one({"_id": video_id})
        if video:
            videos.append(VideoDB(**video))
    
    return videos

@router.get("/scenarios/{scenario_id}/{mode_name}/videos", response_model=List[VideoResponse])
async def get_mode_videos_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the videos associated with a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    - Videos are typically associated with learn_mode
    """
    return await get_videos_by_scenario_mode(db, scenario_id, mode_name, current_user)

#############################################
# DOCUMENTS BY SCENARIO MODE
#############################################

async def get_documents_by_scenario_mode(
    db: Any,
    scenario_id: UUID,
    mode_name: str,
    current_user: Optional[UserDB] = None
) -> List[DocumentDB]:
    """
    Get documents associated with a specific scenario mode
    """
    if not current_user:
        return []
    
    # Get scenario with string ID for MongoDB
    scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Check if the mode exists and has documents
    if mode_name not in scenario or not scenario[mode_name]:
        return []
    
    mode_data = scenario[mode_name]
    if "documents" not in mode_data or not mode_data["documents"]:
        return []
    
    # Get the documents
    documents = []
    for document_id in mode_data["documents"]:
        document = await db.documents.find_one({"_id": document_id})
        if document:
            documents.append(DocumentDB(**document))
    
    return documents

@router.get("/scenarios/{scenario_id}/{mode_name}/documents", response_model=List[DocumentResponse])
async def get_mode_documents_endpoint(
    scenario_id: UUID,
    mode_name: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the documents associated with a specific scenario mode.
    
    - mode_name must be one of: learn_mode, try_mode, assess_mode
    """
    return await get_documents_by_scenario_mode(db, scenario_id, mode_name, current_user)

#############################################
# ADVANCED FILTERING - AVATAR INTERACTIONS
#############################################

async def filter_avatar_interactions(
    db: Any,
    avatar_id: Optional[UUID] = None,
    persona_id: Optional[UUID] = None,
    language_id: Optional[UUID] = None,
    bot_voice_id: Optional[UUID] = None,
    environment_id: Optional[UUID] = None,
    current_user: Optional[UserDB] = None
) -> List[Dict[str, Any]]:
    """
    Find avatar interactions that match specific filtering criteria
    """
    if not current_user:
        return []
    
    # Build the query
    query = {}
    
    # Add filters for each provided parameter
    if avatar_id:
        query["avatars"] = str(avatar_id)
    
    if persona_id:
        query["personas"] = str(persona_id)
    
    if language_id:
        query["languages"] = str(language_id)
    
    if bot_voice_id:
        query["bot_voices"] = str(bot_voice_id)
    
    if environment_id:
        query["environments"] = str(environment_id)
    
    # Get the matching interactions
    interactions = []
    cursor = db.avatar_interactions.find(query)
    async for interaction in cursor:
        interactions.append(interaction)
    
    return interactions

@router.get("/avatar-interactions/filter", response_model=List[Dict[str, Any]])
async def filter_avatar_interactions_endpoint(
    avatar_id: Optional[UUID] = Query(None, description="Filter by avatar"),
    persona_id: Optional[UUID] = Query(None, description="Filter by persona"),
    language_id: Optional[UUID] = Query(None, description="Filter by language"),
    bot_voice_id: Optional[UUID] = Query(None, description="Filter by bot voice"),
    environment_id: Optional[UUID] = Query(None, description="Filter by environment"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Find avatar interactions that match specific filtering criteria.
    """
    return await filter_avatar_interactions(
        db, avatar_id, persona_id, language_id, bot_voice_id, environment_id, current_user
    )

#############################################
# TODO: Add more endpoints as needed
#############################################

# Examples of additional endpoints to implement:

# 1. Get scenarios that use a specific avatar
# @router.get("/avatars/{avatar_id}/scenarios")

# 2. Get bot voices by avatar (assuming avatar specifies gender)
# @router.get("/avatars/{avatar_id}/bot-voices")

# 3. Get avatar interactions by environment
# @router.get("/environments/{environment_id}/avatar-interactions")

# 4. Search scenarios by name, description
# @router.get("/scenarios/search")

# 5. Get user progress in scenarios
# @router.get("/users/{user_id}/scenario-progress")

# 6. Find compatibility - check if specific components can be used together
# @router.post("/check-compatibility")