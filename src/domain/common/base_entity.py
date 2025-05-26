from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

@dataclass(kw_only=True)
class BaseEntity(ABC):
    """Base class for all domain entities"""
    # ALL fields have defaults
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    def update_timestamp(self, updated_by: Optional[UUID] = None):
        """Update the updated_at timestamp and optionally set updated_by"""
        self.updated_at = datetime.now()
        if updated_by:
            self.updated_by = updated_by

    def __eq__(self, other):
        """Entities are equal if their IDs are equal"""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self):
        """Hash based on ID"""
        return hash(self.id)