# API Flow: Archetype System Integration

## Complete End-to-End Flow

### 1. **TEMPLATE GENERATION FLOW** (Primary Method) ⭐

#### Option A: From Document Upload
```
Frontend/Client
    ↓
POST /analyze-template-with-optional-docs
    ↓
Upload: template.docx + supporting_docs (optional)
    ↓
Extract text from document
    ↓
[ARCHETYPE SYSTEM ACTIVATES - AUTOMATIC]
    ↓
EnhancedScenarioGenerator.extract_scenario_info()
    ↓
  ├─> ArchetypeClassifier.classify_scenario()
  │   Returns: {
  │     "primary_archetype": "PERSUASION",
  │     "sub_type": "PHARMA_SALES",
  │     "confidence_score": 0.95
  │   }
  │
  ├─> Extract context, roles, objectives
  └─> Extract evaluation metrics
    ↓
Save to templates collection with archetype data
    ↓
Process supporting docs → Knowledge Base (optional)
    ↓
Return template_id + template_data (EDITABLE)
    ↓
Frontend: User edits template sections
    ↓
POST /generate-prompts-from-template
    ↓
Generate system prompts for learn/try/assess modes
    ↓
EnhancedScenarioGenerator.generate_personas_from_template(
  template_data,
  archetype_classification  ← USES ARCHETYPE!
)
    ↓
Generates archetype-aware personas:
  - PERSUASION: objection_library, decision_criteria
  - CONFRONTATION: defensive_mechanisms, emotional_state
    ↓
Create avatar_interactions with personas
    ↓
POST /modules/{module_id}/scenarios
    ↓
Save complete scenario with archetype fields
    ↓
Returns ScenarioDB to client
```

#### Option B: From Text Prompt
```
Frontend/Client
    ↓
POST /analyze-scenario-enhanced
    ↓
Submit: scenario_document (text) + supporting_docs (optional)
    ↓
[ARCHETYPE SYSTEM ACTIVATES - AUTOMATIC]
    ↓
EnhancedScenarioGenerator.extract_scenario_info()
    ↓
  ├─> ArchetypeClassifier.classify_scenario()
  │   Returns archetype classification
  │
  └─> Extract template structure
    ↓
Save to templates collection
    ↓
(Same flow as Option A from here)
```

### 2. **Direct Scenario Creation Flow** (Alternative)

```
Frontend/Client
    ↓
POST /modules/{module_id}/scenarios
    ↓
create_scenario_endpoint()
    ↓
create_scenario() [core/scenario.py]
    ↓
Links to existing template_id (already has archetype)
    ↓
Saves scenario with archetype fields from template
    ↓
Returns ScenarioDB to client
```

### 3. **Chat Session Flow (Bot Using Archetype)**

```
Frontend/Client
    ↓
POST /chat/sessions (create session)
    ↓
initialize_chat_session() [dynamic_chat.py]
    ↓
Stores: {
  "avatar_interaction": "uuid",
  "persona_id": "uuid",
  "language_id": "uuid"
}
    ↓
POST /chat/sessions/{session_id}/messages
    ↓
get_chat_handler() [DynamicChatFactory]
    ↓
Loads persona from database
    ↓
format_persona_context() [DynamicChatHandler]
    ↓
_build_archetype_instructions() [NEW!]
    ↓
Extracts archetype fields:
  - objection_library
  - defensive_mechanisms
  - emotional_state
  - etc.
    ↓
Builds system prompt:
  "You are Dr. Patel...
   
   ## PERSUASION BEHAVIOR:
   You have specific objections:
   1. Objection: Concerned about side effects
      Underlying concern: Patient safety
   2. Objection: Skeptical about benefits
      Underlying concern: Prefers proven treatments
   
   Your decision criteria: Clinical evidence, Patient safety
   Your personality type: Analytical"
    ↓
Sends to Azure OpenAI
    ↓
Bot responds using objections naturally!
    ↓
Returns streaming response to client
```

