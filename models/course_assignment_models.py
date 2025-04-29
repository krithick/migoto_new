from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

# Base model with common fields
class CourseAssignmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    completed: bool = False
    assigned_date: datetime = Field(default_factory=datetime.now)
    completed_date: Optional[datetime] = None
    
    # Add future fields here as needed (scores, certificates, etc.)
    # For example:
    # score: Optional[float] = None
    # passed: Optional[bool] = None
    # certificate_id: Optional[UUID] = None

# Create model (used when creating a new assignment)
class CourseAssignmentCreate(CourseAssignmentBase):
    pass

# Database model (returned when reading from DB)
class CourseAssignmentDB(CourseAssignmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}

# Update model (used when updating an existing assignment)
class CourseAssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None
    
    # Add future update fields here as needed
    # score: Optional[float] = None
    # passed: Optional[bool] = None

# Response model (returned by API)
class CourseAssignmentResponse(CourseAssignmentBase):
    id: UUID
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Model for completion status updates
class CompletionUpdate(BaseModel):
    completed: bool
    
    # You could add more fields here in the future
    # score: Optional[float] = None
    # comments: Optional[str] = None