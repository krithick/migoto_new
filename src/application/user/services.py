from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

from src.domain.user.entities import User, UserRole
from src.domain.user.value_objects import Email, Password, EmployeeId
from src.domain.user.exceptions import (
    DuplicateEmailException, 
    UnauthorizedAccessException,
    UserDomainException
)
from src.infrastructure.repositories.user_repository import UserRepository
from src.core.events import EventBus
from src.application.user.events import (
    UserCreatedEvent, 
    UserUpdatedEvent, 
    UserDeletedEvent,
    UserPromotedEvent
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        event_bus: EventBus,
        secret_key: str,
        algorithm: str = "HS256",
        token_expire_minutes: int = 60 * 24 * 7  # 1 week
    ):
        self.repository = user_repository
        self.event_bus = event_bus
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
    
    # Authentication methods
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.repository.find_by_email(email)
        if not user or not self._verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, user_id: UUID, role: UserRole) -> tuple[str, int]:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "role": role.value,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, int(expire.timestamp())
    
    # User management methods
    async def create_user(
        self,
        email: str,
        password: str,
        emp_id: str,
        username: str,
        role: UserRole = UserRole.USER,
        created_by: Optional[UUID] = None
    ) -> User:
        """Create new user"""
        # Check for duplicate email
        existing = await self.repository.find_by_email(email)
        if existing:
            raise DuplicateEmailException(f"Email {email} already registered")
        
        # Determine assignee if created by admin
        assignee_emp_id = None
        if created_by:
            creator = await self.repository.find_by_id(created_by)
            if creator and creator.role == UserRole.ADMIN:
                assignee_emp_id = creator.emp_id
        
        # Create user entity
        user = User(
            email=Email(email),
            emp_id=EmployeeId(emp_id),
            username=username,
            hashed_password=self._hash_password(password),
            role=role,
            assignee_emp_id=assignee_emp_id,
            created_by=created_by
        )
        
        # Save to repository
        saved_user = await self.repository.create(user)
        
        # Update admin's managed users if applicable
        if created_by and assignee_emp_id:
            await self.repository.add_managed_user(created_by, saved_user.id)
        
        # Publish event
        await self.event_bus.publish(UserCreatedEvent(
            user_id=saved_user.id,
            email=str(saved_user.email),
            role=saved_user.role,
            created_by=created_by
        ))
        
        return saved_user
    
    async def update_user(
        self,
        user_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID
    ) -> User:
        """Update user information"""
        # Get user and updater
        user = await self.repository.find_by_id(user_id)
        if not user:
            raise UserDomainException("User not found")
        
        updater = await self.repository.find_by_id(updated_by)
        if not updater:
            raise UserDomainException("Updater not found")
        
        # Check permissions
        if not updater.can_manage_user(user):
            raise UnauthorizedAccessException("Insufficient permissions to update user")
        
        # Apply updates
        for key, value in updates.items():
            if value is not None:
                if key == "email":
                    # Check for duplicate email
                    existing = await self.repository.find_by_email(value)
                    if existing and existing.id != user_id:
                        raise DuplicateEmailException(f"Email {value} already in use")
                    user.email = Email(value)
                elif key == "password":
                    user.change_password(self._hash_password(value))
                elif key == "role" and updater.role == UserRole.SUPERADMIN:
                    # Only superadmin can change roles
                    user.role = UserRole(value)
                elif hasattr(user, key):
                    setattr(user, key, value)
        
        user.update_timestamp(updated_by)
        
        # Save changes
        updated_user = await self.repository.update(user_id, user)
        
        # Publish event
        await self.event_bus.publish(UserUpdatedEvent(
            user_id=user_id,
            updates=updates,
            updated_by=updated_by
        ))
        
        return updated_user
    
    async def delete_user(self, user_id: UUID, deleted_by: UUID) -> bool:
        """Delete user"""
        # Get user and deleter
        user = await self.repository.find_by_id(user_id)
        if not user:
            return False
        
        deleter = await self.repository.find_by_id(deleted_by)
        if not deleter:
            raise UnauthorizedAccessException("Deleter not found")
        
        # Check permissions
        if not deleter.can_manage_user(user):
            raise UnauthorizedAccessException("Insufficient permissions to delete user")
        
        # Prevent deletion of admins/superadmins by non-superadmins
        if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN] and deleter.role != UserRole.SUPERADMIN:
            raise UnauthorizedAccessException("Only superadmins can delete admin accounts")
        
        # Delete user
        success = await self.repository.delete(user_id)
        
        if success:
            # Remove from any admin's managed users
            await self.repository.remove_user_from_all_admins(user_id)
            
            # Publish event
            await self.event_bus.publish(UserDeletedEvent(
                user_id=user_id,
                deleted_by=deleted_by
            ))
        
        return success
    
    # Helper methods
    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)