"""
Test script to generate prompts from existing template data
"""
import json
import asyncio
from openai import AsyncAzureOpenAI
from core.system_prompt_generator import SystemPromptGenerator
from core.learn_mode_prompt_generator import LearnModePromptGenerator
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)

async def test_learn_mode_prompt():
    """Generate learn mode trainer prompt"""
    
    # Load template data
    with open("extraction_v2_output.json", "r") as f:
        template_data = json.load(f)
    
    print("=" * 80)
    print("GENERATING LEARN MODE TRAINER PROMPT")
    print("=" * 80)
    
    # Generate trainer prompt
    generator = LearnModePromptGenerator(client, model="gpt-4o")
    trainer_prompt = await generator.generate_trainer_prompt(template_data)
    
    # Validate
    validation = generator.validate_prompt(trainer_prompt)
    
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"Valid: {validation['valid']}")
    print(f"Word Count: {validation['word_count']}")
    print(f"Issues: {validation['issues']}")
    print(f"Warnings: {validation['warnings']}")
    
    # Save to file
    with open("generated_learn_mode_prompt.txt", "w", encoding="utf-8") as f:
        f.write(trainer_prompt)
    
    print("\n✅ Learn mode prompt saved to: generated_learn_mode_prompt.txt")
    
    return trainer_prompt

async def test_assess_mode_prompt():
    """Generate assess mode system prompt (requires persona)"""
    
    # Load template data
    with open("extraction_v2_output.json", "r") as f:
        template_data = json.load(f)
    
    # Create a sample persona based on persona_types
    persona_data = {
        "name": "Dr. Priya Sharma",
        "age": 42,
        "role": "Gynecologist",
        "archetype": "PERSUASION",
        "location": {
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India"
        },
        "detail_categories": {
            "professional_context": {
                "specialty": "Gynecology with focus on endometriosis",
                "years_experience": 15,
                "practice_type": "Private practice in metro hospital",
                "patient_volume": "30-40 patients per day"
            },
            "current_treatment_approach": {
                "current_medication": "Dienogest",
                "satisfaction": "Moderate - concerned about side effects",
                "pain_points": ["Irregular bleeding in patients", "Bone density loss concerns"]
            },
            "decision_criteria": {
                "must_haves": ["Clinical evidence", "Safety profile", "Long-term data"],
                "deal_breakers": ["Lack of evidence", "Higher side effects", "No insurance coverage"]
            },
            "time_constraints": {
                "availability": "Very limited - 5-7 minutes per rep",
                "schedule": "Back-to-back patients, surgery scheduled in 1 hour",
                "frustrations": "Time-wasting, vague pitches"
            }
        },
        "conversation_rules": {
            "opening_behavior": "Wait for learner to initiate",
            "response_style": "Direct, evidence-focused",
            "word_limit": 50
        },
        "behavioral_triggers": {
            "engages_with": ["Clinical data", "Specific evidence", "Addressing concerns"],
            "frustrated_by": ["Vague claims", "Time-wasting", "Ignoring questions"],
            "ends_conversation": ["Disrespect", "Irrelevant product", "Persistent vagueness"]
        }
    }
    
    print("\n" + "=" * 80)
    print("GENERATING ASSESS MODE SYSTEM PROMPT")
    print("=" * 80)
    
    # Generate system prompt
    generator = SystemPromptGenerator(client, model="gpt-4o")
    system_prompt = await generator.generate_system_prompt(
        template_data=template_data,
        persona_data=persona_data,
        mode="assess_mode"
    )
    
    # Validate
    validation = generator.validate_prompt(system_prompt)
    
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print(f"Valid: {validation['valid']}")
    print(f"Word Count: {validation['word_count']}")
    print(f"Issues: {validation['issues']}")
    print(f"Warnings: {validation['warnings']}")
    
    # Save to file
    with open("generated_assess_mode_prompt.txt", "w", encoding="utf-8") as f:
        f.write(system_prompt)
    
    print("\n✅ Assess mode prompt saved to: generated_assess_mode_prompt.txt")
    
    return system_prompt

async def main():
    """Run both tests"""
    
    print("\n🚀 Starting prompt generation tests...\n")
    
    # Test learn mode
    await test_learn_mode_prompt()
    
    # Test assess mode
    await test_assess_mode_prompt()
    
    print("\n" + "=" * 80)
    print("✅ ALL PROMPTS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
