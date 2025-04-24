# from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# from datetime import datetime

# from models_new import (
#     DocumentBase, DocumentCreate, DocumentResponse, DocumentDB,
#      UserRole
# )
# from user_models import UserDB

# # from main import get_db
# from user import get_current_user, get_admin_user, get_superadmin_user

# # Create router
# router = APIRouter(prefix="/documents", tags=["Documents"])

# # Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     from database import get_db  # Import your existing function
#     return await get_db()

# # Document Any Operations
# async def get_documents(
#     db: Any, 
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[DocumentDB]:
#     """
#     Get a list of all documents.
#     - All users can view documents
#     """
#     if not current_user:
#         return []
    
#     documents = []
#     cursor = db.documents.find().skip(skip).limit(limit)
#     async for document in cursor:
#         documents.append(DocumentDB(**document))
    
#     return documents

# async def get_document(
#     db: Any, 
#     document_id: UUID, 
#     current_user: Optional[UserDB] = None
# ) -> Optional[DocumentDB]:
#     """
#     Get a document by ID (all users can view documents)
#     """
#     if not current_user:
#         return None
        
#     document = await db.documents.find_one({"_id": document_id})
#     if document:
#         return DocumentDB(**document)
#     return None

# async def search_documents(
#     db: Any, 
#     title_query: str,
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[DocumentDB]:
#     """
#     Search documents by title
#     """
#     if not current_user:
#         return []
    
#     documents = []
#     # Case-insensitive search with regex
#     cursor = db.documents.find({"title": {"$regex": title_query, "$options": "i"}}).skip(skip).limit(limit)
#     async for document in cursor:
#         documents.append(DocumentDB(**document))
    
#     return documents

# async def get_documents_by_type(
#     db: Any, 
#     file_type: str,
#     skip: int = 0, 
#     limit: int = 100,
#     current_user: Optional[UserDB] = None
# ) -> List[DocumentDB]:
#     """
#     Get documents filtered by file type
#     """
#     if not current_user:
#         return []
    
#     documents = []
#     cursor = db.documents.find({"file_type": file_type}).skip(skip).limit(limit)
#     async for document in cursor:
#         documents.append(DocumentDB(**document))
    
#     return documents

# async def create_document(
#     db: Any, 
#     document: DocumentCreate, 
#     created_by: UUID
# ) -> DocumentDB:
#     """
#     Create a new document (admin/superadmin only)
#     """
#     # Create DocumentDB model
#     document_db = DocumentDB(
#         **document.dict(),
#         created_by=created_by,
#         created_at=datetime.now(),
#         updated_at=datetime.now()
#     )
    
#     # Insert into database
#     document_dict = document_db.dict(by_alias=True)
#     if document_dict.get("_id") is None:
#         document_dict.pop("_id", None)
#     else:
#         document_dict["_id"] = UUID(str(document_dict["_id"]))
    
#     result = await db.documents.insert_one(document_dict)
#     created_document = await db.documents.find_one({"_id": result.inserted_id})
    
#     return DocumentDB(**created_document)

# async def update_document(
#     db: Any, 
#     document_id: UUID, 
#     document_updates: Dict[str, Any], 
#     updated_by: UUID
# ) -> Optional[DocumentDB]:
#     """
#     Update a document with permission checks
#     """
#     # Get the document to update
#     document = await db.documents.find_one({"_id": document_id})
#     if not document:
#         return None
    
#     # Get the user making the update
#     updater = await db.users.find_one({"_id": updated_by})
#     if not updater:
#         return None
    
#     # Convert updater to UserDB for role checking
#     updater = UserDB(**updater)
    
#     # Check permissions
#     if updater.role == UserRole.ADMIN:
#         # Admin can only update documents they created
#         if document.get("created_by") != updated_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only update documents they created"
#             )
#     elif updater.role != UserRole.SUPERADMIN:
#         # Regular users cannot update documents
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update documents"
#         )
    
#     # Add updated timestamp
#     document_updates["updated_at"] = datetime.now()
    
#     # Update in database
#     await db.documents.update_one(
#         {"_id": document_id},
#         {"$set": document_updates}
#     )
    
