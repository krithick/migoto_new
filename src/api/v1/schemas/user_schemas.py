from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.domain.user.entities import UserRole

# Request schemas
class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    emp_id: str = Field(..., min_length=3)
    username: str = Field(..., min_length=3)
    role: UserRole = UserRole.USER

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    username: Optional[str] = Field(None, min_length=3)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# Response schemas
class UserResponse(BaseModel):
    id: UUID
    email: str
    emp_id: str
    username: str
    role: UserRole
    is_active: bool
    assignee_emp_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_entity(cls, user):
        return cls(
            id=user.id,
            email=str(user.email),
            emp_id=str(user.emp_id),
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            assignee_emp_id=user.assignee_emp_id,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

class UserWithCoursesResponse(UserResponse):
    assigned_courses: List[UUID]
    
    @classmethod
    def from_entity(cls, user):
        base = UserResponse.from_entity(user)
        return cls(
            **base.dict(),
            assigned_courses=user.assigned_courses
        )

class AdminUserResponse(UserResponse):
    managed_users: List[UUID]
    
    @classmethod
    def from_entity(cls, user):
        base = UserResponse.from_entity(user)
        return cls(
            **base.dict(),
            managed_users=user.managed_users
        )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int

class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    emp_id: str = Field(..., min_length=3)
    username: str = Field(..., min_length=3)
    managed_users: List[UUID] = Field(default_factory=list)