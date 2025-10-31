import asyncio
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_prompt_has_objections():
    client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint")
    )
    
    generator = EnhancedScenarioGenerator(client)
    
    scenario = """
    A pharmaceutical sales rep must detail EO Dine to Dr. Archana,
    a busy gynecologist satisfied with Dienogest. She has concerns
    about switching patients to new medications.
    """
    
    template_data = await generator.extract_scenario_info(scenario)
    assess_prompt = await generator.generate_assess_mode_from_template(template_data)
    
    print("=" * 80)
    print("ARCHETYPE FIX TEST")
    print("=" * 80)
    print(f"\nArchetype: {template_data.get('archetype_classification', {}).get('primary_archetype')}")
    print(f"\nGenerated Prompt Length: {len(assess_prompt)} chars")
    
    checks = {
        "Has 'objection_library' in template_data": "objection_library" in str(template_data.get('persona_definitions', {})),
        "Prompt mentions 'objection'": "objection" in assess_prompt.lower(),
        "Prompt mentions 'decision'": "decision" in assess_prompt.lower(),
        "Prompt has 'Your Position' section": "Your Position" in assess_prompt or "Your Current Position" in assess_prompt,
    }
    
    print("\n" + "=" * 80)
    print("RESULTS:")
    print("=" * 80)
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    print("\n" + "=" * 80)
    print("PROMPT PREVIEW (first 1000 chars):")
    print("=" * 80)
    print(assess_prompt[:1000])
    
    if all(checks.values()):
        print("\n✅ ARCHETYPE FIX SUCCESSFUL!")
    else:
        print("\n❌ ARCHETYPE FIX INCOMPLETE")

asyncio.run(test_prompt_has_objections())
