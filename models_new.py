from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class PyUUID(UUID):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type, _handler
    ):
        from pydantic_core import core_schema
        return core_schema.uuid_schema()




#############################
# Learning Content Models
#############################

# Persona Models
# Persona Models
class PersonaBase(BaseModel):
    name: str = Field(..., description="Name for this persona")
    description: str = Field(..., description="Brief description of this persona")
    persona_type: str = Field(..., description="Type of persona (customer, employee, etc.)")


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


# Avatar Models
class AvatarBase(BaseModel):
    name: str
    model_url: str
    thumbnail_url: Optional[str] = None


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


# Language Models
class LanguageBase(BaseModel):
    code: str
    name: str


class LanguageCreate(LanguageBase):
    pass


class LanguageDB(LanguageBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class LanguageResponse(LanguageBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# BotVoice Models
class BotVoiceBase(BaseModel):
    name: str
    voice_id: str
    language_code: str


class BotVoiceCreate(BotVoiceBase):
    pass


class BotVoiceDB(BotVoiceBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class BotVoiceResponse(BotVoiceBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}



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


# Video Models
class VideoBase(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    duration: Optional[int] = None  # in seconds


class VideoCreate(VideoBase):
    pass


class VideoDB(VideoBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class VideoResponse(VideoBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# Document Models
class DocumentBase(BaseModel):
    title: str
    file_url: str
    file_type: str
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentDB(DocumentBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class DocumentResponse(DocumentBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# AvatarInteraction Models
class AvatarInteractionBase(BaseModel):
    personas: List[UUID]
    avatars: List[UUID]
    languages: List[UUID]
    bot_voices: List[UUID]
    environments: List[UUID]


class AvatarInteractionCreate(AvatarInteractionBase):
    pass


class AvatarInteractionDB(AvatarInteractionBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class AvatarInteractionResponse(AvatarInteractionBase):
    id: UUID  # Changed from str to UUID
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# Mode Models
class LearnModeBase(BaseModel):
    avatar_interaction: UUID
    system_prompt: str
    bot_role: str
    bot_role_alt: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class LearnModeCreate(LearnModeBase):
    pass


class LearnModeDB(LearnModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionDB]
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class LearnModeResponse(LearnModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionResponse]  # Changed back to UUID
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


class TryModeBase(BaseModel):
    avatar_interaction: UUID
    system_prompt: str
    bot_role: str
    bot_role_alt: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class TryModeCreate(TryModeBase):
    pass


class TryModeDB(TryModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionDB]
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class TryModeResponse(TryModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionResponse]  # Changed back to UUID
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


class AssessModeBase(BaseModel):
    avatar_interaction: UUID
    system_prompt: str
    bot_role: str
    bot_role_alt: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class AssessModeCreate(AssessModeBase):
    pass


class AssessModeDB(AssessModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionDB]
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class AssessModeResponse(AssessModeBase):
    avatar_interaction: Union[UUID, AvatarInteractionResponse]  # Changed back to UUID
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# Scenario Models
class ScenarioBase(BaseModel):
    title: str
    description: Optional[str] = None
    learn_mode: Optional[LearnModeCreate] = None
    try_mode: Optional[TryModeCreate] = None
    assess_mode: Optional[AssessModeCreate] = None


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioDB(ScenarioBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    learn_mode: Optional[LearnModeDB] = None
    try_mode: Optional[TryModeDB] = None
    assess_mode: Optional[AssessModeDB] = None
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
        if not any([self.learn_mode, self.try_mode, self.assess_mode]):
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
    learn_mode: Optional[LearnModeResponse] = None
    try_mode: Optional[TryModeResponse] = None
    assess_mode: Optional[AssessModeResponse] = None
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}



# Module Models
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None


class ModuleCreate(ModuleBase):
    scenarios: Optional[List[UUID]] = Field(default_factory=list)


class ModuleDB(ModuleBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    scenarios: List[Union[UUID, ScenarioDB]] = Field(default_factory=list)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class ModuleResponse(ModuleBase):
    id: UUID  # Changed from str to UUID
    scenarios: List[UUID]  # Changed from List[str] to List[UUID]
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# Course Models
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_published: bool = False


class CourseCreate(CourseBase):
    modules: Optional[List[UUID]] = Field(default_factory=list)


class CourseDB(CourseBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    modules: List[Union[UUID, ModuleDB]] = Field(default_factory=list)
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
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


class CourseWithModulesResponse(CourseBase):
    id: UUID  # Changed from str to UUID
    modules: List[ModuleResponse]
    created_by: UUID  # Changed from str to UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}