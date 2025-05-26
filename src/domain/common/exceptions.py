class DomainException(Exception):
    """Base exception for domain layer"""
    pass

class ValidationException(DomainException):
    """Raised when validation fails"""
    pass

class BusinessRuleViolationException(DomainException):
    """Raised when a business rule is violated"""
    pass

class EntityNotFoundException(DomainException):
    """Raised when an entity is not found"""
    pass

class DuplicateEntityException(DomainException):
    """Raised when trying to create a duplicate entity"""
    pass