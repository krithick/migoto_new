# Complete Archetype System Flow

## 🎯 The Real Scenario Creation Flow

### Step-by-Step: How Users Create Scenarios

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: TEMPLATE GENERATION (Archetype Classification Happens) │
└─────────────────────────────────────────────────────────────────┘

User uploads document OR enters text prompt
         ↓
POST /analyze-template-with-optional-docs
  OR
POST /analyze-scenario-enhanced
         ↓
┌──────────────────────────────────────────┐
│ EnhancedScenarioGenerator                │
│   .extract_scenario_info()               │
│                                          │
│   ┌────────────────────────────────┐    │
│   │ ArchetypeClassifier            │    │
│   │   .classify_scenario()         │    │
│   │                                │    │
│   │   Returns:                     │    │
│   │   - primary_archetype          │    │
│   │   - sub_type                   │    │
│   │   - confidence_score           │    │
│   │   - conversation_pattern       │    │
│   └────────────────────────────────┘    │
│                                          │
│   Extracts:                              │
│   - Context overview                     │
│   - Roles & objectives                   │
│   - Evaluation metrics                   │
│   - Archetype classification ⭐          │
└──────────────────────────────────────────┘
         ↓
Save to templates collection:
{
  "template_id": "uuid",
  "template_data": {
    "context_overview": {...},
    "roles": {...},
    "archetype_classification": {  ⭐ AUTOMATIC
      "primary_archetype": "PERSUASION",
      "sub_type": "PHARMA_SALES",
      "confidence_score": 0.95
    }
  },
  "knowledge_base_id": "kb_uuid" (if docs uploaded)
}
         ↓
Return to frontend for editing


┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: TEMPLATE EDITING (User Reviews & Edits)                │
└─────────────────────────────────────────────────────────────────┘

Frontend displays editable template:
- Context overview
- Roles & objectives
- Evaluation metrics
- Archetype badge (read-only) ⭐

User makes edits (optional)
         ↓
Edited template_data ready for prompt generation


┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: PROMPT GENERATION (Archetype-Aware Personas Created)   │
└─────────────────────────────────────────────────────────────────┘

POST /generate-prompts-from-template
{
  "template_id": "uuid",
  "template_data": {...}  // includes archetype_classification
}
         ↓
┌──────────────────────────────────────────────────────────┐
│ EnhancedScenarioGenerator                                │
│   .generate_personas_from_template(                      │
│     template_data,                                       │
│     archetype_classification  ⭐ PASSED HERE             │
│   )                                                      │
│                                                          │
│   Generates archetype-specific personas:                │
│                                                          │
│   IF PERSUASION:                                        │
│   ├─ objection_library: [                              │
│   │    {objection, underlying_concern, counter_strategy}│
│   │  ]                                                  │
│   ├─ decision_criteria: [...]                          │
│   ├─ personality_type: "Analytical"                    │
│   ├─ current_position: "..."                           │
│   └─ satisfaction_level: "Neutral"                     │
│                                                          │
│   IF CONFRONTATION:                                     │
│   ├─ sub_type: "PERPETRATOR" or "VICTIM"               │
│   ├─ power_dynamics: "Senior"                          │
│   ├─ defensive_mechanisms: [...] (perpetrator)         │
│   ├─ emotional_state: "..." (victim)                   │
│   └─ barriers_to_reporting: [...] (victim)             │
└──────────────────────────────────────────────────────────┘
         ↓
Create avatar_interactions with:
- System prompts (learn/try/assess modes)
- Personas with archetype fields ⭐
         ↓
Save to database:
- avatar_interactions collection
- personas collection (with archetype fields)
         ↓
Return avatar_interaction IDs


┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: SCENARIO CREATION (Links Everything Together)          │
└─────────────────────────────────────────────────────────────────┘

POST /modules/{module_id}/scenarios
{
  "scenario_name": "Pharma Sales Training",
  "template_id": "uuid",  ⭐ Links to template with archetype
  "learn_mode": {
    "avatar_interaction": "uuid"  // Has archetype-aware persona
  },
  "try_mode": {...},
  "assess_mode": {...}
}
         ↓
create_scenario() pulls archetype from template:
{
  "scenario_id": "uuid",
  "template_id": "uuid",
  "archetype": "PERSUASION",  ⭐ FROM TEMPLATE
  "archetype_sub_type": "PHARMA_SALES",
  "archetype_confidence": 0.95,
  "learn_mode": {...},
  "try_mode": {...},
  "assess_mode": {...}
}
         ↓
Scenario ready for training!


┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: TRAINING SESSION (Bot Uses Archetype Behaviors)        │
└─────────────────────────────────────────────────────────────────┘

User starts training session
         ↓
POST /chat/sessions
{
  "avatar_interaction_id": "uuid",
  "persona_id": "uuid",  // Has archetype fields
  "mode": "assess_mode"
}
         ↓
DynamicChatHandler initializes:
         ↓
format_persona_context()
         ↓
_build_archetype_instructions() ⭐ NEW!
         ↓
