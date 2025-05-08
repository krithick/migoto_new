from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Set
from uuid import UUID
from datetime import datetime

from models.avatarInteraction_models import (
    AvatarInteractionBase,AvatarInteractionExpandedResponse,AvatarInteractionType, AvatarInteractionCreate, AvatarInteractionResponse, AvatarInteractionDB,
     
)

from models.user_models import UserDB ,UserRole
from core.user import get_current_user, get_admin_user, get_superadmin_user
from models.avatar_models import AvatarResponse
from models.language_models import LanguageResponse
from models.botVoice_models import BotVoiceResponse
from models.environment_models import EnvironmentResponse

# Create router
router = APIRouter(prefix="/avatar-interactions", tags=["Avatar Interactions"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Helper function to validate references
async def validate_avatar_interaction_references(db: Any, avatar_interaction: AvatarInteractionCreate):
    """
    Validate that all referenced entities exist in the database
    """
    # Check personas
    # for persona_id in avatar_interaction.personas:
    #     persona = await db.personas.find_one({"_id": str(persona_id)})
    #     if not persona:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Persona with ID {persona_id} does not exist"
    #         )
    
    # Check avatars
    for avatar_id in avatar_interaction.avatars:
        print(avatar_id,type(avatar_id))
        avatar = await db.avatars.find_one({"_id": str(avatar_id)})
        print(avatar,avatar["persona_id"])
        if avatar:
            for persona_id in avatar["persona_id"]:
                print(persona_id,type(persona_id))
                persona = await db.personas.find_one({"_id": str(persona_id)})
                if not persona:
                    raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Persona with ID {persona_id} does not exist"
                )
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Avatar with ID {avatar_id} does not exist"
            )
    
    # Check languages
    for language_id in avatar_interaction.languages:
        language = await db.languages.find_one({"_id": str(language_id)})
        if not language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Language with ID {language_id} does not exist"
            )
    
    # Check bot voices
    for bot_voice_id in avatar_interaction.bot_voices:
        bot_voice = await db.bot_voices.find_one({"_id": str(bot_voice_id)})
        if not bot_voice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bot voice with ID {bot_voice_id} does not exist"
            )
    
    # Check environments
    for environment_id in avatar_interaction.environments:
        environment = await db.environments.find_one({"_id": str(environment_id)})
        if not environment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Environment with ID {environment_id} does not exist"
            )