## API Endpoints Reference

### Template Generation (Primary Flow) ⭐

#### Analyze Template from Document
```http
POST /analyze-template-with-optional-docs
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

Form Data:
- template_file: file (required) - .docx, .pdf, or .txt
- template_name: string (required)
- supporting_docs: file[] (optional) - for knowledge base

Response:
{
  "template_id": "uuid",
  "template_data": {
    "context_overview": {...},
    "roles": {...},
    "objectives": {...},
    "evaluation_metrics": {...},
    
    // ⭐ ARCHETYPE DATA (AUTOMATIC)
    "archetype_classification": {
      "primary_archetype": "PERSUASION",
      "sub_type": "PHARMA_SALES",
      "confidence_score": 0.95,
      "conversation_pattern": "mutual"
    }
  },
  "knowledge_base_id": "kb_uuid" or null,
  "supporting_documents_count": 3,
  "has_supporting_docs": true,
  "fact_checking_enabled": true,
  "message": "Template analyzed and ready for editing",
  "next_step": "Edit template sections, then generate prompts"
}
```

#### Analyze Scenario from Text Prompt
```http
POST /analyze-scenario-enhanced
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

Form Data:
- scenario_document: string (required) - text description
- template_name: string (required)
- supporting_docs: file[] (optional)

Response: (Same as above)
{
  "template_id": "uuid",
  "template_data": {
    // Includes archetype_classification automatically
  },
  ...
}
```

#### Generate Prompts from Template
```http
POST /generate-prompts-from-template
Authorization: Bearer {admin_token}

Request Body:
{
  "template_id": "uuid",
  "template_data": {
    // Edited template data (includes archetype_classification)
  }
}

Response:
{
  "template_id": "uuid",
  "learn_mode": {
    "avatar_interaction_id": "uuid",
    "persona": {
      "name": "Dr. Patel",
      // ⭐ ARCHETYPE-AWARE PERSONA
      "objection_library": [...],  // For PERSUASION
      "decision_criteria": [...],
      "personality_type": "Analytical"
    }
  },
  "try_mode": {...},
  "assess_mode": {...}
}
```

### Scenario Management

#### Create Scenario (Links to Template)
```http
POST /modules/{module_id}/scenarios
Authorization: Bearer {admin_token}

Request Body:
{
  "scenario_name": "Pharma Sales Training",
  "scenario_description": "Train reps to handle skeptical doctors...",
  "template_id": "uuid",  // ← Links to template with archetype
  "learn_mode": {
    "avatar_interaction": "uuid",
    "videos": [],
    "documents": []
  },
  "try_mode": {
    "avatar_interaction": "uuid"
  },
  "assess_mode": {
    "avatar_interaction": "uuid"
  }
}

Response: (ARCHETYPE FROM TEMPLATE)
{
  "id": "uuid",
  "scenario_name": "Pharma Sales Training",
  "template_id": "uuid",
  "archetype": "PERSUASION",              // ← FROM TEMPLATE
  "archetype_sub_type": "PHARMA_SALES",   // ← FROM TEMPLATE
  "archetype_confidence": 0.95,           // ← FROM TEMPLATE
  "learn_mode": {...},
  "try_mode": {...},
  "assess_mode": {...},
  "created_at": "2025-01-20T00:00:00Z"
}
```

#### Get Scenario (With Archetype Data)
```http
GET /scenarios/{scenario_id}
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "scenario_name": "Pharma Sales Training",
  "archetype": "PERSUASION",
  "archetype_sub_type": "PHARMA_SALES",
  "archetype_confidence": 0.95,
  "learn_mode": {
    "avatar_interaction": {
      "id": "uuid",
      "system_prompt": "...",
      "bot_role": "Doctor",
      "archetype": "PERSUASION",           // ← ALSO ON AVATAR
      "archetype_sub_type": "PHARMA_SALES"
    }
  },
  ...
}
```

### Chat/Bot Endpoints

