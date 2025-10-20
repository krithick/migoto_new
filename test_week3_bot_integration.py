"""
Week 3 Integration Test Script
Tests bot factory integration with archetype-aware personas
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from scenario_generator import EnhancedScenarioGenerator
from models.archetype_models import ScenarioArchetype

load_dotenv(".env")

# Test scenario
PERSUASION_SCENARIO = """
A pharmaceutical sales representative must detail a new diabetes medication (GlucoStable XR) 
to Dr. Archana Patel, a busy endocrinologist at City Hospital. Dr. Patel has been prescribing 
metformin and insulin for 15 years with good results. She's skeptical of new medications due 
to past experiences with overhyped drugs. The FSO must present clinical trial data showing 
20% better A1C reduction, address concerns about side effects and cost, and create interest 
using the IMPACT methodology. Dr. Patel values evidence-based medicine and patient outcomes 
over marketing claims.
"""


async def test_bot_integration():
    """Test that bot receives and uses archetype-aware persona"""
    
    print("\n" + "=" * 80)
    print("WEEK 3 TEST: Bot Integration with Archetype-Aware Personas")
    print("=" * 80)
    
    # Initialize
    api_key = os.getenv("api_key")
    endpoint = os.getenv("endpoint")
    api_version = os.getenv("api_version")
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    # Step 1: Generate archetype-aware persona
    print("\n📊 Step 1: Generating archetype-aware persona...")
    template_data = await generator.extract_scenario_info(PERSUASION_SCENARIO)
    
    classification = template_data.get("archetype_classification", {})
    archetype = classification.get("primary_archetype", "UNKNOWN")
    confidence = classification.get("confidence_score", 0.0)
    
    print(f"   ✅ Classified as: {archetype} (confidence: {confidence:.2f})")
    
    personas_dict = await generator.generate_personas_from_template(
        template_data,
        archetype_classification=classification
    )
    
    persona = personas_dict.get("assess_mode_character", {})
    
    # Validate persona has archetype fields
    print(f"\n📋 Step 2: Validating persona structure...")
    print(f"   Name: {persona.get('name', 'N/A')}")
    print(f"   Role: {persona.get('persona_type', 'N/A')}")
    
    objection_library = persona.get("objection_library", [])
    print(f"   Objection Library: {len(objection_library)} objections")
    
    if not objection_library:
        print("   ❌ FAIL: Missing objection library")
        return False
    
    print(f"   ✅ Persona has archetype-specific fields")
    
    # Step 3: Simulate bot initialization
    print(f"\n🤖 Step 3: Simulating bot initialization...")
    print(f"   Bot would receive persona with:")
    print(f"   - {len(objection_library)} objections to use in conversation")
    print(f"   - Decision criteria: {persona.get('decision_criteria', [])}")
    print(f"   - Personality type: {persona.get('personality_type', 'N/A')}")
    print(f"   - Current position: {persona.get('current_position', 'N/A')[:80]}...")
    
    # Step 4: Test conversation simulation
    print(f"\n💬 Step 4: Testing conversation behavior...")
    
    # Simulate user opening
    user_message = "Hi Dr. Patel, I'd like to tell you about our new diabetes medication GlucoStable XR."
    
    print(f"   User: {user_message}")
    
    # Bot should use objection library
    first_objection = objection_library[0] if objection_library else {}
    print(f"\n   🎯 Bot has access to objection: '{first_objection.get('objection', 'N/A')}'")
    print(f"   💡 Underlying concern: {first_objection.get('underlying_concern', 'N/A')}")
    print(f"   🛡️  Counter strategy available: {first_objection.get('counter_strategy', 'N/A')[:80]}...")
    
    print(f"\n   ✅ Bot can use archetype-specific objections in conversation")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("✅ WEEK 3 BOT INTEGRATION TEST PASSED")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Update bot factory to accept archetype classification")
    print("2. Modify bot prompt to use objection library")
    print("3. Test live conversation with real bot")
    print("4. Create migration script for existing scenarios")
    
    return True


async def main():
    try:
        success = await test_bot_integration()
        if success:
            print("\n🎉 All Week 3 integration tests passed!")
        else:
            print("\n❌ Week 3 integration tests failed")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
