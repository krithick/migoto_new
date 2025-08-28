from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models.avatar_models import  AvatarBase, AvatarCreate, AvatarResponse, AvatarDB , AvatarGLBFile ,AvatarSelectedComponent
from models.user_models import UserDB ,UserRole

from core.user import get_current_user, get_admin_user, get_superadmin_user

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
    created_by: UUID,
    role:UserRole
) -> AvatarDB:
    """Create a new avatar"""
    # Create AvatarDB model
    avatar_db = AvatarDB(
        **avatar.dict(),
        created_by=created_by,
        creater_role=role,
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
    
    # for "persona_id" in avatar    
    if "persona_id" in avatar_dict and avatar_dict["persona_id"]:
        avatar_dict["persona_id"] = [str(persona_id) for persona_id in avatar_dict["persona_id"]]
    
    # Handle GLB files
    if "glb" in avatar_dict and avatar_dict["glb"]:
        # Check if we need to convert to dict
        if hasattr(avatar_dict["glb"][0], 'dict'):
            # These are Pydantic objects, convert to dict
            avatar_dict["glb"] = [glb_file.dict() for glb_file in avatar_dict["glb"]]
    
    # Handle selected components
    if "selected" in avatar_dict and avatar_dict["selected"]:
        # Check if we need to convert to dict
        if hasattr(avatar_dict["selected"][0], 'dict'):
            # These are Pydantic objects, convert to dict
            avatar_dict["selected"] = [comp.dict() for comp in avatar_dict["selected"]]
    
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
    Update an avatar with 3D model information
    """
    # Get the avatar to update
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        return None
    
    # Get the user making the update
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions
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
    
    # Convert persona_id to string list if present
    if "persona_id" in avatar_updates and avatar_updates["persona_id"]:
        avatar_updates["persona_id"] = [str(persona_id) for persona_id in avatar_updates["persona_id"]]
    
    # Update in database
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
    limit: int = Query(100, ge=1, le=10000),
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
    return await create_avatar(db, avatar, admin_user.id,admin_user.role)

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



@router.put("/{avatar_id}/model-files", response_model=AvatarResponse)
async def update_avatar_model_files(
    avatar_id: UUID,
    fbx: Optional[str] = Body(None),
    animation: Optional[str] = Body(None),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Update avatar model files (FBX, Animation)
    """
    # Get the avatar
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Prepare update data
    update_data = {}
    if fbx is not None:
        update_data["fbx"] = fbx
    if animation is not None:
        update_data["animation"] = animation
    
    # Update the avatar
    if update_data:
        update_data["updated_at"] = datetime.now()
        await db.avatars.update_one(
            {"_id": str(avatar_id)},
            {"$set": update_data}
        )
    
    # Return updated avatar
    updated_avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    return AvatarDB(**updated_avatar)

@router.post("/{avatar_id}/glb", response_model=AvatarResponse)
async def add_glb_file(
    avatar_id: UUID,
    glb_file: AvatarGLBFile,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Add a GLB file to an avatar
    """
    # Get the avatar
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Check if GLB with same name already exists
    glb_files = avatar.get("glb", [])
    for glb in glb_files:
        if glb.get("name") == glb_file.name:
            raise HTTPException(status_code=400, detail=f"GLB file with name '{glb_file.name}' already exists")
    
    # Add the GLB file
    await db.avatars.update_one(
        {"_id": str(avatar_id)},
        {
            "$push": {"glb": glb_file.dict()},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    # Return updated avatar
    updated_avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    return AvatarDB(**updated_avatar)


@router.put("/{avatar_id}/selected", response_model=AvatarResponse)
async def update_selected_components(
    avatar_id: UUID,
    selected: List[AvatarSelectedComponent],
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Update selected components for an avatar
    """
    # Get the avatar
    avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Convert selected components to dict
    selected_dict = [comp.dict() for comp in selected]
    
    # Update selected components
    await db.avatars.update_one(
        {"_id": str(avatar_id)},
        {
            "$set": {
                "selected": selected_dict,
                "updated_at": datetime.now()
            }
        }
    )
    
    # Return updated avatar
    updated_avatar = await db.avatars.find_one({"_id": str(avatar_id)})
    return AvatarDB(**updated_avatar)