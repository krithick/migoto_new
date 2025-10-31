# Testing New 6-Section Prompt Architecture

## What Was Created

### 1. **Prompt Architect V3** (`core/prompt_architect_v3.py`)
- Generates prompts using 6-section architecture
- LLM-based generation for Sections 3 & 5
- Template-based for Sections 1, 2, 4, 6

### 2. **Test API Endpoint** (`core/test_prompt_architect_api.py`)
- Temporary endpoint: `POST /test-prompt-architect/generate`
- Complete flow: scenario description → template → persona → prompt
- Returns all intermediate data for inspection

### 3. **Test Script** (`test_new_architecture.py`)
- Standalone test without API
- Saves outputs to files for inspection

## How to Test

### Option 1: Using the API

1. **Start the server:**
```bash
python main.py
```

2. **Call the endpoint:**
```bash
curl -X POST "http://localhost:9000/test-prompt-architect/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_description": "EO-Dine pharmaceutical sales training where FSOs pitch to gynecologists using IMPACT methodology",
    "mode": "assess_mode"
  }'
```

3. **Check the response:**
```json
{
  "template_data": {...},
  "persona_data": {...},
  "final_prompt": "Language: English\n\n═══════...",
  "stats": {
    "template_archetype": "PERSUASION",
    "persona_name": "Dr. Priya Sharma",
    "detail_categories_count": 7,
    "prompt_length": 5234
  }
}
```

### Option 2: Using the Test Script

```bash
python test_new_architecture.py
```

**Outputs:**
- `test_template_output.json` - Extracted template data
- `test_persona_output.json` - Generated persona
- `test_final_prompt.txt` - Final 6-section prompt

## The 6-Section Architecture

```
┌─────────────────────────────────────────┐
│ SECTION 1: CRITICAL RULES (Universal)  │  ← Hardcoded guardrails
├─────────────────────────────────────────┤
│ SECTION 2: CHARACTER IDENTITY          │  ← From persona data
├─────────────────────────────────────────┤
│ SECTION 3: ARCHETYPE BEHAVIOR          │  ← LLM-generated
├─────────────────────────────────────────┤
│ SECTION 4: SITUATION CONTEXT           │  ← From detail_categories
├─────────────────────────────────────────┤
│ SECTION 5: CONVERSATION FLOW           │  ← LLM-generated
├─────────────────────────────────────────┤
│ SECTION 6: CLOSING & REMINDERS         │  ← Template-based
└─────────────────────────────────────────┘
```

## What to Check

### ✅ Template Extraction
- Archetype correctly identified (PERSUASION for sales)
- Domain knowledge extracted
- Evaluation criteria present

### ✅ Persona Generation
- 7 detail categories generated
- Realistic Indian context
- Conversation rules defined

### ✅ Prompt Quality
- All 6 sections present
- Section 3 has IF-THEN behavior patterns
- Section 5 has clear reaction triggers
- Consistent character throughout

## Example Scenario Descriptions to Test

### 1. Pharmaceutical Sales (PERSUASION)
```
"FSO pitches EO-Dine to gynecologist using IMPACT methodology"
```

### 2. Customer Support (HELP_SEEKING)
```
"Customer calls support with a broken product and needs help"
```

### 3. Workplace Conflict (CONFRONTATION)
```
"Employee confronts manager about unfair treatment"
```

## Integration Plan

Once tested and verified:

1. **Update `scenario.py`** - Add new prompt generation option
2. **Update frontend** - Add toggle for "Use New Architecture"
3. **Migrate existing scenarios** - Batch regenerate prompts
4. **Deprecate old system** - After validation period

## Files Modified

- ✅ `core/prompt_architect_v3.py` (NEW)
- ✅ `core/test_prompt_architect_api.py` (NEW)
- ✅ `test_new_architecture.py` (NEW)
- ✅ `main.py` (router registered)

## Next Steps

1. Test with different archetypes
2. Verify prompt quality manually
3. Compare with old prompts
4. Adjust Section 3 & 5 generation if needed
5. Integrate into main system
