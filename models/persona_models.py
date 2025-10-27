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
    age : int
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
    gender: BotGender


# ============================================================================
# V2 PERSONA MODELS - Dynamic Persona Generation System
# ============================================================================

class PersonaLocation(BaseModel):
    """Universal location model for v2 personas"""
    country: str = "India"
    state: Optional[str] = None
    city: str
    region: Optional[str] = None
    current_physical_location: str
    location_type: str
    languages_spoken: List[str] = ["English", "Hindi"]


class PersonaInstanceV2(BaseModel):
    """
    Flexible persona model with base fields + dynamic detail categories.
    Different scenarios will have different detail categories.
    """
    # Meta
    id: str = Field(default_factory=lambda: str(uuid4()))
    template_id: str
    persona_type: str
    mode: str
    scenario_type: str
    
    # Base fields (always present)
    name: str
    age: int
    gender: str
    role: str
    description: str
    location: PersonaLocation
    
    # Archetype
    archetype: str
    archetype_confidence: float
    archetype_specific_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic detail categories (scenario-specific)
    detail_categories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Conversation parameters
    conversation_rules: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    detail_categories_included: List[str] = Field(default_factory=list)
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)


class PersonaGenerationRequestV2(BaseModel):
    """Request to generate a v2 persona"""
    template_id: str
    mode: str
    persona_type: Optional[str] = None
    gender: Optional[str] = None
    custom_prompt: Optional[str] = None
    variation_id: Optional[int] = None
