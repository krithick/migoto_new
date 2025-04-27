
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


from models.botVoice_models import  BotVoiceBase, BotVoiceCreate, BotVoiceResponse, BotVoiceDB
from models.user_models import UserDB, UserRole

# from main import get_db
from core.user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/bot-voices", tags=["Bot Voices"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# BotVoice Any Operations
async def get_bot_voices(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[BotVoiceDB]:
    """
    Get a list of all bot voices.
    - All users can view bot voices
    """
    if not current_user:
        return []
    
    bot_voices = []
    cursor = db.bot_voices.find().skip(skip).limit(limit)
    async for document in cursor:
        bot_voices.append(BotVoiceDB(**document))
    
    return bot_voices

async def get_bot_voice(
    db: Any, 
    bot_voice_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[BotVoiceDB]:
    """
    Get a bot voice by ID (all users can view bot voices)
    """
    if not current_user:
        return None
        
    # Use string representation for MongoDB query
    bot_voice = await db.bot_voices.find_one({"_id": str(bot_voice_id)})
    if bot_voice:
        return BotVoiceDB(**bot_voice)
    return None

async def get_bot_voices_by_language(
    db: Any, 
    language_code: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[BotVoiceDB]:
    """
    Get bot voices filtered by language code
    """
    if not current_user:
        return []
    
    bot_voices = []
    cursor = db.bot_voices.find({"language_code": language_code}).skip(skip).limit(limit)
    async for document in cursor:
        bot_voices.append(BotVoiceDB(**document))
    
    return bot_voices

async def create_bot_voice(
    db: Any, 
    bot_voice: BotVoiceCreate, 
    created_by: UUID
) -> BotVoiceDB:
    """
    Create a new bot voice (admin/superadmin only)
    """
    # Verify that the language exists
    language = await db.languages.find_one({"code": bot_voice.language_code})
    if not language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language with code '{bot_voice.language_code}' does not exist"
        )
    
    # Create BotVoiceDB model
    bot_voice_db = BotVoiceDB(
        **bot_voice.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    bot_voice_dict = bot_voice_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in bot_voice_dict:
        bot_voice_dict["_id"] = str(bot_voice_dict["_id"])
    
    # Store created_by as string
    if "created_by" in bot_voice_dict:
        bot_voice_dict["created_by"] = str(bot_voice_dict["created_by"])
    
    result = await db.bot_voices.insert_one(bot_voice_dict)
    created_bot_voice = await db.bot_voices.find_one({"_id": str(result.inserted_id)})
    
    return BotVoiceDB(**created_bot_voice)

async def update_bot_voice(
    db: Any, 
    bot_voice_id: UUID, 
    bot_voice_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[BotVoiceDB]:
    """
    Update a bot voice with permission checks
    """
    # Get the bot voice to update - use string representation
    bot_voice = await db.bot_voices.find_one({"_id": str(bot_voice_id)})
    if not bot_voice:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update bot voices they created
        if bot_voice.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update bot voices they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update bot voices
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update bot voices"
        )
    
    # If changing language code, verify that the new language exists
    if "language_code" in bot_voice_updates and bot_voice_updates["language_code"] != bot_voice.get("language_code"):
        language = await db.languages.find_one({"code": bot_voice_updates["language_code"]})
        if not language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Language with code '{bot_voice_updates['language_code']}' does not exist"
            )
    
    # Add updated timestamp
    bot_voice_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.bot_voices.update_one(
        {"_id": str(bot_voice_id)},
        {"$set": bot_voice_updates}
    )
    
    updated_bot_voice = await db.bot_voices.find_one({"_id": str(bot_voice_id)})
    if updated_bot_voice:
        return BotVoiceDB(**updated_bot_voice)
    return None

async def delete_bot_voice(db: Any, bot_voice_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a bot voice with permission checks
    """
    # Get the bot voice to delete - use string representation
    bot_voice = await db.bot_voices.find_one({"_id": str(bot_voice_id)})
    if not bot_voice:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete bot voices they created
        if bot_voice.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete bot voices they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete bot voices
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete bot voices"
        )
    
    # Check if this bot voice is being used in any avatar interactions - use string representation
    avatar_interactions_using_voice = await db.avatar_interactions.find(
        {"bot_voices": str(bot_voice_id)}
    ).to_list(length=1)
    
    if avatar_interactions_using_voice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete bot voice as it is being used in one or more avatar interactions"
        )
    
    # Delete the bot voice - use string representation
    result = await db.bot_voices.delete_one({"_id": str(bot_voice_id)})
    
    return result.deleted_count > 0

# BotVoice API Endpoints
@router.get("/", response_model=List[BotVoiceResponse])
async def get_bot_voices_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all bot voices (all users can view)
    """
    return await get_bot_voices(db, skip, limit, current_user)

@router.get("/language/{language_code}", response_model=List[BotVoiceResponse])
async def get_bot_voices_by_language_endpoint(
    language_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get bot voices filtered by language code
    """
    return await get_bot_voices_by_language(db, language_code, skip, limit, current_user)

@router.get("/{bot_voice_id}", response_model=BotVoiceResponse)
async def get_bot_voice_endpoint(
    bot_voice_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific bot voice by ID
    """
    bot_voice = await get_bot_voice(db, bot_voice_id, current_user)
    if not bot_voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot voice not found")
    return bot_voice

@router.post("/", response_model=BotVoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_bot_voice_endpoint(
    bot_voice: BotVoiceCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create bot voices
):
    """
    Create a new bot voice (admin/superadmin only)
    """
    return await create_bot_voice(db, bot_voice, admin_user.id)

@router.put("/{bot_voice_id}", response_model=BotVoiceResponse)
async def update_bot_voice_endpoint(
    bot_voice_id: UUID,
    bot_voice_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update bot voices
):
    """
    Update a bot voice by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_bot_voice = await update_bot_voice(db, bot_voice_id, bot_voice_updates, admin_user.id)
    if not updated_bot_voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot voice not found")
    return updated_bot_voice

@router.delete("/{bot_voice_id}", response_model=Dict[str, bool])
async def delete_bot_voice_endpoint(
    bot_voice_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete bot voices
):
    """
    Delete a bot voice by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_bot_voice(db, bot_voice_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot voice not found")
    return {"success": True}