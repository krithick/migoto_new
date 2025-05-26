from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.api.v1.schemas.user_schemas import (
    LoginRequest, TokenResponse, PasswordChangeRequest
)
from src.application.user.services import UserService
from src.api.v1.dependencies.auth import get_current_user
from src.domain.user.entities import User

router = APIRouter(prefix="/auth")

@router.post("/token", response_model=TokenResponse)
@inject
async def login_with_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(Provide[Container.user_service])
):
    """OAuth2 compatible token endpoint"""
    user = await service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token, expires_at = service.create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=access_token,
        expires_at=expires_at
    )

@router.post("/login", response_model=TokenResponse)
@inject
async def login(
    credentials: LoginRequest,
    service: UserService = Depends(Provide[Container.user_service])
):
    """Login endpoint with JSON body"""
    user = await service.authenticate(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    access_token, expires_at = service.create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=access_token,
        expires_at=expires_at
    )

@router.post("/password/change")
@inject
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(Provide[Container.user_service])
):
    """Change current user's password"""
    # Verify current password
    authenticated = await service.authenticate(
        str(current_user.email), 
        password_data.current_password
    )
    if not authenticated:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Update password
    await service.update_user(
        user_id=current_user.id,
        updates={"password": password_data.new_password},
        updated_by=current_user.id
    )
    
    return {"success": True}