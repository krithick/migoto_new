"""
Test Persona V2 Generation
Shows how v2 dynamically selects detail categories
"""

import asyncio
import json
from openai import AsyncAzureOpenAI
from core.persona_generator_v2 import PersonaGeneratorV2

# Sample template data (from extraction)
SAMPLE_TEMPLATE = {
    "template_id": "test-001",
    "general_info": {
        "domain": "pharmaceutical_product",
        "title": "EO-Dine Sales Training"
    },
    "context_overview": {
        "scenario_title": "EO-Dine Pitch to Gynecologist"
    },
    "persona_definitions": {
        "assess_mode_ai_bot": {
            "name": "Dr. Priya Sharma",
            "age": 42,
            "gender": "Female",
            "role": "Gynecologist",
            "description": "Experienced gynecologist specializing in endometriosis",
            "location": "Mumbai, Maharashtra",
            "current_situation": "In clinic office",
            "context": "Medical consultation"
        }
    },
    "archetype_classification": {
        "primary_archetype": "HELP_SEEKING",
        "confidence_score": 0.85
    }
}


async def test_persona_v2():
    """Test v2 persona generation"""
    
    print("=" * 80)
    print("PERSONA V2 GENERATION TEST")
    print("=" * 80)
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Create generator
        generator = PersonaGeneratorV2(client, model="gpt-4o")
        
        print("\n📋 Generating persona for assess mode...")
        print(f"Scenario: {SAMPLE_TEMPLATE['context_overview']['scenario_title']}")
        print(f"Domain: {SAMPLE_TEMPLATE['general_info']['domain']}\n")
        
        # Generate persona
        persona = await generator.generate_persona(
            template_data=SAMPLE_TEMPLATE,
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
        print(f"  Location: {persona.location.city}, {persona.location.state}")
        
        print(f"\n📚 DETAIL CATEGORIES SELECTED ({len(persona.detail_categories)}):")
        for category_name in persona.detail_categories_included:
            print(f"  ✓ {category_name}")
        
        print(f"\n📊 CATEGORY DETAILS:")
        for category_name, details in persona.detail_categories.items():
            print(f"\n  {category_name.upper()}:")
            for key, value in details.items():
                print(f"    - {key}: {value}")
        
        print(f"\n💬 CONVERSATION RULES:")
        rules = persona.conversation_rules
        print(f"  Opening: {rules.get('opening_behavior')}")
        print(f"  Style: {rules.get('response_style')}")
        print(f"  Word limit: {rules.get('word_limit')}")
        
        triggers = rules.get('behavioral_triggers', {})
        if triggers:
            print(f"\n  Engages with: {triggers.get('what_engages', [])}")
            print(f"  Frustrated by: {triggers.get('what_frustrates', [])}")
        
        print("\n" + "=" * 80)
        print("📁 FULL OUTPUT SAVED TO: persona_v2_output.json")
        print("=" * 80)
        
        # Save full output
        with open("persona_v2_output.json", "w") as f:
            json.dump(persona.dict(), f, indent=2, default=str)
        
        return persona
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure you have:")
        print("1. .env file with Azure OpenAI credentials")
        raise


async def show_category_library():
    """Show all available detail categories"""
    from core.detail_category_library import DetailCategoryLibrary
    
    print("\n" + "=" * 80)
    print("AVAILABLE DETAIL CATEGORIES (16 total)")
    print("=" * 80)
    
    categories = DetailCategoryLibrary.get_all_categories()
    
    for i, (name, cat) in enumerate(categories.items(), 1):
        print(f"\n{i}. {name.upper()}")
        print(f"   Description: {cat.description}")
        print(f"   When relevant: {cat.when_relevant}")
        print(f"   Example fields: {', '.join(cat.example_fields[:3])}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting Persona V2 Test...\n")
    
    # Show available categories
    asyncio.run(show_category_library())
    
    # Generate persona
    try:
        asyncio.run(test_persona_v2())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
