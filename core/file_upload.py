# core/file_upload.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Path, Query
from fastapi.responses import FileResponse
from typing import List, Optional , Any
from uuid import UUID, uuid4
import os
import mimetypes
import shutil
import aiofiles
from datetime import datetime

from models.user_models import UserDB
from models.file_upload_models import FileUploadCreate, FileUploadDB, FileUploadResponse, FileType
from core.user import get_current_user, get_admin_user, get_superadmin_user , UserRole
from services.file_storage import file_storage_service

# Create router
router = APIRouter(prefix="/uploads", tags=["File Uploads"])

# Configuration
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
LOCAL_URL_PREFIX = os.environ.get("LOCAL_URL_PREFIX", "http://localhost:9000/uploads")
LIVE_URL_PREFIX = os.environ.get("LIVE_URL_PREFIX", "https://meta.novactech.in:5885/uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
for file_type in FileType:
    os.makedirs(os.path.join(UPLOAD_DIR, file_type.value), exist_ok=True)

# Any dependency
async def get_database():
    from database import get_db
    return await get_db()

# File Upload Operations
async def upload_file(
    file: UploadFile,
    file_type: FileType,
    description: Optional[str],
    created_by: UUID,
    db: Any
) -> FileUploadDB:
    """Upload a file and save metadata to database"""
    try:
        # Save the file using the file storage service
        file_info = await file_storage_service.save_file(
            file=file,
            file_type=file_type.value,
            max_file_size=100 * 1024 * 1024  # 100MB
        )
        
        # Create database entry
        file_upload = FileUploadCreate(
            original_filename=file_info["original_filename"],
            file_type=file_type,
            mime_type=file_info["mime_type"],
            file_size=file_info["file_size"],
            local_url=file_info["local_url"],
            live_url=file_info["live_url"],
            description=description
        )
        
        file_upload_db = FileUploadDB(
            **file_upload.dict(),
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Insert into database
        file_dict = file_upload_db.dict(by_alias=True)
        
        # Convert UUIDs to strings for MongoDB
        if "_id" in file_dict:
            file_dict["_id"] = str(file_dict["_id"])
        if "created_by" in file_dict:
            file_dict["created_by"] = str(file_dict["created_by"])
        
        result = await db.file_uploads.insert_one(file_dict)
        created_file = await db.file_uploads.find_one({"_id": str(result.inserted_id)})
        
        return FileUploadDB(**created_file)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Wrap other exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
async def get_file_uploads(
    db: Any,
    file_type: Optional[FileType] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[FileUploadDB]:
    """Get a list of file uploads, optionally filtered by type"""
    if not current_user:
        return []
    
    # Build query
    query = {}
    if file_type:
        query["file_type"] = file_type.value
    
    # Regular users can only see their own uploads
    if current_user.role == UserRole.USER:
        query["created_by"] = str(current_user.id)
    
    # Execute query
    uploads = []
    cursor = db.file_uploads.find(query).skip(skip).limit(limit)
    async for document in cursor:
        uploads.append(FileUploadDB(**document))
    
    return uploads

async def get_file_upload(
    db: Any,
    file_id: UUID,
    current_user: Optional[UserDB] = None
) -> Optional[FileUploadDB]:
    """Get a file upload by ID"""
    if not current_user:
        return None
    
    # Build query
    query = {"_id": str(file_id)}
    
    # Regular users can only see their own uploads
    if current_user.role == UserRole.USER:
        query["created_by"] = str(current_user.id)
    
    # Execute query
    file_upload = await db.file_uploads.find_one(query)
    if file_upload:
        return FileUploadDB(**file_upload)
    
    return None

async def delete_file_upload(
    db: Any,
    file_id: UUID,
    deleted_by: UUID
) -> bool:
    """Delete a file upload"""
    # Get the file upload
    file_upload = await db.file_uploads.find_one({"_id": str(file_id)})
    if not file_upload:
        return False
    
    # Check permissions
    if file_upload.get("created_by") != str(deleted_by):
        user = await db.users.find_one({"_id": str(deleted_by)})
        if not user or user.get("role") not in [UserRole.ADMIN.value, UserRole.SUPERADMIN.value]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this file"
            )
    
    # Delete file from filesystem
    file_path = file_storage_service.get_file_path_from_url(file_upload.get("local_url"))
    if file_path:
        await file_storage_service.delete_file(file_path)
    
    # Delete from database
    result = await db.file_uploads.delete_one({"_id": str(file_id)})
    
    return result.deleted_count > 0
# File Upload API Endpoints
@router.post("/", response_model=FileUploadResponse, status_code=201)
async def upload_file_endpoint(
    file: UploadFile = File(...),
    file_type: FileType = Form(...),
    description: Optional[str] = Form(None),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Upload a file"""
    # TODO: Add validation for file types, sizes, etc.
    
    return await upload_file(file, file_type, description, current_user.id, db)

@router.get("/", response_model=List[FileUploadResponse])
async def get_file_uploads_endpoint(
    file_type: Optional[FileType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a list of file uploads"""
    return await get_file_uploads(db, file_type, skip, limit, current_user)

@router.get("/{file_id}", response_model=FileUploadResponse)
async def get_file_upload_endpoint(
    file_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a specific file upload by ID"""
    file_upload = await get_file_upload(db, file_id, current_user)
    if not file_upload:
        raise HTTPException(status_code=404, detail="File upload not found")
    
    return file_upload

@router.delete("/{file_id}", response_model=dict)
async def delete_file_upload_endpoint(
    file_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Delete a file upload"""
    deleted = await delete_file_upload(db, file_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="File upload not found")
    
    return {"success": True}


@router.get("/{file_type}/{filename}")
async def serve_uploaded_file(
    file_type: str,
    filename: str,
    db: Any = Depends(get_database),
    # current_user: UserDB = Depends(get_current_user)
):
    """Serve an uploaded file"""
    # Make sure this list includes "audio"
    if file_type not in ["document", "video", "image", "audio", "other"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check if file exists
    file_path = os.path.join(UPLOAD_DIR, file_type, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        if file_type == "audio":
            content_type = "audio/wav"
        else:
            content_type = "application/octet-stream"
    
    # Serve file
    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=filename
    )

@router.post("/bulk", response_model=List[FileUploadResponse])
async def upload_files_bulk(
    files: List[UploadFile] = File(...),
    file_type: FileType = Form(...),
    description: Optional[str] = Form(None),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Upload multiple files of the same type at once
    """
    # Initialize results list
    uploaded_files = []
    
    # Process each file
    for file in files:
        try:
            # Use the existing upload_file function for each file
            file_upload = await upload_file(
                file=file,
                file_type=file_type,
                description=description or f"Bulk upload: {file.filename}",
                created_by=current_user.id,
                db=db
            )
            
            uploaded_files.append(file_upload)
            
        except HTTPException as e:
            # Continue processing other files even if one fails
            # But add error information to the response
            uploaded_files.append({
                "filename": file.filename,
                "error": e.detail,
                "status_code": e.status_code
            })
        except Exception as e:
            # Handle unexpected errors
            uploaded_files.append({
                "filename": file.filename,
                "error": str(e),
                "status_code": 500
            })
    
    # Return all results
    return uploaded_files