"""
Week 1 Integration Test Script
Tests archetype classification with sample scenarios
"""

import asyncio
import sys
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.archetype_classifier import ArchetypeClassifier
from scenario_generator import EnhancedScenarioGenerator

load_dotenv(".env")

# Test scenarios
TEST_SCENARIOS = {
    "HELP_SEEKING": """
    A customer service training scenario where employees learn to handle customer complaints 
    about a defective product. The customer is frustrated because their newly purchased laptop 
    stopped working after 2 days. The learner must diagnose the problem, show empathy, and 
    provide a solution following company return/exchange policies.
    """,
    
    "PERSUASION": """
    A pharmaceutical sales representative must detail a new diabetes medication to Dr. Archana, 
    a busy endocrinologist who is currently satisfied with her existing treatment protocols. 
    She has concerns about switching patients to new medications. The FSO must present clinical 
    data, address objections about efficacy and side effects, and create interest in the new 
    product using the IMPACT methodology.
    """,
    
    "CONFRONTATION_PERPETRATOR": """
    A manager must address a team lead who has been making inappropriate comments about a 
    colleague's disability. The team lead doesn't see their behavior as problematic and becomes 
    defensive when approached. The manager must hold them accountable while maintaining 
    professionalism.
    """,
    
    "CONFRONTATION_VICTIM": """
    An HR representative must speak with an employee who has been experiencing disability-related 
    bias from their team lead. The employee is hesitant to speak up, worried about retaliation, 
    and emotionally affected by the ongoing situation.
    """,
    
    "INVESTIGATION": """
    A medical student practices taking patient history from a patient presenting with vague 
    symptoms of fatigue, occasional chest discomfort, and shortness of breath. The patient has 
    difficulty articulating their symptoms clearly. The student must ask appropriate questions 
    to gather complete information for diagnosis.
    """,
    
    "NEGOTIATION": """
    An employee is negotiating a salary increase with their manager. The employee wants a 15% 
    raise based on market research and performance, while the manager has budget constraints 
    but values the employee. Both parties need to find a mutually acceptable solution.
    """
}


async def test_archetype_classification():
    """Test archetype classification with sample scenarios"""
    
    print("=" * 80)
    print("WEEK 1 INTEGRATION TEST: Archetype Classification")
    print("=" * 80)
    print()
    
    # Initialize OpenAI client
    api_key = os.getenv("api_key")
    endpoint = os.getenv("endpoint")
    api_version = os.getenv("api_version")
    
    if not all([api_key, endpoint, api_version]):
        print("❌ ERROR: Missing OpenAI credentials in .env file")
        return
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    # Initialize generator with classifier
    generator = EnhancedScenarioGenerator(client)
    
    results = []
    
    for expected_archetype, scenario_text in TEST_SCENARIOS.items():
        print(f"\n{'=' * 80}")
        print(f"Testing: {expected_archetype}")
        print(f"{'=' * 80}")
        print(f"Scenario: {scenario_text.strip()[:100]}...")
        print()
        
        try:
            # Extract scenario info (includes classification)
            template_data = await generator.extract_scenario_info(scenario_text)
            
            classification = template_data.get("archetype_classification", {})
            
            primary = classification.get("primary_archetype", "UNKNOWN")
            confidence = classification.get("confidence_score", 0.0)
            sub_type = classification.get("sub_type")
            reasoning = classification.get("reasoning", "No reasoning provided")
            alternatives = classification.get("alternative_archetypes", [])
            
            # Determine if test passed
            expected_base = expected_archetype.split("_")[0]
            # Handle enum format (e.g., "ScenarioArchetype.HELP_SEEKING")
            primary_clean = str(primary).split(".")[-1] if "." in str(primary) else str(primary)
            passed = primary_clean == expected_base and confidence >= 0.7
            
            status = "✅ PASS" if passed else ("⚠️ REVIEW" if confidence >= 0.5 else "❌ FAIL")
            
            print(f"Status: {status}")
            print(f"Expected: {expected_archetype}")
            print(f"Got: {primary}" + (f" ({sub_type})" if sub_type else ""))
            print(f"Confidence: {confidence:.2f}")
            print(f"Reasoning: {reasoning}")
            if alternatives:
                print(f"Alternatives: {', '.join(alternatives)}")
            
            results.append({
                "expected": expected_archetype,
                "got": primary,
                "sub_type": sub_type,
                "confidence": confidence,
                "passed": passed,
                "status": status
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "expected": expected_archetype,
                "got": "ERROR",
                "confidence": 0.0,
                "passed": False,
                "status": "❌ ERROR",
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    print(f"{'Expected':<30} {'Got':<20} {'Confidence':<12} {'Status'}")
    print("-" * 80)
    for r in results:
        expected = r["expected"]
        got = r["got"] + (f" ({r['sub_type']})" if r.get("sub_type") else "")
        conf = f"{r['confidence']:.2f}"
        status = r["status"]
        print(f"{expected:<30} {got:<20} {conf:<12} {status}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    elif passed >= total * 0.7:
        print("✅ Most tests passed - system is working well")
    else:
        print("⚠️ Several tests failed - review classifier logic")
    
    print("=" * 80)


async def test_database_seeding():
    """Test that archetype definitions were seeded correctly"""
    
    print("\n" + "=" * 80)
    print("DATABASE SEEDING TEST")
    print("=" * 80)
    
    try:
        from database import get_db
        from core.archetype_definitions import ARCHETYPE_DEFINITIONS
        
        db = await get_db()
        
        print("\nChecking archetype_definitions collection...")
        
        for archetype_id in ARCHETYPE_DEFINITIONS.keys():
            doc = await db.archetype_definitions.find_one({"_id": archetype_id})
            if doc:
                print(f"✅ {archetype_id}: Found in database")
            else:
                print(f"❌ {archetype_id}: NOT found in database")
        
        # Count total
        total_count = await db.archetype_definitions.count_documents({})
        print(f"\nTotal archetype definitions in DB: {total_count}")
        print(f"Expected: {len(ARCHETYPE_DEFINITIONS)}")
        
        if total_count == len(ARCHETYPE_DEFINITIONS):
            print("✅ Database seeding successful!")
        else:
            print("⚠️ Database seeding incomplete")
        
    except Exception as e:
        print(f"❌ Database test error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Week 1 Integration Tests...\n")
    
    # Run tests
    asyncio.run(test_database_seeding())
    asyncio.run(test_archetype_classification())
    
    print("\n✅ Integration tests complete!\n")
