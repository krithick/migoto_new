"""
Simple test for SystemPromptGenerator
Tests with sample data and validates output
"""

import asyncio
import json
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

from core.system_prompt_generator import SystemPromptGenerator

load_dotenv()


async def test_system_prompt_generator():
    """Test the system prompt generator with sample data"""
    
    print("="*60)
    print("Testing SystemPromptGenerator")
    print("="*60)
    
    # Initialize client
    client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("endpoint")
    )
    
    # Load existing template data
    print("\n[TEST] Loading extraction_v2_output.json...")
    with open("extraction_v2_output.json", "r") as f:
        template_data = json.load(f)
    print(f"✓ Template loaded: {template_data.get('general_info', {}).get('title')}")
    
    # Load existing persona data
    print("\n[TEST] Loading persona_from_extraction.json...")
    with open("persona_from_extraction.json", "r") as f:
        persona_data = json.load(f)
    print(f"✓ Persona loaded: {persona_data.get('name')}")
    
    # Generate prompt
    print("\n[TEST] Generating system prompt from existing data...")
    generator = SystemPromptGenerator(client)
    
    system_prompt = await generator.generate_system_prompt(
        template_data=template_data,
        persona_data=persona_data,
        mode="assess_mode"
    )
    
    print(f"\n[TEST] ✓ Prompt generated: {len(system_prompt)} characters")
    
    # Validate
    print("\n[TEST] Validating prompt...")
    validation = generator.validate_prompt(system_prompt)
    
    print(f"\n[VALIDATION RESULTS]")
    print(f"Valid: {validation['valid']}")
    print(f"Length: {validation['length']} chars")
    print(f"Word count: {validation['word_count']} words")
    
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    else:
        print("Issues: None ✓")
    
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    else:
        print("Warnings: None ✓")
    
    # Check for all 6 sections
    print("\n[SECTION CHECK]")
    sections = [
        "SECTION 1: CRITICAL RULES",
        "SECTION 2:",
        "SECTION 3:",
        "SECTION 4:",
        "SECTION 5:",
        "SECTION 6:"
    ]
    
    for section in sections:
        if section in system_prompt:
            print(f"✓ {section} found")
        else:
            print(f"✗ {section} MISSING")
    
    # Check for [FINISH] token
    if "[FINISH]" in system_prompt:
        print("✓ [FINISH] token found")
    else:
        print("✗ [FINISH] token MISSING")
    
    # Save output
    with open("test_system_prompt_output.txt", "w", encoding="utf-8") as f:
        f.write(system_prompt)
    print("\n[TEST] ✓ Saved to: test_system_prompt_output.txt")
    
    # Print preview
    print("\n[PROMPT PREVIEW] (first 500 chars):")
    print("-"*60)
    print(system_prompt[:500])
    print("...")
    print("-"*60)
    
    print("\n" + "="*60)
    if validation['valid']:
        print("✅ TEST PASSED!")
    else:
        print("❌ TEST FAILED!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_system_prompt_generator())
