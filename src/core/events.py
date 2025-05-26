from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Callable, Any, Type
import asyncio
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

@dataclass
class Event(ABC):
    """Base event class"""
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)

class EventBus:
    """Simple in-memory event bus"""
    
    def __init__(self):
        self._handlers: Dict[Type[Event], List[Callable]] = {}
        self._middleware: List[Callable] = []
    
    def subscribe(self, event_type: Type[Event], handler: Callable):
        """Subscribe a handler to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler {handler.__name__} subscribed to {event_type.__name__}")
    
    def unsubscribe(self, event_type: Type[Event], handler: Callable):
        """Unsubscribe a handler from an event type"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to process all events"""
        self._middleware.append(middleware)
    
    async def publish(self, event: Event):
        """Publish an event to all subscribed handlers"""
        event_type = type(event)
        
        # Run middleware
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(event)
                else:
                    middleware(event)
            except Exception as e:
                logger.error(f"Middleware {middleware.__name__} failed: {e}")
        
        # Run handlers
        if event_type in self._handlers:
            handlers = self._handlers[event_type]
            logger.info(f"Publishing {event_type.__name__} to {len(handlers)} handlers")
            
            # Run handlers concurrently
            tasks = []
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(self._run_handler_async(handler, event))
                else:
                    self._run_handler_sync(handler, event)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Handler {handlers[i].__name__} failed: {result}")
    
    async def _run_handler_async(self, handler: Callable, event: Event):
        """Run async handler with error handling"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Async handler {handler.__name__} failed: {e}")
            raise
    
    def _run_handler_sync(self, handler: Callable, event: Event):
        """Run sync handler with error handling"""
        try:
            handler(event)
        except Exception as e:
            logger.error(f"Sync handler {handler.__name__} failed: {e}")