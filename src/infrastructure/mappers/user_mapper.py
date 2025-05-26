from typing import Dict, Any
from uuid import UUID

from src.domain.user.entities import User, UserRole
from src.domain.user.value_objects import Email, EmployeeId
from src.infrastructure.mappers.base_mapper import IMapper

class UserMapper(IMapper[User, Dict[str, Any]]):
    """Maps between User domain entity and MongoDB document"""
    
    def to_domain(self, document: Dict[str, Any]) -> User:
        """Convert MongoDB document to User entity"""
        return User(
            id=UUID(document["_id"]),
            email=Email(document["email"]),
            emp_id=EmployeeId(document["emp_id"]),
            username=document["username"],
            hashed_password=document["hashed_password"],
            role=UserRole(document["role"]),
            is_active=document.get("is_active", True),
            assignee_emp_id=document.get("assignee_emp_id"),
            assigned_courses=[UUID(c) for c in document.get("assigned_courses", [])],
            managed_users=[UUID(u) for u in document.get("managed_users", [])],
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at"),
            created_by=UUID(document["created_by"]) if document.get("created_by") else None,
            updated_by=UUID(document["updated_by"]) if document.get("updated_by") else None
        )
    
    def to_persistence(self, entity: User) -> Dict[str, Any]:
        """Convert User entity to MongoDB document"""
        return self.to_dict(entity)
    
    def to_dict(self, entity: User) -> Dict[str, Any]:
        """Convert User entity to dictionary"""
        return {
            "_id": str(entity.id),
            "email": str(entity.email),
            "emp_id": str(entity.emp_id),
            "username": entity.username,
            "hashed_password": entity.hashed_password,
            "role": entity.role.value,
            "is_active": entity.is_active,
            "assignee_emp_id": entity.assignee_emp_id,
            "assigned_courses": [str(c) for c in entity.assigned_courses],
            "managed_users": [str(u) for u in entity.managed_users],
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "created_by": str(entity.created_by) if entity.created_by else None,
            "updated_by": str(entity.updated_by) if entity.updated_by else None
        }
    
    def from_dict(self, data: Dict[str, Any]) -> User:
        """Alias for to_domain for consistency"""
        return self.to_domain(data)