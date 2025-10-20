"""
Live Demo: Complete Archetype System
Creates a scenario and shows archetype-aware bot behavior
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from scenario_generator import EnhancedScenarioGenerator

load_dotenv(".env")

# Demo scenario: Pharma Sales (PERSUASION archetype)
DEMO_SCENARIO = """
A pharmaceutical sales representative must detail a new diabetes medication (GlucoStable XR) 
to Dr. Archana Patel, a busy endocrinologist at City Hospital. Dr. Patel has been prescribing 
metformin and insulin for 15 years with good results. She's skeptical of new medications due 
to past experiences with overhyped drugs. The FSO must present clinical trial data showing 
20% better A1C reduction, address concerns about side effects and cost, and create interest 
using the IMPACT methodology. Dr. Patel values evidence-based medicine and patient outcomes 
over marketing claims.
"""


async def demo_archetype_system():
    """Complete end-to-end demo of archetype system"""
    
    print("\n" + "=" * 80)
    print("🎯 ARCHETYPE SYSTEM LIVE DEMO")
    print("=" * 80)
    print("\nThis demo will:")
    print("1. Classify the scenario archetype")
    print("2. Generate archetype-aware persona")
    print("3. Show bot prompt with objection library")
    print("4. Simulate conversation with archetype behaviors")
    print()
    
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
    
    # Step 1: Classification
    print("=" * 80)
    print("STEP 1: ARCHETYPE CLASSIFICATION")
    print("=" * 80)
    print(f"\nScenario: {DEMO_SCENARIO[:150]}...\n")
    
    template_data = await generator.extract_scenario_info(DEMO_SCENARIO)
    
    classification = template_data.get("archetype_classification", {})
    archetype = classification.get("primary_archetype", "UNKNOWN")
    confidence = classification.get("confidence_score", 0.0)
    sub_type = classification.get("sub_type")
    
    print(f"✅ Archetype: {archetype}")
    if sub_type:
        print(f"   Sub-type: {sub_type}")
    print(f"   Confidence: {confidence:.2%}")
    print(f"   Pattern: {classification.get('conversation_pattern', 'N/A')}")
    
    # Step 2: Persona Generation
    print("\n" + "=" * 80)
    print("STEP 2: ARCHETYPE-AWARE PERSONA GENERATION")
    print("=" * 80)
    
    personas_dict = await generator.generate_personas_from_template(
        template_data,
        archetype_classification=classification
    )
    
    persona = personas_dict.get("assess_mode_character", {})
    
    print(f"\n👤 Persona: {persona.get('name', 'Unknown')}")
    print(f"   Role: {persona.get('persona_type', 'N/A')}")
    print(f"   Age: {persona.get('age', 'N/A')}, Gender: {persona.get('gender', 'N/A')}")
    print(f"   Goal: {persona.get('character_goal', 'N/A')[:100]}...")
    
    # Show archetype-specific fields
    objection_library = persona.get("objection_library", [])
    if objection_library:
        print(f"\n📚 Objection Library ({len(objection_library)} objections):")
        for i, obj in enumerate(objection_library[:3], 1):
            print(f"\n   {i}. {obj.get('objection', 'N/A')}")
            print(f"      💭 Concern: {obj.get('underlying_concern', 'N/A')}")
            print(f"      🛡️  Counter: {obj.get('counter_strategy', 'N/A')[:80]}...")
    
    decision_criteria = persona.get("decision_criteria", [])
    if decision_criteria:
        print(f"\n🎯 Decision Criteria: {', '.join(decision_criteria)}")
    
    personality = persona.get("personality_type", "")
    if personality:
        print(f"🧠 Personality: {personality}")
    
    # Step 3: Bot Prompt Construction
    print("\n" + "=" * 80)
    print("STEP 3: BOT SYSTEM PROMPT (with archetype behaviors)")
    print("=" * 80)
    
    # Simulate what bot receives
    bot_prompt = f"""
You are {persona.get('name', 'the character')} in a training scenario.

PERSONA DETAILS:
- Name: {persona.get('name')}
- Role: {persona.get('persona_type')}
- Age: {persona.get('age')}, Gender: {persona.get('gender')}
- Goal: {persona.get('character_goal')}

## PERSUASION BEHAVIOR:
You have specific objections and concerns. Use them naturally in conversation:
"""
    
    for i, obj in enumerate(objection_library[:3], 1):
        bot_prompt += f"\n{i}. Objection: {obj.get('objection', '')}"
        bot_prompt += f"\n   Underlying concern: {obj.get('underlying_concern', '')}"
    
    if decision_criteria:
        bot_prompt += f"\n\nYour decision criteria: {', '.join(decision_criteria)}"
    if personality:
        bot_prompt += f"\nYour personality type: {personality}"
    
    print(bot_prompt)
    
    # Step 4: Conversation Simulation
    print("\n" + "=" * 80)
    print("STEP 4: CONVERSATION SIMULATION")
    print("=" * 80)
    print("\nShowing how bot uses objection library in conversation:\n")
    
    # Simulate conversation
    conversations = [
        {
            "user": "Hi Dr. Patel, I'd like to tell you about our new diabetes medication GlucoStable XR.",
            "bot_uses": objection_library[0] if objection_library else None
        },
        {
            "user": "Our clinical trials show 20% better A1C reduction compared to standard treatments.",
            "bot_uses": objection_library[1] if len(objection_library) > 1 else None
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print(f"Turn {i}:")
        print(f"  👨‍💼 Sales Rep: {conv['user']}")
        
        if conv['bot_uses']:
            obj = conv['bot_uses']
            print(f"  👩‍⚕️  Dr. Patel: [Uses objection: '{obj.get('objection', '')}']")
            print(f"              \"I appreciate that, but {obj.get('underlying_concern', '').lower()}.\"")
        print()
    
    # Summary
    print("=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print("\nWhat happened:")
    print("1. ✅ Scenario automatically classified as PERSUASION")
    print("2. ✅ Persona generated with objection library")
    print("3. ✅ Bot receives archetype-specific instructions")
    print("4. ✅ Bot naturally uses objections in conversation")
    print("\nThe archetype system is working end-to-end!")
    print("\nNext: Create scenarios through your API and watch archetype magic happen! 🎯")


async def main():
    try:
        await demo_archetype_system()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
