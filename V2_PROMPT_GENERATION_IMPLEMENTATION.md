# V2 Prompt Generation Implementation

## Overview
V2 flow redesign for system prompt generation with async processing and SSE push notifications.

## Key Changes

### 1. Avatar Interaction Model Updates
**File**: `models/avatarInteraction_models.py`

```python
# BEFORE
system_prompt: str  # Required

# AFTER  
system_prompt: Optional[str] = None  # Optional - generated async
persona_id: Optional[UUID] = None  # Link to persona
```

**Reason**: Learn mode doesn't need persona, prompts generated async and saved to personas.

### 2. New Background Job Manager
**File**: `core/prompt_generation_job.py`

- Tracks async prompt generation jobs
- Manages SSE event queues
- Provides job status tracking
- Handles cleanup after completion

### 3. New V2 Endpoints
**File**: `scenario_prompt_generation_v2.py`

#### POST `/scenario/v2/generate-final-prompts`
Starts async prompt generation for multiple personas.

**Request**:
```json
{
  "template_id": "template_123",
  "persona_ids": ["persona_1", "persona_2", "persona_3"],
  "mode_mapping": {
    "persona_1": "learn_mode",
    "persona_2": "try_mode", 
    "persona_3": "assess_mode"
  }
}
```

**Response**:
```json
{
  "job_id": "job_uuid",
  "message": "Prompt generation started",
  "status": "processing",
  "sse_endpoint": "/scenario/v2/prompt-generation-status/job_uuid",
  "persona_count": 3
}
```

#### GET `/scenario/v2/prompt-generation-status/{job_id}` (SSE)
Real-time updates via Server-Sent Events.

**Event Types**:
```javascript
// Status update
{
  "type": "status_update",
  "status": "processing|completed|failed",
  "error": "error message if failed"
}

// Persona progress
{
  "type": "persona_progress",
  "persona_id": "persona_1",
  "status": "processing|completed|failed"
}

// Final results
{
  "type": "results",
  "results": {
    "template_id": "...",
    "template_data": {...},
    "personas": {
      "persona_1": {
        "status": "completed",
        "mode": "learn_mode",
        "prompt_length": 5000,
        "persona_name": "Dr. Smith"
      }
    },
    "total_personas": 3,
    "successful": 3,
    "failed": 0
  }
}
```

#### GET `/scenario/v2/job-status/{job_id}`
Polling alternative to SSE.

## Workflow

### 1. User Creates Personas
```
POST /scenario/generate-personas
{
  "template_id": "template_123",
  "persona_type": "assess_mode_character",
  "count": 2
}
```

Returns personas WITHOUT prompts.

### 2. User Clicks "Create Avatar Interactions"
Frontend calls:
```
POST /scenario/v2/generate-final-prompts
{
  "template_id": "template_123",
  "persona_ids": ["p1", "p2", "p3"],
  "mode_mapping": {
    "p1": "learn_mode",
    "p2": "try_mode",
    "p3": "assess_mode"
  }
}
```

### 3. Backend Starts Background Task
- Creates job with unique ID
- Returns job_id immediately
- Starts async prompt generation

### 4. Frontend Connects to SSE
```javascript
const eventSource = new EventSource(
  `/scenario/v2/prompt-generation-status/${job_id}`
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'persona_progress') {
    // Update UI: "Generating prompt for Dr. Smith..."
  }
  
  if (data.type === 'results') {
    // Show complete template + persona details
    // Prompts are saved in personas
  }
};
```

### 5. Backend Generates Prompts
For each persona:
- **Learn Mode**: Uses `LearnModePromptGenerator` (template only)
- **Try/Assess Mode**: Uses `SystemPromptGenerator` (template + persona)
- Saves prompt to `personas_v2` collection
- Sends SSE progress update

### 6. Completion
- All prompts saved to persona records
- Final SSE event with results
- Frontend shows template data + persona details

## Try & Assess Mode Handling

