from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.application.common.command import Command
from src.application.common.query import Query

TCommand = TypeVar('TCommand', bound=Command)
TQuery = TypeVar('TQuery', bound=Query)
TResult = TypeVar('TResult')

class ICommandHandler(ABC, Generic[TCommand, TResult]):
    """Base command handler interface"""
    
    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """Handle the command"""
        pass

class IQueryHandler(ABC, Generic[TQuery, TResult]):
    """Base query handler interface"""
    
    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """Handle the query"""
        pass