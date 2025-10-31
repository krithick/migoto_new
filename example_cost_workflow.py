"""
Example Cost Analysis Workflow
Demonstrates complete cost tracking for scenario creation and chat interaction
"""

import asyncio
import json
from datetime import datetime
from cost_analysis_tool import CostAnalyzer, TokenUsage, SpeechUsage

async def example_workflow():
    """Complete example of cost tracking workflow"""
    
    print("🚀 Starting Cost Analysis Example Workflow")
    print("=" * 50)
    
    # Mock database for example
    class MockDB:
        def __init__(self):
            self.cost_tracking = MockCollection()
            self.scenario_cost_tracking = MockCollection()
            self.conversation_cost_tracking = MockCollection()
    
    class MockCollection:
        def __init__(self):
            self.data = []
        
        async def insert_one(self, doc):
            self.data.append(doc)
            print(f"📝 Stored: {doc.get('type', 'data')}")
            return type('Result', (), {'inserted_id': f'mock_id_{len(self.data)}'})()
        
        async def find_one(self, query):
            # Return mock data for scenario/conversation tracking
            if 'scenario_id' in query:
                return {
                    'scenario_id': query['scenario_id'],
                    'scenario_name': 'Example Scenario',
                    'user_id': 'user123',
                    'start_timestamp': datetime.now().isoformat(),
                    'token_usage': [],
                    'total_cost': 0.0,
                    'status': 'in_progress'
                }
            elif 'session_id' in query:
                return {
                    'session_id': query['session_id'],
                    'scenario_name': 'Example Scenario',
                    'mode': 'assess_mode',
                    'user_id': 'user123',
                    'start_timestamp': datetime.now().isoformat(),
                    'token_usage': [],
                    'speech_usage': [],
                    'total_cost': 0.0,
                    'message_count': 0,
                    'status': 'active'
                }
            return None
        
        async def update_one(self, query, update):
            print(f"📊 Updated: {list(query.keys())[0] if query else 'document'}")
            return type('Result', (), {'modified_count': 1})()
        
        async def find(self, query):
            return type('Cursor', (), {
                'to_list': lambda length: asyncio.create_task(asyncio.coroutine(lambda: [])()),
                'sort': lambda field, direction: self
            })()
    
    # Initialize
    db = MockDB()
    analyzer = CostAnalyzer(db)
    
    print("\n📋 PART 1: SCENARIO CREATION COST TRACKING")
    print("-" * 40)
    
    # Step 1: Start scenario creation tracking
    scenario_id = await analyzer.start_scenario_creation_tracking(
        "Customer Service Training Scenario",
        "user123",
        "api_example"
    )
    print(f"✅ Started scenario tracking: {scenario_id}")
    
    # Step 2: Simulate scenario analysis token usage
    analysis_usage = TokenUsage(
        timestamp=datetime.now().isoformat(),
        operation="scenario_analysis",
        model="gpt-4o",
        prompt_tokens=1200,  # Input scenario description
        completion_tokens=800,  # Generated template data
        user_id="user123"
    )
    await analyzer.add_scenario_token_usage(scenario_id, analysis_usage)
    print(f"📊 Scenario Analysis: {analysis_usage.total_tokens} tokens, ${analysis_usage.cost_usd:.4f}")
    
    # Step 3: Simulate persona generation token usage
    persona_usage = TokenUsage(
        timestamp=datetime.now().isoformat(),
        operation="persona_generation",
        model="gpt-4o",
        prompt_tokens=800,   # Template data input
        completion_tokens=1200,  # Generated personas
        user_id="user123"
    )
    await analyzer.add_scenario_token_usage(scenario_id, persona_usage)
    print(f"👥 Persona Generation: {persona_usage.total_tokens} tokens, ${persona_usage.cost_usd:.4f}")
    
    # Step 4: Simulate prompt generation token usage
    prompt_usage = TokenUsage(
        timestamp=datetime.now().isoformat(),
        operation="prompt_generation",
        model="gpt-4o",
        prompt_tokens=1000,  # Template + persona data
        completion_tokens=2500,  # Generated prompts (learn, assess, try modes)
        user_id="user123"
    )
    await analyzer.add_scenario_token_usage(scenario_id, prompt_usage)
    print(f"📝 Prompt Generation: {prompt_usage.total_tokens} tokens, ${prompt_usage.cost_usd:.4f}")
    
    # Step 5: Complete scenario creation tracking
    scenario_report = await analyzer.complete_scenario_creation_tracking(scenario_id)
    print(f"✅ Scenario Creation Complete!")
    print(f"   Total Tokens: {scenario_report['total_tokens']:,}")
    print(f"   Total Cost: ${scenario_report['total_cost_usd']:.4f}")
    
    print("\n💬 PART 2: CONVERSATION SESSION COST TRACKING")
    print("-" * 40)
    
    # Step 1: Start conversation tracking
    session_id = "example_session_123"
    await analyzer.start_conversation_tracking(
        session_id,
        "Customer Service Training Scenario",
        "assess_mode",
        "user123"
    )
    print(f"✅ Started conversation tracking: {session_id}")
    
    # Simulate a 5-message conversation
    conversation_messages = [
        {"user": "Hello, I have a problem with my order", "ai": "I'm sorry to hear about the issue with your order. Can you please provide me with your order number so I can look into this for you?"},
        {"user": "My order number is 12345", "ai": "Thank you for providing the order number. I can see your order here. It looks like there was a delay in processing. Let me check what happened and how we can resolve this."},
        {"user": "How long will it take to fix?", "ai": "I understand your concern about the timing. Based on what I'm seeing, I can expedite your order and have it shipped out today. You should receive it within 2 business days. Would that work for you?"},
        {"user": "That sounds good, thank you", "ai": "Excellent! I've expedited your order and you'll receive a tracking number via email within the next hour. Is there anything else I can help you with today?"},
        {"user": "No, that's all. Thanks for your help!", "ai": "You're very welcome! I'm glad I could help resolve this for you. Have a great day and thank you for your patience!"}
    ]
    
    total_conversation_cost = 0.0
    
    for i, exchange in enumerate(conversation_messages, 1):
        print(f"\n💬 Message {i}:")
        
        # Simulate STT (user speech to text)
        user_message = exchange["user"]
        stt_duration = len(user_message) * 0.08  # ~0.08 seconds per character (rough estimate)
        
        stt_usage = SpeechUsage(
            timestamp=datetime.now().isoformat(),
            operation="stt",
            duration_seconds=stt_duration,
            user_id="user123",
            session_id=session_id
        )
        await analyzer.add_conversation_speech_usage(session_id, stt_usage)
        print(f"   🎤 STT: {stt_duration:.1f}s, ${stt_usage.cost_usd:.4f}")
        
        # Simulate AI response token usage
        ai_response = exchange["ai"]
        response_tokens = TokenUsage(
            timestamp=datetime.now().isoformat(),
            operation="chat_response",
            model="gpt-4o",
            prompt_tokens=len(user_message.split()) * 1.3,  # Rough token estimate
            completion_tokens=len(ai_response.split()) * 1.3,
            user_id="user123",
            session_id=session_id
        )
        await analyzer.add_conversation_token_usage(session_id, response_tokens)
        print(f"   🤖 AI Response: {response_tokens.total_tokens} tokens, ${response_tokens.cost_usd:.4f}")
        
        # Simulate TTS (AI text to speech)
        tts_usage = SpeechUsage(
            timestamp=datetime.now().isoformat(),
            operation="tts",
            character_count=len(ai_response),
            user_id="user123",
            session_id=session_id
        )
        await analyzer.add_conversation_speech_usage(session_id, tts_usage)
        print(f"   🔊 TTS: {len(ai_response)} chars, ${tts_usage.cost_usd:.4f}")
        
        message_cost = stt_usage.cost_usd + response_tokens.cost_usd + tts_usage.cost_usd
        total_conversation_cost += message_cost
        print(f"   💰 Message Total: ${message_cost:.4f}")
    
    # Complete conversation tracking
    conversation_report = await analyzer.complete_conversation_tracking(session_id)
    print(f"\n✅ Conversation Complete!")
    print(f"   Messages: {conversation_report['message_count']}")
    print(f"   Duration: {conversation_report['duration_minutes']:.1f} minutes")
    print(f"   Total Tokens: {conversation_report['total_tokens']:,}")
    print(f"   STT Minutes: {conversation_report['total_stt_minutes']:.1f}")
    print(f"   TTS Characters: {conversation_report['total_tts_characters']:,}")
    print(f"   Total Cost: ${conversation_report['total_cost_usd']:.4f}")
    
    print("\n📊 PART 3: COST REPORT GENERATION")
    print("-" * 40)
    
    # Generate comprehensive cost report
    end_date = datetime.now().isoformat()
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    
    cost_report = await analyzer.generate_cost_report("user123", start_date, end_date)
    
    print("📋 Daily Cost Report:")
    print(f"   Total Cost: ${cost_report['summary']['total_cost_usd']:.4f}")
    print(f"   Scenario Creation: ${cost_report['summary']['scenario_creation_cost']:.4f}")
    print(f"   Conversations: ${cost_report['summary']['conversation_cost']:.4f}")
    print(f"   Scenarios Created: {cost_report['summary']['scenarios_created']}")
    print(f"   Conversations Completed: {cost_report['summary']['conversations_completed']}")
    
    print("\n💡 PART 4: COST ANALYSIS AND INSIGHTS")
    print("-" * 40)
    
    # Calculate cost per scenario and conversation
    scenario_cost = scenario_report['total_cost_usd']
    conversation_cost = conversation_report['total_cost_usd']
    total_cost = scenario_cost + conversation_cost
    
    print(f"📊 Cost Breakdown:")
    print(f"   Scenario Creation: ${scenario_cost:.4f} ({scenario_cost/total_cost*100:.1f}%)")
    print(f"   Conversation: ${conversation_cost:.4f} ({conversation_cost/total_cost*100:.1f}%)")
    print(f"   TOTAL: ${total_cost:.4f}")
    
    # Token usage analysis
    scenario_tokens = scenario_report['total_tokens']
    conversation_tokens = conversation_report['total_tokens']
    total_tokens = scenario_tokens + conversation_tokens
    
    print(f"\n🔢 Token Usage:")
    print(f"   Scenario Creation: {scenario_tokens:,} tokens")
    print(f"   Conversation: {conversation_tokens:,} tokens")
    print(f"   TOTAL: {total_tokens:,} tokens")
    print(f"   Average cost per 1K tokens: ${(total_cost / total_tokens * 1000):.4f}")
    
    # Speech usage analysis
    stt_minutes = conversation_report['total_stt_minutes']
    tts_characters = conversation_report['total_tts_characters']
    
    print(f"\n🎤 Speech Usage:")
    print(f"   STT: {stt_minutes:.1f} minutes")
    print(f"   TTS: {tts_characters:,} characters")
    print(f"   STT cost per minute: ${(stt_minutes * 0.024):.4f}")
    print(f"   TTS cost per 1K chars: ${(tts_characters * 0.000016):.4f}")
    
    print("\n💰 COST OPTIMIZATION RECOMMENDATIONS")
    print("-" * 40)
    
    # Generate recommendations based on usage patterns
    if scenario_cost > conversation_cost:
        print("🔍 Scenario creation is your highest cost component:")
        print("   • Consider caching and reusing scenarios")
        print("   • Optimize prompts to reduce token usage")
        print("   • Use GPT-4o instead of GPT-4 for cost savings")
    else:
        print("🔍 Conversations are your highest cost component:")
        print("   • Optimize conversation prompts")
        print("   • Consider shorter AI responses")
        print("   • Use streaming TTS to reduce latency costs")
    
    if total_tokens > 10000:
        print("🔍 High token usage detected:")
        print("   • Review prompt efficiency")
        print("   • Consider using smaller models for simple tasks")
        print("   • Implement response caching where possible")
    
    if stt_minutes > 5:
        print("🔍 Significant STT usage:")
        print("   • Consider batch processing audio")
        print("   • Optimize audio quality vs cost")
        print("   • Use voice activity detection to reduce processing")
    
    print(f"\n✅ WORKFLOW COMPLETE!")
    print(f"📊 Total Example Cost: ${total_cost:.4f}")
    print(f"🎯 This represents the cost for creating 1 scenario + 1 conversation (5 messages)")
    
    # Extrapolate daily/monthly costs
    daily_scenarios = 5  # Assume 5 scenarios per day
    daily_conversations = 20  # Assume 20 conversations per day
    
    estimated_daily_cost = (scenario_cost * daily_scenarios) + (conversation_cost * daily_conversations)
    estimated_monthly_cost = estimated_daily_cost * 30
    
    print(f"\n📈 COST PROJECTIONS:")
    print(f"   Estimated daily cost (5 scenarios, 20 conversations): ${estimated_daily_cost:.2f}")
    print(f"   Estimated monthly cost: ${estimated_monthly_cost:.2f}")
    
    return {
        "scenario_cost": scenario_cost,
        "conversation_cost": conversation_cost,
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "stt_minutes": stt_minutes,
        "tts_characters": tts_characters,
        "estimated_daily_cost": estimated_daily_cost,
        "estimated_monthly_cost": estimated_monthly_cost
    }

