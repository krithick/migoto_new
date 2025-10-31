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
    id: UUID = Field(default_factory=uuid4, alias="_id")
    full_persona: Dict[str, Any] = Field(..., description="Complete JSON representation")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # V2 fields (optional for backward compatibility)
    detail_categories: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description="V2 dynamic categories")
    detail_categories_included: Optional[List[str]] = Field(default=None, description="V2 category names")
    conversation_rules: Optional[Dict[str, Any]] = Field(default=None, description="V2 conversation rules")
    archetype: Optional[str] = Field(default=None, description="V2 archetype")
    archetype_confidence: Optional[float] = Field(default=None, description="V2 archetype confidence")
    system_prompt: Optional[str] = Field(default=None, description="V2 system prompt")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class PersonaResponse(PersonaCreate):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    # V2 fields (optional)
    detail_categories: Optional[Dict[str, Dict[str, Any]]] = None
    detail_categories_included: Optional[List[str]] = None
    conversation_rules: Optional[Dict[str, Any]] = None
    archetype: Optional[str] = None
    system_prompt: Optional[str] = None
    
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
    Supports both structured and dynamic fields for maximum flexibility.
    """
    # Meta
    id: str = Field(default_factory=lambda: str(uuid4()))
    template_id: str
    persona_type: str
    mode: str
    scenario_type: Optional[str] = None
    
    # Base fields (always present)
    name: str
    age: int
    gender: str
    role: str
    description: str
    location: Union[PersonaLocation, Dict[str, Any]]  # Allow dict for flexibility
    
    # Archetype (optional for backward compatibility)
    archetype: Optional[str] = None
    archetype_confidence: Optional[float] = None
    archetype_specific_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic detail categories (scenario-specific)
    detail_categories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Conversation parameters
    conversation_rules: Dict[str, Any] = Field(default_factory=dict)
    
    # System prompt (generated from template + persona)
    system_prompt: Optional[str] = Field(None, description="Generated system prompt for this persona")
    prompt_mode: Optional[str] = Field(None, description="Mode used for prompt generation (assess/try)")
    prompt_generated_at: Optional[datetime] = Field(None, description="When the prompt was generated")
    
    # Metadata
    detail_categories_included: List[str] = Field(default_factory=list)
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"  # Allow additional fields not defined in model
    
    def to_db_model(self, created_by: UUID) -> "PersonaV2DB":
        """Convert to V2 database model"""
        location_dict = self.location.dict() if isinstance(self.location, PersonaLocation) else self.location
        
        return PersonaV2DB(
            _id=self.id,
            template_id=self.template_id,
            persona_type=self.persona_type,
            mode=self.mode,
            scenario_type=self.scenario_type or "general",
            name=self.name,
            age=self.age,
            gender=self.gender,
            role=self.role,
            description=self.description,
            location=location_dict,
            archetype=self.archetype or "HELP_SEEKING",
            archetype_confidence=self.archetype_confidence or 0.8,
            archetype_specific_data=self.archetype_specific_data,
            detail_categories=self.detail_categories,
            detail_categories_included=self.detail_categories_included,
            conversation_rules=self.conversation_rules,
            system_prompt=self.system_prompt,
            prompt_mode=self.prompt_mode,
            generation_metadata=self.generation_metadata,
            created_by=created_by
        )
    
    def to_legacy_db_model(self, created_by: UUID) -> "PersonaDB":
        """Convert to old PersonaDB model for backward compatibility"""
        location_dict = self.location.dict() if isinstance(self.location, PersonaLocation) else self.location
        location_str = f"{location_dict.get('city', 'Mumbai')}, {location_dict.get('state', 'Maharashtra')}"
        
        # Build full_persona dict with all data
        full_persona = {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "role": self.role,
            "description": self.description,
            "location": location_dict,
            "detail_categories": self.detail_categories,
            "conversation_rules": self.conversation_rules,
            "archetype": self.archetype,
            "system_prompt": self.system_prompt
        }
        
        return PersonaDB(
            _id=UUID(self.id) if isinstance(self.id, str) else self.id,
            name=self.name,
            description=self.description,
            persona_type=self.persona_type,
            gender=self.gender,
            age=self.age,
            character_goal=self.conversation_rules.get("opening_behavior", "Interact naturally"),
            location=location_str,
            persona_details=self.description,
            situation=location_dict.get("current_physical_location", "At location"),
            business_or_personal="business",
            full_persona=full_persona,
            created_by=created_by,
            # V2 fields
            detail_categories=self.detail_categories,
            detail_categories_included=self.detail_categories_included,
            conversation_rules=self.conversation_rules,
            archetype=self.archetype,
            archetype_confidence=self.archetype_confidence,
            system_prompt=self.system_prompt
        )


class PersonaGenerationRequestV2(BaseModel):
    """Request to generate a v2 persona"""
    template_id: str
    mode: str
    persona_type: Optional[str] = None
    gender: Optional[str] = None
    custom_prompt: Optional[str] = None
    variation_id: Optional[int] = None


class PersonaV2DB(BaseModel):
    """V2-specific database model (separate collection)"""
    """Database model for V2 personas with dynamic categories"""
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    template_id: str
    persona_type: str
    mode: str
    scenario_type: str
    
    # Base fields
    name: str
    age: int
    gender: str
    role: str
    description: str
    location: Dict[str, Any]
    
    # Archetype
    archetype: str
    archetype_confidence: float
    archetype_specific_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Dynamic detail categories (16 possible, only relevant ones saved)
    detail_categories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    detail_categories_included: List[str] = Field(default_factory=list)
    
    # Conversation rules
    conversation_rules: Dict[str, Any] = Field(default_factory=dict)
    
    # System prompt
    system_prompt: Optional[str] = None
    prompt_mode: Optional[str] = None
    
    # Metadata
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str, datetime: lambda v: v.isoformat()}


class PersonaV2Response(BaseModel):

    id: str
    template_id: str
    persona_type: str
    mode: str
    name: str
    age: int
    gender: str
    role: str
    description: str
    location: Dict[str, Any]
    archetype: str
    detail_categories: Dict[str, Dict[str, Any]]
    detail_categories_included: List[str]
    conversation_rules: Dict[str, Any]
    system_prompt: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
