# NEW Scenario Creation Workflow

## Overview
The new workflow separates persona generation from prompt generation, allowing you to:
- Generate MULTIPLE personas per template
- Generate prompts for EACH persona separately
- Reuse the same prompt for assess and try modes (they're identical)

## Key Changes

### 1. Assess Mode = Try Mode
- **Same prompt** for both modes
- Only difference is coaching behavior (handled by chat system, not prompt)
- Generate once, use for both

### 2. Multiple Personas Support
- Generate as many personas as you want
- Each persona gets its own prompts
- Store prompts with persona data

## API Workflow

### Step 1: Upload Template + Docs
```
POST /scenario/analyze-template-with-optional-docs
- template_file: Word/PDF template
- supporting_docs: Optional documents
- template_name: Name

Returns: template_id, template_data (editable)
```

### Step 2: Edit Template (Optional)
```
PUT /scenario/templates/{template_id}
- template_data: Edited template

Returns: Updated template
```

### Step 3: Generate Personas (Multiple Times)
```
POST /scenario/generate-personas
- template_id: Template to use
- persona_type: "assess_mode_character" (for assess/try) or "learn_mode_expert"
- gender: Optional gender preference
- prompt: Optional context
- count: Number of personas (default 1)

Returns: Array of personas

Call this MULTIPLE times to generate different personas:
- Dr. Priya (Experienced, Skeptical)
- Dr. Amit (Young, Open to innovation)
- Dr. Sharma (Academic, Data-focused)
```

### Step 4: Generate Prompts for Each Persona
```
POST /scenario/generate-prompts-for-persona
- template_id: Template to use
- persona_data: ONE persona object
- modes: ["assess", "try", "learn"]

Returns: Prompts for that persona

Call this for EACH persona:
- Persona 1 → Prompts 1
- Persona 2 → Prompts 2
- Persona 3 → Prompts 3
```

### Step 5: Create Avatar Interactions
For each persona + prompts:
```
POST /avatar/create-avatar-interaction
- persona_data: Persona object
- system_prompt: Generated prompt (assess/try use same)
- mode: "learn", "assess", or "try"
```

## Frontend Changes Needed

### Current Flow (OLD):
```javascript
// 1. Upload template
const template = await uploadTemplate(file, docs)

// 2. Generate ONE persona
const personas = await generatePersonas(template.id)

// 3. Generate prompts (one set)
const prompts = await generateFinalPrompts(template.data)

// 4. Create scenario with prompts
await createScenario(prompts)
```

### New Flow (RECOMMENDED):
```javascript
// 1. Upload template
const template = await uploadTemplate(file, docs)

// 2. Generate MULTIPLE personas
const persona1 = await generatePersonas(template.id, "assess_mode_character", "Female", "Experienced")
const persona2 = await generatePersonas(template.id, "assess_mode_character", "Male", "Young")
const persona3 = await generatePersonas(template.id, "assess_mode_character", "Female", "Academic")

// 3. Generate learn mode prompt ONCE (no persona needed)
const learnPrompt = await generatePromptsForPersona(template.id, null, ["learn"])

// 4. Generate prompts for EACH persona
const prompts1 = await generatePromptsForPersona(template.id, persona1.personas[0], ["assess", "try"])
const prompts2 = await generatePromptsForPersona(template.id, persona2.personas[0], ["assess", "try"])
const prompts3 = await generatePromptsForPersona(template.id, persona3.personas[0], ["assess", "try"])

// 5. Create avatar interactions for each
await createAvatarInteraction(persona1, prompts1.prompts.assess_mode, "assess")
await createAvatarInteraction(persona1, prompts1.prompts.try_mode, "try")  // Same prompt
await createAvatarInteraction(persona2, prompts2.prompts.assess_mode, "assess")
// ... etc
```

## Simplified Flow (If Only 1 Persona Needed):
```javascript
// Use the old endpoint - still works
const result = await generateFinalPrompts(template.data)
// Returns: learn_mode, assess_mode, try_mode (assess=try)
```

## Key Points

1. **Learn Mode**: 
   - Generate ONCE per template
   - No persona needed (it's a trainer)
   - Uses `LearnModePromptGenerator`

2. **Assess/Try Modes**:
   - Generate ONCE per persona
   - Same prompt for both modes
   - Uses `SystemPromptGenerator`
   - Difference is coaching (handled in chat, not prompt)

3. **Multiple Personas**:
   - Generate as many as you want
   - Each gets their own assess/try prompt
   - All share the same learn mode prompt

## Database Schema Updates Needed

### personas collection (if you store them):
```json
{
  "_id": "persona_id",
  "template_id": "template_id",
  "name": "Dr. Priya Sharma",
  "persona_data": { /* full persona object */ },
  "system_prompt": "generated prompt",  // Store prompt with persona
  "prompt_mode": "assess_mode",
  "prompt_generated_at": "2024-01-01T00:00:00",
  "created_at": "2024-01-01T00:00:00"
}
```

### avatar_interactions collection:
```json
{
  "_id": "interaction_id",
  "persona_id": "persona_id",  // Link to persona
  "system_prompt": "prompt text",
  "mode": "assess" | "try" | "learn",
  "template_id": "template_id"
}
```

## Migration Path

### Option 1: Keep Old Endpoint (Backward Compatible)
- `/generate-final-prompts` still works
- Generates 1 persona, 3 prompts
- Good for simple scenarios

### Option 2: Use New Workflow (Recommended)
- More control
- Multiple personas
- Better organization
- Use `/generate-prompts-for-persona`

## Summary

**OLD**: 1 Template → 1 Persona → 3 Prompts (learn, assess, try)

**NEW**: 1 Template → N Personas → (1 Learn Prompt + N Assess/Try Prompts)

Where:
- Learn prompt: Generated once, shared by all
- Assess/Try prompt: Same prompt per persona, generated N times