**Same persona, same prompt used twice**:
```python
# Generate ONE prompt for both modes
prompt = await system_prompt_gen.generate_system_prompt(
    template_data=template_data,
    persona_data=persona_data,
    mode="assess_mode"  # Same for both
)

# Save to persona
await db.personas_v2.update_one(
    {"_id": persona_id},
    {"$set": {
        "system_prompt": prompt,
        "prompt_mode": "assess_mode",  # or "try_mode"
        "prompt_generated_at": datetime.now().isoformat()
    }}
)
```

## Database Schema Updates

### personas_v2 Collection
```python
{
  "_id": "persona_uuid",
  "name": "Dr. Smith",
  "age": 45,
  "role": "Physician",
  "archetype": "PERSUASION",
  "detail_categories": {...},
  "conversation_rules": {...},
  
  # NEW FIELDS
  "system_prompt": "Complete generated prompt...",  # Optional
  "prompt_mode": "assess_mode",  # Optional
  "prompt_generated_at": "2024-01-15T10:30:00"  # Optional
}
```

### avatar_interactions Collection
```python
{
  "_id": "interaction_uuid",
  "mode": "try_mode",
  "avatars": [...],
  "languages": [...],
  
  # UPDATED FIELDS
  "system_prompt": None,  # Optional now
  "persona_id": "persona_uuid",  # NEW - link to persona
  
  # Fetch prompt from persona during chat
}
```

## Error Handling

### Job Failures
```python
# Individual persona failure
{
  "persona_id": "p1",
  "status": "failed",
  "error": "LLM timeout"
}

# Job continues for other personas
```

### Retry Strategy
- Frontend can retry failed personas
- Call `/generate-final-prompts` with only failed persona_ids

## Frontend Integration

### React Hook Example
```javascript
const usePromptGeneration = (templateId, personas, modeMapping) => {
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState({});
  const [results, setResults] = useState(null);
  
  const startGeneration = async () => {
    // Start job
    const response = await fetch('/scenario/v2/generate-final-prompts', {
      method: 'POST',
      body: JSON.stringify({
        template_id: templateId,
        persona_ids: personas.map(p => p.id),
        mode_mapping: modeMapping
      })
    });
    
    const { job_id, sse_endpoint } = await response.json();
    
    // Connect to SSE
    const eventSource = new EventSource(sse_endpoint);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'status_update') {
        setStatus(data.status);
      }
      
      if (data.type === 'persona_progress') {
        setProgress(prev => ({
          ...prev,
          [data.persona_id]: data.status
        }));
      }
      
      if (data.type === 'results') {
        setResults(data.results);
        eventSource.close();
      }
    };
  };
  
  return { status, progress, results, startGeneration };
};
```

## Benefits

1. **Non-blocking**: User doesn't wait for slow LLM calls
2. **Real-time feedback**: Progress updates via SSE
3. **Scalable**: Can generate prompts for many personas
4. **Flexible**: Try & Assess share same prompt
5. **Clean separation**: Learn mode doesn't need persona

## Migration Notes

### Existing V1 Endpoints
- Keep `/generate-final-prompts` for backward compatibility
- Mark as deprecated
- Redirect to V2 in future

### Database Migration
- No migration needed
- New fields are optional
- Old records still work

## Testing

### Manual Test Flow
1. Create template via `/analyze-scenario-enhanced`
2. Generate personas via `/generate-personas`
3. Start prompt generation via `/generate-final-prompts`
4. Connect to SSE endpoint
5. Verify prompts saved to personas
6. Create avatar interactions with persona_id

### SSE Test (curl)
```bash
curl -N http://localhost:9000/scenario/v2/prompt-generation-status/job_uuid
```

## Next Steps

1. ✅ Make `system_prompt` optional in avatar_interaction model
2. ✅ Add `persona_id` field to avatar_interaction model
3. ✅ Create background job manager
4. ✅ Create V2 endpoints with SSE
5. ⏳ Update frontend to use V2 flow
6. ⏳ Add retry logic for failed personas
7. ⏳ Add job expiration/cleanup
8. ⏳ Add rate limiting for LLM calls
