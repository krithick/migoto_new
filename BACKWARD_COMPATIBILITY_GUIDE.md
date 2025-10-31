# Backward Compatibility Guide

## Problem
Frontend uses old persona endpoints. We added V2 personas with dynamic categories. Need old endpoints to work with both.

## Solution
Updated old `PersonaDB` and `PersonaResponse` models to include **optional** V2 fields.

## What Changed

### 1. Models (`models/persona_models.py`)

**Old PersonaDB** - Now supports V2 data:
```python
class PersonaDB(PersonaCreate):
    # Old fields (required)
    id: UUID
    full_persona: Dict[str, Any]
    created_by: UUID
    
    # NEW: V2 fields (optional)
    detail_categories: Optional[Dict[str, Dict[str, Any]]] = None
    detail_categories_included: Optional[List[str]] = None
    conversation_rules: Optional[Dict[str, Any]] = None
    archetype: Optional[str] = None
    system_prompt: Optional[str] = None
```

**Old PersonaResponse** - Now includes V2 data:
```python
class PersonaResponse(PersonaCreate):
    # Old fields
    id: UUID
    created_at: datetime
    
    # NEW: V2 fields (optional)
    detail_categories: Optional[Dict[str, Dict[str, Any]]] = None
    conversation_rules: Optional[Dict[str, Any]] = None
    archetype: Optional[str] = None
```

### 2. PersonaInstanceV2 - New conversion method

```python
class PersonaInstanceV2:
    def to_legacy_db_model(self, created_by: UUID) -> PersonaDB:
        """Convert V2 persona to old PersonaDB format"""
        # Converts V2 → old format with V2 fields included
```

### 3. Unified Manager (`core/persona_unified_manager.py`)

Replace old persona save/load with:

```python
from core.persona_unified_manager import UnifiedPersonaManager

# Save (works with V1 dict OR V2 PersonaInstanceV2)
persona_id = await UnifiedPersonaManager.save_persona(db, persona, user_id)

# Load (returns PersonaResponse with V2 fields if present)
persona = await UnifiedPersonaManager.get_persona(db, persona_id)

# Check if it has V2 data
if UnifiedPersonaManager.is_v2_persona(persona):
    print(f"V2 persona with {len(persona.detail_categories)} categories")
else:
    print("Old V1 persona")
```

## How to Update Your Endpoints

### OLD CODE (in scenario_generator.py):
```python
@router.post("/personas/save")
async def save_persona(
    persona_data: dict = Body(...),
    created_by: UUID = Body(...),
    db: Any = Depends(get_db)
):
    # Old way - only handles V1
    persona_db = PersonaDB(**persona_data, created_by=created_by)
    result = await db.personas.insert_one(persona_db.dict(by_alias=True))
    return {"persona_id": str(result.inserted_id)}
```

### NEW CODE (backward compatible):
```python
@router.post("/personas/save")
async def save_persona(
    persona_data: dict = Body(...),
    created_by: UUID = Body(...),
    db: Any = Depends(get_db)
):
    # New way - handles BOTH V1 and V2
    from core.persona_unified_manager import UnifiedPersonaManager
    
    persona_id = await UnifiedPersonaManager.save_persona(
        db, persona_data, created_by
    )
    
    return {
        "success": True,
        "persona_id": persona_id
    }
```

### Update List Endpoint:
```python
@router.get("/personas/list")
async def list_personas(
    created_by: Optional[UUID] = None,
    db: Any = Depends(get_db)
):
    from core.persona_unified_manager import UnifiedPersonaManager
    
    personas = await UnifiedPersonaManager.list_personas(db, created_by)
    
    # Frontend gets same format, with V2 fields if present
    return {
        "success": True,
        "personas": [p.dict() for p in personas]
    }
```

## Frontend Impact

**ZERO CHANGES NEEDED!**

Frontend receives:
```json
{
  "id": "uuid",
  "name": "Dr. Priya",
  "age": 42,
  "gender": "female",
  "description": "...",
  
  // Old V1 personas: these are null
  "detail_categories": null,
  "archetype": null,
  
  // New V2 personas: these have data
  "detail_categories": {
    "professional_context": {...},
    "time_constraints": {...}
  },
  "archetype": "PERSUASION"
}
```

Frontend can:
1. Ignore V2 fields (works as before)
2. Check if V2 fields exist and show them (optional enhancement)

## Database Structure

**Same collection (`personas`)** stores both:

```javascript
// Old V1 persona
{
  "_id": "uuid",
  "name": "John",
  "full_persona": {...},
  "detail_categories": null  // V2 field is null
}

// New V2 persona
{
  "_id": "uuid",
  "name": "Dr. Priya",
  "full_persona": {...},
  "detail_categories": {  // V2 field has data
    "professional_context": {...},
    "time_constraints": {...}
  },
  "detail_categories_included": ["professional_context", "time_constraints"],
  "archetype": "PERSUASION"
}
```

## Migration Steps

1. ✅ Models updated (done)
2. ✅ UnifiedPersonaManager created (done)
3. 🔄 Update endpoints in `scenario_generator.py`:
   - Replace persona save logic with `UnifiedPersonaManager.save_persona()`
   - Replace persona list logic with `UnifiedPersonaManager.list_personas()`
   - Replace persona get logic with `UnifiedPersonaManager.get_persona()`

4. ✅ Test with both old and new data

## Testing

```python
# Test V1 persona (old format)
old_persona = {
    "name": "John",
    "age": 30,
    "gender": "male",
    "persona_type": "customer",
    "character_goal": "Buy product",
    "location": "Mumbai",
    "persona_details": "Details",
    "situation": "At store",
    "business_or_personal": "personal"
}
await UnifiedPersonaManager.save_persona(db, old_persona, user_id)

# Test V2 persona (new format)
v2_persona = PersonaInstanceV2(...)  # Generated with V2
await UnifiedPersonaManager.save_persona(db, v2_persona, user_id)

# Both work! Both saved to same collection!
```

## Benefits

✅ No frontend changes needed
✅ Old personas still work
✅ New personas have rich data
✅ Same endpoints, same collection
✅ Gradual migration possible
