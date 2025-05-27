from dataclasses import dataclass ,field
from typing import Optional, Dict, Any ,List
from uuid import UUID

from src.domain.user.entities import UserRole

@dataclass
class CreateUserCommand:
    email: str
    password: str
    emp_id: str
    username: str
    role: UserRole = UserRole.USER
    created_by: Optional[UUID] = None

@dataclass
class UpdateUserCommand:
    user_id: UUID
    updates: Dict[str, Any]
    updated_by: UUID

@dataclass
class DeleteUserCommand:
    user_id: UUID
    deleted_by: UUID

@dataclass
class AssignCourseCommand:
    user_id: UUID
    course_id: UUID
    assigned_by: UUID
    
@dataclass
class CreateAdminCommand:
    email: str
    password: str
    emp_id: str
    username: str
    managed_users: List[UUID] = field(default_factory=list)
    created_by: UUID  # Must be superadmin