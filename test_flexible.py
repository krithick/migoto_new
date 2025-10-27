"""
Quick test script for FlexibleScenarioGenerator
Run this to test the new system
"""

import asyncio
import json
from enhanced_scenario_generator import FlexibleScenarioGenerator

# Mock client for testing
class MockClient:
    class chat:
        class completions:
            @staticmethod
            async def create(**kwargs):
                # Return mock response for testing
                class MockResponse:
                    def __init__(self):
                        self.choices = [MockChoice()]
                
                class MockChoice:
                    def __init__(self):
                        self.message = MockMessage()
                
                class MockMessage:
                    def __init__(self):
                        self.content = '''```json
{
    "scenario_understanding": {
        "main_topic": "Customer Service Excellence",
        "learning_situation": "Training customer service representatives to handle difficult situations",
        "target_skills": ["Active listening", "Empathy", "Problem resolution", "De-escalation"],
        "key_challenges": "Dealing with frustrated customers while maintaining professionalism"
    },
    "participant_roles": {
        "learner_role": "Customer Service Representative",
        "expert_role": "Senior Customer Service Trainer",
        "practice_role": "Frustrated Customer"
    },
    "conversation_dynamics": {
        "learn_mode_purpose": "Trainer teaches de-escalation techniques and best practices",
        "practice_mode_purpose": "Representative practices handling difficult customer situations",
        "typical_interactions": ["Customer complaints", "Product issues", "Billing disputes"],
        "success_looks_like": "Customer feels heard and issue is resolved satisfactorily",
        "failure_patterns": ["Dismissing concerns", "Getting defensive", "Not listening actively"]
    },
    "content_specifics": {
        "key_knowledge": ["Company policies", "De-escalation techniques", "Active listening skills"],
        "procedures_mentioned": ["Complaint handling process", "Escalation procedures"],
        "policies_referenced": ["Customer satisfaction policy", "Refund guidelines"],
        "examples_given": ["Angry customer scenario", "Billing dispute resolution"]
    },
    "conversation_examples": {
        "dialogue_samples": ["Customer: This is unacceptable! Rep: I understand your frustration..."],
        "question_patterns": ["What can you do about this?", "Why did this happen?"],
        "response_patterns": ["I apologize for the inconvenience", "Let me help you resolve this"]
    }
}
```'''
                
                return MockResponse()

async def test_flexible_extraction():
    """Test the flexible extraction system"""
    
    print("🧪 Testing FlexibleScenarioGenerator...")
    
    # Initialize with mock client
    mock_client = MockClient()
    generator = FlexibleScenarioGenerator(mock_client)
    
    # Test 1: Document extraction
    print("\n📄 Test 1: Document Extraction")
    sample_document = """
    Customer Service Training Manual
    
    This manual covers how to handle difficult customer situations.
    
    Key Skills:
    - Active listening
    - Empathy and understanding
    - Problem resolution
    - Professional communication
    
    Common Scenarios:
    - Billing disputes
    - Product complaints
    - Service issues
    
    Best Practices:
    - Always acknowledge the customer's feelings
    - Ask clarifying questions
    - Offer solutions, not excuses
    - Follow up to ensure satisfaction
    """
    
    try:
        doc_result = await generator.flexible_extract_from_document(sample_document)
        print("✅ Document extraction successful!")
        print(f"Main topic: {doc_result.get('scenario_understanding', {}).get('main_topic')}")
        print(f"Target skills: {doc_result.get('scenario_understanding', {}).get('target_skills')}")
    except Exception as e:
        print(f"❌ Document extraction failed: {e}")
    
    # Test 2: Prompt extraction
    print("\n💬 Test 2: Prompt Extraction")
    sample_prompt = "Create a training scenario for sales representatives learning to handle customer objections about pricing"
    
    try:
        prompt_result = await generator.flexible_extract_from_prompt(sample_prompt)
        print("✅ Prompt extraction successful!")
        print(f"Main topic: {prompt_result.get('scenario_understanding', {}).get('main_topic')}")
        print(f"Practice role: {prompt_result.get('participant_roles', {}).get('practice_role')}")
    except Exception as e:
        print(f"❌ Prompt extraction failed: {e}")
    
    # Test 3: Template validation
    print("\n✅ Test 3: Template Validation")
    try:
        validated = await generator.validate_and_enhance_template(doc_result)
        print("✅ Template validation successful!")
        print(f"Validation notes: {validated.get('validation_notes', {})}")
    except Exception as e:
        print(f"❌ Template validation failed: {e}")
    
    # Test 4: Scenario generation
    print("\n🎯 Test 4: Scenario Generation")
    try:
        scenarios = await generator.generate_dynamic_scenarios(validated)
        print("✅ Scenario generation successful!")
        print(f"Generated modes: {list(scenarios.keys())}")
        print(f"Learn mode preview: {scenarios.get('learn_mode', '')[:100]}...")
    except Exception as e:
        print(f"❌ Scenario generation failed: {e}")
    
    print("\n🎉 Testing complete!")
    return True

if __name__ == "__main__":
    asyncio.run(test_flexible_extraction())