# REVISED SAFE IMPLEMENTATION GUIDE

## ⚠️ CRITICAL: Safety-First Approach

**BEFORE implementing anything:**
1. Find and examine existing folder structure
2. Don't replace existing functions - ADD NEW ones alongside
3. Use fallback logic (try new, fall back to old if fails)
4. Keep backwards compatibility

---

## 🔍 STEP 0: Discovery Phase (DO THIS FIRST!)

### Task 0.1: Map Current Project Structure

**Action:** Find and document the current structure

```bash
# Find all relevant files
find . -name "*.py" | grep -E "(persona|scenario|template|extraction)" 

# Look for these key files:
# - Where is extraction happening?
# - Where are personas generated?
# - Where are prompts created?
# - What's the current folder structure?
```

**Create a file:** `PROJECT_STRUCTURE.md` documenting what you find:
```
Current Structure:
├── services/
│   ├── enhanced_scenario_generator.py (FOUND)
│   └── ...
├── core/
│   ├── ... (FOUND)
│   └── ...
├── models/
│   └── ... (FOUND)
```

### Task 0.2: Examine Existing Functions

**Find these functions and document their signatures:**

1. `generate_personas_from_template()` 
   - Where is it?
   - What params does it take?
   - What does it return?
   - Who calls it?

2. `generate_assess_mode_from_template()`
   - Where is it?
   - What does it return?
   - Who uses it?

3. `extract_scenario_info()` or similar extraction function
   - Where is it?
   - What does template_data look like currently?

**Document in:** `EXISTING_FUNCTIONS.md`

---

## 📋 STEP 1: Create New Files (Safe - No Breaking Changes)

### Where to Create New Files

**Based on existing structure, create in appropriate locations:**

If `core/` folder exists:
```
core/
├── detail_category_library.py (NEW)
├── persona_generator_v2.py (NEW - note the v2!)
└── prompt_generator_v2.py (NEW - note the v2!)
```

If `models/` folder exists:
```
models/
└── persona_models.py (NEW - or add to existing models file)
```

**IMPORTANT:** Use `_v2` suffix or similar to avoid conflicts!

---

## 📝 TASK 1: Create Detail Category Library

**File Location:** Find where other "library" or "config" files are, create there.

**Suggested:** `core/detail_category_library.py` or `config/detail_categories.py`

**Code:** (Same as before - this is NEW file, safe to create)

```python
"""
Detail Category Library
Defines all possible persona detail categories.
LLM will choose from these based on scenario.
"""

# ... (use code from previous guide)
```

**Test after creating:**
```python
# Simple test
from core.detail_category_library import DetailCategoryLibrary

lib = DetailCategoryLibrary()
print(lib.get_category_names())
# Should print list of categories
```

---

## 📝 TASK 2: Create Persona Models

**File Location:** 
- If `models/persona.py` exists → Add to it (at bottom)
- Otherwise create: `models/persona_models.py`

