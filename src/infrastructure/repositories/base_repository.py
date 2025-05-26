from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """Base repository interface"""
    
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[T]:
        """Find entity by ID"""
        pass
    
    @abstractmethod
    async def find_all(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[T]:
        """Find all entities with optional filters"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def update(self, id: UUID, entity: T) -> Optional[T]:
        """Update existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        pass
    
    @abstractmethod
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count entities with optional filters"""
        pass