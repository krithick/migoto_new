"""
Quick test script for new 6-section prompt architecture
"""

import asyncio
import json
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

from core.scenario_extractor_v2 import ScenarioExtractorV2
from core.persona_generator_v2 import PersonaGeneratorV2
from core.prompt_architect_v3 import PromptArchitectV3

load_dotenv()


async def test_new_architecture():
    """Test the complete flow"""
    
    # Sample scenario description
    scenario_description = """
    EO-Dine Pharmaceutical Sales Training
    
    This is a pharmaceutical sales training scenario where Field Sales Officers (FSOs) 
    learn to pitch EO-Dine, a new endometriosis treatment, to gynecologists.
    
    The FSO must use the IMPACT methodology to convince doctors to prescribe EO-Dine 
    instead of Dienogest. Key benefits include 60% reduction in irregular bleeding 
    and prevention of bone density loss.
    
    The doctor is busy, evidence-driven, and skeptical of sales pitches.
    """
    
    print("="*60)
    print("Testing New 6-Section Prompt Architecture")
    print("="*60)
    
    # Initialize client
    client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)
    
    # Step 1: Extract template
    print("\n[STEP 1] Extracting template data...")
    extractor = ScenarioExtractorV2(client)
    template_data = await extractor.extract_scenario_info(scenario_description)
    print(f"✓ Archetype: {template_data.get('archetype_classification', {}).get('primary_archetype')}")
    
    # Step 2: Generate persona
    print("\n[STEP 2] Generating persona...")
    persona_generator = PersonaGeneratorV2(client)
    persona = await persona_generator.generate_persona(
        template_data=template_data,
        mode="assess_mode"
    )
    persona_data = persona.dict()
    print(f"✓ Persona: {persona_data.get('name')} ({persona_data.get('role')})")
    print(f"✓ Categories: {persona_data.get('detail_categories_included')}")
    
    # Step 3: Generate prompt
    print("\n[STEP 3] Generating 6-section prompt...")
    architect = PromptArchitectV3(client)
    final_prompt = await architect.generate_prompt(
        template_data=template_data,
        persona_data=persona_data,
        mode="assess_mode"
    )
    print(f"✓ Prompt generated: {len(final_prompt)} characters")
    
    # Save outputs
    print("\n[SAVING] Writing outputs to files...")
    
    with open("test_template_output.json", "w") as f:
        json.dump(template_data, f, indent=2, default=str)
    print("✓ Saved: test_template_output.json")
    
    with open("test_persona_output.json", "w") as f:
        json.dump(persona_data, f, indent=2, default=str)
    print("✓ Saved: test_persona_output.json")
    
    with open("test_final_prompt.txt", "w", encoding="utf-8") as f:
        f.write(final_prompt)
    print("✓ Saved: test_final_prompt.txt")
    
    print("\n" + "="*60)
    print("✅ Test Complete!")
    print("="*60)
    print(f"\nPrompt Preview (first 500 chars):")
    print("-"*60)
    print(final_prompt[:500])
    print("...")
    print("-"*60)


if __name__ == "__main__":
    asyncio.run(test_new_architecture())
