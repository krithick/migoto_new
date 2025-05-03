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
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return UUID(v)
        elif isinstance(v, UUID):
            return v
        raise ValueError("Invalid UUID")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", format="uuid")

#############################
# User Management Models
#############################

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    thumbnail_url:Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserDB(UserBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    role: UserRole = UserRole.USER
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    assigned_courses: List[UUID] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: lambda v: str(v)}

class UserWithCoursesResponse(UserResponse):
    assigned_courses: List[str]
    
    class Config:
        populate_by_name = True


class AdminUserCreate(UserCreate):
    # For admin creation by superadmin
    managed_users: List[UUID] = Field(default_factory=list)
    
    # @model_validator(mode='after')
    # def check_role(cls, values):
    #     if values.get('role') != UserRole.ADMIN:
    #         values['role'] = UserRole.ADMIN
    #     return values
    @model_validator(mode='after')
    def check_role(cls, model):
        if model.role != UserRole.ADMIN:
            model.role = UserRole.ADMIN
        return model

class AdminUserDB(UserDB):
    managed_users: List[UUID] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class AdminUserResponse(UserResponse):
    managed_users: List[str]
    
    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp


class TokenData(BaseModel):
    user_id: UUID
    role: UserRole
    exp: int  # Expiration timestamp


class UserAssignmentUpdate(BaseModel):
    user_ids: List[UUID]
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    @validator('operation')
    def check_operation(cls, v):
        if v not in ['add', 'remove']:
            raise ValueError("Operation must be either 'add' or 'remove'")
        return v

class ModeAssignment(BaseModel):
    avatar_interaction: UUID

class ScenarioAssignment(BaseModel):
    scenario_id: UUID
    learn_mode: Optional[bool] = None
    try_mode: Optional[bool] = None
    assess_mode: Optional[bool] = None

class ModuleAssignment(BaseModel):
    module_id: UUID
    scenarios_assigned: List[ScenarioAssignment]

class CourseAssignment(BaseModel):
    course_id: UUID
    modules_assigned: List[ModuleAssignment]

class CourseAssignmentRequest(BaseModel):
    course_ids: List[CourseAssignment]
    user_id: UUID

class CourseAssignmentUpdate(BaseModel):
    assignments: List[CourseAssignmentRequest]
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    @validator('operation')
    def check_operation(cls, v):
        if v not in ['add', 'remove']:
            raise ValueError("Operation must be either 'add' or 'remove'")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