#### Create Chat Session
```http
POST /chat/sessions
Authorization: Bearer {token}

Request Body:
{
  "avatar_interaction_id": "uuid",
  "mode": "assess_mode",
  "persona_id": "uuid",      // ← Persona has archetype fields
  "language_id": "uuid"
}

Response:
{
  "session_id": "uuid",
  "scenario_name": "Pharma Sales Training",
  "avatar_interaction": "uuid",
  "persona_id": "uuid",
  "created_at": "2025-01-20T00:00:00Z"
}
```

#### Send Message (Bot Uses Archetype)
```http
POST /chat/sessions/{session_id}/messages
Authorization: Bearer {token}

Request Body:
{
  "message": "Hi Dr. Patel, let me tell you about GlucoStable XR",
  "name": "John Smith"
}

Response: (Streaming)
{
  "chunk": "I appreciate that, but I'm concerned about long-term side effects...",
  "finish": null,
  "usage": null
}

// Bot naturally uses objection from objection_library!
```

## Database Schema Changes

### Scenarios Collection
```javascript
{
  "_id": "uuid",
  "scenario_name": "Pharma Sales Training",
  "scenario_description": "...",
  
  // NEW ARCHETYPE FIELDS (added automatically)
  "archetype": "PERSUASION",
  "archetype_sub_type": "PHARMA_SALES",
  "archetype_confidence": 0.95,
  
  "learn_mode": {...},
  "try_mode": {...},
  "assess_mode": {...},
  "created_by": "uuid",
  "company_id": "uuid",
  "created_at": "2025-01-20T00:00:00Z"
}
```

### Personas Collection
```javascript
{
  "_id": "uuid",
  "name": "Dr. Archana Patel",
  "persona_type": "endocrinologist",
  "age": 52,
  "gender": "female",
  "character_goal": "Ensure patient safety...",
  
  // NEW ARCHETYPE FIELDS (for PERSUASION)
  "objection_library": [
    {
      "objection": "Concerned about long-term side effects",
      "underlying_concern": "Patient safety over prolonged use",
      "counter_strategy": "Provide detailed clinical trial data..."
    },
    {
      "objection": "Skeptical about benefits",
      "underlying_concern": "Prefers tried and tested treatments",
      "counter_strategy": "Highlight comparative studies..."
    }
  ],
  "decision_criteria": [
    "Clinical evidence",
    "Patient safety",
    "Cost-effectiveness"
  ],
  "personality_type": "Analytical",
  "current_position": "Prefers established medications...",
  "satisfaction_level": "Neutral",
  
  "created_at": "2025-01-20T00:00:00Z"
}
```

### Avatar Interactions Collection
```javascript
{
  "_id": "uuid",
  "system_prompt": "You are Dr. Patel...",
  "bot_role": "Doctor",
  "bot_role_alt": "Dr. Patel",
  
  // NEW ARCHETYPE FIELDS (optional, for reference)
  "archetype": "PERSUASION",
  "archetype_sub_type": "PHARMA_SALES",
  "archetype_confidence": 0.95,
  
  "created_at": "2025-01-20T00:00:00Z"
}
```

## Integration Points

### Where Archetype System Activates

1. **Scenario Creation** (`scenario_generator.py`)
   - `extract_scenario_info()` → Calls classifier
   - `generate_personas_from_template()` → Uses classification

2. **Bot Initialization** (`dynamic_chat.py`)
   - `format_persona_context()` → Injects archetype instructions
   - `_build_archetype_instructions()` → Extracts archetype fields

3. **Database Queries** (All scenario endpoints)
   - Archetype fields automatically included in responses
   - No code changes needed in existing endpoints!

## Migration for Existing Data

### One-Time Migration
```bash
# Classify all existing scenarios
python migrate_existing_scenarios.py --live
```

This will:
1. Load all scenarios from database
2. Classify each one using ArchetypeClassifier
3. Add archetype fields to scenario documents
4. Update personas with archetype-specific fields (if regenerated)

