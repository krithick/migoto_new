from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.events import Event

class EventStore:
    """Persistent event store using MongoDB"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.events
    
    async def save_event(self, event: Event):
        """Save event to store"""
        event_dict = {
            "_id": str(event.event_id),
            "event_type": event.__class__.__name__,
            "timestamp": event.timestamp,
            "data": self._serialize_event(event)
        }
        await self.collection.insert_one(event_dict)
    
    async def get_events(
        self, 
        aggregate_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve events with filters"""
        query = {}
        
        if aggregate_id:
            query["data.aggregate_id"] = str(aggregate_id)
        
        if event_type:
            query["event_type"] = event_type
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).limit(limit).sort("timestamp", -1)
        return await cursor.to_list(length=limit)
    
    def _serialize_event(self, event: Event) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        data = {}
        for key, value in event.__dict__.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif hasattr(value, '__dict__'):
                data[key] = str(value)
            else:
                data[key] = value
        return data