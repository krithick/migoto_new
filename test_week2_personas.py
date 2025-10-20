"""
Week 2 Integration Test Script
Tests persona generation quality for PERSUASION and CONFRONTATION archetypes
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

# Test scenarios
PHARMA_SALES_SCENARIO = """
A pharmaceutical sales representative must detail a new diabetes medication (GlucoStable XR) 
to Dr. Archana Patel, a busy endocrinologist at City Hospital. Dr. Patel has been prescribing 
metformin and insulin for 15 years with good results. She's skeptical of new medications due 
to past experiences with overhyped drugs. The FSO must present clinical trial data showing 
20% better A1C reduction, address concerns about side effects and cost, and create interest 
using the IMPACT methodology. Dr. Patel values evidence-based medicine and patient outcomes 
over marketing claims.
"""

DISABILITY_BIAS_PERPETRATOR = """
Sarah Chen, a department manager at TechCorp, must address inappropriate behavior by Mark 
Thompson, a senior team lead. Mark has been making comments about a colleague's wheelchair 
use, suggesting they're "milking" their disability for special treatment. He's made jokes 
about parking spaces and questioned their productivity. When initially approached, Mark 
becomes defensive, saying he was "just joking" and that people are "too sensitive." Sarah 
must hold him accountable, explain the impact of his behavior, and ensure it stops while 
maintaining team dynamics.
"""

DISABILITY_BIAS_VICTIM = """
Alex Rivera, a software engineer who uses a wheelchair, must confront their team lead Mark 
Thompson about ongoing discriminatory behavior. Mark has been making inappropriate comments 
about Alex's wheelchair use, questioning their productivity, and making jokes about parking 
spaces. Alex is hesitant to escalate but needs to address the hostile work environment. They're 
emotionally exhausted, worried about retaliation, and fear being labeled a "troublemaker." 
Alex must confront Mark directly about the impact of his behavior while maintaining 
professionalism and documenting the interaction.
"""


async def test_persona_generation(scenario_text: str, expected_archetype: str, test_name: str):
    """Test persona generation for a specific scenario"""
    
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 80}")
    print(f"Scenario: {scenario_text[:150]}...")
    print()
    
    # Initialize OpenAI client
    api_key = os.getenv("api_key")
    endpoint = os.getenv("endpoint")
    api_version = os.getenv("api_version")
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    try:
        # Extract scenario info with classification
        print("📊 Extracting scenario information...")
        template_data = await generator.extract_scenario_info(scenario_text)
        
        # Verify classification
        classification = template_data.get("archetype_classification", {})
        archetype = classification.get("primary_archetype", "UNKNOWN")
        confidence = classification.get("confidence_score", 0.0)
        sub_type = classification.get("sub_type")
        
        print(f"\n✅ Classification: {archetype}" + (f" ({sub_type})" if sub_type else ""))
        print(f"   Confidence: {confidence:.2f}")
        
        expected_base = expected_archetype.split("_")[0]
        archetype_clean = str(archetype).split(".")[-1] if "." in str(archetype) else str(archetype)
        
        if archetype_clean != expected_base:
            print(f"⚠️  WARNING: Expected {expected_base}, got {archetype_clean}")
        
        # Generate personas from template with archetype info
        print(f"\n👤 Generating personas...")
        personas_dict = await generator.generate_personas_from_template(
            template_data,
            archetype_classification=classification
        )
        
        # Extract assess mode persona for validation
        persona = personas_dict.get("assess_mode_character", {})
        
        if not persona:
            print("❌ ERROR: No personas generated!")
            return False
        
        print(f"\n👥 Generated personas: learn_mode_expert, assess_mode_character")
        
        # Analyze assess mode persona in detail
        print(f"\n{'─' * 80}")
        print(f"PERSONA ANALYSIS: {persona.get('name', 'Unknown')}")
        print(f"{'─' * 80}")
        
        # Basic fields
        print(f"\n📋 Basic Information:")
        print(f"   Name: {persona.get('name', 'N/A')}")
        print(f"   Role: {persona.get('persona_type', 'N/A')}")
        print(f"   Age: {persona.get('age', 'N/A')}")
        print(f"   Gender: {persona.get('gender', 'N/A')}")
        print(f"   Goal: {persona.get('character_goal', 'N/A')[:100]}...")
        
        # Archetype-specific validation
        if expected_base == "PERSUASION":
            return validate_persuasion_persona(persona)
        elif expected_base == "CONFRONTATION":
            return validate_confrontation_persona(persona, sub_type)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def validate_persuasion_persona(persona: dict) -> bool:
    """Validate PERSUASION archetype persona quality"""
    
    print(f"\n🎯 PERSUASION Persona Validation:")
    
    issues = []
    
    # Check for objection library
    objection_library = persona.get("objection_library", [])
    print(f"\n   📚 Objection Library: {len(objection_library)} objections")
    
    if not objection_library:
        issues.append("Missing objection library")
    else:
        # Validate objection structure
        for i, obj in enumerate(objection_library[:3], 1):
            objection = obj.get("objection", "N/A")
            concern = obj.get("underlying_concern", "N/A")
            strategy = obj.get("counter_strategy", "N/A")
            print(f"      {i}. {objection}")
            print(f"         Concern: {concern}")
            print(f"         Strategy: {strategy[:80]}...")
            
            if not all([objection, concern, strategy]):
                issues.append(f"Incomplete objection #{i}")
    
    # Check decision criteria
    decision_criteria = persona.get("decision_criteria", [])
    print(f"\n   🎯 Decision Criteria: {', '.join(decision_criteria) if decision_criteria else 'MISSING'}")
    if not decision_criteria:
        issues.append("Missing decision criteria")
    
    # Check personality type
    personality = persona.get("personality_type", "")
    print(f"   🧠 Personality Type: {personality or 'MISSING'}")
    if not personality:
        issues.append("Missing personality type")
    
    # Check current position
    current_position = persona.get("current_position", "")
    print(f"   📍 Current Position: {current_position[:100] if current_position else 'MISSING'}...")
    if not current_position:
        issues.append("Missing current position")
    
    # Check satisfaction level
    satisfaction = persona.get("satisfaction_level", "")
    print(f"   😊 Satisfaction Level: {satisfaction or 'MISSING'}")
    if not satisfaction:
        issues.append("Missing satisfaction level")
    
    # Summary
    print(f"\n{'─' * 80}")
    if issues:
        print(f"⚠️  Issues Found ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ PERSUASION persona validation PASSED")
        return True


def validate_confrontation_persona(persona: dict, sub_type: str) -> bool:
    """Validate CONFRONTATION archetype persona quality"""
    
    print(f"\n⚔️  CONFRONTATION Persona Validation (Sub-type: {sub_type}):")
    
    issues = []
    
    # Check sub_type field
    persona_sub_type = persona.get("sub_type", "")
    print(f"\n   🏷️  Sub-type: {persona_sub_type or 'MISSING'}")
    if not persona_sub_type:
        issues.append("Missing sub_type field")
    
    if "PERPETRATOR" in str(sub_type).upper():
        # Perpetrator-specific validation
        awareness = persona.get("awareness_level", "")
        print(f"   🧠 Awareness Level: {awareness or 'MISSING'}")
        if not awareness:
            issues.append("Missing awareness_level")
        
        defensive = persona.get("defensive_mechanisms", [])
        print(f"   🛡️  Defensive Mechanisms: {', '.join(defensive) if defensive else 'MISSING'}")
        if not defensive:
            issues.append("Missing defensive_mechanisms")
        
        escalation = persona.get("escalation_triggers", [])
        print(f"   ⚡ Escalation Triggers: {', '.join(escalation) if escalation else 'MISSING'}")
        if not escalation:
            issues.append("Missing escalation_triggers")
        
        de_escalation = persona.get("de_escalation_opportunities", [])
        print(f"   ✅ De-escalation Opportunities: {', '.join(de_escalation) if de_escalation else 'MISSING'}")
        if not de_escalation:
            issues.append("Missing de_escalation_opportunities")
    
    elif "VICTIM" in str(sub_type).upper():
        # Victim-specific validation
        emotional_state = persona.get("emotional_state", "")
        print(f"   😢 Emotional State: {emotional_state or 'MISSING'}")
        if not emotional_state:
            issues.append("Missing emotional_state")
        
        trust_level = persona.get("trust_level", "")
        print(f"   🤝 Trust Level: {trust_level or 'MISSING'}")
        if not trust_level:
            issues.append("Missing trust_level")
        
        needs = persona.get("needs", [])
        print(f"   💭 Needs: {', '.join(needs) if needs else 'MISSING'}")
        if not needs:
            issues.append("Missing needs")
        
        barriers = persona.get("barriers_to_reporting", [])
        print(f"   🚧 Barriers to Reporting: {', '.join(barriers) if barriers else 'MISSING'}")
        if not barriers:
            issues.append("Missing barriers_to_reporting")
    
    # Common fields
    power_dynamics = persona.get("power_dynamics", "")
    print(f"   ⚖️  Power Dynamics: {power_dynamics or 'MISSING'}")
    if not power_dynamics:
        issues.append("Missing power_dynamics")
    
    # Summary
    print(f"\n{'─' * 80}")
    if issues:
        print(f"⚠️  Issues Found ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ CONFRONTATION persona validation PASSED")
        return True


async def main():
    """Run all Week 2 tests"""
    
    print("\n" + "=" * 80)
    print("WEEK 2 INTEGRATION TESTS: Persona Generation & Validation")
    print("=" * 80)
    
    results = []
    
    # Test 1: Pharma Sales (PERSUASION)
    result1 = await test_persona_generation(
        PHARMA_SALES_SCENARIO,
        "PERSUASION",
        "Pharma Sales (PERSUASION)"
    )
    results.append(("Pharma Sales", result1))
    
    # Test 2: Disability Bias - Perpetrator (CONFRONTATION)
    result2 = await test_persona_generation(
        DISABILITY_BIAS_PERPETRATOR,
        "CONFRONTATION_PERPETRATOR",
        "Disability Bias - Perpetrator (CONFRONTATION)"
    )
    results.append(("Disability Bias - Perpetrator", result2))
    
    # Test 3: Disability Bias - Victim (CONFRONTATION)
    result3 = await test_persona_generation(
        DISABILITY_BIAS_VICTIM,
        "CONFRONTATION_VICTIM",
        "Disability Bias - Victim (CONFRONTATION)"
    )
    results.append(("Disability Bias - Victim", result3))
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("WEEK 2 TEST SUMMARY")
    print(f"{'=' * 80}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    print(f"{'Test Name':<40} {'Status'}")
    print("-" * 80)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<40} {status}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("🎉 ALL WEEK 2 TESTS PASSED!")
    elif passed >= total * 0.7:
        print("✅ Most tests passed - persona generation working well")
    else:
        print("⚠️ Several tests failed - review persona generation logic")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
