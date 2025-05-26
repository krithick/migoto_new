from src.domain.common.exceptions import DomainException

class UserDomainException(DomainException):
    """Base exception for user domain"""
    pass

class InvalidEmailException(UserDomainException):
    """Invalid email format"""
    pass

class InvalidPasswordException(UserDomainException):
    """Invalid password"""
    pass

class DuplicateEmailException(UserDomainException):
    """Email already exists"""
    pass

class UnauthorizedAccessException(UserDomainException):
    """User doesn't have permission"""
    pass