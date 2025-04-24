# from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from datetime import datetime

# from models_new import (
#     LanguageBase, LanguageCreate, LanguageResponse, LanguageDB,
#      UserRole
# )
# from user_models import UserDB

# # from main import get_db
# from user import get_current_user, get_admin_user, get_superadmin_user

# # Create router
# router = APIRouter(prefix="/languages", tags=["Languages"])

# # Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     from database import get_db  # Import your existing function
#     return await get_db()

# # Language Any Operations
# async def get_languages(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[LanguageDB]:
#     """
#     Get a list of all languages.
#     - All users can view languages
#     """
#     if not current_user:
#         return []
    
#     languages = []
#     cursor = db.languages.find().skip(skip).limit(limit)
#     async for document in cursor:
#         languages.append(LanguageDB(**document))
    
#     return languages

# async def get_language(
#     db: Any, 
#     language_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[LanguageDB]:
#     """
#     Get a language by ID (all users can view languages)
#     """
#     if not current_user:
#         return None
        
#     language = await db.languages.find_one({"_id": language_id})
#     if language:
#         return LanguageDB(**language)
#     return None

# async def get_language_by_code(
#     db: Any, 
#     language_code: str, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[LanguageDB]:
#     """
#     Get a language by its code (all users can view languages)
#     """
#     if not current_user:
#         return None
        
#     language = await db.languages.find_one({"code": language_code})
#     if language:
#         return LanguageDB(**language)
#     return None

# async def create_language(
#     db: Any, 
#     language: LanguageCreate, 
#     created_by: UUID
# ) -> LanguageDB:
#     """
#     Create a new language (admin/superadmin only)
#     """
#     # Check if language with this code already exists
#     existing_language = await get_language_by_code(db, language.code, UserDB(
#         id=created_by,
#         email="temp@example.com",  # Temporary values for validation
#         first_name="temp", 
#         last_name="temp",
#         role=UserRole.ADMIN,
#         hashed_password="temp"
#     ))
    
#     if existing_language:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Language with code '{language.code}' already exists"
#         )
    
#     # Create LanguageDB model
#     language_db = LanguageDB(
#         **language.dict(),
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Insert into database
#     language_dict = language_db.dict(by_alias=True)
#     if language_dict.get("_id") is None:
#         language_dict.pop("_id", None)
#     else:
#         language_dict["_id"] = UUID(str(language_dict["_id"]))
    
#     result = await db.languages.insert_one(language_dict)
#     created_language = await db.languages.find_one({"_id": result.inserted_id})
    
#     return LanguageDB(**created_language)

# async def update_language(
#     db: Any, 
#     language_id: UUID, 
#     language_updates: Dict[str, Any], 
#     updated_by: UUID
# ) -> Optional[LanguageDB]:
#     """
#     Update a language with permission checks
#     """
#     # Get the language to update
#     language = await db.languages.find_one({"_id": language_id})
#     if not language:
#         return None
    
#     # Get the user making the update
#     updater = await db.users.find_one({"_id": updated_by})
#     if not updater:
#         return None
    
#     # Convert updater to UserDB for role checking
#     updater = UserDB(**updater)
    
#     # Check permissions
#     if updater.role == UserRole.ADMIN:
#         # Admin can only update languages they created
#         if language.get("created_by") != updated_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only update languages they created"
#             )
#     elif updater.role != UserRole.SUPERADMIN:
#         # Regular users cannot update languages
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update languages"
#         )
    
#     # Check if trying to update the code to an existing one
#     if "code" in language_updates and language_updates["code"] != language.get("code"):
#         existing_language = await get_language_by_code(db, language_updates["code"], updater)
#         if existing_language:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Language with code '{language_updates['code']}' already exists"
#             )
    
#     # Add updated timestamp
#     language_updates["updated_at"] = datetime.now()
    
#     # Update in database
#     await db.languages.update_one(
#         {"_id": language_id},
#         {"$set": language_updates}
#     )
    
