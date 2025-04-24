# from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from datetime import datetime

# from models_new import (
#     VideoBase, VideoCreate, VideoResponse, VideoDB,
#      UserRole
# )
# from user_models import UserDB

# # from main import get_db
# from user import get_current_user, get_admin_user, get_superadmin_user

# # Create router
# router = APIRouter(prefix="/videos", tags=["Videos"])

# # Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     from database import get_db  # Import your existing function
#     return await get_db()


# # Video Any Operations
# async def get_videos(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[VideoDB]:
#     """
#     Get a list of all videos.
#     - All users can view videos
#     """
#     if not current_user:
#         return []
    
#     videos = []
#     cursor = db.videos.find().skip(skip).limit(limit)
#     async for document in cursor:
#         videos.append(VideoDB(**document))
    
#     return videos

# async def get_video(
#     db: Any, 
#     video_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[VideoDB]:
#     """
#     Get a video by ID (all users can view videos)
#     """
#     if not current_user:
#         return None
        
#     video = await db.videos.find_one({"_id": video_id})
#     if video:
#         return VideoDB(**video)
#     return None

# async def search_videos(
#     db: Any, 
#     title_query: str,
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[VideoDB]:
#     """
#     Search videos by title
#     """
#     if not current_user:
#         return []
    
#     videos = []
#     # Case-insensitive search with regex
#     cursor = db.videos.find({"title": {"$regex": title_query, "$options": "i"}}).skip(skip).limit(limit)
#     async for document in cursor:
#         videos.append(VideoDB(**document))
    
#     return videos

# async def create_video(
#     db: Any, 
#     video: VideoCreate, 
#     created_by: UUID
# ) -> VideoDB:
#     """
#     Create a new video (admin/superadmin only)
#     """
#     # Create VideoDB model
#     video_db = VideoDB(
#         **video.dict(),
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Insert into database
#     video_dict = video_db.dict(by_alias=True)
#     if video_dict.get("_id") is None:
#         video_dict.pop("_id", None)
#     else:
#         video_dict["_id"] = UUID(str(video_dict["_id"]))
    
#     result = await db.videos.insert_one(video_dict)
#     created_video = await db.videos.find_one({"_id": result.inserted_id})
    
#     return VideoDB(**created_video)

# async def update_video(
#     db: Any, 
#     video_id: UUID, 
#     video_updates: Dict[str, Any], 
#     updated_by: UUID
# ) -> Optional[VideoDB]:
#     """
#     Update a video with permission checks
#     """
#     # Get the video to update
#     video = await db.videos.find_one({"_id": video_id})
#     if not video:
#         return None
    
#     # Get the user making the update
#     updater = await db.users.find_one({"_id": updated_by})
#     if not updater:
#         return None
    
#     # Convert updater to UserDB for role checking
#     updater = UserDB(**updater)
    
#     # Check permissions
#     if updater.role == UserRole.ADMIN:
#         # Admin can only update videos they created
#         if video.get("created_by") != updated_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only update videos they created"
#             )
#     elif updater.role != UserRole.SUPERADMIN:
#         # Regular users cannot update videos
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update videos"
#         )
    
#     # Add updated timestamp
#     video_updates["updated_at"] = datetime.now()
    
#     # Update in database
#     await db.videos.update_one(
#         {"_id": video_id},
#         {"$set": video_updates}
#     )
    
#     updated_video = await db.videos.find_one({"_id": video_id})
#     if updated_video:
#         return VideoDB(**updated_video)
#     return None

# async def delete_video(db: Any, video_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete a video with permission checks
#     """
#     # Get the video to delete
#     video = await db.videos.find_one({"_id": video_id})
#     if not video:
#         return False
    
#     # Get the user making the deletion
#     deleter = await db.users.find_one({"_id": deleted_by})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete videos they created
#         if video.get("created_by") != deleted_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete videos they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete videos
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete videos"
#         )
    
#     # Check if this video is being used in any scenarios
#     scenarios_using_video = await db.scenarios.find(
#         {"try_mode.videos": video_id}
#     ).to_list(length=1)
    
#     if scenarios_using_video:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete video as it is being used in one or more scenarios"
#         )
    
#     # Delete the video
#     result = await db.videos.delete_one({"_id": video_id})
    
#     return result.deleted_count > 0

# # Video API Endpoints
# @router.get("/", response_model=List[VideoResponse])
# async def get_videos_endpoint(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all videos (all users can view)
#     """
#     return await get_videos(db, skip, limit, current_user)

# @router.get("/search", response_model=List[VideoResponse])
# async def search_videos_endpoint(
#     query: str = Query(..., description="Title search query"),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Search videos by title
#     """
#     return await search_videos(db, query, skip, limit, current_user)

# @router.get("/{video_id}", response_model=VideoResponse)
# async def get_video_endpoint(
#     video_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific video by ID
#     """
#     video = await get_video(db, video_id, current_user)
#     if not video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
#     return video

