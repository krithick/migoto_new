"""
Integration Script for Cost Tracking
Adds cost tracking to existing chat and scenario generation systems
"""

import asyncio
from datetime import datetime
from typing import Optional, Any
from cost_analysis_tool import CostAnalyzer, TokenUsage, SpeechUsage, enhanced_log_token_usage

class CostTrackingIntegration:
    """Integration helper for adding cost tracking to existing systems"""
    
    def __init__(self, db):
        self.db = db
        self.analyzer = CostAnalyzer(db)
        self.active_sessions = {}  # Track active cost tracking sessions
    
    async def start_scenario_cost_tracking(self, scenario_name: str, user_id: str, template_source: str = "api") -> str:
        """Start cost tracking for scenario creation"""
        scenario_id = await self.analyzer.start_scenario_creation_tracking(
            scenario_name, user_id, template_source
        )
        print(f"💰 Started cost tracking for scenario: {scenario_name} (ID: {scenario_id})")
        return scenario_id
    
    async def track_scenario_token_usage(self, scenario_id: str, response, operation: str, user_id: str):
        """Track token usage for scenario creation"""
        if hasattr(response, 'usage') and response.usage:
            usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation=operation,
                model=getattr(response, 'model', 'gpt-4o'),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=getattr(response.usage, 'completion_tokens', 0),
                total_tokens=response.usage.total_tokens,
                user_id=user_id
            )
            
            await self.analyzer.add_scenario_token_usage(scenario_id, usage)
            print(f"📊 Tracked {usage.total_tokens} tokens for {operation} (Cost: ${usage.cost_usd:.4f})")
    
    async def complete_scenario_tracking(self, scenario_id: str) -> dict:
        """Complete scenario cost tracking"""
        report = await self.analyzer.complete_scenario_creation_tracking(scenario_id)
        print(f"✅ Scenario creation completed. Total cost: ${report['total_cost_usd']:.4f}")
        return report
    
    async def start_conversation_cost_tracking(self, session_id: str, scenario_name: str, mode: str, user_id: str):
        """Start cost tracking for conversation"""
        await self.analyzer.start_conversation_tracking(session_id, scenario_name, mode, user_id)
        self.active_sessions[session_id] = {
            "scenario_name": scenario_name,
            "mode": mode,
            "user_id": user_id,
            "start_time": datetime.now()
        }
        print(f"💬 Started conversation cost tracking: {session_id}")
    
    async def track_conversation_token_usage(self, session_id: str, response, operation: str):
        """Track token usage for conversation"""
        if session_id not in self.active_sessions:
            print(f"⚠️ No active cost tracking for session: {session_id}")
            return
        
        session_info = self.active_sessions[session_id]
        
        if hasattr(response, 'usage') and response.usage:
            usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation=operation,
                model=getattr(response, 'model', 'gpt-4o'),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=getattr(response.usage, 'completion_tokens', 0),
                total_tokens=response.usage.total_tokens,
                user_id=session_info["user_id"],
                session_id=session_id
            )
            
            await self.analyzer.add_conversation_token_usage(session_id, usage)
            print(f"💬 Tracked {usage.total_tokens} tokens for conversation (Cost: ${usage.cost_usd:.4f})")
    
    async def track_stt_usage(self, session_id: str, audio_duration_seconds: float):
        """Track Speech-to-Text usage"""
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        
        usage = SpeechUsage(
            timestamp=datetime.now().isoformat(),
            operation="stt",
            duration_seconds=audio_duration_seconds,
            user_id=session_info["user_id"],
            session_id=session_id
        )
        
        await self.analyzer.add_conversation_speech_usage(session_id, usage)
        print(f"🎤 Tracked {audio_duration_seconds:.1f}s STT (Cost: ${usage.cost_usd:.4f})")
    
    async def track_tts_usage(self, session_id: str, text_length: int):
        """Track Text-to-Speech usage"""
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        
        usage = SpeechUsage(
            timestamp=datetime.now().isoformat(),
            operation="tts",
            character_count=text_length,
            user_id=session_info["user_id"],
            session_id=session_id
        )
        
        await self.analyzer.add_conversation_speech_usage(session_id, usage)
        print(f"🔊 Tracked {text_length} chars TTS (Cost: ${usage.cost_usd:.4f})")
    
    async def complete_conversation_tracking(self, session_id: str) -> dict:
        """Complete conversation cost tracking"""
        if session_id in self.active_sessions:
            report = await self.analyzer.complete_conversation_tracking(session_id)
            del self.active_sessions[session_id]
            print(f"✅ Conversation completed. Total cost: ${report['total_cost_usd']:.4f}")
            return report
        return {}

