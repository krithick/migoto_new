# AI Cost Analysis Tool - Complete Guide

## 📋 Overview

This comprehensive cost analysis system helps you track and optimize costs for your AI-powered training scenarios. It monitors:

- **Token usage** (OpenAI API calls)
- **Speech services** (STT/TTS)
- **Scenario creation costs**
- **Conversation session costs**
- **Detailed cost breakdowns and reports**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas matplotlib seaborn
```

### 2. Add to FastAPI App

```python
# In your main.py
from cost_analysis_tool import router as cost_router
from cost_dashboard import router as dashboard_router

app.include_router(cost_router)
app.include_router(dashboard_router)
```

### 3. Run a Test

```bash
python scenario_cost_tester.py customer_service
```

## 📊 Components

### 1. Cost Analysis Tool (`cost_analysis_tool.py`)
- **CostAnalyzer**: Main cost tracking class
- **TokenUsage**: Track OpenAI API token usage
- **SpeechUsage**: Track STT/TTS usage
- **API endpoints**: RESTful API for cost tracking

### 2. Scenario Cost Tester (`scenario_cost_tester.py`)
- **ScenarioCostTester**: Complete workflow testing
- **Predefined scenarios**: Ready-to-use test cases
- **Cost measurement**: End-to-end cost analysis

### 3. Cost Dashboard (`cost_dashboard.py`)
- **Web interface**: Visual cost analysis dashboard
- **Charts and graphs**: Usage trends and breakdowns
- **Export functionality**: CSV/JSON reports

### 4. Integration Helper (`integrate_cost_tracking.py`)
- **CostTrackingIntegration**: Easy integration with existing code
- **Example code**: How to add cost tracking to your endpoints

## 💰 Current Pricing (Update as needed)

| Service | Unit | Cost (USD) |
|---------|------|------------|
| GPT-4o Input | 1K tokens | $0.005 |
| GPT-4o Output | 1K tokens | $0.015 |
| GPT-4 Input | 1K tokens | $0.03 |
| GPT-4 Output | 1K tokens | $0.06 |
| Speech-to-Text | Per minute | $0.024 |
| Text-to-Speech | Per character | $0.000016 |

## 🔧 Usage Examples

### Track Scenario Creation

```python
from cost_analysis_tool import CostAnalyzer, TokenUsage

# Initialize
analyzer = CostAnalyzer(db)

# Start tracking
scenario_id = await analyzer.start_scenario_creation_tracking(
    "Customer Service Training", "user123", "api_upload"
)

# Track token usage
usage = TokenUsage(
    timestamp=datetime.now().isoformat(),
    operation="scenario_analysis",
    model="gpt-4o",
    prompt_tokens=1500,
    completion_tokens=800,
    user_id="user123"
)
await analyzer.add_scenario_token_usage(scenario_id, usage)

# Complete tracking
report = await analyzer.complete_scenario_creation_tracking(scenario_id)
print(f"Total cost: ${report['total_cost_usd']:.4f}")
```

### Track Conversation Session

```python
# Start conversation tracking
await analyzer.start_conversation_tracking(
    "session_123", "Customer Service Training", "assess_mode", "user123"
)

# Track token usage during conversation
token_usage = TokenUsage(
    timestamp=datetime.now().isoformat(),
    operation="chat_response",
    model="gpt-4o",
    prompt_tokens=200,
    completion_tokens=300,
    user_id="user123",
    session_id="session_123"
)
await analyzer.add_conversation_token_usage("session_123", token_usage)

# Track STT usage
stt_usage = SpeechUsage(
    timestamp=datetime.now().isoformat(),
    operation="stt",
    duration_seconds=15.0,
    user_id="user123",
    session_id="session_123"
)
await analyzer.add_conversation_speech_usage("session_123", stt_usage)

# Track TTS usage
tts_usage = SpeechUsage(
    timestamp=datetime.now().isoformat(),
    operation="tts",
    character_count=250,
    user_id="user123",
    session_id="session_123"
)
await analyzer.add_conversation_speech_usage("session_123", tts_usage)

