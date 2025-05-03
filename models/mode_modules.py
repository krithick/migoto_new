from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from models.avatarInteraction_models import AvatarInteractionDB , AvatarInteractionResponse

# Mode Models
class LearnModeBase(BaseModel):
    avatar_interaction: UUID
    



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

