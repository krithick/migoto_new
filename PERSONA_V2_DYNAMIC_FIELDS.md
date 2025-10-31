# Persona V2 - Dynamic Fields Support

## Overview

The persona system now supports **dynamic fields** to accommodate varying data structures from different sources (like persona extraction, AI generation, etc.) without breaking existing code.

## Key Changes

### 1. **Flexible Model Structure** (`models/persona_models.py`)

```python
class PersonaInstanceV2(BaseModel):
    # Required base fields
    name: str
    age: int
    gender: str
    role: str
    description: str
    
    # Optional/flexible fields
    scenario_type: Optional[str] = None
    archetype: Optional[str] = None
    location: Union[PersonaLocation, Dict[str, Any]]  # Accepts both
    
    # Dynamic detail categories (any structure)
    detail_categories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"  # ✅ Allows additional fields not defined in model
```

**Benefits:**
- ✅ Accepts personas from extraction with complex detail categories
- ✅ Backward compatible with existing personas
- ✅ No validation errors for new/unknown fields
- ✅ Preserves all data when storing/retrieving

### 2. **Safe Storage Functions** (`core/persona.py`)

```python
async def store_persona_v2(db, persona, created_by):
    """Stores persona preserving ALL fields including dynamic ones"""
    persona_dict = persona.dict(exclude_none=False)  # Keep all fields
    # ... stores in personas_v2 collection
```

### 3. **JSON Loading Utility** (`core/persona_loader.py`)

```python
async def load_persona_from_json(db, persona_data, created_by):
    """Load persona from JSON (like extraction output)"""
    # Validates only required base fields
    # Preserves ALL other fields as-is
    # Stores in personas_v2 collection
```

## API Endpoints

### Load Persona from JSON
```http
POST /personas/v2/load-from-json
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "id": "3cecf0aa-1877-4469-9815-45e58f49942b",
  "name": "Dr. Priya Sharma",
  "age": 42,
  "gender": "Female",
  "role": "Experienced Gynecologist",
  "description": "A seasoned medical professional...",
  "persona_type": "Experienced Gynecologist",
  "mode": "assess_mode",
  "location": {
    "country": "India",
    "city": "Mumbai",
    ...
  },
  "detail_categories": {
    "time_constraints": { ... },
    "decision_criteria": { ... },
    "professional_context": { ... }
    // Any number of categories with any structure
  },
  "conversation_rules": { ... },
  // Any additional fields are preserved
}
```

**Response:**
```json
{
  "success": true,
  "version": "v2",
  "persona_id": "3cecf0aa-1877-4469-9815-45e58f49942b",
  "detail_categories_count": 7,
  "persona": { /* full persona with all fields */ }
}
```

### Get Persona V2
```http
GET /personas/v2/{persona_id}
Authorization: Bearer <token>
```

Returns the complete persona with ALL fields preserved.

### Update Persona V2
```http
PUT /personas/v2/{persona_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "description": "Updated description",
  "detail_categories": {
    "new_category": { "field": "value" }
  }
  // Update any fields
}
```

## Database Structure

### Collection: `personas_v2`

```javascript
{
  "_id": "3cecf0aa-1877-4469-9815-45e58f49942b",
  "name": "Dr. Priya Sharma",
  "age": 42,
  "gender": "Female",
  "role": "Experienced Gynecologist",
  "description": "...",
  "persona_type": "Experienced Gynecologist",
  "mode": "assess_mode",
  "scenario_type": "pharmaceutical_product",
  
  // Location (flexible structure)
  "location": {
    "country": "India",
    "state": "Maharashtra",
    "city": "Mumbai",
    "languages_spoken": ["English", "Hindi"]
  },
  
  // Archetype (optional)
  "archetype": "PERSUASION",
  "archetype_confidence": 0.95,
  
  // Dynamic detail categories (any structure)
  "detail_categories": {
    "time_constraints": {
      "typical_day_schedule": { ... },
      "competing_priorities": [ ... ]
    },
    "decision_criteria": {
      "must_haves": [ ... ],
      "deal_breakers": [ ... ]
    },
    // ... any number of categories
  },
  
  // Conversation rules
  "conversation_rules": {
    "opening_behavior": "...",
    "response_style": "...",
    "word_limit": 50
  },
  
  // Metadata
  "detail_categories_included": ["time_constraints", "decision_criteria", ...],
  "generation_metadata": { ... },
  
  // System fields
  "created_by": "user-uuid",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z"),
  "version": "v2"
}
```

## Backward Compatibility

### ✅ Existing Code Still Works

1. **Old personas (v1)** remain in `personas` collection
2. **New personas (v2)** go to `personas_v2` collection
3. **Old endpoints** (`/personas/*`) unchanged
4. **New endpoints** (`/personas/v2/*`) for dynamic personas

### Migration Path

```python
# Old way (still works)
persona = await create_persona(db, PersonaCreate(...), user_id)

# New way (for dynamic personas)
persona_data = load_from_json("persona_from_extraction.json")
stored = await load_persona_from_json(db, persona_data, user_id)
```

## Testing

Run the test script:

```bash
cd d:\migoto_dev\migoto_new
python test_persona_loading.py
```

Expected output:
```
✅ Loaded persona_from_extraction.json
✅ All required base fields present
✅ Found 7 detail categories:
   - time_constraints
   - decision_criteria
   - professional_context
   ...
✅ Persona structure is valid and compatible!
✅ PersonaInstanceV2 model accepts the data structure
✅ All tests passed!
```

## Example: Loading Extraction Persona

```python
import json
from core.persona_loader import load_persona_from_json

# Load from file
with open("persona_from_extraction.json") as f:
    persona_data = json.load(f)

# Store in database
stored = await load_persona_from_json(db, persona_data, admin_user.id)

print(f"Stored persona: {stored['name']}")
print(f"Detail categories: {len(stored['detail_categories'])}")
# All fields preserved!
```

## Benefits

1. ✅ **No Breaking Changes** - Existing code continues to work
2. ✅ **Flexible Structure** - Accepts any detail category structure
3. ✅ **Data Preservation** - All fields stored and retrieved intact
4. ✅ **Easy Integration** - Simple API for loading from JSON
5. ✅ **Type Safety** - Base fields validated, dynamic fields flexible
6. ✅ **Future Proof** - Can add new categories without code changes

## Notes

- **Required base fields**: name, age, gender, role, description, persona_type, mode
- **Optional fields**: Everything else (archetype, location details, etc.)
- **Dynamic fields**: detail_categories can have any structure
- **Storage**: Uses separate `personas_v2` collection for clarity
- **Retrieval**: Returns raw dict to preserve all dynamic fields
