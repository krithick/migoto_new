"""
Test script for coaching language functionality
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncAzureOpenAI
from core.azure_search_manager import EnhancedFactChecker, AzureVectorSearchManager
from models_old import Message
from datetime import datetime

async def test_coaching_language():
    # Setup
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client.migoto_new
    
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        azure_endpoint=os.getenv("endpoint"),
        api_version=os.getenv("api_version")
    )
    
    # Test different languages
    test_cases = [
        {
            "language_id": "YOUR_ARABIC_LANGUAGE_ID",  # Replace with actual ID
            "user_message": "The package costs 50,000 rupees",
            "expected_language": "Arabic"
        },
        {
            "language_id": "YOUR_SPANISH_LANGUAGE_ID",  # Replace with actual ID  
            "user_message": "I don't know the price",
            "expected_language": "Spanish"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== Testing {test_case['expected_language']} ===")
        
        # Get language instructions
        language = await db.languages.find_one({"_id": test_case["language_id"]})
        if not language:
            print(f"Language {test_case['language_id']} not found")
            continue
            
        language_instructions = language.get("prompt", "Default instructions")
        print(f"Language instructions: {language_instructions}")
        
        # Create fact checker with language
        vector_search = AzureVectorSearchManager()
        fact_checker = EnhancedFactChecker(
            vector_search, 
            openai_client,
            coaching_rules={},
            language_instructions=language_instructions
        )
        
        # Test coaching
        conversation_history = [
            Message(role="assistant", content="Hello, how can I help?", timestamp=datetime.now()),
            Message(role="user", content=test_case["user_message"], timestamp=datetime.now())
        ]
        
        try:
            # Test enhanced coaching
            verification = await fact_checker.verify_response_with_coaching(
                test_case["user_message"], 
                conversation_history, 
                "test_knowledge_base"
            )
            
            print(f"Result: {verification.result}")
            print(f"Coaching feedback: {verification.coaching_feedback}")
            print(f"Explanation: {verification.explanation}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_coaching_language())