Extracts from persona:
- objection_library (PERSUASION)
- defensive_mechanisms (CONFRONTATION)
- emotional_state, barriers, etc.
         ↓
Builds system prompt:
"You are Dr. Patel...

## PERSUASION BEHAVIOR:
You have specific objections:
1. Objection: Concerned about long-term side effects
   Underlying concern: Patient safety
2. Objection: Skeptical about benefits
   Underlying concern: Prefers proven treatments

Your decision criteria: Clinical evidence, Patient safety
Your personality type: Analytical"
         ↓
Sends to Azure OpenAI
         ↓
Bot responds using objections naturally! ⭐
         ↓
User: "Let me tell you about GlucoStable XR"
Bot: "I appreciate that, but I'm concerned about 
      long-term side effects. My patients' safety 
      is paramount..."
```

## 🔑 Key Integration Points

### 1. Template Generation (Classification)
**File**: `scenario_generator.py`
**Function**: `extract_scenario_info()`
**What happens**: 
- Calls `ArchetypeClassifier.classify_scenario()`
- Returns template_data with `archetype_classification`

### 2. Persona Generation (Archetype-Aware)
**File**: `scenario_generator.py`
**Function**: `generate_personas_from_template()`
**What happens**:
- Receives `archetype_classification` parameter
- Generates archetype-specific prompts
- Creates personas with objection libraries, defensive mechanisms, etc.

### 3. Bot Initialization (Behavior Injection)
**File**: `dynamic_chat.py`
**Function**: `_build_archetype_instructions()`
**What happens**:
- Extracts archetype fields from persona
- Builds behavioral instructions
- Injects into system prompt

## 📊 Data Flow Through Collections

```
templates collection
├─ template_id
├─ template_data
│  └─ archetype_classification ⭐
└─ knowledge_base_id

         ↓ (used to generate)

personas collection
├─ persona_id
├─ name, age, gender, etc.
└─ archetype fields ⭐
   ├─ objection_library (PERSUASION)
   ├─ defensive_mechanisms (CONFRONTATION)
   └─ emotional_state, barriers, etc.

         ↓ (linked to)

avatar_interactions collection
├─ avatar_interaction_id
├─ system_prompt
├─ bot_role
└─ persona_id (reference)

         ↓ (used in)

scenarios collection
├─ scenario_id
├─ template_id (reference)
├─ archetype ⭐ (from template)
├─ archetype_sub_type
├─ archetype_confidence
└─ learn_mode, try_mode, assess_mode
   └─ avatar_interaction (reference)

         ↓ (creates)

sessions collection
├─ session_id
├─ avatar_interaction (reference)
├─ persona_id (reference)
└─ conversation_history

         ↓ (bot loads persona)

Bot System Prompt
├─ Basic persona info
└─ Archetype instructions ⭐
   ├─ Objection library
   ├─ Defensive mechanisms
   └─ Behavioral patterns
```

## 🎯 What Makes This Powerful

### Before Archetype System:
```
User uploads document
  ↓
Generic template extracted
  ↓
Generic personas created
  ↓
Bot has basic personality
  ↓
Conversation feels scripted
```

### After Archetype System:
```
User uploads document
  ↓
Template + ARCHETYPE classified ⭐
  ↓
Archetype-aware personas with objection libraries ⭐
  ↓
Bot has specific objections and behaviors ⭐
  ↓
Conversation feels REALISTIC ⭐
```

## 🚀 Example: Pharma Sales Scenario

### Input (User uploads):
```
"A pharmaceutical sales rep must convince Dr. Patel,
a skeptical endocrinologist, to prescribe GlucoStable XR..."
```

### Step 1 - Classification (Automatic):
```json
{
  "primary_archetype": "PERSUASION",
  "sub_type": "PHARMA_SALES",
  "confidence_score": 0.95
}
```

### Step 2 - Persona Generation (Archetype-Aware):
```json
{
  "name": "Dr. Archana Patel",
  "persona_type": "endocrinologist",
  "objection_library": [
    {
      "objection": "Concerned about long-term side effects",
      "underlying_concern": "Patient safety over prolonged use",
      "counter_strategy": "Provide detailed clinical trial data..."
    }
  ],
  "decision_criteria": ["Clinical evidence", "Patient safety"],
  "personality_type": "Analytical"
}
```

### Step 3 - Bot Behavior (Natural Objections):
```
User: "Let me tell you about GlucoStable XR"

Bot (Dr. Patel): "I appreciate that, but I'm concerned 
about long-term side effects. My patients' safety is 
paramount. What clinical trial data do you have on 
prolonged use?"

[Bot naturally used objection #1 from objection_library!]
```

## ✅ Summary

**The archetype system is fully integrated into your existing template generation flow!**

1. ✅ User uploads document/text → Archetype classified
2. ✅ Template saved with archetype data
3. ✅ Personas generated with archetype-specific fields
4. ✅ Bot uses archetype behaviors in conversation
5. ✅ Zero breaking changes to existing API

**Everything happens automatically - no manual intervention needed!** 🎉
