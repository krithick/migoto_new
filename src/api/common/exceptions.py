from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class APIException(HTTPException):
    """Base API exception"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class BadRequestException(APIException):
    """400 Bad Request"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnauthorizedException(APIException):
    """401 Unauthorized"""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(APIException):
    """403 Forbidden"""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFoundException(APIException):
    """404 Not Found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ConflictException(APIException):
    """409 Conflict"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)