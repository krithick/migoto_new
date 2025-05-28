from typing import Optional, List, Dict, Any
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.user.entities import User, UserRole
from src.domain.user.value_objects import Email, EmployeeId
from src.infrastructure.repositories.base_mongo_repository import BaseMongoRepository
from src.infrastructure.mappers.user_mapper import UserMapper

class UserRepository(BaseMongoRepository[User]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", UserMapper())
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        doc = await self.collection.find_one({"email": email})
        return self.mapper.from_dict(doc) if doc else None
    
    async def find_by_emp_id(self, emp_id: str) -> Optional[User]:
        """Find user by employee ID"""
        doc = await self.collection.find_one({"emp_id": emp_id})
        return self.mapper.from_dict(doc) if doc else None
    
    async def find_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Find users by role"""
        cursor = self.collection.find({"role": role.value}).skip(skip).limit(limit)
        return [self.mapper.from_dict(doc) async for doc in cursor]
    
    # async def find_by_admin(self, admin_id: UUID) -> List[User]:
    #     """Find users managed by specific admin"""
    #     # Find admin first to get their emp_id
    #     admin = await self.find_by_id(admin_id)
    #     if not admin or admin.role != UserRole.ADMIN:
    #         return []
        
    #     # Find users assigned to this admin
    #     cursor = self.collection.find({"assignee_emp_id": admin.emp_id})
    #     return [self.mapper.from_dict(doc) async for doc in cursor]
    
    async def find_by_admin(self, admin_id: UUID) -> List[User]:
        """Find users managed by specific admin using managed_users field"""
        # Get admin document
        admin_doc = await self.collection.find_one({"_id": str(admin_id)})
    
        if not admin_doc or admin_doc.get("role") != UserRole.ADMIN.value:
            return []
    
        # Get managed user IDs from admin document
        managed_user_ids = admin_doc.get("managed_users", [])
    
        if not managed_user_ids:
            return []
    
        # Find all users whose IDs are in managed_users list
        cursor = self.collection.find({"_id": {"$in": managed_user_ids}})
        return [self.mapper.from_dict(doc) async for doc in cursor]
    
    async def add_managed_user(self, admin_id: UUID, user_id: UUID) -> bool:
        """Add user to admin's managed users list"""
        result = await self.collection.update_one(
            {"_id": str(admin_id)},
            {"$addToSet": {"managed_users": str(user_id)}}
        )
        return result.modified_count > 0
    
    async def remove_managed_user(self, admin_id: UUID, user_id: UUID) -> bool:
        """Remove user from admin's managed users list"""
        result = await self.collection.update_one(
            {"_id": str(admin_id)},
            {"$pull": {"managed_users": str(user_id)}}
        )
        return result.modified_count > 0
    
    async def remove_user_from_all_admins(self, user_id: UUID) -> int:
        """Remove user from all admin's managed users lists"""
        result = await self.collection.update_many(
            {"managed_users": str(user_id)},
            {"$pull": {"managed_users": str(user_id)}}
        )
        return result.modified_count
    
    async def add_course_assignment(self, user_id: UUID, course_id: UUID) -> bool:
        """Add course to user's assigned courses"""
        result = await self.collection.update_one(
            {"_id": str(user_id)},
            {"$addToSet": {"assigned_courses": str(course_id)}}
        )
        return result.modified_count > 0
    
    async def remove_course_assignment(self, user_id: UUID, course_id: UUID) -> bool:
        """Remove course from user's assigned courses"""
        result = await self.collection.update_one(
            {"_id": str(user_id)},
            {"$pull": {"assigned_courses": str(course_id)}}
        )
        return result.modified_count > 0
    
    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role"""
        return await self.collection.count_documents({"role": role.value})