"""
Test PERSUASION archetype behavior:
- Dr. Archana should NOT volunteer objections immediately
- She should only raise objections when provoked or when learner fails to address concerns
- She should be skeptical but not hostile
"""

import asyncio
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv(".env")

# Initialize client
client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)

# Load the generated prompt
with open("test_assess_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

async def simulate_conversation(user_messages, test_name):
    """Simulate a conversation with the AI persona"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}\n")
    
    messages = [{"role": "system", "content": system_prompt}]
    
    for i, user_msg in enumerate(user_messages, 1):
        messages.append({"role": "user", "content": user_msg})
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        bot_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": bot_response})
        
        print(f"Turn {i}")
        print(f"USER: {user_msg}")
        print(f"DR. ARCHANA: {bot_response}")
        print()
        
        if "[FINISH]" in bot_response:
            print("[Conversation ended by bot]")
            break
    
    return messages

async def main():
    print("\n" + "="*80)
    print("TESTING PERSUASION ARCHETYPE BEHAVIOR")
    print("="*80)
    
    # Test 1: Ideal learner - follows IMPACT, addresses concerns proactively
    ideal_learner = [
        "Hello Dr. Archana, I am Rajesh from Integrace Orthopedics, the makers of Dubinor, Lizolid and Esoz, trusted by more than 34,000 Indian doctors.",
        "I visited you 3 weeks ago and detailed our endometriosis portfolio. Since then, have you had a chance to prescribe any of our products?",
        "That's great that you're treating endometriosis actively. Doctor, what are your key concerns when treating endometriosis patients?",
        "Exactly, Doctor. That's where EO-Dine excels. It reduces chronic pelvic pain by 49%, dysmenorrhea by 44%, and has superior tolerability for up to 15 years compared to Dienogest, which can cause bone loss with long-term use.",
        "I have the clinical data here showing head-to-head comparisons. EO-Dine has high contraceptive efficacy and better safety profile. Can I share these studies with you?",
        "Thank you Doctor. I look forward to your prescriptions for EO-Dine in your next endometriosis patient. I'll leave the data and samples with your staff."
    ]
    
    await simulate_conversation(ideal_learner, "IDEAL LEARNER - Proactive, addresses concerns")
    
    print("\n" + "="*80 + "\n")
    
    # Test 2: Poor learner - vague, doesn't address concerns, triggers objections
    poor_learner = [
        "Hi Doctor.",
        "I'm here to talk about a new product.",
        "It's called EO-Dine. It's for endometriosis.",
        "It's better than what you're using now.",
        "Because it works better.",
        "Okay, thanks. Bye."
    ]
    
    await simulate_conversation(poor_learner, "POOR LEARNER - Vague, should trigger objections")
    
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    print("\nExpected behavior:")
    print("1. IDEAL LEARNER: Dr. Archana should be receptive, ask clarifying questions")
    print("   - Should NOT immediately say 'How is EO-Dine better than Dienogest?'")
    print("   - Should respond to learner's probing with her concerns")
    print("   - Should be satisfied when data is offered")
    print()
    print("2. POOR LEARNER: Dr. Archana should be skeptical and raise objections")
    print("   - Should ask 'How is it better than Dienogest?'")
    print("   - Should demand efficacy data")
    print("   - Should end conversation if learner can't provide value")

if __name__ == "__main__":
    asyncio.run(main())