#     updated_language = await db.languages.find_one({"_id": language_id})
#     if updated_language:
#         return LanguageDB(**updated_language)
#     return None

# async def delete_language(db: Any, language_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete a language with permission checks
#     """
#     # Get the language to delete
#     language = await db.languages.find_one({"_id": language_id})
#     if not language:
#         return False
    
#     # Get the user making the deletion
#     deleter = await db.users.find_one({"_id": deleted_by})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete languages they created
#         if language.get("created_by") != deleted_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete languages they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete languages
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete languages"
#         )
    
#     # Check if this language is being used in any avatar interactions
#     avatar_interactions_using_language = await db.avatar_interactions.find(
#         {"languages": language_id}
#     ).to_list(length=1)
    
#     if avatar_interactions_using_language:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete language as it is being used in one or more avatar interactions"
#         )
    
#     # Check if this language is associated with any bot voices
#     bot_voices_using_language = await db.bot_voices.find(
#         {"language_code": language.get("code")}
#     ).to_list(length=1)
    
#     if bot_voices_using_language:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete language as it is being used by one or more bot voices"
#         )
    
#     # Delete the language
#     result = await db.languages.delete_one({"_id": language_id})
    
#     return result.deleted_count > 0

# # Language API Endpoints
# @router.get("/", response_model=List[LanguageResponse])
# async def get_languages_endpoint(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all languages (all users can view)
#     """
#     return await get_languages(db, skip, limit, current_user)

# @router.get("/code/{language_code}", response_model=LanguageResponse)
# async def get_language_by_code_endpoint(
#     language_code: str,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a language by its code
#     """
#     language = await get_language_by_code(db, language_code, current_user)
#     if not language:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
#     return language

# @router.get("/{language_id}", response_model=LanguageResponse)
# async def get_language_endpoint(
#     language_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific language by ID
#     """
#     language = await get_language(db, language_id, current_user)
#     if not language:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
#     return language

# @router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
# async def create_language_endpoint(
#     language: LanguageCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create languages
# ):
#     """
#     Create a new language (admin/superadmin only)
#     """
#     return await create_language(db, language, admin_user.id)

# @router.put("/{language_id}", response_model=LanguageResponse)
# async def update_language_endpoint(
#     language_id: UUID,
#     language_updates: Dict[str, Any] = Body(...),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update languages
# ):
#     """
#     Update a language by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     updated_language = await update_language(db, language_id, language_updates, admin_user.id)
#     if not updated_language:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
#     return updated_language

# @router.delete("/{language_id}", response_model=Dict[str, bool])
# async def delete_language_endpoint(
#     language_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete languages
# ):
#     """
#     Delete a language by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_language(db, language_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
#     return {"success": True}
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models_new import (
    LanguageBase, LanguageCreate, LanguageResponse, LanguageDB,
     UserRole
)
from user_models import UserDB

