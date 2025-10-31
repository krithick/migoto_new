# Critical Issues Found in IMPACT Scenario Flow

## Test Results Summary
- ❌ Objection library NOT injected into persona
- ❌ Archetype-specific behavior NOT in prompt  
- ❌ Bot behaves like generic customer, not Dr. Archana
- ⚠️ IMPACT framework not in conversation topics
- ⚠️ Product details not in key facts

## Issue #1: Archetype Classification Failing

**Problem**: `archetype_classification` is empty in template_data

**Evidence**:
```json
{
  "archetype_classification": {}  // EMPTY!
}
```

**Impact**: 
- `_inject_archetype_fields()` has no archetype to work with
- No objection_library, decision_criteria, personality_type added
- Prompt gets empty `{archetype_specific_behavior}` section

**Root Cause**: 
The archetype classifier is either:
1. Failing silently (exception caught but not logged properly)
2. Returning None/empty result
3. Not being called at all

## Issue #2: Archetype Fields Not in Persona

**Expected**:
```json
{
  "assess_mode_ai_bot": {
    "role": "Dr. Archana Pandey",
    "objection_library": [
      {
        "objection": "How is EO-Dine better than Dienogest?",
        "underlying_concern": "Need proof of superiority"
      }
    ],
    "decision_criteria": ["Clinical data", "Safety profile"],
    "personality_type": "Analytical",
    "current_position": "Satisfied with Dienogest"
  }
}
```

**Actual**:
```json
{
  "assess_mode_ai_bot": {
    "role": "Sales Customer/Client",  // WRONG!
    "background": "...",
    "goal": "needs assistance"  // WRONG!
  }
}
```

## Issue #3: Prompt Missing Archetype Section

**Expected in Prompt**:
```
## Your Position & Objections
Current: Satisfied with Dienogest
Personality: Analytical
Objections:
1. How is EO-Dine better than Dienogest? (Concern: Need proof)
2. Share efficacy data (Concern: Need clinical evidence)
Decision criteria: Clinical efficacy, Safety profile, Patient tolerability
```

**Actual in Prompt**:
```
## 🧠 Character Background
[PERSONA_PLACEHOLDER]

<EMPTY - NO ARCHETYPE SECTION>

## 🗣️ First Response
```

## Issue #4: Wrong Bot Behavior

**Expected**:
```
USER: "Hello Dr. Archana, I am Rajesh from Integrace Orthopedics..."
BOT: "Hello Rajesh. I have a caesarean section in an hour, so please be brief. What brings you here?"
```

**Actual**:
```
USER: "Hello Dr. Archana, I am Rajesh from Integrace Orthopedics..."
BOT: "Hello Rajesh. I'm considering adding new products to my clinic's offerings..."
```

Bot is acting like a **generic customer** instead of **Dr. Archana with specific objections**.

## Issue #5: IMPACT Framework Not Extracted

**Expected in conversation_topics**:
```json
[
  "Introduction (I) - Company name, credentials, trust builders",
  "Memorizing (M) - Reference last visit, build continuity",
  "Probing (P) - Ask about prescribing habits, concerns",
  "Articulation (A) - Detail brand benefits vs competition",
  "Clarify (C) - Handle objections confidently",
  "Take Commitment (T) - Ask for prescription commitment"
]
```

**Actual**:
```json
[
  "Basic sales concepts and fundamentals",
  "Practical sales applications",
  "Common sales challenges"
]
```

## Recommended Fixes

### Fix #1: Debug Archetype Classification
Add logging to see why classification fails:
```python
try:
    print(f"DEBUG: Calling archetype classifier...")
    archetype_result = await self.archetype_classifier.classify_scenario(scenario_document, template_data)
    print(f"DEBUG: Archetype result: {archetype_result}")
    print(f"DEBUG: Primary archetype: {archetype_result.primary_archetype}")
except Exception as e:
    print(f"ERROR: Archetype classification failed: {e}")
    import traceback
    traceback.print_exc()
```

### Fix #2: Ensure Archetype Fields Injection
Verify `_inject_archetype_fields()` is called AFTER successful classification:
```python
# Classify archetype FIRST
archetype_result = await self.archetype_classifier.classify_scenario(...)
template_data["archetype_classification"] = {...}

# THEN inject fields
self._inject_archetype_fields(template_data)

# VERIFY injection worked
assess_persona = template_data.get("persona_definitions", {}).get("assess_mode_ai_bot", {})
print(f"DEBUG: Has objection_library: {'objection_library' in assess_persona}")
```

### Fix #3: Improve Extraction Prompt
The extraction prompt should explicitly ask for:
- IMPACT framework steps in conversation_topics
- EO-Dine vs Dienogest comparison in key_facts
- Dr. Archana's specific profile (busy, skeptical, time-pressed)
- Suggested objections as objection_library

### Fix #4: Validate Template Before Prompt Generation
Add validation step:
```python
def validate_template_for_archetype(template_data):
    archetype = template_data.get("archetype_classification", {}).get("primary_archetype")
    persona = template_data.get("persona_definitions", {}).get("assess_mode_ai_bot", {})
    
    if archetype == "PERSUASION":
        assert "objection_library" in persona, "Missing objection_library for PERSUASION"
        assert "decision_criteria" in persona, "Missing decision_criteria"
    
    return True
```

## Test Again After Fixes
Run: `python test_impact_scenario_flow.py`

Expected output:
- ✅ Archetype: PERSUASION (confidence: 0.9+)
- ✅ Objection library properly injected (2+ objections)
- ✅ Archetype-specific behavior in prompt
- ✅ IMPACT framework in conversation topics
- ✅ Bot behaves like Dr. Archana with objections