async def quick_cost_estimate():
    """Quick cost estimation without full tracking"""
    print("\n🧮 QUICK COST ESTIMATION TOOL")
    print("=" * 40)
    
    # Typical usage patterns
    scenarios = {
        "simple": {"tokens": 3000, "description": "Simple scenario (basic template)"},
        "moderate": {"tokens": 6000, "description": "Moderate scenario (detailed template + personas)"},
        "complex": {"tokens": 12000, "description": "Complex scenario (full template + multiple personas + detailed prompts)"}
    }
    
    conversations = {
        "short": {"messages": 3, "tokens_per_msg": 150, "stt_seconds": 10, "tts_chars": 200},
        "medium": {"messages": 8, "tokens_per_msg": 200, "stt_seconds": 15, "tts_chars": 300},
        "long": {"messages": 15, "tokens_per_msg": 250, "stt_seconds": 20, "tts_chars": 400}
    }
    
    print("📊 Scenario Creation Costs:")
    for scenario_type, data in scenarios.items():
        tokens = data["tokens"]
        # Assume 70% input, 30% output for GPT-4o
        input_tokens = tokens * 0.7
        output_tokens = tokens * 0.3
        cost = (input_tokens / 1000 * 0.005) + (output_tokens / 1000 * 0.015)
        print(f"   {scenario_type.capitalize()}: {tokens:,} tokens → ${cost:.4f} ({data['description']})")
    
    print("\n💬 Conversation Costs:")
    for conv_type, data in conversations.items():
        messages = data["messages"]
        tokens_per_msg = data["tokens_per_msg"]
        stt_seconds = data["stt_seconds"]
        tts_chars = data["tts_chars"]
        
        # Calculate costs
        total_tokens = messages * tokens_per_msg
        input_tokens = total_tokens * 0.4  # User input
        output_tokens = total_tokens * 0.6  # AI response
        
        token_cost = (input_tokens / 1000 * 0.005) + (output_tokens / 1000 * 0.015)
        stt_cost = (stt_seconds * messages / 60) * 0.024
        tts_cost = (tts_chars * messages) * 0.000016
        
        total_cost = token_cost + stt_cost + tts_cost
        
        print(f"   {conv_type.capitalize()}: {messages} msgs, {total_tokens:,} tokens → ${total_cost:.4f}")
        print(f"      Tokens: ${token_cost:.4f}, STT: ${stt_cost:.4f}, TTS: ${tts_cost:.4f}")
    
    print("\n📈 Daily Usage Scenarios:")
    usage_scenarios = [
        {"name": "Light User", "scenarios": 2, "conversations": 5, "conv_type": "short"},
        {"name": "Regular User", "scenarios": 5, "conversations": 15, "conv_type": "medium"},
        {"name": "Heavy User", "scenarios": 10, "conversations": 30, "conv_type": "long"},
        {"name": "Enterprise", "scenarios": 25, "conversations": 100, "conv_type": "medium"}
    ]
    
    for usage in usage_scenarios:
        # Use moderate scenario cost and appropriate conversation cost
        scenario_cost = 6000 * 0.7 / 1000 * 0.005 + 6000 * 0.3 / 1000 * 0.015  # Moderate scenario
        conv_data = conversations[usage["conv_type"]]
        
        conv_tokens = conv_data["messages"] * conv_data["tokens_per_msg"]
        conv_token_cost = (conv_tokens * 0.4 / 1000 * 0.005) + (conv_tokens * 0.6 / 1000 * 0.015)
        conv_stt_cost = (conv_data["stt_seconds"] * conv_data["messages"] / 60) * 0.024
        conv_tts_cost = (conv_data["tts_chars"] * conv_data["messages"]) * 0.000016
        conv_cost = conv_token_cost + conv_stt_cost + conv_tts_cost
        
        daily_cost = (scenario_cost * usage["scenarios"]) + (conv_cost * usage["conversations"])
        monthly_cost = daily_cost * 30
        
        print(f"   {usage['name']}: ${daily_cost:.2f}/day, ${monthly_cost:.2f}/month")
        print(f"      ({usage['scenarios']} scenarios, {usage['conversations']} {usage['conv_type']} conversations)")

if __name__ == "__main__":
    print("🧪 Cost Analysis Example Workflow")
    print("This example demonstrates complete cost tracking for AI services")
    print("=" * 60)
    
    # Run the complete workflow example
    results = asyncio.run(example_workflow())
    
    # Run quick cost estimation
    asyncio.run(quick_cost_estimate())
    
    print(f"\n🎉 Example completed successfully!")
    print(f"💰 Total example cost: ${results['total_cost']:.4f}")
    print(f"📊 Use this as a baseline for your actual usage costs")