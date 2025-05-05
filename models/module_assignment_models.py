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
    pass

# Database model (returned when reading from DB)
class ModuleAssignmentDB(ModuleAssignmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

# Update model (used when updating an existing assignment)
class ModuleAssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None
    
    # Add future update fields here as needed
    # progress_percentage: Optional[float] = None

# Response model (returned by API)
class ModuleAssignmentResponse(ModuleAssignmentBase):
    id: UUID
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Bulk assignment model
class BulkModuleAssignmentCreate(BaseModel):
    user_id: UUID
    course_id: UUID
    module_ids: list[UUID]
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    class Config:
        json_encoders = {UUID: str}