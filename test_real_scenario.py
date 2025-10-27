"""
Test with the actual IMPACT scenario to verify correct persona extraction
"""

import asyncio
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv(".env")

client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)

async def test_real_scenario():
    # Read the IMPACT scenario
    with open("TEST_SCENARIO_IMPACT.txt", "r", encoding="utf-8") as f:
        scenario_text = f.read()
    
    print("="*80)
    print("TESTING REAL IMPACT SCENARIO")
    print("="*80)
    print(f"\nScenario length: {len(scenario_text)} characters\n")
    
    # Generate template
    generator = EnhancedScenarioGenerator(client)
    template_data = await generator.extract_scenario_info(scenario_text)
    
    # Check persona extraction
    assess_persona = template_data.get("persona_definitions", {}).get("assess_mode_ai_bot", {})
    
    print("\n" + "="*80)
    print("PERSONA EXTRACTION RESULTS")
    print("="*80)
    
    print(f"\nName: {assess_persona.get('name', 'NOT FOUND')}")
    print(f"Gender: {assess_persona.get('gender', 'NOT FOUND')}")
    print(f"Age: {assess_persona.get('age', 'NOT FOUND')}")
    print(f"Role: {assess_persona.get('role', 'NOT FOUND')}")
    print(f"Location: {assess_persona.get('location', 'NOT FOUND')}")
    
    print(f"\n[ARCHETYPE] {template_data.get('archetype_classification', {}).get('primary_archetype', 'NOT FOUND')}")
    print(f"Confidence: {template_data.get('archetype_classification', {}).get('confidence_score', 'N/A')}")
    
    print(f"\n[OBJECTIONS]")
    objections = assess_persona.get('objection_library', [])
    if objections:
        for i, obj in enumerate(objections, 1):
            print(f"{i}. {obj.get('objection', 'N/A')}")
    else:
        print("NO OBJECTIONS FOUND")
    
    print(f"\n[DECISION CRITERIA]")
    criteria = assess_persona.get('decision_criteria', [])
    if criteria:
        for c in criteria:
            print(f"- {c}")
    else:
        print("NO CRITERIA FOUND")
    
    # Check if it's correct
    print("\n" + "="*80)
    print("VALIDATION")
    print("="*80)
    
    is_correct = True
    issues = []
    
    if assess_persona.get('name') != 'Dr. Archana Pandey':
        issues.append(f"❌ Name is '{assess_persona.get('name')}', should be 'Dr. Archana Pandey'")
        is_correct = False
    else:
        print("✅ Name correct: Dr. Archana Pandey")
    
    if assess_persona.get('gender', '').lower() != 'female':
        issues.append(f"❌ Gender is '{assess_persona.get('gender')}', should be 'Female'")
        is_correct = False
    else:
        print("✅ Gender correct: Female")
    
    if 'gynecologist' not in assess_persona.get('role', '').lower():
        issues.append(f"❌ Role is '{assess_persona.get('role')}', should contain 'Gynecologist'")
        is_correct = False
    else:
        print("✅ Role correct: Gynecologist")
    
    if not objections or len(objections) < 2:
        issues.append(f"❌ Only {len(objections)} objections, should have 2")
        is_correct = False
    else:
        print(f"✅ Objections correct: {len(objections)} found")
    
    archetype = template_data.get('archetype_classification', {}).get('primary_archetype', '')
    if archetype != 'PERSUASION':
        issues.append(f"❌ Archetype is '{archetype}', should be 'PERSUASION'")
        is_correct = False
    else:
        print("✅ Archetype correct: PERSUASION")
    
    if issues:
        print("\n[ISSUES FOUND]")
        for issue in issues:
            print(issue)
    
    if is_correct:
        print("\n✅ ALL CHECKS PASSED - Persona extracted correctly!")
    else:
        print("\n❌ PERSONA EXTRACTION FAILED")
    
    # Save for inspection
    with open("test_real_scenario_result.json", "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2, default=str)
    print("\n[SAVED] Full template saved to: test_real_scenario_result.json")
    
    # Generate prompt
    assess_prompt = await generator.generate_assess_mode_from_template(template_data)
    with open("test_real_scenario_prompt.txt", "w", encoding="utf-8") as f:
        f.write(assess_prompt)
    print("[SAVED] Assess prompt saved to: test_real_scenario_prompt.txt")

if __name__ == "__main__":
    asyncio.run(test_real_scenario())
