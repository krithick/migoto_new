# Quick Start - Dynamic Persona Fields

## 🚀 What Changed?

The persona system now accepts **any structure** for detail categories without requiring code changes.

## ✅ Key Points

1. **No breaking changes** - existing code works as-is
2. **New endpoints** for dynamic personas (`/personas/v2/*`)
3. **Flexible storage** - preserves all fields automatically
4. **Minimal validation** - only base fields required

---

## 📋 Required Base Fields

Only these fields are required:
```json
{
  "name": "string",
  "age": 42,
  "gender": "string",
  "role": "string",
  "description": "string",
  "persona_type": "string",
  "mode": "string"
}
```

**Everything else is optional and flexible!**

---

## 🔧 Quick Usage

### Load Persona from JSON

```python
import json
from core.persona_loader import load_persona_from_json

# Load any persona JSON
with open("persona_from_extraction.json") as f:
    data = json.load(f)

# Store (preserves ALL fields)
stored = await load_persona_from_json(db, data, user_id)
```

### API Call

```bash
curl -X POST http://localhost:9000/personas/v2/load-from-json \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @persona_from_extraction.json
```

---

## 📊 Example Structures

### Minimal Persona
```json
{
  "name": "John Doe",
  "age": 35,
  "gender": "Male",
  "role": "Customer",
  "description": "A typical customer",
  "persona_type": "customer",
  "mode": "assess_mode"
}
```

### Full Persona (with dynamic fields)
```json
{
  "name": "Dr. Priya Sharma",
  "age": 42,
  "gender": "Female",
  "role": "Experienced Gynecologist",
  "description": "A seasoned medical professional",
  "persona_type": "Experienced Gynecologist",
  "mode": "assess_mode",
  "scenario_type": "pharmaceutical_product",
  
  "location": {
    "country": "India",
    "city": "Mumbai",
    "languages_spoken": ["English", "Hindi"]
  },
  
  "archetype": "PERSUASION",
  "archetype_confidence": 0.95,
  
  "detail_categories": {
    "time_constraints": {
      "typical_day_schedule": { ... },
      "competing_priorities": [ ... ]
    },
    "decision_criteria": {
      "must_haves": [ ... ],
      "deal_breakers": [ ... ]
    }
    // Add ANY categories with ANY structure
  },
  
  "conversation_rules": {
    "opening_behavior": "...",
    "word_limit": 50
  }
  
  // Add ANY additional fields!
}
```

---

## 🎯 API Endpoints

### Load from JSON
```http
POST /personas/v2/load-from-json
Body: { /* persona data */ }
```

### Get Persona
```http
GET /personas/v2/{persona_id}
```

### Update Persona
```http
PUT /personas/v2/{persona_id}
Body: { /* fields to update */ }
```

---

## ✅ Testing

```bash
# Run test script
python test_persona_loading.py

# Expected output:
# ✅ All tests passed!
```

---

## 🔍 Verify in Database

```javascript
// MongoDB query
db.personas_v2.findOne({ "_id": "your-persona-id" })

// Should return ALL fields including:
// - detail_categories (with all sub-fields)
// - conversation_rules
// - Any custom fields you added
```

---

## 💡 Tips

1. **Only base fields validated** - everything else is stored as-is
2. **Use personas_v2 collection** - separate from old personas
3. **All fields preserved** - no data loss on store/retrieve
4. **Backward compatible** - old endpoints still work

---

## 🐛 Troubleshooting

### Missing required field error
```
Error: Missing required field: name
```
**Fix:** Ensure all 7 base fields are present (name, age, gender, role, description, persona_type, mode)

### Fields not preserved
```
Stored persona missing some fields
```
**Fix:** Use `/personas/v2/*` endpoints, not old `/personas/*` endpoints

### Model validation error
```
PersonaInstanceV2 validation failed
```
**Fix:** Check that base fields have correct types (age=int, name=str, etc.)

---

## 📚 More Info

- Full docs: `PERSONA_V2_DYNAMIC_FIELDS.md`
- Changes summary: `CHANGES_SUMMARY.md`
- Test script: `test_persona_loading.py`

---

## ⚡ That's It!

You can now load personas with **any structure** without code changes. Just ensure the 7 base fields are present, and everything else is flexible!
