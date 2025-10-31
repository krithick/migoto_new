# Testing Persona V2 Endpoints

## Quick Test Guide

### 1. Test `/generate-personas` Endpoint (Updated)

**Request**:
```bash
POST /scenario/generate-personas
{
  "template_id": "your_template_id",
  "persona_type": "assess_mode_character",
  "gender": "Female",
  "prompt": "Focus on time pressure",
  "count": 1
}
```

**Expected Response**:
```json
{
  "template_id": "your_template_id",
  "persona_type": "assess_mode_character",
  "mode": "assess_mode",
  "count": 1,
  "personas": [{
    "v1": {
      "name": "Dr. Sharma",
      "role": "Doctor",
      ...
    },
    "v2": {
      "id": "persona_uuid",
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
      "detail_categories_included": ["time_constraints", "professional_context"],
      "conversation_rules": {
        "opening_behavior": "Wait for learner",
        "response_style": "Professional but busy",
        "word_limit": 50
      }
    }
  }],
  "v2_categories_included": ["time_constraints", "professional_context"]
}
```

### 2. Test `/personas/` POST Endpoint (Updated)

#### Test V2 Format:
```bash
POST /personas/
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
      "current_time_pressure": "Very high"
    }
  },
  "detail_categories_included": ["time_constraints"]
}
```

**Expected Response**:
```json
{
  "success": true,
  "version": "v2",
  "persona_id": "persona_uuid",
  "persona": { /* full V2 persona */ },
  "detail_categories_count": 1
}
```

#### Test V1 Format (Backward Compatibility):
```bash
POST /personas/
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

**Expected Response**:
```json
{
  "success": true,
  "version": "v1",
  "persona_id": "persona_uuid",
  "persona": { /* full V1 persona */ }
}
```

### 3. Test `/personas/generate-v2` Endpoint (Existing)

```bash
POST /personas/generate-v2
{
  "template_id": "template_123",
  "mode": "assess_mode",
  "gender": "Female",
  "custom_prompt": "Focus on time pressure"
}
```

**Expected Response**:
```json
{
  "success": true,
  "version": "v2",
  "template_id": "template_123",
  "persona_id": "persona_uuid",
  "persona": { /* full V2 persona with dynamic categories */ }
}
```

## Complete Workflow Test

### Step 1: Generate Persona from Template
```bash
POST /scenario/generate-personas
{
  "template_id": "template_123",
  "persona_type": "assess_mode_character",
  "gender": "Female"
}
```

### Step 2: Save V2 Persona
```bash
POST /personas/
{
  # Use v2 data from Step 1 response
  "template_id": "template_123",
  "name": "Dr. Priya Sharma",
  ...
}
```

### Step 3: Retrieve Saved Persona
```bash
GET /personas/v2/{persona_id}
```

### Step 4: List All V2 Personas
```bash
GET /personas/v2/list?template_id=template_123
```

## Verification Checklist

- [ ] `/generate-personas` returns both V1 and V2 formats
- [ ] V2 personas have `detail_categories` field
- [ ] V2 personas have `archetype` field
- [ ] `/personas/` POST accepts V2 format
- [ ] `/personas/` POST still accepts V1 format (backward compatibility)
- [ ] V2 personas saved to `personas_v2` collection
- [ ] V1 personas saved to `personas` collection
- [ ] Response includes version indicator ("v1" or "v2")
- [ ] Dynamic categories are preserved in database
- [ ] Can retrieve V2 personas with all dynamic fields intact

## Database Verification

### Check V2 Persona in MongoDB:
```javascript
db.personas_v2.findOne({_id: "persona_uuid"})
```

**Should contain**:
- `detail_categories` (dynamic object)
- `detail_categories_included` (array of category names)
- `archetype` (string)
- `archetype_confidence` (number)
- `conversation_rules` (object)
- `version: "v2"`

### Check V1 Persona in MongoDB:
```javascript
db.personas.findOne({_id: "persona_uuid"})
```

**Should contain**:
- `full_persona` (object)
- `persona_details` (string)
- `situation` (string)
- No `detail_categories` field

## Error Handling Tests

### Test Invalid Template ID:
```bash
POST /scenario/generate-personas
{
  "template_id": "invalid_id",
  "persona_type": "assess_mode_character"
}
```
**Expected**: 404 error "Template not found"

### Test Invalid Persona Type:
```bash
POST /scenario/generate-personas
{
  "template_id": "valid_id",
  "persona_type": "invalid_type"
}
```
**Expected**: Defaults to "assess_mode"

### Test Malformed V2 Data:
```bash
POST /personas/
{
  "name": "Test",
  "detail_categories": "not_an_object"
}
```
**Expected**: 500 error with validation message

## Success Criteria

✅ All endpoints return expected response structures
✅ Both V1 and V2 formats work correctly
✅ Data is saved to correct collections
✅ Dynamic categories are preserved
✅ Backward compatibility maintained
✅ Error handling works as expected
