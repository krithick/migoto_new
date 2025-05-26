from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.domain.common.exceptions import (
    DomainException,
    ValidationException,
    EntityNotFoundException,
    DuplicateEntityException
)
from src.api.common.responses import ErrorResponse

async def domain_exception_handler(request: Request, exc: DomainException):
    """Handle domain exceptions"""
    if isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, EntityNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateEntityException):
        status_code = status.HTTP_409_CONFLICT
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    
    response = ErrorResponse(error=str(exc))
    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors[field] = error["msg"]
    
    response = ErrorResponse(
        error="Validation failed",
        details=errors
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.dict()
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    response = ErrorResponse(error=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )