from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

# Base model with common fields
class ModuleAssignmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    module_id: UUID
    assigned_date: datetime = Field(default_factory=datetime.now)
    completed: bool = False
    completed_date: Optional[datetime] = None
    
    # Add future fields here as needed
    # For example:
    # progress_percentage: Optional[float] = 0.0

# Create model (used when creating a new assignment)
class ModuleAssignmentCreate(ModuleAssignmentBase):
    # Company context will be auto-filled during assignment creation
    pass

# Database model (returned when reading from DB)
class ModuleAssignmentDB(ModuleAssignmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    # Company hierarchy context - tracks assignment flow
    assigned_by_company: UUID                    # Which company's admin made this assignment
    source_company: UUID                        # Which company owns the module being assigned
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

# Update model (used when updating an existing assignment)
class ModuleAssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None
    
    # Archive operations
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = None
    
    # Add future update fields here as needed
    # progress_percentage: Optional[float] = None

# Response model (returned by API)
class ModuleAssignmentResponse(ModuleAssignmentBase):
    id: UUID
    
    # Company context for transparency
    assigned_by_company: UUID
    source_company: UUID
    assignment_context: str
    assigned_by: UUID
    
    # Archive status
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Bulk assignment model
class BulkModuleAssignmentCreate(BaseModel):
    user_id: UUID
    course_id: UUID
    module_ids: list[UUID]
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    # Company context will be auto-filled during bulk assignment
    
    class Config:
        json_encoders = {UUID: str}

# Assignment context helper enum
class AssignmentContext:
    """
    Assignment Context Rules:
    
    INTERNAL: 
    - Admin assigns module from their own company to their users
    - source_company == assigned_by_company
    - Most common scenario
    
    CROSS_COMPANY:
    - Admin assigns MOTHER company module to their users
    - source_company (MOTHER) != assigned_by_company (CLIENT/SUBSIDIARY)
    - Enabled by company hierarchy rules
    
    Usage in assignment creation:
    if source_module.company_id == assigning_admin.company_id:
        assignment_context = "internal"
    else:
        assignment_context = "cross_company"
    """
    INTERNAL = "internal"
    CROSS_COMPANY = "cross_company"