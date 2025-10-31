import pytest
import asyncio
from core.system_prompt_generator import SystemPromptGenerator

@pytest.mark.asyncio
async def test_prompt_generation_basic():
    """Test basic prompt generation"""
    
    # Mock data
    template_data = {
        "general_info": {"title": "Test Scenario", "domain": "test"},
        "mode_descriptions": {
            "assess_mode": {
                "what_happens": "Testing",
                "learner_role": "Tester",
                "ai_bot_role": "Test Subject"
            }
        }
    }
    
    persona_data = {
        "name": "Test Person",
        "role": "Test Role",
        "archetype": "PERSUASION",
        "age": 30,
        "location": {"city": "Test City"},
        "detail_categories": {}
    }
    
    generator = SystemPromptGenerator(client)
    prompt = await generator.generate_system_prompt(
        template_data, persona_data, "assess_mode"
    )
    
    assert len(prompt) > 1000
    assert "SECTION 1" in prompt
    assert "Test Person" in prompt
    assert "[FINISH]" in prompt


@pytest.mark.asyncio
async def test_prompt_validation():
    """Test prompt validation"""
    
    generator = SystemPromptGenerator(client)
    
    # Good prompt
    good_prompt = """
    SECTION 1: CRITICAL RULES
    SECTION 2: WHO YOU ARE
    SECTION 3: BEHAVIOR
    SECTION 4: CONTEXT
    SECTION 5: FLOW
    SECTION 6: CLOSING
    [FINISH]
    """ * 100  # Make it long enough
    
    validation = generator.validate_prompt(good_prompt)
    assert validation["valid"] == True
    
    # Bad prompt (missing sections)
    bad_prompt = "SECTION 1: CRITICAL RULES"
    
    validation = generator.validate_prompt(bad_prompt)
    assert validation["valid"] == False
    assert len(validation["issues"]) > 0