# AvatarInteraction Any Operations
async def get_avatar_interactions(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[AvatarInteractionDB]:
    """
    Get a list of all avatar interactions.
    - All users can view avatar interactions
    """
    if not current_user:
        return []
    
    avatar_interactions = []
    cursor = db.avatar_interactions.find().skip(skip).limit(limit)
    async for document in cursor:
        avatar_interactions.append(AvatarInteractionDB(**document))
    
    return avatar_interactions

# async def get_avatar_interaction(
#     db: Any, 
#     avatar_interaction_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[AvatarInteractionDB]:
#     """
#     Get an avatar interaction by ID (all users can view avatar interactions)
#     """
#     if not current_user:
#         return None
    
#     # Use string for MongoDB query    
#     avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
#     if avatar_interaction:
#         return AvatarInteractionDB(**avatar_interaction)
#     return None
async def get_avatar_interaction(
    db: Any, 
    avatar_interaction_id: UUID, 
    current_user: Optional[UserDB] = None,
    expand: Optional[List[str]] = None
) -> Optional[Dict]:
    """
    Get an avatar interaction by ID with options to expand related entities
    """
    if not current_user:
        return None
    
    # Get the base avatar interaction
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    
    if not avatar_interaction:
        return None
    
    # Convert MongoDB _id to id
    avatar_interaction["id"] = avatar_interaction.pop("_id")
    
    # Handle expansion if requested
    if expand and isinstance(expand, list):
        if "avatars" in expand and "avatars" in avatar_interaction:
            avatar_ids = avatar_interaction["avatars"]
            avatar_objects = []
            
            for avatar_id in avatar_ids:
                avatar_doc = await db.avatars.find_one({"_id": str(avatar_id)})
                if avatar_doc:
                    # Expand personas for this avatar if they exist
                    if "persona_id" in avatar_doc:
                        personas = []
                        for persona_id in avatar_doc["persona_id"]:
                            persona = await db.personas.find_one({"_id": str(persona_id)})
                            if persona:
                                persona["id"] = persona.pop("_id")
                                personas.append(persona)
                        avatar_doc["persona_id"] = personas
                        
                    # Convert _id to id
                    avatar_doc["id"] = avatar_doc.pop("_id")
                    avatar_objects.append(avatar_doc)
            avatar_interaction["avatars"] = avatar_objects
            
        # Process languages expansion
        if "languages" in expand and "languages" in avatar_interaction:
            language_ids = avatar_interaction["languages"]
            language_objects = []
            
            for language_id in language_ids:
                language_doc = await db.languages.find_one({"_id": str(language_id)})
                if language_doc:
                    # Convert _id to id
                    language_doc["id"] = language_doc.pop("_id")
                    language_objects.append(language_doc)
            avatar_interaction["languages"] = language_objects
            
        # Process bot_voices expansion
        if "bot_voices" in expand and "bot_voices" in avatar_interaction:
            voice_ids = avatar_interaction["bot_voices"]
            voice_objects = []
            
            for voice_id in voice_ids:
                voice_doc = await db.bot_voices.find_one({"_id": str(voice_id)})
                if voice_doc:
                    # Convert _id to id
                    voice_doc["id"] = voice_doc.pop("_id")
                    voice_objects.append(voice_doc)
            avatar_interaction["bot_voices"] = voice_objects
            
        # Process environments expansion
        if "environments" in expand and "environments" in avatar_interaction:
            environment_ids = avatar_interaction["environments"]
            environment_objects = []
            
            for environment_id in environment_ids:
                environment_doc = await db.environments.find_one({"_id": str(environment_id)})
                if environment_doc:
                    # Convert _id to id
                    environment_doc["id"] = environment_doc.pop("_id")
                    environment_objects.append(environment_doc)
            avatar_interaction["environments"] = environment_objects
        if "assigned_documents" in expand and "assigned_documents" in avatar_interaction:
            document_ids = avatar_interaction["assigned_documents"]
            document_objects = []
            
            for doc_id in document_ids:
                doc = await db.documents.find_one({"_id": str(doc_id)})
                if doc:
                    doc["id"] = doc.pop("_id")
                    document_objects.append(doc)
            
            avatar_interaction["assigned_documents"] = document_objects
        
        # Add expansion for assigned videos
        if "assigned_videos" in expand and "assigned_videos" in avatar_interaction:
            video_ids = avatar_interaction["assigned_videos"]
            video_objects = []
            
            for vid_id in video_ids:
                vid = await db.videos.find_one({"_id": str(vid_id)})
                if vid:
                    vid["id"] = vid.pop("_id")
                    video_objects.append(vid)
            
            avatar_interaction["assigned_videos"] = video_objects    
    # Return the document
    return avatar_interaction
#fixxx
async def get_avatar_interactions_by_persona(
    db: Any, 
    persona_id: UUID,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[AvatarInteractionDB]:
    """
    Get avatar interactions filtered by persona
    """
    if not current_user:
        return []
    
    avatar_interactions = []
    # Use string for MongoDB query
    cursor = db.avatar_interactions.find({"personas": str(persona_id)}).skip(skip).limit(limit)
    async for document in cursor:
        avatar_interactions.append(AvatarInteractionDB(**document))
    
    return avatar_interactions

async def get_avatar_interactions_by_avatar(
    db: Any, 
    avatar_id: UUID,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[AvatarInteractionDB]:
    """
    Get avatar interactions filtered by avatar
    """
    if not current_user:
        return []
    
    avatar_interactions = []
    # Use string for MongoDB query
    cursor = db.avatar_interactions.find({"avatars": str(avatar_id)}).skip(skip).limit(limit)
    async for document in cursor:
        avatar_interactions.append(AvatarInteractionDB(**document))
    
    return avatar_interactions

async def get_avatar_interactions_by_environment(
    db: Any, 
    environment_id: UUID,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[AvatarInteractionDB]:
    """
    Get avatar interactions filtered by environment
    """
    if not current_user:
        return []
    
    avatar_interactions = []
    # Use string for MongoDB query
    cursor = db.avatar_interactions.find({"environments": str(environment_id)}).skip(skip).limit(limit)
    async for document in cursor:
        avatar_interactions.append(AvatarInteractionDB(**document))
    
    return avatar_interactions

async def create_avatar_interaction(
    db: Any, 
    avatar_interaction: AvatarInteractionCreate, 
    created_by: UUID
) -> AvatarInteractionDB:
    """
    Create a new avatar interaction (admin/superadmin only)
    """
    # Validate that referenced entities exist
    await validate_avatar_interaction_references(db, avatar_interaction)
    
    # Create AvatarInteractionDB model
    avatar_interaction_db = AvatarInteractionDB(
        **avatar_interaction.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    avatar_interaction_dict = avatar_interaction_db.dict(by_alias=True)
    print(avatar_interaction_dict)
    # Always use string for _id in MongoDB
    if "_id" in avatar_interaction_dict:
        avatar_interaction_dict["_id"] = str(avatar_interaction_dict["_id"])
    
    # Convert all UUIDs in the lists to strings for MongoDB
    for field in [ "avatars", "languages", "bot_voices", "environments"]:
        if field in avatar_interaction_dict and avatar_interaction_dict[field]:
            avatar_interaction_dict[field] = [str(item_id) for item_id in avatar_interaction_dict[field]]
 
    # Store created_by as string
    if "created_by" in avatar_interaction_dict:
        avatar_interaction_dict["created_by"] = str(avatar_interaction_dict["created_by"])
    if "scenario_id" in avatar_interaction_dict:
        avatar_interaction_dict["scenario_id"] = str(avatar_interaction_dict["scenario_id"])
    
    result = await db.avatar_interactions.insert_one(avatar_interaction_dict)
    created_avatar_interaction = await db.avatar_interactions.find_one({"_id": str(result.inserted_id)})
    
    return AvatarInteractionDB(**created_avatar_interaction)

async def update_avatar_interaction(
    db: Any, 
    avatar_interaction_id: UUID, 
    avatar_interaction_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[AvatarInteractionDB]:
    """
    Update an avatar interaction with permission checks
    """
    # Get the avatar interaction to update - use string representation
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update avatar interactions they created
        if avatar_interaction.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update avatar interactions they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update avatar interactions
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update avatar interactions"
        )
    
    # If updating reference lists, validate that the referenced entities exist
    if any(field in avatar_interaction_updates for field in ["personas", "avatars", "languages", "bot_voices", "environments"]):
        # Combine current values with updates for validation
        temp_interaction = avatar_interaction.copy()
        temp_interaction.update(avatar_interaction_updates)
        
        # Create a temporary AvatarInteractionCreate for validation
        temp_create = AvatarInteractionCreate(
            personas=temp_interaction.get("personas", []),
            avatars=temp_interaction.get("avatars", []),
            languages=temp_interaction.get("languages", []),
            bot_voices=temp_interaction.get("bot_voices", []),
            environments=temp_interaction.get("environments", [])
        )
        
        await validate_avatar_interaction_references(db, temp_create)
    
    # Add updated timestamp
    avatar_interaction_updates["updated_at"] = datetime.now()
    
    # Convert all UUIDs in the lists to strings for MongoDB
    for field in ["personas", "avatars", "languages", "bot_voices", "environments"]:
        if field in avatar_interaction_updates and avatar_interaction_updates[field]:
            avatar_interaction_updates[field] = [str(item_id) for item_id in avatar_interaction_updates[field]]
    
    # Update in database - use string representation
    await db.avatar_interactions.update_one(
        {"_id": str(avatar_interaction_id)},
        {"$set": avatar_interaction_updates}
    )
    
    updated_avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if updated_avatar_interaction:
        return AvatarInteractionDB(**updated_avatar_interaction)
    return None

async def delete_avatar_interaction(db: Any, avatar_interaction_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete an avatar interaction with permission checks
    """
    # Get the avatar interaction to delete - use string representation
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete avatar interactions they created
        if avatar_interaction.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete avatar interactions they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete avatar interactions
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete avatar interactions"
        )
    
    # Check if this avatar interaction is being used in any scenarios - use string representation
    scenarios_using_interaction = []
    
    # Check learn mode
    learn_mode_scenarios = await db.scenarios.find(
        {"learn_mode.avatar_interaction": str(avatar_interaction_id)}
    ).to_list(length=1)
    scenarios_using_interaction.extend(learn_mode_scenarios)
    
    # Check try mode
    try_mode_scenarios = await db.scenarios.find(
        {"try_mode.avatar_interaction": str(avatar_interaction_id)}
    ).to_list(length=1)
    scenarios_using_interaction.extend(try_mode_scenarios)
    
    # Check assess mode
    assess_mode_scenarios = await db.scenarios.find(
        {"assess_mode.avatar_interaction": str(avatar_interaction_id)}
    ).to_list(length=1)
    scenarios_using_interaction.extend(assess_mode_scenarios)
    
    if scenarios_using_interaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete avatar interaction as it is being used in one or more scenarios"
        )
    
    # Delete the avatar interaction - use string representation
    result = await db.avatar_interactions.delete_one({"_id": str(avatar_interaction_id)})
    
    return result.deleted_count > 0

# AvatarInteraction API Endpoints
@router.get("/", response_model=List[AvatarInteractionResponse])
async def get_avatar_interactions_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all avatar interactions (all users can view)
    """
    return await get_avatar_interactions(db, skip, limit, current_user)

@router.get("/persona/{persona_id}", response_model=List[AvatarInteractionResponse])
async def get_avatar_interactions_by_persona_endpoint(
    persona_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get avatar interactions filtered by persona
    """
    return await get_avatar_interactions_by_persona(db, persona_id, skip, limit, current_user)

@router.get("/avatar/{avatar_id}", response_model=List[AvatarInteractionResponse])
async def get_avatar_interactions_by_avatar_endpoint(
    avatar_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get avatar interactions filtered by avatar
    """
    return await get_avatar_interactions_by_avatar(db, avatar_id, skip, limit, current_user)

@router.get("/environment/{environment_id}", response_model=List[AvatarInteractionResponse])
async def get_avatar_interactions_by_environment_endpoint(
    environment_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get avatar interactions filtered by environment
    """
    return await get_avatar_interactions_by_environment(db, environment_id, skip, limit, current_user)

# @router.get("/{avatar_interaction_id}", response_model=AvatarInteractionResponse)
# async def get_avatar_interaction_endpoint(
#     avatar_interaction_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific avatar interaction by ID
#     """
#     avatar_interaction = await get_avatar_interaction(db, avatar_interaction_id, current_user)
#     if not avatar_interaction:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar interaction not found")
#     return avatar_interaction
@router.get("/{avatar_interaction_id}", response_model=None)
async def get_avatar_interaction_endpoint(
    avatar_interaction_id: UUID,
    expand: Optional[List[str]] = Query(None, description="Fields to expand (avatars, languages, bot_voices, environments)"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific avatar interaction by ID with options to expand related entities
    """
    avatar_interaction = await get_avatar_interaction(
        db, 
        avatar_interaction_id, 
        current_user,
        expand=expand
    )
    
    if not avatar_interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar interaction not found")
    
    return avatar_interaction
   
@router.post("/", response_model=AvatarInteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar_interaction_endpoint(
    avatar_interaction: AvatarInteractionCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create avatar interactions
):
    """
    Create a new avatar interaction (admin/superadmin only)
    """
    return await create_avatar_interaction(db, avatar_interaction, admin_user.id)

@router.put("/{avatar_interaction_id}", response_model=AvatarInteractionResponse)
async def update_avatar_interaction_endpoint(
    avatar_interaction_id: UUID,
    avatar_interaction_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update avatar interactions
):
    """
    Update an avatar interaction by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_avatar_interaction = await update_avatar_interaction(db, avatar_interaction_id, avatar_interaction_updates, admin_user.id)
    if not updated_avatar_interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar interaction not found")
    return updated_avatar_interaction

@router.delete("/{avatar_interaction_id}", response_model=Dict[str, bool])
async def delete_avatar_interaction_endpoint(
    avatar_interaction_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete avatar interactions
):
    """
    Delete an avatar interaction by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_avatar_interaction(db, avatar_interaction_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar interaction not found")
    return {"success": True}



@router.put("/{avatar_interaction_id}/documents", response_model=dict)
async def assign_documents(
    avatar_interaction_id: UUID,
    document_ids: List[UUID] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Assign documents to an avatar interaction
    """
    # Get the avatar interaction
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        raise HTTPException(status_code=404, detail="Avatar interaction not found")
    
    # Verify all documents exist
    for doc_id in document_ids:
        doc = await db.documents.find_one({"_id": str(doc_id)})
        if not doc:
            raise HTTPException(status_code=400, detail=f"Document with ID {doc_id} not found")
    
    # Convert to strings for MongoDB
    document_ids_str = [str(doc_id) for doc_id in document_ids]
    
    # Update the avatar interaction
    await db.avatar_interactions.update_one(
        {"_id": str(avatar_interaction_id)},
        {"$set": {"assigned_documents": document_ids_str}}
    )
    
    return {"success": True, "document_count": len(document_ids)}

@router.put("/{avatar_interaction_id}/videos", response_model=dict)
async def assign_videos(
    avatar_interaction_id: UUID,
    video_ids: List[UUID] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Assign videos to an avatar interaction
    """
    # Get the avatar interaction
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        raise HTTPException(status_code=404, detail="Avatar interaction not found")
    
    # Verify all videos exist
    for vid_id in video_ids:
        vid = await db.videos.find_one({"_id": str(vid_id)})
        if not vid:
            raise HTTPException(status_code=400, detail=f"Video with ID {vid_id} not found")
    
    # Convert to strings for MongoDB
    video_ids_str = [str(vid_id) for vid_id in video_ids]
    
    # Update the avatar interaction
    await db.avatar_interactions.update_one(
        {"_id": str(avatar_interaction_id)},
        {"$set": {"assigned_videos": video_ids_str}}
    )
    
    return {"success": True, "video_count": len(video_ids)}