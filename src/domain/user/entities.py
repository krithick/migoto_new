from dataclasses import dataclass, field
from typing import List, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from src.domain.common.base_entity import BaseEntity
from src.domain.user.value_objects import Email, Password, EmployeeId
from src.domain.user.exceptions import UserDomainException

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

@dataclass(kw_only=True)
class User(BaseEntity):
    # Non-default fields MUST come first
    email: Email
    emp_id: EmployeeId
    username: str
    hashed_password: str
    
    # Fields with defaults come after
    role: UserRole = UserRole.USER
    is_active: bool = True
    # assignee_emp_id: Optional[str] = None
    assigned_courses: List[UUID] = field(default_factory=list)
    managed_users: List[UUID] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate user after initialization"""
        self.validate()
    
    def validate(self):
        """Validate user state"""
        if not self.username or len(self.username) < 3:
            raise UserDomainException("Username must be at least 3 characters")
        
        if self.role == UserRole.ADMIN and not isinstance(self.managed_users, list):
            self.managed_users = []
        
        if self.role == UserRole.USER and self.managed_users:
            raise UserDomainException("Regular users cannot have managed users")
    
    def change_password(self, new_password_hash: str):
        """Change user password"""
        self.hashed_password = new_password_hash
        self.update_timestamp()
    
    def assign_course(self, course_id: UUID):
        """Assign a course to user"""
        if course_id not in self.assigned_courses:
            self.assigned_courses.append(course_id)
            self.update_timestamp()
    
    def unassign_course(self, course_id: UUID):
        """Remove course assignment"""
        if course_id in self.assigned_courses:
            self.assigned_courses.remove(course_id)
            self.update_timestamp()
    
    def can_manage_user(self, target_user: 'User') -> bool:
        """Check if this user can manage target user"""
        if self.role == UserRole.SUPERADMIN:
            return True
        
        if self.role == UserRole.ADMIN:
            # Admin can manage users assigned to them
            return (
                target_user.id in self.managed_users or
                # target_user.assignee_emp_id == self.emp_id or
                target_user.id == self.id  # Can manage self
            )
        
        # Regular users can only manage themselves
        return target_user.id == self.id
    
    def promote_to_admin(self):
        """Promote user to admin role"""
        if self.role == UserRole.SUPERADMIN:
            raise UserDomainException("Cannot promote superadmin")
        self.role = UserRole.ADMIN
        self.managed_users = []
        self.update_timestamp()
    
    def add_managed_user(self, user_id: UUID):
        """Add user to managed users (admin only)"""
        if self.role != UserRole.ADMIN:
            raise UserDomainException("Only admins can manage users")
        if user_id not in self.managed_users:
            self.managed_users.append(user_id)
            self.update_timestamp()