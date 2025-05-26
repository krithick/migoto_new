from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.domain.user.entities import User, UserRole
from src.infrastructure.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UserRepository = Depends(Provide[Container.user_repository]),
    secret_key: str = Depends(Provide[Container.config.secret_key]),
    algorithm: str = Depends(Provide[Container.config.algorithm])
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await repository.find_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin or superadmin role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user

async def require_superadmin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require superadmin role"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Superadmin access required"
        )
    return current_user