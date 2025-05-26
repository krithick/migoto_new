from typing import TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from abc import abstractmethod

from src.infrastructure.repositories.base_repository import IRepository
from src.infrastructure.mappers.base_mapper import IMapper

T = TypeVar('T')

class BaseMongoRepository(IRepository[T], Generic[T]):
    """Base MongoDB repository with common operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, mapper: IMapper):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.mapper = mapper
    
    async def find_by_id(self, id: UUID) -> Optional[T]:
        """Find document by ID"""
        doc = await self.collection.find_one({"_id": str(id)})
        return self.mapper.from_dict(doc) if doc else None
    
    async def find_all(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[T]:
        """Find all documents with optional filters"""
        query = filters or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return [self.mapper.from_dict(doc) async for doc in cursor]
    
    async def create(self, entity: T) -> T:
        """Create new document"""
        doc = self.mapper.to_dict(entity)
        await self.collection.insert_one(doc)
        return entity
    
    async def update(self, id: UUID, entity: T) -> Optional[T]:
        """Update existing document"""
        doc = self.mapper.to_dict(entity)
        result = await self.collection.replace_one({"_id": str(id)}, doc)
        return entity if result.modified_count > 0 else None
    
    async def delete(self, id: UUID) -> bool:
        """Delete document by ID"""
        result = await self.collection.delete_one({"_id": str(id)})
        return result.deleted_count > 0
    
    async def exists(self, id: UUID) -> bool:
        """Check if document exists"""
        count = await self.collection.count_documents({"_id": str(id)}, limit=1)
        return count > 0
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count documents with optional filters"""
        query = filters or {}
        return await self.collection.count_documents(query)
    
    async def create_index(self, field: str, unique: bool = False):
        """Create index on field"""
        await self.collection.create_index(field, unique=unique)
    
    async def create_compound_index(self, fields: List[tuple], unique: bool = False):
        """Create compound index on multiple fields"""
        await self.collection.create_index(fields, unique=unique)