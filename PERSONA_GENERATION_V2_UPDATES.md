# Persona Generation V2 Updates

## Summary
Updated persona generation and saving endpoints to work with the new `PersonaGeneratorV2` class while maintaining backward compatibility with V1 format.

## Changes Made

### 1. `/generate-personas` Endpoint (scenario_generator_routes.py)
**Location**: `scenario_generator_routes.py`

**What Changed**:
- Now uses `PersonaGeneratorV2` for generating personas
- Returns BOTH V1 and V2 formats for backward compatibility
- Maps persona_type to mode (learn_mode_expert → learn_mode, assess_mode_character → assess_mode)
- Includes V2 dynamic categories in response

**Request**:
```json
{
  "template_id": "template_123",
  "persona_type": "assess_mode_character",
  "gender": "Female",
  "prompt": "Focus on time pressure",
  "count": 1
}
```

**Response**:
```json
{
  "template_id": "template_123",
  "persona_type": "assess_mode_character",
  "mode": "assess_mode",
  "count": 1,
  "personas": [{
    "v1": { /* old format */ },
    "v2": {
      "name": "Dr. Priya Sharma",
      "detail_categories": {
        "time_constraints": { /* dynamic fields */ },
        "professional_context": { /* dynamic fields */ }
      },
      "detail_categories_included": ["time_constraints", "professional_context"]
    }
  }],
  "v2_categories_included": ["time_constraints", "professional_context"]
}
```

### 2. `/personas/` POST Endpoint (core/persona.py)
**Location**: `core/persona.py`

**What Changed**:
- Now accepts generic `Dict[str, Any]` instead of strict `PersonaCreate`
- Auto-detects V1 vs V2 format based on presence of `detail_categories` or `archetype` fields
- Saves V2 personas to `personas_v2` collection
- Saves V1 personas to `personas` collection (existing behavior)

**V1 Request** (old format):
```json
{
  "name": "John Doe",
  "description": "Sales rep",
  "persona_type": "sales",
  "character_goal": "Meet quota",
  "location": "Mumbai",
  "persona_details": "Experienced rep",
  "situation": "Busy day",
  "business_or_personal": "business",
  "background_story": "10 years experience"
}
```

**V2 Request** (new format):
```json
{
  "template_id": "template_123",
  "persona_type": "Doctor",
  "mode": "assess_mode",
  "name": "Dr. Priya Sharma",
  "age": 42,
  "gender": "Female",
  "role": "General Practitioner",
  "archetype": "PERSUASION",
  "detail_categories": {
    "time_constraints": {
      "current_time_pressure": "Very high",
      "typical_consultation_time": "10 minutes"
    },
    "professional_context": {
      "practice_type": "Private clinic",
      "years_experience": 15
    }
  },
  "detail_categories_included": ["time_constraints", "professional_context"]
}
```

**Response** (both formats):
```json
{
  "success": true,
  "version": "v2",  // or "v1"
  "persona_id": "persona_uuid",
  "persona": { /* full persona data */ },
  "detail_categories_count": 2  // only for v2
}
```

### 3. `/personas/generate` Endpoint (core/persona.py)
**What Changed**:
- Updated response format to include version info
- Still uses V1 generation (AI-based from description)
- Returns consistent response structure

## Database Collections

### V1 Personas
- **Collection**: `personas`
- **Format**: Fixed schema with `full_persona` field
- **Use Case**: Simple personas created from descriptions

### V2 Personas
- **Collection**: `personas_v2`
- **Format**: Dynamic schema with `detail_categories` (flexible fields)
- **Use Case**: Rich personas generated from templates with scenario-specific details

## Backward Compatibility

✅ **Fully Backward Compatible**:
- Old V1 requests still work exactly as before
- V1 personas saved to `personas` collection
- V2 personas saved to separate `personas_v2` collection
- No breaking changes to existing API contracts

## Usage Examples

### Generate V2 Persona from Template
```python
# 1. Generate persona
response = await client.post("/generate-personas", json={
    "template_id": "template_123",
    "persona_type": "assess_mode_character",
    "gender": "Female",
    "prompt": "Focus on time pressure"
})

# 2. Save V2 persona
persona_v2 = response["personas"][0]["v2"]
save_response = await client.post("/personas/", json=persona_v2)

# 3. Use persona_id for prompts
persona_id = save_response["persona_id"]
```

### Create V1 Persona (Old Way)
```python
# Still works exactly as before
response = await client.post("/personas/", json={
    "name": "John Doe",
    "description": "Sales rep",
    "persona_type": "sales",
    # ... other V1 fields
})
```

## Key Benefits

1. **Dynamic Categories**: V2 personas have flexible detail categories based on scenario needs
2. **Richer Context**: More detailed persona information for better AI interactions
3. **Archetype Support**: Built-in archetype classification (PERSUASION, HELP_SEEKING, etc.)
4. **Validation**: Auto-validation and fixing of persona data
5. **Backward Compatible**: No breaking changes to existing code

## Next Steps

1. ✅ Update `/generate-personas` to use PersonaGeneratorV2
2. ✅ Update `/personas/` POST to handle both V1 and V2
3. ✅ Maintain backward compatibility
4. 🔄 Update prompt generation to use V2 persona data
5. 🔄 Update frontend to display V2 dynamic categories
