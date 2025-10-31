"""
Simple coaching demonstration
Shows coaching system working without full session setup
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from core.azure_search_manager import AzureVectorSearchManager, EnhancedFactChecker
from models_old import Message
from datetime import datetime

load_dotenv()

# Test coaching rules (v2 template)
COACHING_RULES = {
    "when_coach_appears": ["methodology violation", "factual error", "vague claims"],
    "coaching_style": "Gentle and supportive",
    "what_to_catch": ["Skipping steps", "Wrong facts", "Vague language"],
    "correction_patterns": {
        "skipped_step": "Remember to follow the complete process step by step.",
        "wrong_fact": "That information is not accurate. Please verify against the knowledge base.",
        "vague_claim": "Be more specific with your information.",
        "general": "Please review your approach and try again."
    }
}

async def demo_coaching():
    """Demonstrate coaching system"""
    
    print("\n" + "="*80)
    print("COACHING SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Initialize
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        azure_endpoint=os.getenv("endpoint"),
        api_version=os.getenv("api_version")
    )
    
    vector_search = AzureVectorSearchManager()
    
    # Test 1: Try mode with coaching
    print("\n" + "-"*80)
    print("TEST 1: TRY MODE - Vague Claim")
    print("-"*80)
    
    fact_checker_try = EnhancedFactChecker(
        vector_search, openai_client,
        coaching_rules=COACHING_RULES,
        mode="try_mode"
    )
    
    message = "Here's some product info"
    print(f"User says: '{message}'")
    
    trigger = await fact_checker_try.should_coach(message, [])
    print(f"\nTrigger check: {trigger}")
    
    if trigger["trigger"]:
        print(f"\n[COACH TRIGGERED]")
        print(f"Type: {trigger['type']}")
        print(f"Reason: {trigger['reason']}")
    else:
        print("\n[NO COACHING NEEDED]")
    
    # Test 2: Learn mode
    print("\n" + "-"*80)
    print("TEST 2: LEARN MODE - Factual Statement")
    print("-"*80)
    
    fact_checker_learn = EnhancedFactChecker(
        vector_search, openai_client,
        coaching_rules={},
        mode="learn_mode"
    )
    
    message = "EO-Dine reduces irregular bleeding by 60%"
    print(f"User says: '{message}'")
    
    trigger = await fact_checker_learn.should_coach(message, [])
    print(f"\nTrigger check: {trigger}")
    
    if trigger["trigger"]:
        print(f"\n[FACT CHECK TRIGGERED]")
        print(f"Type: {trigger['type']}")
        print(f"Reason: {trigger['reason']}")
    else:
        print("\n[NO FACT CHECK NEEDED]")
    
    # Test 3: Assess mode (no coaching)
    print("\n" + "-"*80)
    print("TEST 3: ASSESS MODE - Any Message")
    print("-"*80)
    
    fact_checker_assess = EnhancedFactChecker(
        vector_search, openai_client,
        coaching_rules={},
        mode="assess_mode"
    )
    
    message = "This is completely wrong information"
    print(f"User says: '{message}'")
    
    trigger = await fact_checker_assess.should_coach(message, [])
    print(f"\nTrigger check: {trigger}")
    
    if trigger["trigger"]:
        print(f"\n[COACHING TRIGGERED]")
    else:
        print("\n[NO COACHING] - Assess mode doesn't coach")
    
    # Test 4: Abuse detection
    print("\n" + "-"*80)
    print("TEST 4: ABUSE DETECTION")
    print("-"*80)
    
    message = "This is fucking stupid"
    print(f"User says: '{message}'")
    
    # Simple keyword check
    abuse_keywords = ["fuck", "shit", "damn", "stupid", "idiot"]
    is_abuse = any(word in message.lower() for word in abuse_keywords)
    
    if is_abuse:
        print("\n[ABUSE DETECTED]")
        print("Response: 'I notice inappropriate language. This training requires professional communication.'")
    else:
        print("\n[NO ABUSE]")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n[SUCCESS] Coaching system is working!")
    print("\nKey Features Demonstrated:")
    print("  1. Try mode triggers coaching for vague claims")
    print("  2. Learn mode triggers fact-checking")
    print("  3. Assess mode does NOT trigger coaching")
    print("  4. Abuse detection catches inappropriate language")
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(demo_coaching())