**Code:** (Same as before - new classes, shouldn't break anything)

```python
"""
New Persona Models (v2)
Safe to add - doesn't modify existing models
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4

# ... (use code from previous guide)
```

---

## 📝 TASK 3: Create Persona Generator V2 (Safe!)

**File Location:** `core/persona_generator_v2.py` (note the v2!)

**Why v2?** Don't replace existing persona generation - create NEW alongside

**Code:** (Same as before, but note it's a separate file)

```python
"""
Persona Generator V2
NEW implementation - doesn't replace existing system
Can be used alongside old system
"""

# ... (use code from previous guide)
```

---

## 📝 TASK 4: Create Prompt Generator V2 (Safe!)

**File Location:** `core/prompt_generator_v2.py` (note the v2!)

**Code:** (Same as before)

```python
"""
Prompt Generator V2
NEW implementation using PersonaInstance
"""

# ... (use code from previous guide)
```

---

## 📝 TASK 5: Safe Integration (Don't Break Existing!)

**File:** Find where `generate_personas_from_template` is defined

**DON'T replace it! ADD NEW function alongside:**

```python
# ===== EXISTING FUNCTION (KEEP AS-IS) =====
async def generate_personas_from_template(self, template_data, gender='', context='', archetype_classification=None):
    """
    EXISTING IMPLEMENTATION - DO NOT MODIFY
    Keep this for backwards compatibility
    """
    # ... existing code stays exactly as-is ...
    pass


# ===== NEW V2 FUNCTION (ADD THIS) =====
async def generate_personas_from_template_v2(
    self, 
    template_data, 
    gender='', 
    context='', 
    archetype_classification=None
):
    """
    NEW IMPLEMENTATION: Uses PersonaGenerator v2
    Safe to call - has fallback to v1 if fails
    """
    try:
        from core.persona_generator_v2 import PersonaGenerator
        
        # Try new system
        persona_gen = PersonaGenerator(self.client, self.model)
        
        assess_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender=gender,
            custom_prompt=context
        )
        
        learn_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="learn_mode",
            gender=gender or "Female",
            custom_prompt=None
        )
        
        return {
            "learn_mode_expert": learn_persona.dict(),
            "assess_mode_character": assess_persona.dict(),
            "version": "v2"  # Mark as v2 for tracking
        }
        
    except Exception as e:
        print(f"[WARN] V2 generation failed: {e}")
        print("[INFO] Falling back to V1 generation")
        
        # FALLBACK to existing v1 function
        return await self.generate_personas_from_template(
            template_data, gender, context, archetype_classification
        )


# ===== SAME FOR ASSESS MODE =====
async def generate_assess_mode_from_template_v2(self, template_data):
    """
    NEW IMPLEMENTATION: Uses PromptGenerator v2
    Safe to call - has fallback to v1 if fails
    """
    try:
        from core.persona_generator_v2 import PersonaGenerator
        from core.prompt_generator_v2 import PromptGenerator
        
        # Try new system
        persona_gen = PersonaGenerator(self.client, self.model)
        persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode"
        )
        
        prompt_gen = PromptGenerator(self.client, self.model)
        system_prompt = await prompt_gen.generate_system_prompt(
            persona=persona,
            template_data=template_data
        )
        
        return system_prompt
        
    except Exception as e:
        print(f"[WARN] V2 prompt generation failed: {e}")
        print("[INFO] Falling back to V1 generation")
        
        # FALLBACK to existing v1 function
        return await self.generate_assess_mode_from_template(template_data)
```

---

## 📝 TASK 6: API Endpoints - Safe Updates

**Find your API route files** (probably in `routes/` or `api/`)

**DON'T modify existing endpoints! ADD NEW ones:**

```python
# ===== EXISTING ENDPOINT (KEEP AS-IS) =====
@router.post("/generate-personas")
async def generate_personas(...):
    """EXISTING - DO NOT MODIFY"""
    # ... existing code ...
    pass


# ===== NEW V2 ENDPOINT (ADD THIS) =====
@router.post("/generate-personas-v2")
async def generate_personas_v2(
    template_id: str = Body(...),
    mode: str = Body(...),
    gender: str = Body(default=""),
    custom_prompt: str = Body(default=""),
    use_fallback: bool = Body(default=True),  # Enable/disable fallback
    db: Any = Depends(get_db)
):
    """
    V2 endpoint - uses new PersonaGenerator
    Safe: falls back to v1 if fails (when use_fallback=True)
    """
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        
        # Try V2
        from core.persona_generator_v2 import PersonaGenerator
        persona_gen = PersonaGenerator(azure_openai_client)
        
        persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode=mode,
            gender=gender,
            custom_prompt=custom_prompt
        )
        
        return {
            "success": True,
            "version": "v2",
            "template_id": template_id,
            "persona": persona.dict()
        }
        
    except Exception as e:
        if use_fallback:
            # Fall back to v1
            print(f"[WARN] V2 failed, using v1 fallback: {e}")
            return await generate_personas(...)  # Call existing v1 endpoint
        else:
            raise HTTPException(status_code=500, detail=f"V2 generation failed: {str(e)}")
```

---

## ✅ TASK 7: Feature Flag (Optional but Recommended)

**Create:** `config/feature_flags.py` or add to existing config

```python
"""
Feature Flags
Toggle new features on/off safely
"""

class FeatureFlags:
    # Persona system
    USE_PERSONA_V2 = False  # Start with False (disabled)
    
    # If True, use v2; if False, use v1
    # Change to True only after testing!
```

**Then in your code:**

```python
from config.feature_flags import FeatureFlags

if FeatureFlags.USE_PERSONA_V2:
    result = await generate_personas_from_template_v2(...)
else:
    result = await generate_personas_from_template(...)  # Old system
```

---

## 🧪 Testing Strategy

### Phase 1: Isolated Testing (Safe)

Test NEW functions WITHOUT touching existing system:

```python
# Test new system in isolation
from core.persona_generator_v2 import PersonaGenerator

persona_gen = PersonaGenerator(client)
persona = await persona_gen.generate_persona(template_data, "assess_mode")

print(persona.dict())  # Check output
```

### Phase 2: V2 Endpoint Testing

Call NEW endpoint `/generate-personas-v2`:
- Test with fallback=True (safe)
- If works → great!
- If fails → falls back to v1 automatically

### Phase 3: Gradual Rollout

1. Keep feature flag OFF initially
2. Test v2 manually with specific scenarios
3. Once confident → flip flag to ON
4. Monitor for issues
5. Can flip back to OFF if problems

---

## 📊 What We're Keeping/Adding

### ✅ Keeping (No Changes):
- All existing functions
- All existing endpoints  
- All existing models
- Current folder structure

### ➕ Adding (New):
- `detail_category_library.py`
- `persona_generator_v2.py`
- `prompt_generator_v2.py`
- `persona_models.py` (or additions to existing)
- New v2 functions alongside existing
- New v2 endpoints alongside existing
- Feature flags for safe rollout

### 🔄 Modified (Minimal):
- Nothing replaced
- Only ADD imports where needed
- Only ADD new function calls (optional usage)

---

## 🚨 Rollback Plan

If anything breaks:

1. **Feature Flag Approach:**
   ```python
   FeatureFlags.USE_PERSONA_V2 = False  # Flip back to v1
   ```

2. **Endpoint Approach:**
   - Just use `/generate-personas` (old endpoint)
   - Don't use `/generate-personas-v2` (new endpoint)

3. **Code Approach:**
   - Don't call `generate_personas_from_template_v2()`
   - Keep using `generate_personas_from_template()` (existing)

**Nothing breaks because old system still intact!**

---

## 📝 Implementation Checklist

Before starting:
- [ ] Run discovery phase (map current structure)
- [ ] Document existing functions
- [ ] Backup current code

Phase 1 (Safe - No Breaking Changes):
- [ ] Create `detail_category_library.py`
- [ ] Create `persona_models.py`
- [ ] Test library loads correctly

Phase 2 (Safe - Separate Files):
- [ ] Create `persona_generator_v2.py`
- [ ] Create `prompt_generator_v2.py`
- [ ] Test in isolation (don't integrate yet)

Phase 3 (Safe - Add Functions):
- [ ] Add `generate_personas_from_template_v2()` (don't replace v1!)
- [ ] Add `generate_assess_mode_from_template_v2()` (don't replace v1!)
- [ ] Add fallback logic to v2 functions

Phase 4 (Safe - New Endpoints):
- [ ] Add `/generate-personas-v2` endpoint
- [ ] Keep old `/generate-personas` endpoint
- [ ] Test both endpoints work

Phase 5 (Optional - Feature Flag):
- [ ] Add feature flags
- [ ] Start with flags OFF
- [ ] Test with flags ON manually
- [ ] Gradual rollout

---

## ⚠️ Red Flags (Stop if You See These!)

🚨 **STOP implementing if:**
- You need to delete existing functions
- You need to modify existing function signatures
- Tests start failing
- Existing endpoints stop working
- Can't find where to add new code

**Instead:** Ask for help or clarification!

---

## 💡 Key Principles

1. **Additive, not destructive** - Add new, don't replace old
2. **Fallback always** - v2 fails → use v1
3. **Test in isolation** - Test new system separately first
4. **Gradual rollout** - Feature flags let you control
5. **Easy rollback** - Can always go back to v1

---

## 🎯 Success Criteria

✅ Old system still works exactly as before
✅ New v2 functions work when called
✅ Fallback logic works (v2 fails → v1 runs)
✅ No existing tests broken
✅ Can toggle between v1 and v2 easily

---

## 📞 Next Steps After Implementation

1. **Test v2 in isolation** (don't affect production)
2. **Compare v2 vs v1 output** (which is better?)
3. **Report results** (what worked, what didn't)
4. **Decide on rollout** (when to use v2 by default)

---

**Remember: This is a SAFE, gradual approach. Nothing should break!** 🛡️
