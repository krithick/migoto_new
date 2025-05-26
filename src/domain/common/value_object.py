from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for value objects"""
    
    @abstractmethod
    def validate(self):
        """Validate the value object state"""
        pass
    
    def __post_init__(self):
        """Auto-validate after initialization"""
        self.validate()