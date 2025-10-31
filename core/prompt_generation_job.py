"""Background job manager for async prompt generation"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

class PromptGenerationJobManager:
    """Manages async prompt generation jobs and SSE queues"""
    
    jobs: Dict[str, Dict[str, Any]] = {}
    event_queues: Dict[str, asyncio.Queue] = {}
    
    @classmethod
    def create_job(cls, template_id: str, persona_ids: list) -> str:
        """Create new job and return job_id"""
        job_id = str(uuid4())
        cls.jobs[job_id] = {
            "job_id": job_id,
            "template_id": template_id,
            "persona_ids": persona_ids,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "persona_progress": {},
            "results": None,
            "error": None
        }
        cls.event_queues[job_id] = asyncio.Queue()
        return job_id
    
    @classmethod
    async def send_event(cls, job_id: str, event: Dict[str, Any]):
        """Send SSE event to job queue"""
        if job_id in cls.event_queues:
            await cls.event_queues[job_id].put(event)
    
    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        return cls.jobs.get(job_id)
    
    @classmethod
    def update_job(cls, job_id: str, updates: Dict[str, Any]):
        """Update job data"""
        if job_id in cls.jobs:
            cls.jobs[job_id].update(updates)
    
    @classmethod
    async def get_event_queue(cls, job_id: str) -> Optional[asyncio.Queue]:
        """Get event queue for SSE streaming"""
        # Wait briefly if queue doesn't exist yet (race condition)
        for _ in range(10):
            if job_id in cls.event_queues:
                return cls.event_queues[job_id]
            await asyncio.sleep(0.1)
        return None
    
    @classmethod
    def cleanup_job(cls, job_id: str):
        """Remove job after completion"""
        cls.jobs.pop(job_id, None)
        cls.event_queues.pop(job_id, None)
