from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator,field_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from models.avatar_models import AvatarResponse
from models.language_models import LanguageResponse
from models.botVoice_models import BotVoiceResponse
from models.environment_models import EnvironmentResponse

class AvatarInteractionType(str, Enum):
    Try = "try_mode"
    Assess = "assess_mode"
    Learn = "learn_mode"
# AvatarInteraction Models
class AvatarInteractionBase(BaseModel):
    # personas: List[UUID]
    avatars: List[UUID]
    languages: List[UUID]
    bot_voices: List[UUID]
    environments: List[UUID]
    bot_role: str
    bot_role_alt: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    system_prompt: str
    layout: int
    # scenario_id :UUID
    mode: AvatarInteractionType
    @field_validator('mode', mode='before')
    @classmethod
    def validate_mode(cls, v):
        allowed = [e.value for e in AvatarInteractionType]
        if v not in allowed:
            raise ValueError(f"Invalid mode '{v}'. Must be one of: {', '.join(allowed)}.")
        return v
    
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

# Expanded model with object lists
class AvatarInteractionExpandedResponse(BaseModel):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    bot_role: str
    bot_role_alt: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    system_prompt: str
    scenario_id: UUID
    mode: str
    
    # Expanded fields
    avatars: Union[List[UUID],Optional[List[AvatarResponse]]] = None
    languages: Union[List[UUID],Optional[List[LanguageResponse]]] = None
    bot_voices: Union[List[UUID],Optional[List[BotVoiceResponse]]] = None
    environments: Union[List[UUID],Optional[List[EnvironmentResponse]]] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}