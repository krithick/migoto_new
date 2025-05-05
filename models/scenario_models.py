from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


from models.mode_modules import LearnModeCreate,TryModeCreate,AssessModeCreate,LearnModeDB,TryModeDB,AssessModeDB,LearnModeResponse,TryModeResponse,AssessModeResponse
# Scenario Models
class ScenarioBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url:str
    learn_mode: LearnModeCreate 
    try_mode: TryModeCreate 
    assess_mode: AssessModeCreate 


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioDB(ScenarioBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    learn_mode: LearnModeDB 
    try_mode: TryModeDB 
    assess_mode: AssessModeDB 
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    # @model_validator(mode='after')
    # def check_at_least_one_mode(cls, values):
    #     if not any([values.get('learn_mode'), values.get('try_mode'), values.get('assess_mode')]):
    #         raise ValueError("At least one mode (learn, try, or assess) must be provided")
    #     return values
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
    id: UUID  # Changed from str to UUID
    title: str
    description: Optional[str] = None
    learn_mode: LearnModeResponse
    try_mode: TryModeResponse
    assess_mode: AssessModeResponse
    thumbnail_url: str
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

