from functools import wraps
from typing import Callable
from fastapi import HTTPException

# Import your domain exceptions
from src.domain.common.exceptions import (
    DomainException,
    ValidationException,
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException
)
from src.domain.user.exceptions import (
    UserDomainException,
    DuplicateEmailException,
    UnauthorizedAccessException,
    InvalidEmailException,
    InvalidPasswordException
)

# Import your API exceptions
from src.api.common.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException
)

def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle domain exceptions and convert them to API exceptions
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
            
        # User-specific exceptions
        except DuplicateEmailException as e:
            raise ConflictException(f"Email already registered: {str(e)}")
            
        except InvalidEmailException as e:
            raise BadRequestException(f"Invalid email format: {str(e)}")
            
        except InvalidPasswordException as e:
            raise BadRequestException(f"Invalid password: {str(e)}")
            
        except UnauthorizedAccessException as e:
            raise ForbiddenException(str(e))
            
        # Generic domain exceptions
        except DuplicateEntityException as e:
            raise ConflictException(str(e))
            
        except EntityNotFoundException as e:
            raise NotFoundException("User", str(e))
            
        except ValidationException as e:
            raise BadRequestException(f"Validation error: {str(e)}")
            
        except BusinessRuleViolationException as e:
            raise BadRequestException(f"Business rule violation: {str(e)}")
            
        except UserDomainException as e:
            raise BadRequestException(str(e))
            
        except DomainException as e:
            raise BadRequestException(f"Domain error: {str(e)}")
            
        except HTTPException:
            # If it's already an HTTPException, just re-raise it
            raise
            
        except Exception as e:
            # Log unexpected exceptions
            print(f"Unexpected error in {func.__name__}: {type(e).__name__}: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    
    return wrapper