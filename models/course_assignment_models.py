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
    # Company context will be auto-filled during assignment creation
    pass

# Database model (returned when reading from DB)
class CourseAssignmentDB(CourseAssignmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    # Company hierarchy context - tracks assignment flow
    assigned_by_company: UUID                    # Which company's admin made this assignment
    source_company: UUID                        # Which company owns the course being assigned
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
class CourseAssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_date: Optional[datetime] = None
    
    # Archive operations
    is_archived: Optional[bool] = None
    archived_reason: Optional[str] = None
    
    # Add future update fields here as needed
    # score: Optional[float] = None
    # passed: Optional[bool] = None

# Response model (returned by API)
class CourseAssignmentResponse(CourseAssignmentBase):
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

# Model for completion status updates
class CompletionUpdate(BaseModel):
    completed: bool
    
    # You could add more fields here in the future
    # score: Optional[float] = None
    # comments: Optional[str] = None

# Assignment context helper enum
class AssignmentContext:
    """
    Assignment Context Rules:
    
    INTERNAL: 
    - Admin assigns course from their own company to their users
    - source_company == assigned_by_company
    - Most common scenario
    
    CROSS_COMPANY:
    - Admin assigns MOTHER company course to their users
    - source_company (MOTHER) != assigned_by_company (CLIENT/SUBSIDIARY)
    - Enabled by company hierarchy rules
    
    Usage in assignment creation:
    if source_course.company_id == assigning_admin.company_id:
        assignment_context = "internal"
    else:
        assignment_context = "cross_company"
    """
    INTERNAL = "internal"
    CROSS_COMPANY = "cross_company"