## Frontend Integration Examples

### Display Archetype Badge
```javascript
// Scenario card component
<ScenarioCard>
  <h3>{scenario.scenario_name}</h3>
  
  {/* NEW: Show archetype badge */}
  {scenario.archetype && (
    <Badge color={getArchetypeColor(scenario.archetype)}>
      {scenario.archetype}
      {scenario.archetype_sub_type && ` - ${scenario.archetype_sub_type}`}
    </Badge>
  )}
  
  <p>{scenario.scenario_description}</p>
</ScenarioCard>
```

### Filter by Archetype
```javascript
// Scenario list with filters
<ScenarioFilters>
  <Select onChange={handleArchetypeFilter}>
    <option value="">All Archetypes</option>
    <option value="PERSUASION">Persuasion</option>
    <option value="CONFRONTATION">Confrontation</option>
    <option value="HELP_SEEKING">Help Seeking</option>
    <option value="INVESTIGATION">Investigation</option>
    <option value="NEGOTIATION">Negotiation</option>
  </Select>
</ScenarioFilters>

// API call
GET /scenarios?archetype=PERSUASION
```

### Show Archetype-Specific Tips
```javascript
// Training tips based on archetype
{scenario.archetype === 'PERSUASION' && (
  <TipBox>
    <h4>Persuasion Training Tips:</h4>
    <ul>
      <li>Listen for objections and underlying concerns</li>
      <li>Address decision criteria systematically</li>
      <li>Adapt to personality type (Analytical, Emotional, etc.)</li>
    </ul>
  </TipBox>
)}

{scenario.archetype === 'CONFRONTATION' && (
  <TipBox>
    <h4>Confrontation Training Tips:</h4>
    <ul>
      <li>Recognize defensive mechanisms</li>
      <li>Maintain calm and professional tone</li>
      <li>Focus on behavior, not person</li>
    </ul>
  </TipBox>
)}
```

## Testing the Flow

### 1. Create a Scenario
```bash
curl -X POST http://localhost:9000/modules/{module_id}/scenarios \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "Pharma Sales Training",
    "scenario_description": "A pharma rep must convince Dr. Patel...",
    "assess_mode": {
      "avatar_interaction": "{avatar_id}"
    }
  }'
```

### 2. Check Archetype Was Added
```bash
curl -X GET http://localhost:9000/scenarios/{scenario_id} \
  -H "Authorization: Bearer {token}"

# Response should include:
# "archetype": "PERSUASION"
# "archetype_sub_type": "PHARMA_SALES"
# "archetype_confidence": 0.95
```

### 3. Start Chat Session
```bash
curl -X POST http://localhost:9000/chat/sessions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "avatar_interaction_id": "{avatar_id}",
    "mode": "assess_mode",
    "persona_id": "{persona_id}"
  }'
```

### 4. Send Message and See Archetype Behavior
```bash
curl -X POST http://localhost:9000/chat/sessions/{session_id}/messages \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Let me tell you about GlucoStable XR"
  }'

# Bot will respond using objections from objection_library!
# Example: "I appreciate that, but I'm concerned about long-term side effects..."
```

## Summary

### What Happens Automatically:
1. ✅ Scenario creation → Archetype classification
2. ✅ Persona generation → Archetype-specific fields
3. ✅ Bot initialization → Archetype instructions injected
4. ✅ Conversation → Bot uses archetype behaviors

### What You Need to Do:
1. ❌ Nothing! System works automatically
2. ✅ (Optional) Display archetype badges in UI
3. ✅ (Optional) Add archetype filters
4. ✅ (Optional) Run migration for existing scenarios

### Key Benefits:
- **Zero Breaking Changes**: Existing API calls work unchanged
- **Automatic Enhancement**: New scenarios get archetype data automatically
- **Backward Compatible**: Old scenarios without archetypes still work
- **Production Ready**: Fully tested and integrated

The archetype system is now a seamless part of your API flow! 🎯
