# from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from datetime import datetime

# from models_new import (
#     EnvironmentBase, EnvironmentCreate, EnvironmentResponse, EnvironmentDB,
#      UserRole
# )
# from user_models import UserDB

# # from main import get_db
# from user import get_current_user, get_admin_user, get_superadmin_user

# # Create router
# router = APIRouter(prefix="/environments", tags=["Environments"])

# # Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     from database import get_db  # Import your existing function
#     return await get_db()

# # Environment Any Operations
# async def get_environments(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[EnvironmentDB]:
#     """
#     Get a list of all environments.
#     - All users can view environments
#     """
#     if not current_user:
#         return []
    
#     environments = []
#     cursor = db.environments.find().skip(skip).limit(limit)
#     async for document in cursor:
#         environments.append(EnvironmentDB(**document))
    
#     return environments

# async def get_environment(
#     db: Any, 
#     environment_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[EnvironmentDB]:
#     """
#     Get an environment by ID (all users can view environments)
#     """
#     if not current_user:
#         return None
        
#     environment = await db.environments.find_one({"_id": environment_id})
#     if environment:
#         return EnvironmentDB(**environment)
#     return None

# async def search_environments(
#     db: Any, 
#     name_query: str,
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[EnvironmentDB]:
#     """
#     Search environments by name
#     """
#     if not current_user:
#         return []
    
#     environments = []
#     # Case-insensitive search with regex
#     cursor = db.environments.find({"name": {"$regex": name_query, "$options": "i"}}).skip(skip).limit(limit)
#     async for document in cursor:
#         environments.append(EnvironmentDB(**document))
    
#     return environments

# async def create_environment(
#     db: Any, 
#     environment: EnvironmentCreate, 
#     created_by: UUID
# ) -> EnvironmentDB:
#     """
#     Create a new environment (admin/superadmin only)
#     """
#     # Create EnvironmentDB model
#     environment_db = EnvironmentDB(
#         **environment.dict(),
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Insert into database
#     environment_dict = environment_db.dict(by_alias=True)
#     if environment_dict.get("_id") is None:
#         environment_dict.pop("_id", None)
#     else:
#         environment_dict["_id"] = UUID(str(environment_dict["_id"]))
    
#     result = await db.environments.insert_one(environment_dict)
#     created_environment = await db.environments.find_one({"_id": result.inserted_id})
    
#     return EnvironmentDB(**created_environment)

# async def update_environment(
#     db: Any, 
#     environment_id: UUID, 
#     environment_updates: Dict[str, Any], 
#     updated_by: UUID
# ) -> Optional[EnvironmentDB]:
#     """
#     Update an environment with permission checks
#     """
#     # Get the environment to update
#     environment = await db.environments.find_one({"_id": environment_id})
#     if not environment:
#         return None
    
#     # Get the user making the update
#     updater = await db.users.find_one({"_id": updated_by})
#     if not updater:
#         return None
    
#     # Convert updater to UserDB for role checking
#     updater = UserDB(**updater)
    
#     # Check permissions
#     if updater.role == UserRole.ADMIN:
#         # Admin can only update environments they created
#         if environment.get("created_by") != updated_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only update environments they created"
#             )
#     elif updater.role != UserRole.SUPERADMIN:
#         # Regular users cannot update environments
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update environments"
#         )
    
#     # Add updated timestamp
#     environment_updates["updated_at"] = datetime.now()
    
#     # Update in database
#     await db.environments.update_one(
#         {"_id": environment_id},
#         {"$set": environment_updates}
#     )
    
#     updated_environment = await db.environments.find_one({"_id": environment_id})
#     if updated_environment:
#         return EnvironmentDB(**updated_environment)
#     return None

# async def delete_environment(db: Any, environment_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete an environment with permission checks
#     """
#     # Get the environment to delete
#     environment = await db.environments.find_one({"_id": environment_id})
#     if not environment:
#         return False
    
#     # Get the user making the deletion
#     deleter = await db.users.find_one({"_id": deleted_by})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete environments they created
#         if environment.get("created_by") != deleted_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete environments they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete environments
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete environments"
#         )
    
#     # Check if this environment is being used in any avatar interactions
#     avatar_interactions_using_environment = await db.avatar_interactions.find(
#         {"environments": environment_id}
#     ).to_list(length=1)
    
#     if avatar_interactions_using_environment:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete environment as it is being used in one or more avatar interactions"
#         )
    
#     # Delete the environment
#     result = await db.environments.delete_one({"_id": environment_id})
    
#     return result.deleted_count > 0

# # Environment API Endpoints
# @router.get("/", response_model=List[EnvironmentResponse])
# async def get_environments_endpoint(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all environments (all users can view)
#     """
#     return await get_environments(db, skip, limit, current_user)

# @router.get("/search", response_model=List[EnvironmentResponse])
# async def search_environments_endpoint(
#     query: str = Query(..., description="Name search query"),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Search environments by name
#     """
#     return await search_environments(db, query, skip, limit, current_user)

# @router.get("/{environment_id}", response_model=EnvironmentResponse)
# async def get_environment_endpoint(
#     environment_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific environment by ID
#     """
#     environment = await get_environment(db, environment_id, current_user)
#     if not environment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
#     return environment

# @router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
# async def create_environment_endpoint(
#     environment: EnvironmentCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create environments
# ):
#     """
#     Create a new environment (admin/superadmin only)
#     """
#     return await create_environment(db, environment, admin_user.id)

# @router.put("/{environment_id}", response_model=EnvironmentResponse)
# async def update_environment_endpoint(
#     environment_id: UUID,
#     environment_updates: Dict[str, Any] = Body(...),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update environments
# ):
#     """
#     Update an environment by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     updated_environment = await update_environment(db, environment_id, environment_updates, admin_user.id)
#     if not updated_environment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
#     return updated_environment

# @router.delete("/{environment_id}", response_model=Dict[str, bool])
# async def delete_environment_endpoint(
#     environment_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete environments
# ):
#     """
#     Delete an environment by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_environment(db, environment_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
#     return {"success": True}
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models_new import (
    EnvironmentBase, EnvironmentCreate, EnvironmentResponse, EnvironmentDB,
     UserRole
)
from user_models import UserDB

# from main import get_db
from user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/environments", tags=["Environments"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Environment Any Operations
async def get_environments(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[EnvironmentDB]:
    """
    Get a list of all environments.
    - All users can view environments
    """
    if not current_user:
        return []
    
    environments = []
    cursor = db.environments.find().skip(skip).limit(limit)
    async for document in cursor:
        environments.append(EnvironmentDB(**document))
    
    return environments

async def get_environment(
    db: Any, 
    environment_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[EnvironmentDB]:
    """
    Get an environment by ID (all users can view environments)
    """
    if not current_user:
        return None
        
    # Always use string representation for MongoDB query
    environment = await db.environments.find_one({"_id": str(environment_id)})
    if environment:
        return EnvironmentDB(**environment)
    return None

async def search_environments(
    db: Any, 
    name_query: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[EnvironmentDB]:
    """
    Search environments by name
    """
    if not current_user:
        return []
    
    environments = []
    # Case-insensitive search with regex
    cursor = db.environments.find({"name": {"$regex": name_query, "$options": "i"}}).skip(skip).limit(limit)
    async for document in cursor:
        environments.append(EnvironmentDB(**document))
    
    return environments

async def create_environment(
    db: Any, 
    environment: EnvironmentCreate, 
    created_by: UUID
) -> EnvironmentDB:
    """
    Create a new environment (admin/superadmin only)
    """
    # Create EnvironmentDB model
    environment_db = EnvironmentDB(
        **environment.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    environment_dict = environment_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in environment_dict:
        environment_dict["_id"] = str(environment_dict["_id"])
    
    # Store created_by as string
    if "created_by" in environment_dict:
        environment_dict["created_by"] = str(environment_dict["created_by"])
    
    result = await db.environments.insert_one(environment_dict)
    created_environment = await db.environments.find_one({"_id": str(result.inserted_id)})
    
    return EnvironmentDB(**created_environment)

async def update_environment(
    db: Any, 
    environment_id: UUID, 
    environment_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[EnvironmentDB]:
    """
    Update an environment with permission checks
    """
    # Get the environment to update - use string representation
    environment = await db.environments.find_one({"_id": str(environment_id)})
    if not environment:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update environments they created
        if environment.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update environments they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update environments
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update environments"
        )
    
    # Add updated timestamp
    environment_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.environments.update_one(
        {"_id": str(environment_id)},
        {"$set": environment_updates}
    )
    
    updated_environment = await db.environments.find_one({"_id": str(environment_id)})
    if updated_environment:
        return EnvironmentDB(**updated_environment)
    return None

async def delete_environment(db: Any, environment_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete an environment with permission checks
    """
    # Get the environment to delete - use string representation
    environment = await db.environments.find_one({"_id": str(environment_id)})
    if not environment:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete environments they created
        if environment.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete environments they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete environments
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete environments"
        )
    
    # Check if this environment is being used in any avatar interactions - use string representation
    avatar_interactions_using_environment = await db.avatar_interactions.find(
        {"environments": str(environment_id)}
    ).to_list(length=1)
    
    if avatar_interactions_using_environment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete environment as it is being used in one or more avatar interactions"
        )
    
    # Delete the environment - use string representation
    result = await db.environments.delete_one({"_id": str(environment_id)})
    
    return result.deleted_count > 0

# Environment API Endpoints
@router.get("/", response_model=List[EnvironmentResponse])
async def get_environments_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all environments (all users can view)
    """
    return await get_environments(db, skip, limit, current_user)

@router.get("/search", response_model=List[EnvironmentResponse])
async def search_environments_endpoint(
    query: str = Query(..., description="Name search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Search environments by name
    """
    return await search_environments(db, query, skip, limit, current_user)

@router.get("/{environment_id}", response_model=EnvironmentResponse)
async def get_environment_endpoint(
    environment_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific environment by ID
    """
    environment = await get_environment(db, environment_id, current_user)
    if not environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    return environment

@router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment_endpoint(
    environment: EnvironmentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create environments
):
    """
    Create a new environment (admin/superadmin only)
    """
    return await create_environment(db, environment, admin_user.id)

@router.put("/{environment_id}", response_model=EnvironmentResponse)
async def update_environment_endpoint(
    environment_id: UUID,
    environment_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update environments
):
    """
    Update an environment by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_environment = await update_environment(db, environment_id, environment_updates, admin_user.id)
    if not updated_environment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    return updated_environment

@router.delete("/{environment_id}", response_model=Dict[str, bool])
async def delete_environment_endpoint(
    environment_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete environments
):
    """
    Delete an environment by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_environment(db, environment_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found")
    return {"success": True}