"""
Combined Test: Extraction V2 → Persona V2
Uses extraction_v2_output.json to generate personas
"""

import asyncio
import json
from openai import AsyncAzureOpenAI
from core.persona_generator_v2 import PersonaGeneratorV2


async def test_extraction_to_persona():
    """Load extraction output and generate persona from it"""
    
    print("=" * 80)
    print("EXTRACTION V2 → PERSONA V2 TEST")
    print("=" * 80)
    
    # Load extraction output
    print("\n📂 Loading extraction_v2_output.json...")
    with open("extraction_v2_output.json", "r") as f:
        template_data = json.load(f)
    
    print(f"✓ Loaded extraction for: {template_data['context_overview']['scenario_title']}")
    print(f"✓ Domain: {template_data['general_info']['domain']}")
    print(f"✓ Extraction version: {template_data.get('extraction_version', 'v1')}")
    
    # Show persona types extracted
    persona_types = template_data.get('persona_types', [])
    print(f"\n👥 Extracted {len(persona_types)} persona types:")
    for pt in persona_types:
        print(f"  - {pt['type']}: {pt['description'][:60]}...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            api_version=os.getenv("api_version"),
            azure_endpoint=os.getenv("endpoint")
        )
        
        # V2 extraction already has persona_types, no fallback needed
        
        # Add template_id if missing
        if not template_data.get("template_id"):
            template_data["template_id"] = "extracted-scenario-001"
        
        # Add archetype if missing
        if not template_data.get("archetype_classification"):
            template_data["archetype_classification"] = {
                "primary_archetype": "HELP_SEEKING",
                "confidence_score": 0.8
            }
        
        print("\n🤖 Generating persona with V2...")
        
        # Create generator
        generator = PersonaGeneratorV2(client, model="gpt-4o")
        
        # Generate persona for assess mode
        persona = await generator.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender="Female"
        )
        
        print("\n✅ PERSONA GENERATED!\n")
        print("=" * 80)
        
        # Display results
        print(f"\n👤 BASE INFO:")
        print(f"  Name: {persona.name}")
        print(f"  Age: {persona.age}")
        print(f"  Gender: {persona.gender}")
        print(f"  Role: {persona.role}")
        print(f"  Type: {persona.persona_type}")
        print(f"  Location: {persona.location.city}, {persona.location.state}")
        
        print(f"\n📚 DETAIL CATEGORIES SELECTED ({len(persona.detail_categories)}):")
        for category_name in persona.detail_categories_included:
            print(f"  ✓ {category_name}")
        
        print(f"\n📊 CATEGORY DETAILS:")
        for category_name, details in persona.detail_categories.items():
            print(f"\n  {category_name.upper().replace('_', ' ')}:")
            for key, value in details.items():
                if isinstance(value, list):
                    print(f"    - {key}: {', '.join(str(v) for v in value[:2])}...")
                else:
                    print(f"    - {key}: {value}")
        
        print(f"\n💬 CONVERSATION RULES:")
        rules = persona.conversation_rules
        print(f"  Opening: {rules.get('opening_behavior')}")
        print(f"  Style: {rules.get('response_style')}")
        print(f"  Word limit: {rules.get('word_limit')}")
        
        triggers = rules.get('behavioral_triggers', {})
        if triggers:
            print(f"\n  🎯 BEHAVIORAL TRIGGERS:")
            engages = triggers.get('what_engages', [])
            if engages:
                print(f"    Engages with: {', '.join(engages[:2])}")
            frustrates = triggers.get('what_frustrates', [])
            if frustrates:
                print(f"    Frustrated by: {', '.join(frustrates[:2])}")
        
        print("\n" + "=" * 80)
        print("📁 FULL PERSONA SAVED TO: persona_from_extraction.json")
        print("=" * 80)
        
        # Save full output
        with open("persona_from_extraction.json", "w") as f:
            json.dump(persona.dict(), f, indent=2, default=str)
        
        # Show how extraction data influenced persona
        print("\n🔗 HOW EXTRACTION INFLUENCED PERSONA:")
        print(f"  ✓ Used persona type: {persona_types[0]['type']}")
        print(f"  ✓ Applied characteristics: {list(persona_types[0]['key_characteristics'].keys())}")
        print(f"  ✓ Context from mode: {template_data['mode_descriptions']['assess_mode']['context']}")
        print(f"  ✓ Domain knowledge available: {len(template_data['domain_knowledge']['key_facts'])} facts")
        
        return persona
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have:")
        print("1. .env file with Azure OpenAI credentials")
        print("2. extraction_v2_output.json in current directory")
        raise


if __name__ == "__main__":
    print("\n🚀 Testing Full Pipeline: Extraction → Persona\n")
    
    try:
        asyncio.run(test_extraction_to_persona())
        print("\n✅ Full pipeline test completed successfully!")
        print("\nYou now have:")
        print("  1. extraction_v2_output.json - Rich scenario extraction")
        print("  2. persona_from_extraction.json - Dynamic persona with selected categories")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