# Complete tracking
report = await analyzer.complete_conversation_tracking("session_123")
```

### Generate Cost Reports

```python
# Generate comprehensive report
report = await analyzer.generate_cost_report(
    "user123", 
    "2024-01-01T00:00:00", 
    "2024-01-31T23:59:59"
)

print(f"Total cost: ${report['summary']['total_cost_usd']:.4f}")
print(f"Scenarios created: {report['summary']['scenarios_created']}")
print(f"Conversations: {report['summary']['conversations_completed']}")
```

## 🌐 Web Dashboard

Access the web dashboard at: `http://localhost:9000/cost-dashboard/`

Features:
- **Real-time cost monitoring**
- **Interactive charts and graphs**
- **Service breakdown analysis**
- **Export functionality**
- **Usage trends over time**

## 📈 API Endpoints

### Cost Tracking
- `POST /cost-analysis/scenario/start-tracking` - Start scenario cost tracking
- `POST /cost-analysis/scenario/{id}/add-token-usage` - Add token usage
- `POST /cost-analysis/scenario/{id}/complete` - Complete scenario tracking
- `POST /cost-analysis/conversation/start-tracking` - Start conversation tracking
- `POST /cost-analysis/conversation/{id}/add-token-usage` - Add token usage
- `POST /cost-analysis/conversation/{id}/add-speech-usage` - Add STT/TTS usage
- `POST /cost-analysis/conversation/{id}/complete` - Complete conversation tracking

### Reports and Dashboard
- `GET /cost-analysis/report` - Generate cost report
- `GET /cost-analysis/pricing` - Get current pricing
- `GET /cost-dashboard/` - Web dashboard
- `GET /cost-dashboard/export` - Export detailed reports
- `GET /cost-dashboard/api/data` - Dashboard data API

## 🔄 Integration with Existing Code

### 1. Scenario Generator Integration

```python
# In your scenario_generator.py
from integrate_cost_tracking import CostTrackingIntegration

@router.post("/analyze-scenario-with-tracking")
async def analyze_scenario_with_tracking(
    scenario_document: str = Body(...),
    scenario_name: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    # Initialize cost tracking
    cost_tracker = CostTrackingIntegration(db)
    scenario_id = await cost_tracker.start_scenario_cost_tracking(
        scenario_name, str(current_user.id)
    )
    
    try:
        # Your existing scenario generation code
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Track each API call
        template_data = await generator.extract_scenario_info(scenario_document)
        # await cost_tracker.track_scenario_token_usage(scenario_id, response, "analysis", str(current_user.id))
        
        personas = await generator.generate_personas_from_template(template_data)
        # await cost_tracker.track_scenario_token_usage(scenario_id, response, "personas", str(current_user.id))
        
        # Complete tracking
        cost_report = await cost_tracker.complete_scenario_tracking(scenario_id)
        
        return {
            "template_data": template_data,
            "personas": personas,
            "cost_report": cost_report
        }
    except Exception as e:
        await cost_tracker.complete_scenario_tracking(scenario_id)
        raise e
```

### 2. Chat System Integration

```python
# In your chat.py
from integrate_cost_tracking import CostTrackingIntegration

@router.post("/chat/initialize-with-tracking")
async def initialize_chat_with_tracking(
    avatar_interaction_id: UUID = Form(...),
    mode: str = Form(...),
    scenario_name: str = Form(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    # Initialize chat session
    session = await initialize_chat_session(db, avatar_interaction_id, mode, current_user.id)
    
    # Start cost tracking
    cost_tracker = CostTrackingIntegration(db)
    await cost_tracker.start_conversation_cost_tracking(
        session.id, scenario_name, mode, str(current_user.id)
    )
    
    return {"session_id": session.id, "cost_tracking": True}

# In your streaming response
async def stream_with_cost_tracking():
    cost_tracker = CostTrackingIntegration(db)
    
    # When processing user message (STT)
    await cost_tracker.track_stt_usage(session_id, audio_duration)
    
    # When getting AI response
    await cost_tracker.track_conversation_token_usage(session_id, response, "chat")
    
    # When generating TTS
    await cost_tracker.track_tts_usage(session_id, len(response_text))
    
    # When conversation ends
    if conversation_finished:
        cost_report = await cost_tracker.complete_conversation_tracking(session_id)
```

