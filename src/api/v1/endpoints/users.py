from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.api.v1.schemas.user_schemas import (
    UserCreateRequest, UserResponse, UserUpdateRequest,
    UserWithCoursesResponse, AdminUserResponse,AdminCreateRequest
)
from src.application.user.services import UserService
from src.api.v1.dependencies.auth import get_current_user, require_admin, require_superadmin
from src.domain.user.entities import User, UserRole
from src.domain.user.exceptions import (
    DuplicateEmailException, 
    UnauthorizedAccessException,
    UserDomainException
)
from src.api.common.exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException
)
from src.domain.common.exceptions import (
    DomainException,
    ValidationException,
    EntityNotFoundException,
    DuplicateEntityException,
    BusinessRuleViolationException
)
from src.api.common.decorators import handle_exceptions

router = APIRouter(prefix="/users")

@router.post("/", response_model=List[UserResponse])
@inject
@handle_exceptions  # Add decorator
async def create_users(
    users: List[UserCreateRequest],
    current_user: User = Depends(require_admin),
    service: UserService = Depends(Provide[Container.user_service])
):
    """Create new users (admin/superadmin only)"""
    created_users = []
    
    # No try-except needed!
    for user_data in users:
        user = await service.create_user(
            email=user_data.email,
            password=user_data.password,
            emp_id=user_data.emp_id,
            username=user_data.username,
            role=user_data.role,
            created_by=current_user.id
        )
        created_users.append(UserResponse.from_entity(user))
    
    return created_users

@router.get("/me", response_model=UserResponse)
@handle_exceptions
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user"""
    return UserResponse.from_entity(current_user)

@router.get("/", response_model=List[UserWithCoursesResponse])
@inject
@handle_exceptions
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    service: UserService = Depends(Provide[Container.user_service]),
    repository = Depends(Provide[Container.user_repository])
):
    """Get list of users (admin: managed users, superadmin: all users)"""
    if current_user.role == UserRole.SUPERADMIN:
        users = await repository.find_all(skip=skip, limit=limit)
    else:
        users = await repository.find_by_admin(current_user.id)
    
    return [UserWithCoursesResponse.from_entity(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
@inject
@handle_exceptions
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    repository = Depends(Provide[Container.user_repository])
):
    """Get specific user by ID"""
    user = await repository.find_by_id(user_id)
    if not user:
        raise EntityNotFoundException(f"User with ID {user_id} not found")
    
    # Check permissions
    if not current_user.can_manage_user(user):
        raise UnauthorizedAccessException("Access denied")
    
    return UserResponse.from_entity(user)

@router.put("/{user_id}", response_model=UserResponse)
@inject
@handle_exceptions

async def update_user(
    user_id: UUID,
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(Provide[Container.user_service])
):
    """Update user information"""
   
        # Convert update request to dict, excluding None values
    updates = {k: v for k, v in update_data.dict().items() if v is not None}
        
    user = await service.update_user(
            user_id=user_id,
            updates=updates,
            updated_by=current_user.id
        )
    return UserResponse.from_entity(user)


@router.delete("/{user_id}")
@inject
@handle_exceptions

async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(Provide[Container.user_service])
):
    """Delete user"""
    success = await service.delete_user(
            user_id=user_id,
            deleted_by=current_user.id
        )
    # if not success:
    #     raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}

    

@router.post("/admins", response_model=AdminUserResponse)
@inject
@handle_exceptions
async def create_admin(
    request: AdminCreateRequest,
    current_user: User = Depends(require_superadmin),  # Only superadmin
    service: UserService = Depends(Provide[Container.user_service])
):
    """Create new admin user (superadmin only)"""
    # try:
    admin = await service.create_admin(
            email=request.email,
            password=request.password,
            emp_id=request.emp_id,
            username=request.username,
            managed_users=request.managed_users,
            created_by=current_user.id
        )
    return AdminUserResponse.from_entity(admin)
    # except UnauthorizedAccessException as e:
    #     raise HTTPException(status_code=403, detail=str(e))
    # except DuplicateEmailException as e:
    #     raise HTTPException(status_code=400, detail=str(e))