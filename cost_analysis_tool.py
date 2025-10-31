"""
Comprehensive Cost Analysis Tool for AI Services
Tracks tokens, STT/TTS usage, and generates detailed cost reports
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException, Body, Form
from database import get_db
from models.user_models import UserDB
from core.user import get_current_user

# Cost per unit (update these with current Azure pricing)
PRICING = {
    # OpenAI GPT-4o pricing (per 1K tokens)
    "gpt-4o": {
        "input": 0.005,   # $0.005 per 1K input tokens
        "output": 0.015   # $0.015 per 1K output tokens
    },
    # OpenAI GPT-4 pricing (per 1K tokens)
    "gpt-4": {
        "input": 0.03,    # $0.03 per 1K input tokens
        "output": 0.06    # $0.06 per 1K output tokens
    },
    # Embedding pricing (per 1K tokens)
    "text-embedding-ada-002": {
        "input": 0.0001,  # $0.0001 per 1K tokens
        "output": 0.0     # No output cost for embeddings
    },
    # Speech Services pricing
    "speech": {
        "stt_per_minute": 0.024,      # $0.024 per minute transcribed
        "tts_per_character": 0.000016  # $0.000016 per character synthesized
    },
    # Azure Search pricing (estimated)
    "search": {
        "query_cost": 0.001,  # $0.001 per search query
        "index_cost": 0.0001  # $0.0001 per document indexed
    }
}

@dataclass
class TokenUsage:
    """Track token usage for a single API call"""
    timestamp: str
    operation: str
    model: str
    prompt_tokens: int
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class SpeechUsage:
    """Track STT/TTS usage"""
    timestamp: str
    operation: str  # "stt" or "tts"
    duration_seconds: float = 0.0  # For STT
    character_count: int = 0       # For TTS
    cost_usd: float = 0.0
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ScenarioCreationCost:
    """Track costs for creating a complete scenario"""
    scenario_id: str
    scenario_name: str
    creation_timestamp: str
    user_id: str
    template_source: str  # "file_upload", "text_input", etc.
    
    # Token usage breakdown
    template_analysis_tokens: TokenUsage
    persona_generation_tokens: List[TokenUsage]
    prompt_generation_tokens: List[TokenUsage]
    
    # Total costs
    total_tokens: int
    total_cost_usd: float
    
    # Metadata
    supporting_docs_count: int = 0

@dataclass
class ConversationCost:
    """Track costs for a complete conversation session"""
    session_id: str
    scenario_name: str
    mode: str  # "learn_mode", "assess_mode", "try_mode"
    start_timestamp: str
    user_id: str
    
    # Usage breakdown
    token_usage: List[TokenUsage]
    speech_usage: List[SpeechUsage]
    
    # Optional fields with defaults
    end_timestamp: Optional[str] = None
    search_queries: int = 0
    total_tokens: int = 0
    total_stt_minutes: float = 0.0
    total_tts_characters: int = 0
    total_cost_usd: float = 0.0
    message_count: int = 0
    conversation_duration_minutes: float = 0.0

class CostAnalyzer:
    """Main cost analysis and tracking system"""
    
    def __init__(self, db):
        self.db = db
        self.cost_log_file = Path("cost_analysis_log.json")
        
    def calculate_token_cost(self, usage: TokenUsage) -> float:
        """Calculate cost for token usage"""
        model_pricing = PRICING.get(usage.model, PRICING["gpt-4o"])
        
        input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def calculate_speech_cost(self, usage: SpeechUsage) -> float:
        """Calculate cost for speech services"""
        if usage.operation == "stt":
            return (usage.duration_seconds / 60) * PRICING["speech"]["stt_per_minute"]
        elif usage.operation == "tts":
            return usage.character_count * PRICING["speech"]["tts_per_character"]
        return 0.0
    
    async def log_token_usage(self, usage: TokenUsage) -> TokenUsage:
        """Log token usage and calculate cost"""
        usage.cost_usd = self.calculate_token_cost(usage)
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        
        # Store in database
        await self.db.cost_tracking.insert_one({
            "type": "token_usage",
            "data": asdict(usage),
            "timestamp": datetime.now()
        })
        
        return usage
    
    async def log_speech_usage(self, usage: SpeechUsage) -> SpeechUsage:
        """Log speech usage and calculate cost"""
        usage.cost_usd = self.calculate_speech_cost(usage)
        
        # Store in database
        await self.db.cost_tracking.insert_one({
            "type": "speech_usage", 
            "data": asdict(usage),
            "timestamp": datetime.now()
        })
        
        return usage
    
    async def start_scenario_creation_tracking(self, scenario_name: str, user_id: str, template_source: str) -> str:
        """Start tracking costs for scenario creation"""
        scenario_id = str(uuid.uuid4())
        
        tracking_record = {
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "user_id": user_id,
            "template_source": template_source,
            "start_timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "token_usage": [],
            "total_cost": 0.0
        }
        
        await self.db.scenario_cost_tracking.insert_one(tracking_record)
        return scenario_id
    
    async def add_scenario_token_usage(self, scenario_id: str, usage: TokenUsage):
        """Add token usage to scenario creation tracking"""
        usage = await self.log_token_usage(usage)
        
        await self.db.scenario_cost_tracking.update_one(
            {"scenario_id": scenario_id},
            {
                "$push": {"token_usage": asdict(usage)},
                "$inc": {"total_cost": usage.cost_usd}
            }
        )
    
    async def complete_scenario_creation_tracking(self, scenario_id: str) -> ScenarioCreationCost:
        """Complete scenario creation tracking and generate report"""
        record = await self.db.scenario_cost_tracking.find_one({"scenario_id": scenario_id})
        
        if not record:
            raise ValueError(f"Scenario tracking not found: {scenario_id}")
        
        # Update status
        await self.db.scenario_cost_tracking.update_one(
            {"scenario_id": scenario_id},
            {
                "$set": {
                    "status": "completed",
                    "end_timestamp": datetime.now().isoformat()
                }
            }
        )
        
        # Calculate totals
        total_tokens = sum(usage["total_tokens"] for usage in record["token_usage"])
        total_cost = sum(usage["cost_usd"] for usage in record["token_usage"])
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": record["scenario_name"],
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "token_usage_breakdown": record["token_usage"],
            "creation_duration": record.get("end_timestamp", datetime.now().isoformat())
        }
    
    async def start_conversation_tracking(self, session_id: str, scenario_name: str, mode: str, user_id: str):
        """Start tracking costs for a conversation session"""
        tracking_record = {
            "session_id": session_id,
            "scenario_name": scenario_name,
            "mode": mode,
            "user_id": user_id,
            "start_timestamp": datetime.now().isoformat(),
            "status": "active",
            "token_usage": [],
            "speech_usage": [],
            "search_queries": 0,
            "message_count": 0,
            "total_cost": 0.0
        }
        
        await self.db.conversation_cost_tracking.insert_one(tracking_record)
    
    async def add_conversation_token_usage(self, session_id: str, usage: TokenUsage):
        """Add token usage to conversation tracking"""
        usage = await self.log_token_usage(usage)
        
        await self.db.conversation_cost_tracking.update_one(
            {"session_id": session_id},
            {
                "$push": {"token_usage": asdict(usage)},
                "$inc": {
                    "total_cost": usage.cost_usd,
                    "message_count": 1
                }
            }
        )
    
    async def add_conversation_speech_usage(self, session_id: str, usage: SpeechUsage):
        """Add speech usage to conversation tracking"""
        usage = await self.log_speech_usage(usage)
        
        await self.db.conversation_cost_tracking.update_one(
            {"session_id": session_id},
            {
                "$push": {"speech_usage": asdict(usage)},
                "$inc": {"total_cost": usage.cost_usd}
            }
        )
    
    async def complete_conversation_tracking(self, session_id: str) -> ConversationCost:
        """Complete conversation tracking and generate report"""
        record = await self.db.conversation_cost_tracking.find_one({"session_id": session_id})
        
        if not record:
            raise ValueError(f"Conversation tracking not found: {session_id}")
        
        # Calculate duration
        start_time = datetime.fromisoformat(record["start_timestamp"])
        end_time = datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        # Update status
        await self.db.conversation_cost_tracking.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": "completed",
                    "end_timestamp": end_time.isoformat(),
                    "duration_minutes": duration_minutes
                }
            }
        )
        
        # Calculate totals
        total_tokens = sum(usage["total_tokens"] for usage in record["token_usage"])
        total_stt_minutes = sum(usage["duration_seconds"] / 60 for usage in record["speech_usage"] if usage["operation"] == "stt")
        total_tts_characters = sum(usage["character_count"] for usage in record["speech_usage"] if usage["operation"] == "tts")
        
        return {
            "session_id": session_id,
            "scenario_name": record["scenario_name"],
            "mode": record["mode"],
            "total_tokens": total_tokens,
            "total_stt_minutes": total_stt_minutes,
            "total_tts_characters": total_tts_characters,
            "total_cost_usd": record["total_cost"],
            "duration_minutes": duration_minutes,
            "message_count": record["message_count"],
            "token_usage_breakdown": record["token_usage"],
            "speech_usage_breakdown": record["speech_usage"]
        }
    
    async def generate_cost_report(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate comprehensive cost report for a user and date range"""
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Get scenario creation costs
        scenario_costs = await self.db.scenario_cost_tracking.find({
            "user_id": user_id,
            "start_timestamp": {
                "$gte": start_dt.isoformat(),
                "$lte": end_dt.isoformat()
            }
        }).to_list(length=None)
        
        # Get conversation costs
        conversation_costs = await self.db.conversation_cost_tracking.find({
            "user_id": user_id,
            "start_timestamp": {
                "$gte": start_dt.isoformat(),
                "$lte": end_dt.isoformat()
            }
        }).to_list(length=None)
        
        # Calculate totals
        total_scenario_cost = sum(record.get("total_cost", 0) for record in scenario_costs)
        total_conversation_cost = sum(record.get("total_cost", 0) for record in conversation_costs)
        total_cost = total_scenario_cost + total_conversation_cost
        
        # Token usage breakdown
        total_tokens = 0
        for record in scenario_costs + conversation_costs:
            for usage in record.get("token_usage", []):
                total_tokens += usage.get("total_tokens", 0)
        
        # Speech usage breakdown
        total_stt_minutes = 0
        total_tts_characters = 0
        for record in conversation_costs:
            for usage in record.get("speech_usage", []):
                if usage.get("operation") == "stt":
                    total_stt_minutes += usage.get("duration_seconds", 0) / 60
                elif usage.get("operation") == "tts":
                    total_tts_characters += usage.get("character_count", 0)
        
        return {
            "user_id": user_id,
            "report_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_cost_usd": total_cost,
                "scenario_creation_cost": total_scenario_cost,
                "conversation_cost": total_conversation_cost,
                "scenarios_created": len(scenario_costs),
                "conversations_completed": len(conversation_costs)
            },
            "usage_breakdown": {
                "total_tokens": total_tokens,
                "total_stt_minutes": total_stt_minutes,
                "total_tts_characters": total_tts_characters
            },
            "detailed_scenarios": scenario_costs,
            "detailed_conversations": conversation_costs,
            "generated_at": datetime.now().isoformat()
        }

