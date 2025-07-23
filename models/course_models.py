from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from models.modules_models import ModuleDB, ModuleResponse
from models.user_models import UserRole

# Company Hierarchy Visibility Enum
class ContentVisibility(str, Enum):
    """
    Content Visibility Rules:
    
    CREATOR_ONLY: 
    - Only the creator (admin/superadmin) can assign this content
    - DEFAULT for all new content
    - Most restrictive setting
    
    COMPANY_WIDE: 
    - All admins/superadmins in the SAME company can assign this content
    - Creator can toggle this ON to share with company colleagues
    - Only applies within the same company
    
    Note: MOTHER company content is automatically accessible to ALL companies
    regardless of visibility setting - this is enforced in access control logic
    """
    CREATOR_ONLY = "creator_only"    # DEFAULT - Only creator can assign
    COMPANY_WIDE = "company_wide"    # All company admins can assign

# Course Models
class ContentStatus(str, Enum):
    ARCHIVED = "Archived"
    ACTIVE = "Active"
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_published: bool = False
    thumbnail_url: str

class CourseCreate(CourseBase):
    modules: Optional[List[UUID]] = Field(default_factory=list)
    # Company will be auto-filled from creator's company
    # Visibility defaults to CREATOR_ONLY

class CourseDB(CourseBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    modules: List[Union[UUID, ModuleDB]] = Field(default_factory=list)
    
    # Creator information
    creater_role: UserRole
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Company hierarchy fields
    company_id: UUID                                          # Which company owns this course
    visibility: ContentVisibility = ContentVisibility.CREATOR_ONLY  # Who can assign this course
    
    # Soft deletion for assignment history
    is_archived: bool = False                                 # Soft delete - keep for history
    archived_at: Optional[datetime] = None                   # When was it archived
    archived_by: Optional[UUID] = None                       # Who archived it
    archived_reason: Optional[str] = None                    # Why was it archived
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

class CourseResponse(CourseBase):
    id: UUID
    modules: List[UUID]
    creater_role: UserRole
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    # Company hierarchy fields
    company_id: UUID
    visibility: ContentVisibility
    
    # Archive status
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}
        
class CourseWithModulesResponse(CourseBase):
    id: UUID
    modules: List[ModuleResponse]
    creater_role: UserRole
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    # Company hierarchy fields
    company_id: UUID
    visibility: ContentVisibility
    
    # Archive status
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

class CourseWithAssignmentResponse(CourseResponse):
    """Course response model with assignment data"""
    assigned_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    
    # Assignment context information
    assigned_by_company: Optional[UUID] = None    # Which company assigned this
    assignment_context: Optional[str] = None     # "internal" or "cross_company"
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Course update model
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    visibility: Optional[ContentVisibility] = None
    
    # Archive operations
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = None