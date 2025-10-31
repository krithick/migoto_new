"""
Scenario Cost Testing Script
Creates a complete scenario with chat interaction and measures all associated costs
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Import your existing modules
from cost_analysis_tool import CostAnalyzer, TokenUsage, SpeechUsage, PRICING
from database import get_db
from scenario_generator import EnhancedScenarioGenerator
from dynamic_chat import get_chat_factory, initialize_chat_session

class ScenarioCostTester:
    """Complete scenario testing with cost measurement"""
    
    def __init__(self):
        self.cost_analyzer = None
        self.db = None
        self.results = {}
        
    async def initialize(self):
        """Initialize database connection and cost analyzer"""
        self.db = await get_db()
        self.cost_analyzer = CostAnalyzer(self.db)
        
    async def test_scenario_creation(self, scenario_description: str, scenario_name: str) -> Dict[str, Any]:
        """Test complete scenario creation and measure costs"""
        print(f"🚀 Starting scenario creation test: {scenario_name}")
        
        # Start cost tracking
        scenario_id = await self.cost_analyzer.start_scenario_creation_tracking(
            scenario_name, "test_user", "api_test"
        )
        
        start_time = time.time()
        
        try:
            # Initialize scenario generator
            from openai import AsyncAzureOpenAI
            import os
            
            azure_openai_client = AsyncAzureOpenAI(
                api_key=os.getenv("api_key"),
                api_version=os.getenv("api_version"),
                azure_endpoint=os.getenv("endpoint")
            )
            
            generator = EnhancedScenarioGenerator(azure_openai_client)
            
            # Step 1: Extract scenario info (measure tokens)
            print("📊 Step 1: Analyzing scenario...")
            template_data = await generator.extract_scenario_info(scenario_description)
            
            # Log token usage for scenario analysis
            # Note: You'll need to modify extract_scenario_info to return response object
            # For now, we'll estimate based on input/output length
            analysis_usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation="scenario_analysis",
                model="gpt-4o",
                prompt_tokens=len(scenario_description.split()) * 1.3,  # Rough estimate
                completion_tokens=len(str(template_data).split()) * 1.3,
                user_id="test_user"
            )
            await self.cost_analyzer.add_scenario_token_usage(scenario_id, analysis_usage)
            
            # Step 2: Generate personas (measure tokens)
            print("👥 Step 2: Generating personas...")
            personas = await generator.generate_personas_from_template(template_data)
            
            persona_usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation="persona_generation",
                model="gpt-4o",
                prompt_tokens=len(str(template_data).split()) * 1.3,
                completion_tokens=len(str(personas).split()) * 1.3,
                user_id="test_user"
            )
            await self.cost_analyzer.add_scenario_token_usage(scenario_id, persona_usage)
            
            # Step 3: Generate prompts (measure tokens)
            print("📝 Step 3: Generating prompts...")
            learn_mode_prompt = await generator.generate_learn_mode_from_template(template_data)
            assess_mode_prompt = await generator.generate_assess_mode_from_template(template_data)
            try_mode_prompt = await generator.generate_try_mode_from_template(template_data)
            
            prompt_usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                operation="prompt_generation",
                model="gpt-4o",
                prompt_tokens=len(str(template_data).split()) * 1.3,
                completion_tokens=(len(learn_mode_prompt.split()) + len(assess_mode_prompt.split()) + len(try_mode_prompt.split())) * 1.3,
                user_id="test_user"
            )
            await self.cost_analyzer.add_scenario_token_usage(scenario_id, prompt_usage)
            
            creation_time = time.time() - start_time
            
            # Complete scenario tracking
            scenario_report = await self.cost_analyzer.complete_scenario_creation_tracking(scenario_id)
            
            print(f"✅ Scenario creation completed in {creation_time:.2f} seconds")
            print(f"💰 Total cost: ${scenario_report['total_cost_usd']:.4f}")
            
            return {
                "scenario_id": scenario_id,
                "creation_time_seconds": creation_time,
                "cost_report": scenario_report,
                "generated_content": {
                    "template_data": template_data,
                    "personas": personas,
                    "prompts": {
                        "learn_mode": learn_mode_prompt[:200] + "...",
                        "assess_mode": assess_mode_prompt[:200] + "...",
                        "try_mode": try_mode_prompt[:200] + "..."
                    }
                }
            }
            
        except Exception as e:
            print(f"❌ Error in scenario creation: {e}")
            return {"error": str(e), "scenario_id": scenario_id}
    
    async def test_conversation_session(self, scenario_name: str, mode: str = "assess_mode", message_count: int = 5) -> Dict[str, Any]:
        """Test a complete conversation session and measure costs"""
        print(f"💬 Starting conversation test: {scenario_name} ({mode})")
        
        session_id = f"test_session_{int(time.time())}"
        
        # Start conversation tracking
        await self.cost_analyzer.start_conversation_tracking(
            session_id, scenario_name, mode, "test_user"
        )
        
        start_time = time.time()
        
        try:
            # Simulate conversation messages
            test_messages = [
                "Hello, I need help with this situation.",
                "Can you explain the process to me?",
                "What should I do if there are complications?",
                "How do I handle customer objections?",
                "Thank you for your help."
            ]
            
            total_stt_duration = 0.0
            total_tts_characters = 0
            
            for i, message in enumerate(test_messages[:message_count]):
                print(f"📨 Message {i+1}: {message[:50]}...")
                
                # Simulate STT (Speech-to-Text) usage
                stt_duration = len(message) * 0.1  # Rough estimate: 0.1 seconds per character
                total_stt_duration += stt_duration
                
                stt_usage = SpeechUsage(
                    timestamp=datetime.now().isoformat(),
                    operation="stt",
                    duration_seconds=stt_duration,
                    session_id=session_id,
                    user_id="test_user"
                )
                await self.cost_analyzer.add_conversation_speech_usage(session_id, stt_usage)
                
                # Simulate AI response token usage
                response_length = len(message) * 2  # AI response roughly 2x input length
                
                token_usage = TokenUsage(
                    timestamp=datetime.now().isoformat(),
                    operation="chat_response",
                    model="gpt-4o",
                    prompt_tokens=len(message.split()) * 1.3,
                    completion_tokens=response_length * 0.75,  # Rough token estimate
                    session_id=session_id,
                    user_id="test_user"
                )
                await self.cost_analyzer.add_conversation_token_usage(session_id, token_usage)
                
                # Simulate TTS (Text-to-Speech) usage
                tts_characters = response_length
                total_tts_characters += tts_characters
                
                tts_usage = SpeechUsage(
                    timestamp=datetime.now().isoformat(),
                    operation="tts",
                    character_count=tts_characters,
                    session_id=session_id,
                    user_id="test_user"
                )
                await self.cost_analyzer.add_conversation_speech_usage(session_id, tts_usage)
                
                # Small delay to simulate real conversation
                await asyncio.sleep(0.5)
            
            conversation_time = time.time() - start_time
            
            # Complete conversation tracking
            conversation_report = await self.cost_analyzer.complete_conversation_tracking(session_id)
            
            print(f"✅ Conversation completed in {conversation_time:.2f} seconds")
            print(f"💰 Total cost: ${conversation_report['total_cost_usd']:.4f}")
            print(f"🎤 STT: {total_stt_duration:.1f} seconds")
            print(f"🔊 TTS: {total_tts_characters} characters")
            
            return {
                "session_id": session_id,
                "conversation_time_seconds": conversation_time,
                "cost_report": conversation_report,
                "usage_summary": {
                    "messages_sent": message_count,
                    "total_stt_seconds": total_stt_duration,
                    "total_tts_characters": total_tts_characters
                }
            }
            
        except Exception as e:
            print(f"❌ Error in conversation: {e}")
            return {"error": str(e), "session_id": session_id}
    
    async def run_complete_test(self, scenario_description: str, scenario_name: str) -> Dict[str, Any]:
        """Run complete test: scenario creation + conversation + cost analysis"""
        print("🧪 Starting Complete Scenario Cost Test")
        print("=" * 50)
        
        await self.initialize()
        
        # Test 1: Scenario Creation
        scenario_result = await self.test_scenario_creation(scenario_description, scenario_name)
        
        # Test 2: Conversation Session (Assess Mode)
        conversation_result = await self.test_conversation_session(scenario_name, "assess_mode", 5)
        
        # Test 3: Generate Cost Report
        end_date = datetime.now().isoformat()
        start_date = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
        
        cost_report = await self.cost_analyzer.generate_cost_report("test_user", start_date, end_date)
        
        # Calculate total costs
        total_scenario_cost = scenario_result.get("cost_report", {}).get("total_cost_usd", 0)
        total_conversation_cost = conversation_result.get("cost_report", {}).get("total_cost_usd", 0)
        total_cost = total_scenario_cost + total_conversation_cost
        
        print("\n📊 COMPLETE TEST RESULTS")
        print("=" * 50)
        print(f"Scenario Creation Cost: ${total_scenario_cost:.4f}")
        print(f"Conversation Cost: ${total_conversation_cost:.4f}")
        print(f"TOTAL COST: ${total_cost:.4f}")
        
        return {
            "test_completed_at": datetime.now().isoformat(),
            "scenario_name": scenario_name,
            "total_cost_usd": total_cost,
            "breakdown": {
                "scenario_creation": scenario_result,
                "conversation_session": conversation_result,
                "full_cost_report": cost_report
            },
            "cost_per_component": {
                "scenario_creation": total_scenario_cost,
                "conversation": total_conversation_cost,
                "tokens_total": cost_report.get("usage_breakdown", {}).get("total_tokens", 0),
                "stt_minutes": cost_report.get("usage_breakdown", {}).get("total_stt_minutes", 0),
                "tts_characters": cost_report.get("usage_breakdown", {}).get("total_tts_characters", 0)
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scenario_cost_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
        return filename

# Predefined test scenarios
TEST_SCENARIOS = {
    "customer_service": {
        "name": "Customer Service Training",
        "description": """
        Create a customer service training scenario where employees learn to handle difficult customer complaints.
        The scenario should include:
        - A frustrated customer with a billing issue
        - Multiple escalation levels
        - Empathy and problem-solving techniques
        - De-escalation strategies
        The AI should play a customer who is initially angry but can be calmed down with proper techniques.
        """
    },
    "sales_training": {
        "name": "Sales Conversation Training", 
        "description": """
        Create a sales training scenario for insurance agents learning to sell life insurance policies.
        The scenario should include:
        - A potential customer who is hesitant about life insurance
        - Objection handling techniques
        - Needs assessment questions
        - Product presentation skills
        The AI should play a customer with specific concerns about cost and coverage.
        """
    },
    "dei_training": {
        "name": "DEI Workplace Training",
        "description": """
        Create a diversity, equity, and inclusion training scenario for managers.
        The scenario should include:
        - A workplace situation involving unconscious bias
        - Inclusive communication techniques
        - Conflict resolution approaches
        - Cultural sensitivity awareness
        The AI should play a team member experiencing workplace bias.
        """
    }
}

async def run_test_scenario(scenario_key: str = "customer_service"):
    """Run a predefined test scenario"""
    if scenario_key not in TEST_SCENARIOS:
        print(f"❌ Unknown scenario: {scenario_key}")
        print(f"Available scenarios: {list(TEST_SCENARIOS.keys())}")
        return
    
    scenario = TEST_SCENARIOS[scenario_key]
    tester = ScenarioCostTester()
    
    results = await tester.run_complete_test(
        scenario["description"], 
        scenario["name"]
    )
    
    # Save results
    filename = tester.save_results(results)
    
    return results, filename

async def run_custom_test(scenario_name: str, scenario_description: str):
    """Run test with custom scenario"""
    tester = ScenarioCostTester()
    
    results = await tester.run_complete_test(scenario_description, scenario_name)
    
    # Save results
    filename = tester.save_results(results)
    
    return results, filename

def print_pricing_info():
    """Print current pricing information"""
    print("💰 CURRENT PRICING INFORMATION")
    print("=" * 40)
    
    for service, pricing in PRICING.items():
        print(f"\n{service.upper()}:")
        for metric, cost in pricing.items():
            print(f"  {metric}: ${cost}")
    
    print("\n📝 COST ESTIMATION EXAMPLES:")
    print("- 1000 tokens (GPT-4o): ~$0.005-0.015")
    print("- 1 minute STT: ~$0.024")
    print("- 1000 characters TTS: ~$0.016")
    print("- Typical scenario creation: ~$0.10-0.50")
    print("- 10-message conversation: ~$0.05-0.20")

if __name__ == "__main__":
    import sys
    
    print("🧪 Scenario Cost Testing Tool")
    print("=" * 40)
    
    # Print pricing info
    print_pricing_info()
    
    if len(sys.argv) > 1:
        scenario_key = sys.argv[1]
        print(f"\n🚀 Running test scenario: {scenario_key}")
        results, filename = asyncio.run(run_test_scenario(scenario_key))
    else:
        print("\n🚀 Running default test scenario: customer_service")
        results, filename = asyncio.run(run_test_scenario("customer_service"))
    
    print(f"\n✅ Test completed! Results saved to: {filename}")
    print(f"💰 Total cost: ${results['total_cost_usd']:.4f}")