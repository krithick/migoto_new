
from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
# Environment Models
class EnvironmentBase(BaseModel):
    name: str
    scene_url: str
    thumbnail_url: Optional[str] = None
    


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentDB(EnvironmentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class EnvironmentResponse(EnvironmentBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

