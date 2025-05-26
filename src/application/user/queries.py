from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

@dataclass
class GetUserByIdQuery:
    user_id: UUID

@dataclass
class GetUserByEmailQuery:
    email: str

@dataclass
class GetUsersByAdminQuery:
    admin_id: UUID
    skip: int = 0
    limit: int = 100

@dataclass
class GetAllUsersQuery:
    skip: int = 0
    limit: int = 100
    role_filter: Optional[str] = None