#     updated_document = await db.documents.find_one({"_id": document_id})
#     if updated_document:
#         return DocumentDB(**updated_document)
#     return None

# async def delete_document(db: Any, document_id: UUID, deleted_by: UUID) -> bool:
#     """
#     Delete a document with permission checks
#     """
#     # Get the document to delete
#     document = await db.documents.find_one({"_id": document_id})
#     if not document:
#         return False
    
#     # Get the user making the deletion
#     deleter = await db.users.find_one({"_id": deleted_by})
#     if not deleter:
#         return False
    
#     # Convert deleter to UserDB for role checking
#     deleter = UserDB(**deleter)
    
#     # Check permissions
#     if deleter.role == UserRole.ADMIN:
#         # Admin can only delete documents they created
#         if document.get("created_by") != deleted_by:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admins can only delete documents they created"
#             )
#     elif deleter.role != UserRole.SUPERADMIN:
#         # Regular users cannot delete documents
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete documents"
#         )
    
#     # Check if this document is being used in any scenarios
#     scenarios_using_document = await db.scenarios.find(
#         {"try_mode.documents": document_id}
#     ).to_list(length=1)
    
#     if scenarios_using_document:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete document as it is being used in one or more scenarios"
#         )
    
#     # Delete the document
#     result = await db.documents.delete_one({"_id": document_id})
    
#     return result.deleted_count > 0

# # Document API Endpoints
# @router.get("/", response_model=List[DocumentResponse])
# async def get_documents_endpoint(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all documents (all users can view)
#     """
#     return await get_documents(db, skip, limit, current_user)

# @router.get("/search", response_model=List[DocumentResponse])
# async def search_documents_endpoint(
#     query: str = Query(..., description="Title search query"),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Search documents by title
#     """
#     return await search_documents(db, query, skip, limit, current_user)

# @router.get("/type/{file_type}", response_model=List[DocumentResponse])
# async def get_documents_by_type_endpoint(
#     file_type: str,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get documents filtered by file type
#     """
#     return await get_documents_by_type(db, file_type, skip, limit, current_user)

# @router.get("/{document_id}", response_model=DocumentResponse)
# async def get_document_endpoint(
#     document_id: UUID,
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a specific document by ID
#     """
#     document = await get_document(db, document_id, current_user)
#     if not document:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
#     return document

# @router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
# async def create_document_endpoint(
#     document: DocumentCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create documents
# ):
#     """
#     Create a new document (admin/superadmin only)
#     """
#     return await create_document(db, document, admin_user.id)

# @router.put("/{document_id}", response_model=DocumentResponse)
# async def update_document_endpoint(
#     document_id: UUID,
#     document_updates: Dict[str, Any] = Body(...),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update documents
# ):
#     """
#     Update a document by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     updated_document = await update_document(db, document_id, document_updates, admin_user.id)
#     if not updated_document:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
#     return updated_document

# @router.delete("/{document_id}", response_model=Dict[str, bool])
# async def delete_document_endpoint(
#     document_id: UUID,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete documents
# ):
#     """
#     Delete a document by ID (admin/superadmin only, with ownership checks for admins)
#     """
#     deleted = await delete_document(db, document_id, admin_user.id)
#     if not deleted:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
#     return {"success": True}
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models_new import (
    DocumentBase, DocumentCreate, DocumentResponse, DocumentDB,
     UserRole
)
from user_models import UserDB

