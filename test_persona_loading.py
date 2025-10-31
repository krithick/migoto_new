"""
Test script to verify persona loading with dynamic fields.
Tests loading persona_from_extraction.json structure.
"""

import json
from pathlib import Path


def test_persona_structure():
    """Test that the extraction persona structure is valid"""
    
    # Load the extraction persona
    persona_file = Path("persona_from_extraction.json")
    if not persona_file.exists():
        print("❌ persona_from_extraction.json not found")
        return False
    
    with open(persona_file, 'r') as f:
        persona_data = json.load(f)
    
    print("✅ Loaded persona_from_extraction.json")
    
    # Check required base fields
    required_fields = ["name", "age", "gender", "role", "description", "persona_type", "mode"]
    missing = [f for f in required_fields if f not in persona_data]
    
    if missing:
        print(f"❌ Missing required fields: {', '.join(missing)}")
        return False
    
    print(f"✅ All required base fields present")
    
    # Check dynamic fields
    detail_categories = persona_data.get("detail_categories", {})
    print(f"✅ Found {len(detail_categories)} detail categories:")
    for category in detail_categories.keys():
        print(f"   - {category}")
    
    # Check location structure
    location = persona_data.get("location", {})
    if isinstance(location, dict):
        print(f"✅ Location structure: {location.get('city', 'N/A')}, {location.get('country', 'N/A')}")
    
    # Check conversation rules
    conv_rules = persona_data.get("conversation_rules", {})
    if conv_rules:
        print(f"✅ Conversation rules present with {len(conv_rules)} keys")
    
    # Check archetype
    archetype = persona_data.get("archetype")
    confidence = persona_data.get("archetype_confidence")
    if archetype:
        print(f"✅ Archetype: {archetype} (confidence: {confidence})")
    
    print("\n✅ Persona structure is valid and compatible!")
    print(f"   Total fields: {len(persona_data)}")
    print(f"   Detail categories: {len(detail_categories)}")
    
    return True


def test_model_compatibility():
    """Test that PersonaInstanceV2 can handle the structure"""
    from models.persona_models import PersonaInstanceV2
    
    persona_file = Path("persona_from_extraction.json")
    with open(persona_file, 'r') as f:
        persona_data = json.load(f)
    
    try:
        # Try to create model instance
        persona = PersonaInstanceV2(**persona_data)
        print("\n✅ PersonaInstanceV2 model accepts the data structure")
        print(f"   Name: {persona.name}")
        print(f"   Role: {persona.role}")
        print(f"   Detail categories: {len(persona.detail_categories)}")
        return True
    except Exception as e:
        print(f"\n❌ Model validation failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Persona Loading with Dynamic Fields")
    print("=" * 60)
    print()
    
    # Test 1: Structure validation
    if not test_persona_structure():
        print("\n❌ Structure test failed")
        exit(1)
    
    # Test 2: Model compatibility
    if not test_model_compatibility():
        print("\n❌ Model compatibility test failed")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Persona loading is ready.")
    print("=" * 60)