from user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/languages", tags=["Languages"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Language Any Operations
async def get_languages(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[LanguageDB]:
    """
    Get a list of all languages.
    - All users can view languages
    """
    if not current_user:
        return []
    
    languages = []
    cursor = db.languages.find().skip(skip).limit(limit)
    async for document in cursor:
        languages.append(LanguageDB(**document))
    
    return languages

async def get_language(
    db: Any, 
    language_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[LanguageDB]:
    """
    Get a language by ID (all users can view languages)
    """
    if not current_user:
        return None
    
    # Use string representation of UUID for MongoDB query    
    language = await db.languages.find_one({"_id": str(language_id)})
    if language:
        return LanguageDB(**language)
    return None

async def get_language_by_code(
    db: Any, 
    language_code: str, 
    current_user: Optional[UserDB] = None
) -> Optional[LanguageDB]:
    """
    Get a language by its code (all users can view languages)
    """
    if not current_user:
        return None
        
    language = await db.languages.find_one({"code": language_code})
    if language:
        return LanguageDB(**language)
    return None

async def create_language(
    db: Any, 
    language: LanguageCreate, 
    created_by: UUID
) -> LanguageDB:
    """
    Create a new language (admin/superadmin only)
    """
    # Check if language with this code already exists
    existing_language = await get_language_by_code(db, language.code, UserDB(
        id=created_by,
        email="temp@example.com",  # Temporary values for validation
        first_name="temp", 
        last_name="temp",
        role=UserRole.ADMIN,
        hashed_password="temp"
    ))
    
    if existing_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language with code '{language.code}' already exists"
        )
    
    # Create LanguageDB model
    language_db = LanguageDB(
        **language.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    language_dict = language_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in language_dict:
        language_dict["_id"] = str(language_dict["_id"])
    
    # Store created_by as string
    if "created_by" in language_dict:
        language_dict["created_by"] = str(language_dict["created_by"])
    
    result = await db.languages.insert_one(language_dict)
    created_language = await db.languages.find_one({"_id": str(result.inserted_id)})
    
    return LanguageDB(**created_language)

async def update_language(
    db: Any, 
    language_id: UUID, 
    language_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[LanguageDB]:
    """
    Update a language with permission checks
    """
    # Get the language to update - use string representation
    language = await db.languages.find_one({"_id": str(language_id)})
    if not language:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update languages they created
        if language.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update languages they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update languages
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update languages"
        )
    
    # Check if trying to update the code to an existing one
    if "code" in language_updates and language_updates["code"] != language.get("code"):
        existing_language = await get_language_by_code(db, language_updates["code"], updater)
        if existing_language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Language with code '{language_updates['code']}' already exists"
            )
    
    # Add updated timestamp
    language_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.languages.update_one(
        {"_id": str(language_id)},
        {"$set": language_updates}
    )
    
    updated_language = await db.languages.find_one({"_id": str(language_id)})
    if updated_language:
        return LanguageDB(**updated_language)
    return None

async def delete_language(db: Any, language_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a language with permission checks
    """
    # Get the language to delete - use string representation
    language = await db.languages.find_one({"_id": str(language_id)})
    if not language:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete languages they created
        if language.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete languages they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete languages
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete languages"
        )
    
    # Check if this language is being used in any avatar interactions - use string representation
    avatar_interactions_using_language = await db.avatar_interactions.find(
        {"languages": str(language_id)}
    ).to_list(length=1)
    
    if avatar_interactions_using_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete language as it is being used in one or more avatar interactions"
        )
    
    # Check if this language is associated with any bot voices
    bot_voices_using_language = await db.bot_voices.find(
        {"language_code": language.get("code")}
    ).to_list(length=1)
    
    if bot_voices_using_language:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete language as it is being used by one or more bot voices"
        )
    
    # Delete the language - use string representation
    result = await db.languages.delete_one({"_id": str(language_id)})
    
    return result.deleted_count > 0

# Language API Endpoints
@router.get("/", response_model=List[LanguageResponse])
async def get_languages_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all languages (all users can view)
    """
    return await get_languages(db, skip, limit, current_user)

@router.get("/code/{language_code}", response_model=LanguageResponse)
async def get_language_by_code_endpoint(
    language_code: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a language by its code
    """
    language = await get_language_by_code(db, language_code, current_user)
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return language

@router.get("/{language_id}", response_model=LanguageResponse)
async def get_language_endpoint(
    language_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific language by ID
    """
    language = await get_language(db, language_id, current_user)
    if not language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return language

@router.post("/", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language_endpoint(
    language: LanguageCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create languages
):
    """
    Create a new language (admin/superadmin only)
    """
    return await create_language(db, language, admin_user.id)

@router.put("/{language_id}", response_model=LanguageResponse)
async def update_language_endpoint(
    language_id: UUID,
    language_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update languages
):
    """
    Update a language by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_language = await update_language(db, language_id, language_updates, admin_user.id)
    if not updated_language:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return updated_language

@router.delete("/{language_id}", response_model=Dict[str, bool])
async def delete_language_endpoint(
    language_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete languages
):
    """
    Delete a language by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_language(db, language_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return {"success": True}