# Integration functions for existing code

async def integrate_with_scenario_generator():
    """Example integration with scenario generator"""
    print("🔧 Integrating cost tracking with scenario generator...")
    
    # This is how you would modify your existing scenario_generator.py
    integration_code = '''
# Add to scenario_generator.py imports:
from integrate_cost_tracking import CostTrackingIntegration

# Modify your scenario generation endpoints:

@router.post("/analyze-scenario-with-cost-tracking")
async def analyze_scenario_with_cost_tracking(
    scenario_document: str = Body(...),
    scenario_name: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Analyze scenario with cost tracking"""
    
    # Initialize cost tracking
    cost_tracker = CostTrackingIntegration(db)
    scenario_id = await cost_tracker.start_scenario_cost_tracking(
        scenario_name, str(current_user.id), "api_analysis"
    )
    
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Step 1: Extract scenario info with cost tracking
        template_data = await generator.extract_scenario_info(scenario_document)
        # Note: You need to modify extract_scenario_info to return the response object
        # await cost_tracker.track_scenario_token_usage(scenario_id, response, "scenario_analysis", str(current_user.id))
        
        # Step 2: Generate personas with cost tracking
        personas = await generator.generate_personas_from_template(template_data)
        # await cost_tracker.track_scenario_token_usage(scenario_id, response, "persona_generation", str(current_user.id))
        
        # Step 3: Generate prompts with cost tracking
        learn_mode = await generator.generate_learn_mode_from_template(template_data)
        assess_mode = await generator.generate_assess_mode_from_template(template_data)
        try_mode = await generator.generate_try_mode_from_template(template_data)
        # Track each prompt generation...
        
        # Complete cost tracking
        cost_report = await cost_tracker.complete_scenario_tracking(scenario_id)
        
        return {
            "template_data": template_data,
            "personas": personas,
            "prompts": {
                "learn_mode": learn_mode,
                "assess_mode": assess_mode,
                "try_mode": try_mode
            },
            "cost_report": cost_report
        }
        
    except Exception as e:
        # Still complete tracking even on error
        await cost_tracker.complete_scenario_tracking(scenario_id)
        raise e
    '''
    
    print("📝 Integration code example generated")
    return integration_code

async def integrate_with_chat_system():
    """Example integration with chat system"""
    print("🔧 Integrating cost tracking with chat system...")
    
    integration_code = '''
# Add to chat.py imports:
from integrate_cost_tracking import CostTrackingIntegration

# Modify your chat initialization:

@router.post("/chat/initialize-with-cost-tracking")
async def initialize_chat_with_cost_tracking(
    avatar_interaction_id: UUID = Form(...),
    mode: str = Form(...),
    scenario_name: str = Form(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Initialize chat with cost tracking"""
    
    # Initialize chat session (existing code)
    session = await initialize_chat_session(db, avatar_interaction_id=avatar_interaction_id, mode=mode, current_user=current_user.id)
    
    # Initialize cost tracking
    cost_tracker = CostTrackingIntegration(db)
    await cost_tracker.start_conversation_cost_tracking(
        session.id, scenario_name, mode, str(current_user.id)
    )
    
    return {
        "session_id": session.id,
        "cost_tracking_enabled": True,
        "scenario_name": scenario_name,
        "mode": mode
    }

# Modify your chat stream endpoint:

@router.get("/chat/stream-with-cost-tracking")
async def chat_stream_with_cost_tracking(
    id: str = Query(...),
    db: Any = Depends(get_db)
):
    """Chat stream with cost tracking"""
    
    cost_tracker = CostTrackingIntegration(db)
    
    # Your existing chat stream logic...
    # When you get AI response:
    # await cost_tracker.track_conversation_token_usage(id, response, "chat_response")
    
    # When you process STT:
    # await cost_tracker.track_stt_usage(id, audio_duration_seconds)
    
    # When you generate TTS:
    # await cost_tracker.track_tts_usage(id, len(response_text))
    
    # When conversation ends:
    # cost_report = await cost_tracker.complete_conversation_tracking(id)
    '''
    
    print("📝 Chat integration code example generated")
    return integration_code

