"""
Test all 4 fixes for extraction and persona generation
"""

import asyncio
import json
from openai import AsyncAzureOpenAI

PHARMA_SALES_SCENARIO = """
# Pharmaceutical Sales Training: EO-Dine Product Launch

## Overview
Train Field Sales Officers (FSOs) to pitch EO-Dine to gynecologists using IMPACT methodology.

## Learn Mode
Expert trainer teaches IMPACT: Introduce, Motivate, Present, Address, Close, Thank.

## Assess Mode
FSO practices pitching EO-Dine to a gynecologist in Mumbai. The doctor is experienced, 
specializes in endometriosis, currently prescribes Dienogest, and is concerned about 
irregular bleeding and bone loss side effects.

## Key Facts
- EO-Dine reduces irregular bleeding by 60% vs Dienogest
- Prevents bone density loss
- Approved for long-term use
"""


async def test_all_fixes():
    """Test all 4 fixes"""
    
    print("=" * 80)
    print("TESTING ALL 4 FIXES")
    print("=" * 80)
    
    try:
        from dotenv import load_dotenv
        import os
        from core.scenario_extractor_v2 import ScenarioExtractorV2
        from core.persona_generator_v2 import PersonaGeneratorV2
        
        load_dotenv()
        
        client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        azure_endpoint=os.getenv("endpoint"),
        api_version=os.getenv("api_version")
    )
        
        # Step 1: Extract scenario
        print("\n📄 STEP 1: Extracting scenario...")
        extractor = ScenarioExtractorV2(client)
        template_data = await extractor.extract_scenario_info(PHARMA_SALES_SCENARIO)
        
        # TEST FIX #1: Check archetype
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype")
        print(f"\n✅ FIX #1 - ARCHETYPE:")
        print(f"  Result: {archetype}")
        print(f"  Expected: PERSUASION")
        print(f"  Status: {'✅ PASS' if archetype == 'PERSUASION' else '❌ FAIL'}")
        
        # Add persona_definitions for compatibility
        template_data["persona_definitions"] = {
            "assess_mode_ai_bot": {
                "name": "Dr. Priya Sharma",
                "age": 42,
                "gender": "Female",
                "role": "Gynecologist",
                "description": "Experienced gynecologist",
                "location": "Mumbai, Maharashtra",
                "current_situation": "In clinic",
                "context": "Office"
            }
        }
        template_data["template_id"] = "test-pharma-001"
        
        # Step 2: Generate persona
        print("\n👤 STEP 2: Generating persona...")
        generator = PersonaGeneratorV2(client)
        persona = await generator.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender="Female"
        )
        
        # TEST FIX #2: Check required categories
        print(f"\n✅ FIX #2 - REQUIRED CATEGORIES:")
        required = ["time_constraints", "sales_rep_history", "decision_criteria"]
        for cat in required:
            has_it = cat in persona.detail_categories_included
            print(f"  {cat}: {'✅ INCLUDED' if has_it else '❌ MISSING'}")
        
        all_required = all(cat in persona.detail_categories_included for cat in required)
        print(f"  Status: {'✅ PASS' if all_required else '❌ FAIL'}")
        
        # TEST FIX #3: Check conversation context
        print(f"\n✅ FIX #3 - CONVERSATION CONTEXT:")
        conv_rules = persona.conversation_rules
        opening = conv_rules.get("opening_behavior", "")
        triggers = conv_rules.get("behavioral_triggers", {})
        
        # Should NOT mention patient care
        has_patient_confusion = "patient" in opening.lower()
        print(f"  Opening: {opening[:80]}...")
        print(f"  Mentions 'patient': {'❌ YES (wrong)' if has_patient_confusion else '✅ NO (correct)'}")
        
        # Should mention sales/FSO context
        has_sales_context = any(word in opening.lower() for word in ["sales", "fso", "rep", "pitch"])
        print(f"  Has sales context: {'✅ YES' if has_sales_context else '❌ NO'}")
        print(f"  Status: {'✅ PASS' if not has_patient_confusion else '❌ FAIL'}")
        
        # TEST FIX #4: Check validation
        print(f"\n✅ FIX #4 - VALIDATION:")
        from core.persona_validator import PersonaValidator
        
        issues = PersonaValidator.validate(persona, template_data)
        print(f"  Issues found: {len(issues)}")
        if issues:
            for issue in issues:
                print(f"    - {issue}")
        
        # Check location consistency
        main_city = persona.location.city
        prof_context = persona.detail_categories.get("professional_context", {})
        prof_location = prof_context.get("location", "")
        location_consistent = main_city in prof_location if prof_location else True
        
        print(f"  Location consistency: {'✅ PASS' if location_consistent else '❌ FAIL'}")
        print(f"  Status: {'✅ PASS' if len(issues) == 0 else '⚠️  ISSUES FOUND'}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Fix #1 (Archetype): {'✅ PASS' if archetype == 'PERSUASION' else '❌ FAIL'}")
        print(f"Fix #2 (Categories): {'✅ PASS' if all_required else '❌ FAIL'}")
        print(f"Fix #3 (Context): {'✅ PASS' if not has_patient_confusion else '❌ FAIL'}")
        print(f"Fix #4 (Validation): {'✅ PASS' if len(issues) == 0 else '⚠️  ISSUES'}")
        
        # Save results
        with open("test_fixes_output.json", "w") as f:
            json.dump({
                "template_data": template_data,
                "persona": persona.dict()
            }, f, indent=2, default=str)
        
        print("\n📁 Full output saved to: test_fixes_output.json")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_all_fixes())
