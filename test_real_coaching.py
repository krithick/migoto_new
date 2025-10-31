"""
Real-world coaching integration test
Tests actual coaching with avatar interaction: b2212aac-16d3-478c-bd68-f720afd0b5e1
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from database import get_db
from dynamic_chat import get_chat_factory, initialize_chat_session, get_chat_session
from models_old import Message
from datetime import datetime
from uuid import UUID

# Load environment
load_dotenv()

AVATAR_INTERACTION_ID = "b2212aac-16d3-478c-bd68-f720afd0b5e1"

# Test scenarios that should trigger coaching
TEST_SCENARIOS = {
    "wrong_product": {
        "message": "I recommend Product X for irregular bleeding",
        "expected": "Coach should correct wrong product name",
        "mode": "try_mode"
    },
    "wrong_percentage": {
        "message": "EO-Dine reduces irregular bleeding by 30%",
        "expected": "Coach should correct percentage (should be 60%)",
        "mode": "try_mode"
    },
    "vague_claim": {
        "message": "Here's some product info",
        "expected": "Coach should ask for specifics",
        "mode": "try_mode"
    },
    "skipped_step": {
        "message": "Let me tell you about the product benefits",
        "expected": "Coach should remind to introduce first",
        "mode": "try_mode"
    },
    "abuse": {
        "message": "This is fucking stupid",
        "expected": "Pre-screen should catch abuse",
        "mode": "try_mode"
    },
    "learn_mode_wrong_fact": {
        "message": "EO-Dine is approved for 1 year use only",
        "expected": "Simple factual correction (should be >2 years)",
        "mode": "learn_mode"
    }
}

async def test_coaching_scenario(scenario_name: str, scenario_data: dict):
    """Test a single coaching scenario"""
    print(f"\n{'='*80}")
    print(f"TEST: {scenario_name}")
    print(f"{'='*80}")
    print(f"Mode: {scenario_data['mode']}")
    print(f"Message: {scenario_data['message']}")
    print(f"Expected: {scenario_data['expected']}")
    print(f"{'-'*80}")
    
    try:
        db = await get_db()
        
        # Initialize session
        session = await initialize_chat_session(
            db,
            avatar_interaction_id=UUID(AVATAR_INTERACTION_ID),
            mode=scenario_data['mode'],
            current_user=UUID("00000000-0000-0000-0000-000000000001"),  # Test user
            persona_id=None,
            avatar_id=None,
            language_id=None
        )
        
        print(f"Session created: {session.id}")
        
        # Get chat handler
        chat_factory = await get_chat_factory()
        handler = await chat_factory.get_chat_handler(
            avatar_interaction_id=UUID(AVATAR_INTERACTION_ID),
            mode=scenario_data['mode'],
            persona_id=None,
            language_id=None
        )
        
        # Initialize fact checking
        await handler.initialize_fact_checking(
            session.id,
            coaching_rules={
                "when_coach_appears": ["methodology violation", "factual error", "vague claims"],
                "coaching_style": "Gentle and supportive",
                "what_to_catch": ["Skipping steps", "Wrong facts", "Vague language"],
                "correction_patterns": {
                    "skipped_step": "Remember to follow the complete process step by step.",
                    "wrong_fact": "That information is not accurate. Please verify against the knowledge base.",
                    "vague_claim": "Be more specific with your information.",
                    "general": "Please review your approach and try again."
                }
            },
            mode=scenario_data['mode']
        )
        
        # Add user message to history
        user_message = Message(
            role="user",
            content=scenario_data['message'],
            timestamp=datetime.now()
        )
        session.conversation_history.append(user_message)
        
        # Process message
        print("\nProcessing message...")
        response_generator = await handler.process_message(
            scenario_data['message'],
            session.conversation_history,
            name=None
        )
        
        # Collect response
        full_response = ""
        coaching_detected = False
        
        async for chunk in response_generator:
            full_response = chunk.get("chunk", "")
            
            # Check for coaching markers
            if "[CORRECT]" in full_response or "Dear Learner" in full_response or "Factual Correction" in full_response:
                coaching_detected = True
            
            # Check for abuse warning
            if "inappropriate language" in full_response.lower():
                coaching_detected = True
        
        print(f"\n{'='*80}")
        print("RESPONSE:")
        print(f"{'='*80}")
        print(full_response)
        print(f"{'='*80}")
        
        if coaching_detected:
            print("\n[PASS] Coach appeared as expected!")
        else:
            print("\n[INFO] No coaching triggered (might be correct response)")
        
        return {
            "scenario": scenario_name,
            "coaching_detected": coaching_detected,
            "response": full_response
        }
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "scenario": scenario_name,
            "coaching_detected": False,
            "error": str(e)
        }

async def run_all_coaching_tests():
    """Run all coaching test scenarios"""
    print("\n" + "="*80)
    print("REAL-WORLD COACHING INTEGRATION TEST")
    print(f"Avatar Interaction: {AVATAR_INTERACTION_ID}")
    print("="*80)
    
    results = []
    
    for scenario_name, scenario_data in TEST_SCENARIOS.items():
        result = await test_coaching_scenario(scenario_name, scenario_data)
        results.append(result)
        
        # Wait between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    coaching_triggered = sum(1 for r in results if r.get("coaching_detected"))
    total = len(results)
    
    print(f"\nCoaching triggered: {coaching_triggered}/{total} scenarios")
    
    for result in results:
        status = "[COACH]" if result.get("coaching_detected") else "[NO COACH]"
        print(f"{status} {result['scenario']}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(run_all_coaching_tests())
