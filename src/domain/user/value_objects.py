from dataclasses import dataclass
import re
from typing import Optional

from src.domain.user.exceptions import InvalidEmailException, InvalidPasswordException

@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise InvalidEmailException(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self):
        return self.value

@dataclass(frozen=True)
class Password:
    """Password value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_password(self.value):
            raise InvalidPasswordException("Password must be at least 8 characters")
    
    @staticmethod
    def _is_valid_password(password: str) -> bool:
        return len(password) >= 8
    
    def __str__(self):
        return self.value

@dataclass(frozen=True)
class EmployeeId:
    """Employee ID value object"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("Employee ID must be at least 3 characters")
    
    def __str__(self):
        return self.value