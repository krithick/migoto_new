# from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from datetime import datetime

# from models_new import (
#     AvatarBase, AvatarCreate, AvatarResponse, AvatarDB,
#      UserRole
# )
# from user_models import UserDB

# from user import get_current_user, get_admin_user, get_superadmin_user

# # Create router
# router = APIRouter(prefix="/avatars", tags=["Avatars"])

# # Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     from database import get_db  # Import your existing function
#     return await get_db()

# # Avatar Any Operations
# async def get_avatars(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[AvatarDB]:
#     """
#     Get a list of all avatars.
#     - All users can view avatars
#     """
#     if not current_user:
#         return []
    
#     avatars = []
#     cursor = db.avatars.find().skip(skip).limit(limit)
#     async for document in cursor:
#         avatars.append(AvatarDB(**document))
    
#     return avatars

# async def get_avatar(
#     db: Any, 
#     avatar_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[AvatarDB]:
#     """
#     Get an avatar by ID (all users can view avatars)
#     """
#     if not current_user:
#         return None
        
#     avatar = await db.avatars.find_one({"_id": avatar_id})
#     if avatar:
#         return AvatarDB(**avatar)
#     return None

# async def create_avatar(
#     db: Any, 
#     avatar: AvatarCreate, 
#     created_by: UUID
# ) -> AvatarDB:
#     """
#     Create a new avatar (admin/superadmin only)
#     """
#     # Create AvatarDB model
#     avatar_db = AvatarDB(
#         **avatar.dict(),
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Insert into database
#     avatar_dict = avatar_db.dict(by_alias=True)
#     if avatar_dict.get("_id") is None:
#         avatar_dict.pop("_id", None)
#     else:
#         avatar_dict["_id"] = UUID(str(avatar_dict["_id"]))
    
#     result = await db.avatars.insert_one(avatar_dict)
#     created_avatar = await db.avatars.find_one({"_id": result.inserted_id})
    
#     return AvatarDB(**created_avatar)

# async def update_avatar(
#     db: Any, 
#     avatar_id: UUID, 
#     avatar_updates: Dict[str, Any], 
#     updated_by: UUID
# ) -> Optional[AvatarDB]:
#     """
#     Update an avatar with permission checks
#     """
#     # Get the avatar to update
#     avatar = await db.avatars.find_one({"_id": avatar_id})
#     if not avatar:
#         return None
    
#     # Get the user making the update
#     updater = await db.users.find_one({"_id": updated_by})
#     if not updater:
#         return None
    
#     # Convert updater to UserDB for role checking
#     updater = UserDB(**updater)
    
#     # Check permissions
#     if updater.role == UserRole.ADMIN:
#         # Admin can only update avatars they created
#         if avatar.get("created_by") != updated_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only update avatars they created"
#             )
#     elif updater.role != UserRole.SUPERADMIN:
#         # Regular users cannot update avatars
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update avatars"
#         )
    
#     # Add updated timestamp
#     avatar_updates["updated_at"] = datetime.now()
    
#     # Update in database
#     await db.avatars.update_one(
#         {"_id": avatar_id},
#         {"$set": avatar_updates}
#     )
    
#     updated_avatar = await db.avatars.find_one({"_id": avatar_id})
#     if updated_avatar:
#         return AvatarDB(**updated_avatar)
#     return None

# async def delete_avatar(db: Any, avatar_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete an avatar with permission checks
#     """
#     # Get the avatar to delete
#     avatar = await db.avatars.find_one({"_id": avatar_id})
#     if not avatar:
#         return False
    
#     # Get the user making the deletion
#     deleter = await db.users.find_one({"_id": deleted_by})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete avatars they created
#         if avatar.get("created_by") != deleted_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete avatars they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete avatars
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete avatars"
#         )
    
#     # Check if this avatar is being used in any avatar interactions
#     avatar_interactions_using_avatar = await db.avatar_interactions.find(
#         {"avatars": avatar_id}
#     ).to_list(length=1)
    
#     if avatar_interactions_using_avatar:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete avatar as it is being used in one or more avatar interactions"
#         )
    
#     # Delete the avatar
#     result = await db.avatars.delete_one({"_id": avatar_id})
    
#     return result.deleted_count > 0

# # Avatar API Endpoints
# @router.get("/", response_model=List[AvatarResponse])
# async def get_avatars_endpoint(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all avatars (all users can view)
#     """
#     return await get_avatars(db, skip, limit, current_user)

# @router.get("/{avatar_id}", response_model=AvatarResponse)
# async def get_avatar_endpoint(
#     avatar_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific avatar by ID
#     """
#     avatar = await get_avatar(db, avatar_id, current_user)
#     if not avatar:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
#     return avatar

