from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr,field_validator ,validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
# Avatar Models
class AvatarGender(str, Enum):
    Male = "male"
    Female = "female"
class AvatarBase(BaseModel):
    name: str
    model_url: str
    thumbnail_url: Optional[str] = None
    persona_id : List[UUID] = Field(default_factory=list)
    gender:AvatarGender
    @field_validator('gender', mode='before')
    @classmethod
    def validate_mode(cls, v):
        allowed = [e.value for e in AvatarGender]
        if v not in allowed:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

class AvatarCreate(AvatarBase):
    pass


class AvatarDB(AvatarBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class AvatarResponse(AvatarBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}

