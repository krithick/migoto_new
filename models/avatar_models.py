# models/avatar_models.py
from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, field_validator, validator, root_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

# Avatar Models
class AvatarGender(str, Enum):
    Male = "male"
    Female = "female"

class AvatarGLBFile(BaseModel):
    file: str  # GLB file link
    thumbnail: str  # Thumbnail link (PNG)
    name: str  # File name

class AvatarSelectedComponent(BaseModel):
    category: str  # Category name (body, shirt, pant, etc.)
    file_name: str  # Selected file name

class AvatarBase(BaseModel):
    name: str
    fbx: Optional[str] = None  # FBX file link
    animation: Optional[str] = None  # Animation file link (GLB)
    glb: List[AvatarGLBFile] = Field(default_factory=list)
    selected: List[AvatarSelectedComponent] = Field(default_factory=list)
    persona_id: List[UUID] = Field(default_factory=list)
    gender: AvatarGender
    thumbnail_url: Optional[str] = None
    animation: Optional[str] = None  # Animation file link (GLB)
    glb: List[AvatarGLBFile] = Field(default_factory=list)
    selected: List[AvatarSelectedComponent] = Field(default_factory=list)
    @field_validator('gender', mode='before')
    @classmethod
    def validate_mode(cls, v):
        allowed = [e.value for e in AvatarGender]
        if v not in allowed:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

class AvatarCreate(AvatarBase):
    pass

class AvatarDB(AvatarBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

class AvatarResponse(AvatarBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# New model for updating avatar files
class AvatarFileUpdate(BaseModel):
    fbx: Optional[str] = None
    animation: Optional[str] = None
    glb_files: Optional[List[AvatarGLBFile]] = None
    selected_components: Optional[List[AvatarSelectedComponent]] = None

# New model for adding a GLB file
class AddGLBFile(BaseModel):
    file: str
    thumbnail: str
    name: str

# New model for updating selected components
class UpdateSelectedComponents(BaseModel):
    selected: List[AvatarSelectedComponent]