## 📊 Testing and Validation

### Run Predefined Tests

```bash
# Test customer service scenario
python scenario_cost_tester.py customer_service

# Test sales training scenario
python scenario_cost_tester.py sales_training

# Test DEI training scenario
python scenario_cost_tester.py dei_training
```

### Custom Test

```python
from scenario_cost_tester import run_custom_test

results, filename = await run_custom_test(
    "My Custom Scenario",
    "Create a training scenario for..."
)
```

## 💡 Cost Optimization Tips

1. **Use GPT-4o instead of GPT-4**: ~5x cheaper for similar quality
2. **Optimize prompts**: Shorter, focused prompts reduce token usage
3. **Cache scenarios**: Reuse generated content instead of recreating
4. **Batch operations**: Process multiple items in single API calls
5. **Monitor usage**: Use dashboard to identify cost hotspots
6. **Set budgets**: Implement usage limits and alerts
7. **Choose appropriate models**: Use smaller models for simple tasks

## 🔍 Monitoring and Alerts

### Set Up Cost Alerts

```python
async def check_daily_budget(user_id: str, budget_limit: float):
    """Check if user is approaching daily budget"""
    today = datetime.now().replace(hour=0, minute=0, second=0)
    tomorrow = today + timedelta(days=1)
    
    report = await analyzer.generate_cost_report(
        user_id, today.isoformat(), tomorrow.isoformat()
    )
    
    current_cost = report["summary"]["total_cost_usd"]
    
    if current_cost > budget_limit * 0.8:  # 80% of budget
        # Send alert
        print(f"⚠️ User {user_id} approaching budget: ${current_cost:.4f} / ${budget_limit:.2f}")
    
    return current_cost
```

### Usage Analytics

```python
async def analyze_usage_patterns(user_id: str):
    """Analyze user's usage patterns"""
    # Get last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    report = await analyzer.generate_cost_report(
        user_id, start_date.isoformat(), end_date.isoformat()
    )
    
    # Calculate averages
    daily_avg = report["summary"]["total_cost_usd"] / 30
    scenarios_per_day = report["summary"]["scenarios_created"] / 30
    conversations_per_day = report["summary"]["conversations_completed"] / 30
    
    return {
        "daily_average_cost": daily_avg,
        "scenarios_per_day": scenarios_per_day,
        "conversations_per_day": conversations_per_day,
        "cost_per_scenario": daily_avg / scenarios_per_day if scenarios_per_day > 0 else 0,
        "cost_per_conversation": daily_avg / conversations_per_day if conversations_per_day > 0 else 0
    }
```

## 🛠️ Troubleshooting

### Common Issues

1. **Missing token usage data**
   - Ensure you're calling cost tracking functions after each API call
   - Check that response objects have usage information

2. **Incorrect cost calculations**
   - Verify pricing constants in `PRICING` dictionary
   - Update pricing regularly as Azure rates change

3. **Dashboard not loading**
   - Check that matplotlib and seaborn are installed
   - Ensure database connection is working

4. **Integration errors**
   - Make sure cost tracking is initialized before use
   - Handle exceptions properly to avoid breaking existing functionality

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints to track cost calculations
analyzer = CostAnalyzer(db)
analyzer.debug = True  # Add this flag to enable debug output
```

## 📚 Additional Resources

- **Azure OpenAI Pricing**: https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/
- **Azure Speech Services Pricing**: https://azure.microsoft.com/pricing/details/cognitive-services/speech-services/
- **Cost Optimization Guide**: Internal documentation on optimizing AI costs
- **API Documentation**: Detailed API reference for all endpoints

## 🤝 Support

For questions or issues:
1. Check this guide first
2. Review the example code in the repository
3. Test with the provided test scenarios
4. Contact the development team for assistance

---

**Last Updated**: January 2024
**Version**: 1.0.0