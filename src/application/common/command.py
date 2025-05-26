from abc import ABC
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class Command(ABC):
    """Base command class"""
    executed_by: Optional[UUID] = None