# @router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
# async def create_video_endpoint(
#     video: VideoCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create videos
# ):
#     """
#     Create a new video (admin/superadmin only)
#     """
#     return await create_video(db, video, admin_user.id)

# @router.put("/{video_id}", response_model=VideoResponse)
# async def update_video_endpoint(
#     video_id: UUID,
#     video_updates: Dict[str, Any] = Body(...),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update videos
# ):
#     """
#     Update a video by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     updated_video = await update_video(db, video_id, video_updates, admin_user.id)
#     if not updated_video:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
#     return updated_video

# @router.delete("/{video_id}", response_model=Dict[str, bool])
# async def delete_video_endpoint(
#     video_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete videos
# ):
#     """
#     Delete a video by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_video(db, video_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
#     return {"success": True}

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models_new import (
    VideoBase, VideoCreate, VideoResponse, VideoDB,
     UserRole
)
from user_models import UserDB

from user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/videos", tags=["Videos"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()


# Video Any Operations
async def get_videos(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[VideoDB]:
    """
    Get a list of all videos.
    - All users can view videos
    """
    if not current_user:
        return []
    
    videos = []
    cursor = db.videos.find().skip(skip).limit(limit)
    async for document in cursor:
        videos.append(VideoDB(**document))
    
    return videos

async def get_video(
    db: Any, 
    video_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[VideoDB]:
    """
    Get a video by ID (all users can view videos)
    """
    if not current_user:
        return None
        
    # Use string representation for MongoDB query
    video = await db.videos.find_one({"_id": str(video_id)})
    if video:
        return VideoDB(**video)
    return None

async def search_videos(
    db: Any, 
    title_query: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[VideoDB]:
    """
    Search videos by title
    """
    if not current_user:
        return []
    
    videos = []
    # Case-insensitive search with regex
    cursor = db.videos.find({"title": {"$regex": title_query, "$options": "i"}}).skip(skip).limit(limit)
    async for document in cursor:
        videos.append(VideoDB(**document))
    
    return videos

async def create_video(
    db: Any, 
    video: VideoCreate, 
    created_by: UUID
) -> VideoDB:
    """
    Create a new video (admin/superadmin only)
    """
    # Create VideoDB model
    video_db = VideoDB(
        **video.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    video_dict = video_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in video_dict:
        video_dict["_id"] = str(video_dict["_id"])
    
    # Store created_by as string
    if "created_by" in video_dict:
        video_dict["created_by"] = str(video_dict["created_by"])
    
    result = await db.videos.insert_one(video_dict)
    created_video = await db.videos.find_one({"_id": str(result.inserted_id)})
    
    return VideoDB(**created_video)

async def update_video(
    db: Any, 
    video_id: UUID, 
    video_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[VideoDB]:
    """
    Update a video with permission checks
    """
    # Get the video to update - use string representation
    video = await db.videos.find_one({"_id": str(video_id)})
    if not video:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update videos they created
        if video.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update videos they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update videos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update videos"
        )
    
    # Add updated timestamp
    video_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.videos.update_one(
        {"_id": str(video_id)},
        {"$set": video_updates}
    )
    
    updated_video = await db.videos.find_one({"_id": str(video_id)})
    if updated_video:
        return VideoDB(**updated_video)
    return None

async def delete_video(db: Any, video_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a video with permission checks
    """
    # Get the video to delete - use string representation
    video = await db.videos.find_one({"_id": str(video_id)})
    if not video:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete videos they created
        if video.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete videos they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete videos
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete videos"
        )
    
    # Check if this video is being used in any scenarios - use string representation
    scenarios_using_video = await db.scenarios.find(
        {"try_mode.videos": str(video_id)}
    ).to_list(length=1)
    
    if scenarios_using_video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete video as it is being used in one or more scenarios"
        )
    
    # Delete the video - use string representation
    result = await db.videos.delete_one({"_id": str(video_id)})
    
    return result.deleted_count > 0

# Video API Endpoints
@router.get("/", response_model=List[VideoResponse])
async def get_videos_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all videos (all users can view)
    """
    return await get_videos(db, skip, limit, current_user)

@router.get("/search", response_model=List[VideoResponse])
async def search_videos_endpoint(
    query: str = Query(..., description="Title search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Search videos by title
    """
    return await search_videos(db, query, skip, limit, current_user)

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_endpoint(
    video_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific video by ID
    """
    video = await get_video(db, video_id, current_user)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video_endpoint(
    video: VideoCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create videos
):
    """
    Create a new video (admin/superadmin only)
    """
    return await create_video(db, video, admin_user.id)

@router.put("/{video_id}", response_model=VideoResponse)
async def update_video_endpoint(
    video_id: UUID,
    video_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update videos
):
    """
    Update a video by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_video = await update_video(db, video_id, video_updates, admin_user.id)
    if not updated_video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return updated_video

@router.delete("/{video_id}", response_model=Dict[str, bool])
async def delete_video_endpoint(
    video_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete videos
):
    """
    Delete a video by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_video(db, video_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return {"success": True}