# FastAPI Router for cost analysis endpoints
router = APIRouter(prefix="/cost-analysis", tags=["Cost Analysis"])

@router.post("/scenario/start-tracking")
async def start_scenario_tracking(
    scenario_name: str = Body(...),
    template_source: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Start tracking costs for scenario creation"""
    analyzer = CostAnalyzer(db)
    scenario_id = await analyzer.start_scenario_creation_tracking(
        scenario_name, str(current_user.id), template_source
    )
    
    return {
        "scenario_id": scenario_id,
        "message": "Scenario cost tracking started",
        "user_id": str(current_user.id)
    }

@router.post("/scenario/{scenario_id}/add-token-usage")
async def add_scenario_token_usage(
    scenario_id: str,
    operation: str = Body(...),
    model: str = Body(...),
    prompt_tokens: int = Body(...),
    completion_tokens: int = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Add token usage to scenario creation tracking"""
    analyzer = CostAnalyzer(db)
    
    usage = TokenUsage(
        timestamp=datetime.now().isoformat(),
        operation=operation,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        user_id=str(current_user.id)
    )
    
    await analyzer.add_scenario_token_usage(scenario_id, usage)
    
    return {
        "message": "Token usage added to scenario tracking",
        "cost_usd": analyzer.calculate_token_cost(usage)
    }

@router.post("/scenario/{scenario_id}/complete")
async def complete_scenario_tracking(
    scenario_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Complete scenario creation tracking and get final report"""
    analyzer = CostAnalyzer(db)
    report = await analyzer.complete_scenario_creation_tracking(scenario_id)
    
    return {
        "message": "Scenario creation tracking completed",
        "report": report
    }

@router.post("/conversation/start-tracking")
async def start_conversation_tracking(
    session_id: str = Body(...),
    scenario_name: str = Body(...),
    mode: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Start tracking costs for a conversation session"""
    analyzer = CostAnalyzer(db)
    await analyzer.start_conversation_tracking(
        session_id, scenario_name, mode, str(current_user.id)
    )
    
    return {
        "message": "Conversation cost tracking started",
        "session_id": session_id
    }

@router.post("/conversation/{session_id}/add-token-usage")
async def add_conversation_token_usage(
    session_id: str,
    operation: str = Body(...),
    model: str = Body(...),
    prompt_tokens: int = Body(...),
    completion_tokens: int = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Add token usage to conversation tracking"""
    analyzer = CostAnalyzer(db)
    
    usage = TokenUsage(
        timestamp=datetime.now().isoformat(),
        operation=operation,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        user_id=str(current_user.id),
        session_id=session_id
    )
    
    await analyzer.add_conversation_token_usage(session_id, usage)
    
    return {
        "message": "Token usage added to conversation tracking",
        "cost_usd": analyzer.calculate_token_cost(usage)
    }

@router.post("/conversation/{session_id}/add-speech-usage")
async def add_conversation_speech_usage(
    session_id: str,
    operation: str = Body(...),  # "stt" or "tts"
    duration_seconds: float = Body(0.0),
    character_count: int = Body(0),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Add speech usage to conversation tracking"""
    analyzer = CostAnalyzer(db)
    
    usage = SpeechUsage(
        timestamp=datetime.now().isoformat(),
        operation=operation,
        duration_seconds=duration_seconds,
        character_count=character_count,
        user_id=str(current_user.id),
        session_id=session_id
    )
    
    await analyzer.add_conversation_speech_usage(session_id, usage)
    
    return {
        "message": f"{operation.upper()} usage added to conversation tracking",
        "cost_usd": analyzer.calculate_speech_cost(usage)
    }

@router.post("/conversation/{session_id}/complete")
async def complete_conversation_tracking(
    session_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Complete conversation tracking and get final report"""
    analyzer = CostAnalyzer(db)
    report = await analyzer.complete_conversation_tracking(session_id)
    
    return {
        "message": "Conversation tracking completed",
        "report": report
    }

@router.get("/report")
async def generate_cost_report(
    start_date: str,
    end_date: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Generate comprehensive cost report for date range"""
    analyzer = CostAnalyzer(db)
    report = await analyzer.generate_cost_report(
        str(current_user.id), start_date, end_date
    )
    
    return report

@router.get("/pricing")
async def get_current_pricing():
    """Get current pricing information"""
    return {
        "pricing": PRICING,
        "currency": "USD",
        "last_updated": "2024-01-15",
        "note": "Prices are estimates based on Azure pricing. Update PRICING constant for current rates."
    }

# Utility functions for integration with existing systems

def create_token_usage_from_response(response, operation: str, user_id: str = None, session_id: str = None) -> TokenUsage:
    """Create TokenUsage object from OpenAI response (compatible with existing log_token_usage)"""
    if hasattr(response, 'usage') and response.usage:
        usage = response.usage
        return TokenUsage(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            model=getattr(response, 'model', 'gpt-4o'),
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=getattr(usage, 'completion_tokens', 0),
            total_tokens=usage.total_tokens,
            user_id=user_id,
            session_id=session_id
        )
    return None

async def enhanced_log_token_usage(response, operation: str, user_id: str = None, session_id: str = None, db = None):
    """Enhanced version of log_token_usage that also tracks costs"""
    # Original logging (keep existing functionality)
    from core.simple_token_logger import log_token_usage
    log_token_usage(response, operation, user_id)
    
    # Enhanced cost tracking
    if db:
        usage = create_token_usage_from_response(response, operation, user_id, session_id)
        if usage:
            analyzer = CostAnalyzer(db)
            await analyzer.log_token_usage(usage)
            
            # If this is part of a conversation, add to conversation tracking
            if session_id:
                try:
                    await analyzer.add_conversation_token_usage(session_id, usage)
                except:
                    pass  # Conversation tracking might not be started
    
    return usage

# Export main classes and functions
__all__ = [
    'CostAnalyzer', 
    'TokenUsage', 
    'SpeechUsage', 
    'ScenarioCreationCost', 
    'ConversationCost',
    'PRICING',
    'router',
    'enhanced_log_token_usage',
    'create_token_usage_from_response'
]