from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List , Dict , Any
from datetime import datetime
from uuid import UUID

T = TypeVar('T')

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.now)

class DataResponse(BaseResponse, Generic[T]):
    """Response with data"""
    data: T

class ListResponse(BaseResponse, Generic[T]):
    """Response with list of items"""
    data: List[T]
    total: int
    skip: int = 0
    limit: int = 100

class ErrorResponse(BaseResponse):
    """Error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class CreatedResponse(BaseResponse):
    """Response for created resources"""
    id: UUID
    message: str = "Resource created successfully"

class UpdatedResponse(BaseResponse):
    """Response for updated resources"""
    message: str = "Resource updated successfully"

class DeletedResponse(BaseResponse):
    """Response for deleted resources"""
    message: str = "Resource deleted successfully"