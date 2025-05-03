from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr,field_validator, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
# Persona Models
class BotGender(str, Enum):
    Male = "male"
    Female = "female"
class PersonaBase(BaseModel):
    name: str = Field(..., description="Name for this persona")
    description: str = Field(..., description="Brief description of this persona")
    persona_type: str = Field(..., description="Type of persona (customer, employee, etc.)")
    gender:BotGender
    @field_validator('gender', mode='before')
    @classmethod
    def validate_mode(cls, v):
        allowed = [e.value for e in BotGender]
        if v not in allowed:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {', '.join(allowed)}.")
        return v    

class PersonaCreate(PersonaBase):
    character_goal: str = Field(..., description="Primary goal or objective of the character")
    location: str = Field(..., description="Where the character is based")
    persona_details: str = Field(..., description="Detailed persona description")
    situation: str = Field(..., description="Current circumstances or situation")
    business_or_personal: str = Field(..., description="Whether this is a business or personal context")
    background_story: Optional[str] = Field(None, description="Optional background story")


class PersonaDB(PersonaCreate):
    id: UUID = Field(default_factory=uuid4, alias="_id")  # Keeping UUID
    full_persona: Dict[str, Any] = Field(..., description="Complete JSON representation")
    created_by: UUID  # Keeping UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class PersonaResponse(PersonaCreate):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


class PersonaGenerateRequest(BaseModel):
    persona_description: str = Field(..., 
        description="One-line description of the persona",
        example="Tech-savvy young professional looking for premium banking services")
    persona_type: str = Field(..., 
        description="Type of persona (customer, employee, etc.)",
        example="customer")
    business_or_personal: str = Field(..., 
        description="Whether this is a business or personal context",
        example="personal")
    location: Optional[str] = Field(None, 
        description="Optional location",
        example="Mumbai")

