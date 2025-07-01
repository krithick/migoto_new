from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator, model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from models.scenario_assignment_models import ScenarioModeType
from models.mode_modules import (
    LearnModeCreate, TryModeCreate, AssessModeCreate,
    LearnModeDB, TryModeDB, AssessModeDB,
    LearnModeResponse, TryModeResponse, AssessModeResponse
)
from models.user_models import UserRole

# Import ContentVisibility to maintain consistency
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

# Scenario Models
class ScenarioBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url: str
    learn_mode: LearnModeCreate 
    try_mode: TryModeCreate 
    assess_mode: AssessModeCreate 
    template_id: Optional[str]
class ScenarioCreate(ScenarioBase):
    # Company will be auto-filled from creator's company
    # Visibility defaults to CREATOR_ONLY
    pass

class ScenarioDB(ScenarioBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    learn_mode: LearnModeDB 
    try_mode: TryModeDB 
    assess_mode: AssessModeDB 
    
    # Creator information
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Company hierarchy fields
    company_id: UUID                                          # Which company owns this scenario
    visibility: ContentVisibility = ContentVisibility.CREATOR_ONLY  # Who can assign this scenario
    
    # Soft deletion for assignment history
    is_archived: bool = False                                 # Soft delete - keep for history
    archived_at: Optional[datetime] = None                   # When was it archived
    archived_by: Optional[UUID] = None                       # Who archived it
    archived_reason: Optional[str] = None                    # Why was it archived
    
    @model_validator(mode='after')
    def check_at_least_one_mode(self) -> 'ScenarioDB':
        # Access attributes directly instead of using .get()
        if not all([self.learn_mode, self.try_mode, self.assess_mode]):
            raise ValueError("At least one mode (learn, try, or assess) must be provided")
        return self    
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

class ScenarioResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    learn_mode: LearnModeResponse
    try_mode: TryModeResponse
    assess_mode: AssessModeResponse
    thumbnail_url: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    template_id: Optional[str]
    # Company hierarchy fields
    company_id: UUID
    visibility: ContentVisibility
    
    # Archive status
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

class ScenarioWithAssignmentResponse(ScenarioResponse):
    """Scenario response model with assignment data"""
    assigned_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    assigned_modes: List[ScenarioModeType] = None
    
    # Assignment context information
    assigned_by_company: Optional[UUID] = None    # Which company assigned this
    assignment_context: Optional[str] = None     # "internal" or "cross_company"
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Scenario update model
class ScenarioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    learn_mode: Optional[LearnModeCreate] = None
    try_mode: Optional[TryModeCreate] = None
    assess_mode: Optional[AssessModeCreate] = None
    visibility: Optional[ContentVisibility] = None
    
    # Archive operations
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = None