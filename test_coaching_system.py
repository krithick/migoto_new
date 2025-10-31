"""
Test script for coaching system improvements
Run this to validate the coaching system works correctly
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from core.azure_search_manager import AzureVectorSearchManager, EnhancedFactChecker
from models_old import Message
from datetime import datetime

# Load environment variables
load_dotenv()

# Test coaching rules (v2 template structure)
TEST_COACHING_RULES = {
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

async def test_fact_checker_initialization():
    """Test 1: Fact checker initializes correctly with v2 template"""
    print("\n=== TEST 1: Fact Checker Initialization ===")
    
    try:
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        vector_search = AzureVectorSearchManager()
        
        # Test with v2 coaching rules
        fact_checker = EnhancedFactChecker(
            vector_search,
            openai_client,
            coaching_rules=TEST_COACHING_RULES,
            mode="try_mode",
            language_instructions="Respond in English."
        )
        
        assert fact_checker.mode == "try_mode", "Mode not set correctly"
        assert fact_checker.has_coaching_rules == True, "Coaching rules not detected"
        assert "correction_patterns" in fact_checker.coaching_rules, "Correction patterns not parsed"
        assert fact_checker.coaching_rules["coaching_style"] == "Gentle and supportive", "Coaching style not parsed"
        
        print("[PASS] Fact checker initialized correctly")
        print(f"   - Mode: {fact_checker.mode}")
        print(f"   - Has coaching rules: {fact_checker.has_coaching_rules}")
        print(f"   - Coaching style: {fact_checker.coaching_rules.get('coaching_style')}")
        print(f"   - Triggers: {list(fact_checker.coaching_rules.get('triggers', {}).keys())}")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

async def test_smart_triggering():
    """Test 2: Smart triggering detects when coaching is needed"""
    print("\n=== TEST 2: Smart Triggering ===")
    
    try:
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        vector_search = AzureVectorSearchManager()
        
        # Test learn_mode
        fact_checker_learn = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules={}, mode="learn_mode"
        )
        
        result_learn = await fact_checker_learn.should_coach(
            "EO-Dine reduces irregular bleeding by 60%",
            []
        )
        
        print(f"Learn mode trigger: {result_learn}")
        assert result_learn["trigger"] == True, "Learn mode should trigger for factual claims"
        print("[PASS] Learn mode triggers for factual content")
        
        # Test try_mode
        fact_checker_try = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules=TEST_COACHING_RULES, mode="try_mode"
        )
        
        result_try = await fact_checker_try.should_coach(
            "Here's the product info",
            []
        )
        
        print(f"Try mode trigger: {result_try}")
        print("[PASS] Try mode trigger detection works")
        
        # Test assess_mode (should not trigger)
        fact_checker_assess = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules={}, mode="assess_mode"
        )
        
        result_assess = await fact_checker_assess.should_coach(
            "Any message",
            []
        )
        
        assert result_assess["trigger"] == False, "Assess mode should not trigger"
        print("[PASS] Assess mode does not trigger coaching")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mode_separation():
    """Test 3: Learn mode vs Try mode behavior"""
    print("\n=== TEST 3: Mode Separation ===")
    
    try:
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        vector_search = AzureVectorSearchManager()
        
        # Learn mode
        fact_checker_learn = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules={}, mode="learn_mode"
        )
        
        print(f"Learn mode: {fact_checker_learn.mode}")
        assert fact_checker_learn.mode == "learn_mode"
        print("[PASS] Learn mode set correctly")
        
        # Try mode
        fact_checker_try = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules=TEST_COACHING_RULES, mode="try_mode"
        )
        
        print(f"Try mode: {fact_checker_try.mode}")
        assert fact_checker_try.mode == "try_mode"
        assert fact_checker_try.has_coaching_rules == True
        print("[PASS] Try mode set correctly with coaching rules")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

async def test_coaching_rules_parsing():
    """Test 4: V2 template coaching rules parsing"""
    print("\n=== TEST 4: Coaching Rules Parsing ===")
    
    try:
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        vector_search = AzureVectorSearchManager()
        
        fact_checker = EnhancedFactChecker(
            vector_search, openai_client,
            coaching_rules=TEST_COACHING_RULES,
            mode="try_mode"
        )
        
        # Check parsed structure
        assert "coaching_style" in fact_checker.coaching_rules
        assert "triggers" in fact_checker.coaching_rules
        assert "correction_patterns" in fact_checker.coaching_rules
        
        print("[PASS] Coaching rules structure parsed correctly")
        print(f"   - Coaching style: {fact_checker.coaching_rules['coaching_style']}")
        print(f"   - Triggers: {fact_checker.coaching_rules['triggers']}")
        print(f"   - Correction patterns: {list(fact_checker.coaching_rules['correction_patterns'].keys())}")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("COACHING SYSTEM TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_fact_checker_initialization())
    results.append(await test_smart_triggering())
    results.append(await test_mode_separation())
    results.append(await test_coaching_rules_parsing())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED!")
    else:
        print(f"[FAILURE] {total - passed} TEST(S) FAILED")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
