import asyncio
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os

async def test_prompt_has_objections():
    client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint")
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    # Pharma sales scenario
    scenario = """
    A pharmaceutical sales rep must detail EO Dine to Dr. Archana,
    a busy gynecologist satisfied with Dienogest. She has concerns
    about switching patients to new medications.
    """
    
    # Extract template
    template_data = await generator.extract_scenario_info(scenario)
    
    # Generate assess mode prompt
    assess_prompt = await generator.generate_assess_mode_from_template(template_data)
    
    # CHECK: Does prompt contain objection library?
    print("=" * 80)
    print("ARCHETYPE PROMPT GENERATION TEST")
    print("=" * 80)
    print(f"\nArchetype: {template_data.get('archetype_classification', {}).get('primary_archetype')}")
    print(f"\nGenerated Prompt Length: {len(assess_prompt)} chars")
    
    # Critical checks
    checks = {
        "Has 'objection_library'": "objection_library" in str(template_data.get('persona_definitions', {})),
        "Prompt mentions objections": "objection" in assess_prompt.lower(),
        "Has decision_criteria": "decision_criteria" in str(template_data.get('persona_definitions', {})),
        "Prompt mentions decision": "decision" in assess_prompt.lower(),
    }
    
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    # Show first 500 chars of prompt
    print("\n" + "=" * 80)
    print("PROMPT PREVIEW:")
    print("=" * 80)
    print(assess_prompt[:500])
    
    if not all(checks.values()):
        print("\n❌ ARCHETYPE DATA NOT IN PROMPT!")
        print("Archetype classification works, but prompt generation doesn't use it.")
    else:
        print("\n✅ ARCHETYPE SYSTEM WORKING!")

asyncio.run(test_prompt_has_objections())
