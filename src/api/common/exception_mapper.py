from fastapi import HTTPException
from src.domain.common.exceptions import (
    DomainException,
    ValidationException,
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException
)
from src.domain.user.exceptions import UnauthorizedAccessException
from src.api.common.exceptions import (
    BadRequestException,
    NotFoundException,
    ConflictException,
    ForbiddenException
)

def map_domain_to_api_exception(exc: Exception) -> HTTPException:
    """Map domain exceptions to API exceptions"""
    
    # Specific mappings
    if isinstance(exc, ValidationException):
        return BadRequestException(str(exc))
    
    if isinstance(exc, EntityNotFoundException):
        return NotFoundException(str(exc))
    
    if isinstance(exc, DuplicateEntityException):
        return ConflictException(str(exc))
    
    if isinstance(exc, UnauthorizedAccessException):
        return ForbiddenException(str(exc))
    
    if isinstance(exc, BusinessRuleViolationException):
        return BadRequestException(str(exc))
    
    # Generic domain exception
    if isinstance(exc, DomainException):
        return BadRequestException(str(exc))
    
    # Unknown exception - return generic 500
    return HTTPException(status_code=500, detail="Internal server error")