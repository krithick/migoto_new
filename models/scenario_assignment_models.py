from typing import Optional, Dict, List
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class ScenarioModeType(str, Enum):
    LEARN_MODE = "learn_mode"
    TRY_MODE = "try_mode"
    ASSESS_MODE = "assess_mode"

class ModeModeProgress(BaseModel):
    completed: bool = False
    completed_date: Optional[datetime] = None

# Base model with common fields
class ScenarioAssignmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    module_id: UUID
    scenario_id: UUID
    assigned_date: datetime = Field(default_factory=datetime.now)
    assigned_modes: List[ScenarioModeType] = Field(default_factory=list)
    completed: bool = False
    completed_date: Optional[datetime] = None
    mode_progress: Dict[ScenarioModeType, ModeModeProgress] = Field(default_factory=dict)
    
    @validator('assigned_modes')
    def validate_assigned_modes(cls, v):
        """Validate that assigned modes are valid ScenarioModeType values"""
        if not all(isinstance(mode, ScenarioModeType) for mode in v):
            raise ValueError("All assigned modes must be valid ScenarioModeType values")
        return v

# Create model (used when creating a new assignment)
class ScenarioAssignmentCreate(ScenarioAssignmentBase):
    # Company context will be auto-filled during assignment creation
    pass

# Database model (returned when reading from DB)
class ScenarioAssignmentDB(ScenarioAssignmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    # Company hierarchy context - tracks assignment flow
    assigned_by_company: UUID                    # Which company's admin made this assignment
    source_company: UUID                        # Which company owns the scenario being assigned
    assignment_context: str                     # "internal" or "cross_company"
    
    # Assignment tracking
    assigned_by: UUID                           # Which admin/superadmin made the assignment
    
    # Soft deletion for assignment history
    is_archived: bool = False                   # When assignment is "removed" but kept for history
    archived_at: Optional[datetime] = None     # When was assignment archived
    archived_by: Optional[UUID] = None         # Who archived the assignment
    archived_reason: Optional[str] = None      # Why was assignment removed
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

# Mode update model
class ModeProgressUpdate(BaseModel):
    completed: bool
    completed_date: Optional[datetime] = None

# Update model (used when updating an existing assignment)
class ScenarioAssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None
    assigned_modes: Optional[List[ScenarioModeType]] = None
    mode_progress: Optional[Dict[ScenarioModeType, ModeProgressUpdate]] = None
    
    # Archive operations
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = None
    
    @validator('assigned_modes')
    def validate_assigned_modes(cls, v):
        """Validate that assigned modes are valid ScenarioModeType values"""
        if v is not None and not all(isinstance(mode, ScenarioModeType) for mode in v):
            raise ValueError("All assigned modes must be valid ScenarioModeType values")
        return v

# Response model (returned by API)
class ScenarioAssignmentResponse(ScenarioAssignmentBase):
    id: UUID
    
    # Company context for transparency
    assigned_by_company: UUID
    source_company: UUID
    assignment_context: str
    assigned_by: UUID
    info: Optional[Dict[str, str]] = None  # Additional scenario details if needed
    # Archive status
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Bulk assignment model
class BulkScenarioAssignmentCreate(BaseModel):
    user_id: UUID
    module_id: UUID
    course_id: UUID
    scenario_ids: list[UUID]
    assigned_modes: Optional[Dict[UUID, List[ScenarioModeType]]] = None
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    # Company context will be auto-filled during bulk assignment
    
    @validator('operation')
    def validate_operation(cls, v):
        if v not in ['add', 'remove']:
            raise ValueError("Operation must be either 'add' or 'remove'")
        return v
    
    class Config:
        json_encoders = {UUID: str}

# Assignment context helper enum
class AssignmentContext:
    """
    Assignment Context Rules:
    
    INTERNAL: 
    - Admin assigns scenario from their own company to their users
    - source_company == assigned_by_company
    - Most common scenario
    
    CROSS_COMPANY:
    - Admin assigns MOTHER company scenario to their users
    - source_company (MOTHER) != assigned_by_company (CLIENT/SUBSIDIARY)
    - Enabled by company hierarchy rules
    
    Usage in assignment creation:
    if source_scenario.company_id == assigning_admin.company_id:
        assignment_context = "internal"
    else:
        assignment_context = "cross_company"
    """
    INTERNAL = "internal"
    CROSS_COMPANY = "cross_company"