from user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/documents", tags=["Documents"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Document Any Operations
async def get_documents(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[DocumentDB]:
    """
    Get a list of all documents.
    - All users can view documents
    """
    if not current_user:
        return []
    
    documents = []
    cursor = db.documents.find().skip(skip).limit(limit)
    async for document in cursor:
        documents.append(DocumentDB(**document))
    
    return documents

async def get_document(
    db: Any, 
    document_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[DocumentDB]:
    """
    Get a document by ID (all users can view documents)
    """
    if not current_user:
        return None
    
    # Use string representation for MongoDB query
    document = await db.documents.find_one({"_id": str(document_id)})
    if document:
        return DocumentDB(**document)
    return None

async def search_documents(
    db: Any, 
    title_query: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[DocumentDB]:
    """
    Search documents by title
    """
    if not current_user:
        return []
    
    documents = []
    # Case-insensitive search with regex
    cursor = db.documents.find({"title": {"$regex": title_query, "$options": "i"}}).skip(skip).limit(limit)
    async for document in cursor:
        documents.append(DocumentDB(**document))
    
    return documents

async def get_documents_by_type(
    db: Any, 
    file_type: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[DocumentDB]:
    """
    Get documents filtered by file type
    """
    if not current_user:
        return []
    
    documents = []
    cursor = db.documents.find({"file_type": file_type}).skip(skip).limit(limit)
    async for document in cursor:
        documents.append(DocumentDB(**document))
    
    return documents

async def create_document(
    db: Any, 
    document: DocumentCreate, 
    created_by: UUID
) -> DocumentDB:
    """
    Create a new document (admin/superadmin only)
    """
    # Create DocumentDB model
    document_db = DocumentDB(
        **document.dict(),
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    document_dict = document_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in document_dict:
        document_dict["_id"] = str(document_dict["_id"])
    
    # Store created_by as string
    if "created_by" in document_dict:
        document_dict["created_by"] = str(document_dict["created_by"])
    
    result = await db.documents.insert_one(document_dict)
    created_document = await db.documents.find_one({"_id": str(result.inserted_id)})
    
    return DocumentDB(**created_document)

async def update_document(
    db: Any, 
    document_id: UUID, 
    document_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[DocumentDB]:
    """
    Update a document with permission checks
    """
    # Get the document to update - use string representation
    document = await db.documents.find_one({"_id": str(document_id)})
    if not document:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update documents they created
        if document.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update documents they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update documents
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update documents"
        )
    
    # Add updated timestamp
    document_updates["updated_at"] = datetime.now()
    
    # Update in database - use string representation
    await db.documents.update_one(
        {"_id": str(document_id)},
        {"$set": document_updates}
    )
    
    updated_document = await db.documents.find_one({"_id": str(document_id)})
    if updated_document:
        return DocumentDB(**updated_document)
    return None

async def delete_document(db: Any, document_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a document with permission checks
    """
    # Get the document to delete - use string representation
    document = await db.documents.find_one({"_id": str(document_id)})
    if not document:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete documents they created
        if document.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete documents they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete documents
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete documents"
        )
    
    # Check if this document is being used in any scenarios - use string representation
    scenarios_using_document = await db.scenarios.find(
        {"try_mode.documents": str(document_id)}
    ).to_list(length=1)
    
    if scenarios_using_document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete document as it is being used in one or more scenarios"
        )
    
    # Delete the document - use string representation
    result = await db.documents.delete_one({"_id": str(document_id)})
    
    return result.deleted_count > 0

# Document API Endpoints
@router.get("/", response_model=List[DocumentResponse])
async def get_documents_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all documents (all users can view)
    """
    return await get_documents(db, skip, limit, current_user)

@router.get("/search", response_model=List[DocumentResponse])
async def search_documents_endpoint(
    query: str = Query(..., description="Title search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Search documents by title
    """
    return await search_documents(db, query, skip, limit, current_user)

@router.get("/type/{file_type}", response_model=List[DocumentResponse])
async def get_documents_by_type_endpoint(
    file_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get documents filtered by file type
    """
    return await get_documents_by_type(db, file_type, skip, limit, current_user)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_endpoint(
    document_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific document by ID
    """
    document = await get_document(db, document_id, current_user)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_endpoint(
    document: DocumentCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create documents
):
    """
    Create a new document (admin/superadmin only)
    """
    return await create_document(db, document, admin_user.id)

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document_endpoint(
    document_id: UUID,
    document_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update documents
):
    """
    Update a document by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_document = await update_document(db, document_id, document_updates, admin_user.id)
    if not updated_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return updated_document

@router.delete("/{document_id}", response_model=Dict[str, bool])
async def delete_document_endpoint(
    document_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete documents
):
    """
    Delete a document by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_document(db, document_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"success": True}