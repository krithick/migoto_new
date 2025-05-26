from abc import ABC, abstractmethod
from typing import TypeVar, Dict, Any, Generic

TEntity = TypeVar('TEntity')
TModel = TypeVar('TModel')

class IMapper(ABC, Generic[TEntity, TModel]):
    """Base mapper interface for converting between domain entities and persistence models"""
    
    @abstractmethod
    def to_domain(self, model: TModel) -> TEntity:
        """Convert persistence model to domain entity"""
        pass
    
    @abstractmethod
    def to_persistence(self, entity: TEntity) -> TModel:
        """Convert domain entity to persistence model"""
        pass
    
    @abstractmethod
    def to_dict(self, entity: TEntity) -> Dict[str, Any]:
        """Convert domain entity to dictionary"""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> TEntity:
        """Convert dictionary to domain entity"""
        pass