# Utility functions for easy integration

def create_enhanced_log_function(db):
    """Create enhanced logging function for existing code"""
    async def enhanced_log(response, operation: str, user_id: str = None, session_id: str = None):
        """Enhanced logging with cost tracking"""
        # Original logging
        from core.simple_token_logger import log_token_usage
        log_token_usage(response, operation, user_id)
        
        # Cost tracking
        if hasattr(response, 'usage') and response.usage:
            usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation=operation,
                model=getattr(response, 'model', 'gpt-4o'),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=getattr(response.usage, 'completion_tokens', 0),
                total_tokens=response.usage.total_tokens,
                user_id=user_id,
                session_id=session_id
            )
            
            analyzer = CostAnalyzer(db)
            await analyzer.log_token_usage(usage)
            
            return usage
    
    return enhanced_log

async def test_integration():
    """Test the cost tracking integration"""
    print("🧪 Testing cost tracking integration...")
    
    # Mock database for testing
    class MockDB:
        def __init__(self):
            self.cost_tracking = MockCollection()
            self.scenario_cost_tracking = MockCollection()
            self.conversation_cost_tracking = MockCollection()
    
    class MockCollection:
        def __init__(self):
            self.data = []
        
        async def insert_one(self, doc):
            self.data.append(doc)
            return type('Result', (), {'inserted_id': 'mock_id'})()
        
        async def find_one(self, query):
            return self.data[0] if self.data else None
        
        async def update_one(self, query, update):
            return type('Result', (), {'modified_count': 1})()
        
        async def find(self, query):
            return type('Cursor', (), {
                'to_list': lambda length: asyncio.create_task(asyncio.coroutine(lambda: self.data)()),
                'sort': lambda field, direction: self
            })()
    
    # Test scenario cost tracking
    db = MockDB()
    cost_tracker = CostTrackingIntegration(db)
    
    # Test scenario creation tracking
    scenario_id = await cost_tracker.start_scenario_cost_tracking("Test Scenario", "test_user")
    print(f"✅ Started scenario tracking: {scenario_id}")
    
    # Test conversation tracking
    await cost_tracker.start_conversation_cost_tracking("test_session", "Test Scenario", "assess_mode", "test_user")
    print("✅ Started conversation tracking")
    
    # Test STT/TTS tracking
    await cost_tracker.track_stt_usage("test_session", 30.0)  # 30 seconds
    await cost_tracker.track_tts_usage("test_session", 500)   # 500 characters
    print("✅ Tracked speech usage")
    
    print("🎉 Integration test completed successfully!")

if __name__ == "__main__":
    print("🚀 Cost Tracking Integration Tool")
    print("=" * 40)
    
    # Generate integration examples
    asyncio.run(integrate_with_scenario_generator())
    asyncio.run(integrate_with_chat_system())
    
    # Run test
    asyncio.run(test_integration())
    
    print("\n📋 INTEGRATION STEPS:")
    print("1. Add cost tracking imports to your existing files")
    print("2. Initialize CostTrackingIntegration in your endpoints")
    print("3. Add cost tracking calls around API usage")
    print("4. Use the dashboard to monitor costs")
    print("\n💡 TIP: Start with one endpoint and gradually add to others")