# @router.post("/", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
# async def create_avatar_endpoint(
#     avatar: AvatarCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create avatars
# ):
#     """
#     Create a new avatar (admin/superadmin only)
#     """
#     return await create_avatar(db, avatar, admin_user.id)

# @router.put("/{avatar_id}", response_model=AvatarResponse)
# async def update_avatar_endpoint(
#     avatar_id: UUID,
#     avatar_updates: Dict[str, Any] = Body(...),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update avatars
# ):
#     """
#     Update an avatar by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     updated_avatar = await update_avatar(db, avatar_id, avatar_updates, admin_user.id)
#     if not updated_avatar:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
#     return updated_avatar

# @router.delete("/{avatar_id}", response_model=Dict[str, bool])
# async def delete_avatar_endpoint(
#     avatar_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete avatars
# ):
#     """
#     Delete an avatar by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_avatar(db, avatar_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
#     return {"success": True}
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models_new import (
    AvatarBase, AvatarCreate, AvatarResponse, AvatarDB,
     UserRole
)
from user_models import UserDB

from user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/avatars", tags=["Avatars"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Avatar Any Operations
async def get_avatars(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[AvatarDB]:
    """
    Get a list of all avatars.
    - All users can view avatars
    """
    if not current_user:
        return []
    
    avatars = []
    cursor = db.avatars.find().skip(skip).limit(limit)
    async for document in cursor:
        avatars.append(AvatarDB(**document))
    
    return avatars

async def get_avatar(
    db: Any, 
    avatar_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[AvatarDB]:
    """
    Get an avatar by ID (all users can view avatars)
    """
    if not current_user:
        return None
        
    # Always use string representation for MongoDB query
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if avatar:
        return AvatarDB(**avatar)
    return None

async def create_avatar(
    db: Any, 
    avatar: AvatarCreate, 
    created_by: UUID
) -> AvatarDB:
    """
    Create a new avatar (admin/superadmin only)
    """
    # Create AvatarDB model
    avatar_db = AvatarDB(
        **avatar.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    avatar_dict = avatar_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in avatar_dict:
        avatar_dict["_id"] = str(avatar_dict["_id"])
    
    # Store created_by as string
    if "created_by" in avatar_dict:
        avatar_dict["created_by"] = str(avatar_dict["created_by"])
    
    result = await db.avatars.insert_one(avatar_dict)
    created_avatar = await db.avatars.find_one({"_id": str(result.inserted_id)})
    
    return AvatarDB(**created_avatar)

async def update_avatar(
    db: Any, 
    avatar_id: UUID, 
    avatar_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[AvatarDB]:
    """
    Update an avatar with permission checks
    """
    # Get the avatar to update - use string representation
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update avatars they created
        if avatar.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update avatars they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update avatars
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update avatars"
        )
    
    # Add updated timestamp
    avatar_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.avatars.update_one(
        {"_id": str(avatar_id)},
        {"$set": avatar_updates}
    )
    
    updated_avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if updated_avatar:
        return AvatarDB(**updated_avatar)
    return None

async def delete_avatar(db: Any, avatar_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete an avatar with permission checks
    """
    # Get the avatar to delete - use string representation
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete avatars they created
        if avatar.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete avatars they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete avatars
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete avatars"
        )
    
    # Check if this avatar is being used in any avatar interactions - use string representation
    avatar_interactions_using_avatar = await db.avatar_interactions.find(
        {"avatars": str(avatar_id)}
    ).to_list(length=1)
    
    if avatar_interactions_using_avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete avatar as it is being used in one or more avatar interactions"
        )
    
    # Delete the avatar - use string representation
    result = await db.avatars.delete_one({"_id": str(avatar_id)})
    
    return result.deleted_count > 0

# Avatar API Endpoints
@router.get("/", response_model=List[AvatarResponse])
async def get_avatars_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all avatars (all users can view)
    """
    return await get_avatars(db, skip, limit, current_user)

@router.get("/{avatar_id}", response_model=AvatarResponse)
async def get_avatar_endpoint(
    avatar_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific avatar by ID
    """
    avatar = await get_avatar(db, avatar_id, current_user)
    if not avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return avatar

@router.post("/", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar_endpoint(
    avatar: AvatarCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create avatars
):
    """
    Create a new avatar (admin/superadmin only)
    """
    return await create_avatar(db, avatar, admin_user.id)

@router.put("/{avatar_id}", response_model=AvatarResponse)
async def update_avatar_endpoint(
    avatar_id: UUID,
    avatar_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update avatars
):
    """
    Update an avatar by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_avatar = await update_avatar(db, avatar_id, avatar_updates, admin_user.id)
    if not updated_avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return updated_avatar

@router.delete("/{avatar_id}", response_model=Dict[str, bool])
async def delete_avatar_endpoint(
    avatar_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete avatars
):
    """
    Delete an avatar by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_avatar(db, avatar_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    return {"success": True}