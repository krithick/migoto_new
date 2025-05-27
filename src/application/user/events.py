from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any ,List
from uuid import UUID

from src.core.events import Event
from src.domain.user.entities import UserRole

@dataclass(kw_only=True)
class UserCreatedEvent(Event):
    user_id: UUID
    email: str
    role: UserRole
    created_by: Optional[UUID]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(kw_only=True)
class UserUpdatedEvent(Event):
    user_id: UUID
    updates: Dict[str, Any]
    updated_by: UUID
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(kw_only=True)
class UserDeletedEvent(Event):
    user_id: UUID
    deleted_by: UUID
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(kw_only=True)
class UserPromotedEvent(Event):
    user_id: UUID
    new_role: UserRole
    promoted_by: UUID
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(kw_only=True)
class CourseAssignedToUserEvent(Event):
    user_id: UUID
    course_id: UUID
    assigned_by: UUID
    timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass(kw_only=True)
class AdminCreatedEvent(Event):
    admin_id: UUID
    email: str
    managed_users: List[UUID]
    created_by: UUID
    timestamp: datetime = field(default_factory=datetime.now)