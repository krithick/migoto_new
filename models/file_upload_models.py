# models/file_upload_models.py
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    MODEL = "model"  # For 3D models like FBX, GLB, etc.
    OTHER = "other"

class FileUploadBase(BaseModel):
    original_filename: str
    file_type: FileType
    mime_type: str
    file_size: int
    local_url: str  # URL for local development environment
    live_url: str   # URL for production environment
    description: Optional[str] = None
    
class FileUploadCreate(FileUploadBase):
    pass

class FileUploadDB(FileUploadBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

class FileUploadResponse(FileUploadBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}