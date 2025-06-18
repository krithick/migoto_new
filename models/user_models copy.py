# models/user_models.py (Updated)

from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator, model_validator
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    BOSS_ADMIN = "boss_admin"  # New role for mother company


class AccountType(str, Enum):
    REGULAR = "regular"
    DEMO = "demo"
    TRIAL = "trial"


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
    emp_id: str
    username: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER
    company_id: UUID  # Required for all users
    account_type: AccountType = AccountType.REGULAR
    demo_expires_at: Optional[datetime] = None  # For demo accounts
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    @validator('demo_expires_at')
    def validate_demo_expiry(cls, v, values):
        if values.get('account_type') == AccountType.DEMO and not v:
            # Set default demo expiry to 1 week from now
            return datetime.now() + timedelta(weeks=1)
        elif values.get('account_type') != AccountType.DEMO and v:
            raise ValueError("Demo expiry date only applies to demo accounts")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    account_type: Optional[AccountType] = None
    demo_expires_at: Optional[datetime] = None


class UserDB(UserBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    role: UserRole = UserRole.USER
    hashed_password: str
    emp_id: str
    
    # Company relationship
    company_id: UUID
    
    # Account type and demo settings
    account_type: AccountType = AccountType.REGULAR
    demo_expires_at: Optional[datetime] = None
    
    # Tracking fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    assigned_courses: List[UUID] = Field(default_factory=list)
    
    # Permission tracking
    can_access_analytics: bool = False  # For boss admin to grant analytics access
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}
    
    def is_demo_expired(self) -> bool:
        """Check if demo account has expired"""
        if self.account_type != AccountType.DEMO:
            return False
        if not self.demo_expires_at:
            return False
        return datetime.now() > self.demo_expires_at


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    emp_id: str
    company_id: UUID
    account_type: AccountType
    created_at: datetime
    updated_at: datetime
    demo_expires_at: Optional[datetime] = None
    is_demo_expired: bool = False
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: lambda v: str(v)}


class UserWithCoursesResponse(UserResponse):
    assigned_courses: List[UUID]
    
    class Config:
        populate_by_name = True


class AdminUserCreate(UserCreate):
    # For admin creation by superadmin or boss admin
    managed_users: List[UUID] = Field(default_factory=list)
    managed_companies: List[UUID] = Field(default_factory=list)  # For boss admin
    
    @model_validator(mode='after')
    def check_role(cls, model):
        if model.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            model.role = UserRole.ADMIN
        return model


class AdminUserDB(UserDB):
    managed_users: List[UUID] = Field(default_factory=list)
    managed_companies: List[UUID] = Field(default_factory=list)  # For boss admin only
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class BossAdminDB(AdminUserDB):
    """Boss Admin - can manage multiple companies"""
    role: UserRole = UserRole.BOSS_ADMIN
    
    # Additional permissions
    can_create_companies: bool = True
    can_view_all_analytics: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class SuperAdminDB(AdminUserDB):
    """SuperAdmin - manages one company but has full control within it"""
    role: UserRole = UserRole.SUPERADMIN
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class AdminUserResponse(UserResponse):
    managed_users: List[str]
    managed_companies: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class BossAdminResponse(AdminUserResponse):
    can_create_companies: bool
    can_view_all_analytics: bool
    
    class Config:
        populate_by_name = True


# Demo User specific models
class DemoUserCreate(UserCreate):
    account_type: AccountType = AccountType.DEMO
    demo_duration_days: int = Field(default=7, ge=1, le=30)  # 1-30 days
    
    @model_validator(mode='after')
    def set_demo_expiry(cls, model):
        if model.account_type == AccountType.DEMO:
            model.demo_expires_at = datetime.now() + timedelta(days=model.demo_duration_days)
        return model


class DemoExtensionRequest(BaseModel):
    user_id: UUID
    extension_days: int = Field(..., ge=1, le=30)
    reason: Optional[str] = None


# Token and Authentication models (updated)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp
    user_role: UserRole
    company_id: str
    account_type: AccountType
    is_demo_expired: bool = False


class TokenData(BaseModel):
    user_id: UUID
    role: UserRole
    company_id: UUID
    account_type: AccountType
    exp: int  # Expiration timestamp


# Assignment models (updated)
class UserAssignmentUpdate(BaseModel):
    user_ids: List[UUID]
    operation: str = Field(..., description="Either 'add' or 'remove'")
    
    @validator('operation')
    def check_operation(cls, v):
        if v not in ['add', 'remove']:
            raise ValueError("Operation must be either 'add' or 'remove'")
        return v


class CourseAssignmentUpdate(BaseModel):
    course_ids: List[UUID]
    user_id: UUID
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