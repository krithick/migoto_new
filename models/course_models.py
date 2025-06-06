from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from models.modules_models import ModuleDB ,ModuleResponse
from models.user_models import UserRole
# Course Models

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_published: bool = False
    thumbnail_url:str

class CourseCreate(CourseBase):
    modules: Optional[List[UUID]] = Field(default_factory=list)


class CourseDB(CourseBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    modules: List[Union[UUID, ModuleDB]] = Field(default_factory=list)
    creater_role:UserRole
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class CourseResponse(CourseBase):
    id: UUID  # Changed from str to UUID
    modules: List[UUID]  # Changed from List[str] to List[UUID]
    creater_role:UserRole
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}
        
class CourseWithModulesResponse(CourseBase):
    id: UUID  # Changed from str to UUID
    modules: List[ModuleResponse]
    creater_role:UserRole
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

class CourseWithAssignmentResponse(CourseResponse):
    """Course response model with assignment data"""
    assigned_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    
    # Future fields would go here
    # score: Optional[float] = None
    # certificate_id: Optional[UUID] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}