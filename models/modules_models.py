from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from models.scenario_models import ScenarioDB , ScenarioWithAssignmentResponse,ScenarioResponse
from models.user_models import UserRole
# Module Models
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url:str


class ModuleCreate(ModuleBase):
    scenarios: Optional[List[UUID]] = Field(default_factory=list)


class ModuleDB(ModuleBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    scenarios: List[Union[UUID, ScenarioDB]] = Field(default_factory=list)
    creater_role:UserRole
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class ModuleResponse(ModuleBase):
    id: UUID  # Changed from str to UUID
    scenarios: List[UUID]
    creater_role:UserRole# Changed from List[str] to List[UUID]
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

# Expanded Response Models for nested data
class ModuleWithScenariosResponse(ModuleBase):
    id: UUID  # Changed from str to UUID
    scenarios: List[ScenarioResponse]
    creater_role:UserRole
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


class ModuleWithAssignmentResponse(ModuleResponse):
    """Module response model with assignment data"""
    assigned_date: Optional[datetime] = None
    completed: bool = False
    completed_date: Optional[datetime] = None
    # scenarios : List[ScenarioWithAssignmentResponse]
    # Future fields would go here
    # score: Optional[float] = None
    # certificate_id: Optional[UUID] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}