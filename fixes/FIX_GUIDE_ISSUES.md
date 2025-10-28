# FIX GUIDE: Extraction & Persona Generation Issues

## 🎯 Overview

The extraction and persona generation structure is **PERFECT**, but the content has **4 critical issues** that need fixing:

1. ❌ Wrong archetype (HELP_SEEKING instead of PERSUASION)
2. ❌ Missing key detail categories (time_constraints, sales_rep_history)
3. ❌ Wrong conversation context (patient care instead of sales pitch)
4. ❌ Location inconsistency (Mumbai vs Bangalore)

**This guide provides exact fixes for each issue.**

---

## 🔧 FIX #1: Correct Archetype Classification

### Issue:
```json
"archetype": "HELP_SEEKING",  // ❌ WRONG for pharma sales!
```

### Root Cause:
The archetype classifier doesn't understand that in a **SALES scenario**, the person being pitched to should be **PERSUASION** archetype, not HELP_SEEKING.

### Solution 1: Add Scenario-Aware Archetype Logic

**File to modify:** `core/scenario_extractor_v2.py` (or wherever archetype classification happens)

**Add this function:**

```python
def determine_correct_archetype(template_data: Dict[str, Any]) -> str:
    """
    Determine correct archetype based on scenario context.
    Override LLM classification if obviously wrong.
    """
    
    domain = template_data.get("general_info", {}).get("domain", "")
    assess_mode = template_data.get("assess_mode", {})
    ai_bot_role = assess_mode.get("ai_bot_role", "")
    what_happens = assess_mode.get("what_happens", "")
    
    # Rule-based archetype determination for common cases
    
    # PERSUASION: Sales, pitching, convincing scenarios
    if any(keyword in domain.lower() for keyword in ["sales", "pharmaceutical", "product"]):
        if any(keyword in what_happens.lower() for keyword in ["pitch", "sell", "convince", "present product"]):
            return "PERSUASION"
    
    # PERSUASION: Customer/client being sold to
    if any(role in ai_bot_role.lower() for role in ["customer", "client", "doctor", "buyer", "patient (buying)"]):
        if "pitch" in what_happens.lower() or "sell" in what_happens.lower():
            return "PERSUASION"
    
    # HELP_SEEKING: Customer seeking help/service
    if any(keyword in what_happens.lower() for keyword in ["seeks help", "needs assistance", "has problem", "inquiring"]):
        return "HELP_SEEKING"
    
    # CONFRONTATION: Conflict, bias, complaint scenarios
    if any(keyword in domain.lower() for keyword in ["dei", "bias", "conflict", "complaint"]):
        return "CONFRONTATION"
    
    # INVESTIGATION: Questioning, interviewing scenarios
    if any(keyword in what_happens.lower() for keyword in ["interview", "investigate", "question", "gather information"]):
        return "INVESTIGATION"
    
    # NEGOTIATION: Deal-making, bargaining scenarios
    if any(keyword in what_happens.lower() for keyword in ["negotiate", "bargain", "deal", "contract"]):
        return "NEGOTIATION"
    
    # Default: return None (use LLM classification)
    return None


def validate_and_correct_archetype(template_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate archetype classification and correct if wrong.
    Call this AFTER extraction is complete.
    """
    
    current_archetype = template_data.get("archetype_classification", {}).get("primary_archetype")
    correct_archetype = determine_correct_archetype(template_data)
    
    if correct_archetype and current_archetype != correct_archetype:
        print(f"[ARCHETYPE FIX] Correcting archetype from {current_archetype} to {correct_archetype}")
        
        template_data["archetype_classification"] = {
            "primary_archetype": correct_archetype,
            "confidence_score": 0.95,  # High confidence for rule-based
            "corrected": True,
            "original_archetype": current_archetype
        }
    
    return template_data
```

**Use it in extraction:**

```python
async def extract_scenario_info(self, document_text: str) -> Dict[str, Any]:
    """Enhanced extraction with archetype validation"""
    
    # ... existing extraction code ...
    
    # ADD THIS: Validate and correct archetype
    template_data = validate_and_correct_archetype(template_data)
    
    return template_data
```

### Solution 2: Improve Archetype Classification Prompt

**File to modify:** Wherever you call LLM for archetype classification

**Add to the prompt:**

```python
archetype_prompt = f"""
...existing prompt...

**CRITICAL RULES FOR ARCHETYPE CLASSIFICATION:**

1. **PERSUASION** - Use when:
   - Someone is being sold to / pitched to / convinced
   - Sales scenarios (pharma rep → doctor, salesperson → customer)
   - AI plays: customer, doctor, buyer, client being approached
   - Learner must: convince, persuade, pitch, sell

2. **HELP_SEEKING** - Use when:
   - Someone seeks help / has a problem / needs service
   - AI plays: customer with problem, person needing assistance
   - Learner must: help, assist, solve problem, provide service

3. **CONFRONTATION** - Use when:
   - Conflict, bias incident, uncomfortable situation
   - DEI scenarios, complaints, interpersonal issues

4. **INVESTIGATION** - Use when:
   - Gathering information through questions
   - Interviewing, investigating, fact-finding

5. **NEGOTIATION** - Use when:
   - Two parties making a deal
   - Bargaining, contracting, finding agreement

**For THIS scenario:**
Domain: {domain}
What happens: {what_happens}
AI role: {ai_bot_role}

Based on these rules, classify the archetype.
"""
```

---

## 🔧 FIX #2: Ensure Key Categories Are Selected

### Issue:
For pharma sales, these categories are missing:
- `time_constraints` (doctor is busy!)
- `sales_rep_history` (FSO has visited before?)

### Solution: Add Scenario-Specific Category Requirements

**File to modify:** `core/persona_generator_v2.py`

**Update the `_determine_relevant_categories` method:**

```python
async def _determine_relevant_categories(
    self,
    template_data: Dict[str, Any],
    base_persona: Dict[str, Any],
    mode: str
) -> List[str]:
    """
    LLM analyzes scenario and decides which detail categories are relevant.
    NOW WITH: Scenario-specific required categories!
    """
    
    # NEW: Get scenario-specific requirements
    required_categories = self._get_scenario_required_categories(template_data)
    
    # Get all available categories
    available_categories = self.category_library.get_all_categories()
    
    # Build category descriptions for LLM
    category_descriptions = "\n".join([
        f"- **{name}**: {cat.description}\n  When relevant: {cat.when_relevant}"
        for name, cat in available_categories.items()
    ])
    
    analysis_prompt = f"""
You are analyzing a training scenario to determine which persona detail categories are needed.

**Scenario Context:**
{json.dumps(template_data.get("context_overview", {}), indent=2)}

**Domain:** {template_data.get("general_info", {}).get("domain", "general")}
**Archetype:** {template_data.get("archetype_classification", {}).get("primary_archetype", "unknown")}

**Base Persona:**
- Role: {base_persona["role"]}
- Description: {base_persona["description"]}

**Mode:** {mode}

**Available Detail Categories:**
{category_descriptions}

**REQUIRED CATEGORIES (MUST include these):**
{json.dumps(required_categories, indent=2)}

**Task:** 
1. START with the required categories above
2. Add 2-5 MORE categories that are truly relevant
3. Total should be 5-8 categories

**Rules:**
- Only add categories that significantly affect behavior
- Don't add everything - be selective
- Consider the archetype requirements
- Consider what makes this persona realistic

**Output Format:**
Return ONLY a JSON array of category names:
["category1", "category2", "category3"]

Respond with the complete list (required + additional).
"""
    
    try:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You select relevant persona detail categories."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        categories = json.loads(response_text)
        
        # Validate: ensure required categories are included
        for req_cat in required_categories:
            if req_cat not in categories:
                categories.append(req_cat)
        
        # Validate categories exist
        valid_categories = [
            cat for cat in categories 
            if cat in available_categories
        ]
        
        return valid_categories
        
    except Exception as e:
        print(f"[ERROR] Category selection failed: {e}")
        # Fallback: return required + basic categories
        return required_categories + ["professional_context", "decision_criteria"]


def _get_scenario_required_categories(self, template_data: Dict[str, Any]) -> List[str]:
    """
    Determine required categories based on scenario type.
    These MUST be included for the scenario to work properly.
    """
    
    domain = template_data.get("general_info", {}).get("domain", "")
    archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
    assess_mode = template_data.get("assess_mode", {})
    what_happens = assess_mode.get("what_happens", "")
    
    required = []
    
    # PERSUASION archetype always needs decision_criteria
    if archetype == "PERSUASION":
        required.append("decision_criteria")
    
    # Sales scenarios need these
    if "sales" in domain.lower() or "pharmaceutical" in domain.lower():
        required.extend([
            "professional_context",  # Need to know their practice
            "time_constraints",      # Sales people face busy professionals
            "sales_rep_history"      # Context of past interactions
        ])
    
    # Medical scenarios need medical_philosophy
    if any(keyword in domain.lower() for keyword in ["medical", "pharmaceutical", "healthcare"]):
        required.append("medical_philosophy")
    
    # DEI/Confrontation scenarios need these
    if archetype == "CONFRONTATION":
        required.extend([
            "emotional_state",
            "incident_context",
            "work_relationships"
        ])
    
    # Service/Help scenarios need these
    if archetype == "HELP_SEEKING":
        required.extend([
            "problem_description",
            "anxiety_factors"
        ])
    
    # Remove duplicates
    required = list(set(required))
    
    print(f"[CATEGORIES] Required categories for this scenario: {required}")
    
    return required
```

---

## 🔧 FIX #3: Correct Generation Context (Sales vs Patient Care)

### Issue:
Generated persona sounds like they're talking to PATIENTS, not to FSO:
- "patient's well-being"
- "patient education"
- "patient affordability"

### Solution: Add Clear Context to Generation Prompts

**File to modify:** `core/persona_generator_v2.py`

**Update `_generate_single_category` method:**

```python
async def _generate_single_category(
    self,
    category_name: str,
    template_data: Dict[str, Any],
    base_persona: Dict[str, Any],
    custom_prompt: Optional[str]
) -> Dict[str, Any]:
    """Generate details for a single category with CLEAR CONTEXT"""
    
    category_def = self.category_library.get_category_definition(category_name)
    
    # NEW: Build context about who persona interacts with
    interaction_context = self._build_interaction_context(template_data, base_persona)
    
    generation_prompt = f"""
Generate realistic, detailed information for the "{category_name}" category of this persona.

**Category Definition:** {category_def.description}

**Example Fields:** {", ".join(category_def.example_fields)}

**Persona:**
- Name: {base_persona["name"]}
- Age: {base_persona["age"]}
- Role: {base_persona["role"]}
- Location: {base_persona["location"].city}

**Scenario Context:**
{json.dumps(template_data.get("context_overview", {}), indent=2)}

**Domain:** {template_data.get("general_info", {}).get("domain", "general")}

{interaction_context}

{f"**Custom Instructions:** {custom_prompt}" if custom_prompt else ""}

**Task:** Generate rich, realistic details for this category that make the persona feel human and authentic.

**Requirements:**
1. Use realistic Indian context (names, locations, cultural details)
2. Make details specific and concrete (not generic)
3. Include numeric details where relevant
4. Show depth and nuance
5. Connect details to the scenario
6. **CRITICAL:** Focus on how this persona interacts with {template_data.get("assess_mode", {}).get("learner_role", "the learner")}

**Output Format:**
Return a JSON object with detailed fields for this category.

Generate detailed JSON for "{category_name}":
"""
    
    # ... rest of the method stays the same ...


def _build_interaction_context(self, template_data: Dict[str, Any], base_persona: Dict[str, Any]) -> str:
    """
    Build clear context about WHO the persona interacts with and HOW.
    This prevents confusion (e.g., doctor talking to patient vs doctor talking to FSO).
    """
    
    assess_mode = template_data.get("assess_mode", {})
    learner_role = assess_mode.get("learner_role", "learner")
    ai_bot_role = assess_mode.get("ai_bot_role", base_persona["role"])
    what_happens = assess_mode.get("what_happens", "")
    archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
    
    context = f"""
**CRITICAL INTERACTION CONTEXT:**

**This persona is:** {ai_bot_role}
**They are interacting with:** {learner_role}
**What's happening:** {what_happens}
**Archetype:** {archetype}

"""
    
    # Add archetype-specific context
    if archetype == "PERSUASION":
        context += f"""
**This means:**
- The {learner_role} is trying to CONVINCE/PERSUADE/SELL to this persona
- This persona is being PITCHED TO or SOLD TO
- Behavioral triggers should be about the SALES INTERACTION (not patient care!)
- Focus on: What convinces them? What frustrates them about sales pitches?
- Opening behavior: How they greet a {learner_role} who approaches them

**WRONG FOCUS:** Patient care, patient education, patient outcomes
**RIGHT FOCUS:** Sales pitch evaluation, evidence requirements, time management with sales reps
"""
    
    elif archetype == "HELP_SEEKING":
        context += f"""
**This means:**
- This persona HAS A PROBLEM and is seeking help from {learner_role}
- The {learner_role} should HELP/ASSIST/SOLVE the problem
- Focus on: What's their problem? What help do they need? What would satisfy them?
"""
    
    elif archetype == "CONFRONTATION":
        context += f"""
**This means:**
- There's a conflict, bias incident, or uncomfortable situation
- This persona is INVOLVED in the situation (victim, perpetrator, or bystander)
- Focus on: Emotional state, incident details, how they react to approach
"""
    
    return context
```

**Also update `_generate_conversation_rules` with same context:**

```python
async def _generate_conversation_rules(
    self,
    template_data: Dict[str, Any],
    base_persona: Dict[str, Any],
    detail_categories: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate conversation rules with CLEAR CONTEXT"""
    
    archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
    learner_role = template_data.get("assess_mode", {}).get("learner_role", "learner")
    
    # Build interaction context
    interaction_context = self._build_interaction_context(template_data, base_persona)
    
    # Build context from detail categories
    context_summary = "\n".join([
        f"**{cat_name}:** {json.dumps(details, indent=2)}"
        for cat_name, details in detail_categories.items()
    ])
    
    rules_prompt = f"""
Generate conversation rules and behavioral parameters for this persona.

**Persona:** {base_persona["name"]}, {base_persona["role"]}
**Archetype:** {archetype}

{interaction_context}

**Detail Categories:**
{context_summary}

**Generate:**
1. opening_behavior: How they start when {learner_role} approaches
2. response_style: How they communicate (brief/detailed, formal/casual, skeptical/open)
3. word_limit: Typical response length (30-100 words)
4. behavioral_triggers: 
   - what_engages: What makes them receptive to {learner_role}
   - what_frustrates: What annoys them about {learner_role}'s approach
   - what_escalates: What makes them more negative/resistant
   - what_ends_conversation: What makes them end the interaction

**CRITICAL:** All behavioral triggers should be about interaction with {learner_role}, NOT about other contexts!

**Output JSON:**
{{
    "opening_behavior": "...",
    "response_style": "...",
    "word_limit": 50,
    "behavioral_triggers": {{
        "what_engages": [],
        "what_frustrates": [],
        "what_escalates": [],
        "what_ends_conversation": []
    }}
}}
"""
    
    # ... rest of method ...
```

---

## 🔧 FIX #4: Add Validation for Consistency

### Issue:
Location says Mumbai but professional_context says Bangalore.

### Solution: Add Post-Generation Validation

**File to create:** `core/persona_validator.py`

```python
"""
Persona Validator
Validates generated personas for consistency and quality.
"""

from typing import Dict, Any, List
from models.persona_models import PersonaInstance


class PersonaValidator:
    """
    Validates generated personas and fixes common issues.
    """
    
    @staticmethod
    def validate(persona: PersonaInstance, template_data: Dict[str, Any]) -> List[str]:
        """
        Validate persona and return list of issues found.
        """
        issues = []
        
        # Check 1: Archetype correctness
        expected_archetype = PersonaValidator._get_expected_archetype(template_data)
        if expected_archetype and persona.archetype != expected_archetype:
            issues.append(f"Wrong archetype: got {persona.archetype}, expected {expected_archetype}")
        
        # Check 2: Location consistency
        location_issues = PersonaValidator._check_location_consistency(persona)
        issues.extend(location_issues)
        
        # Check 3: Required categories present
        missing_categories = PersonaValidator._check_required_categories(persona, template_data)
        if missing_categories:
            issues.append(f"Missing required categories: {missing_categories}")
        
        # Check 4: Conversation context appropriate
        context_issues = PersonaValidator._check_conversation_context(persona, template_data)
        issues.extend(context_issues)
        
        return issues
    
    @staticmethod
    def _get_expected_archetype(template_data: Dict[str, Any]) -> str:
        """Determine expected archetype from scenario"""
        domain = template_data.get("general_info", {}).get("domain", "")
        what_happens = template_data.get("assess_mode", {}).get("what_happens", "")
        
        if "sales" in domain.lower() or "pitch" in what_happens.lower():
            return "PERSUASION"
        elif "help" in what_happens.lower() or "problem" in what_happens.lower():
            return "HELP_SEEKING"
        elif "bias" in domain.lower() or "conflict" in what_happens.lower():
            return "CONFRONTATION"
        
        return None
    
    @staticmethod
    def _check_location_consistency(persona: PersonaInstance) -> List[str]:
        """Check if location is consistent across all fields"""
        issues = []
        
        main_city = persona.location.city
        main_state = persona.location.state
        
        # Check professional_context if exists
        prof_context = persona.detail_categories.get("professional_context", {})
        if "location" in prof_context:
            prof_location = prof_context["location"]
            if main_city not in prof_location and main_state not in prof_location:
                issues.append(f"Location mismatch: base location is {main_city}, {main_state} but professional_context says {prof_location}")
        
        return issues
    
    @staticmethod
    def _check_required_categories(persona: PersonaInstance, template_data: Dict[str, Any]) -> List[str]:
        """Check if required categories are present"""
        
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        domain = template_data.get("general_info", {}).get("domain", "")
        
        required = []
        
        # Archetype requirements
        if archetype == "PERSUASION":
            required.append("decision_criteria")
        
        # Domain requirements
        if "sales" in domain.lower() or "pharmaceutical" in domain.lower():
            required.extend(["time_constraints", "sales_rep_history"])
        
        # Check what's missing
        missing = [cat for cat in required if cat not in persona.detail_categories_included]
        
        return missing
    
    @staticmethod
    def _check_conversation_context(persona: PersonaInstance, template_data: Dict[str, Any]) -> List[str]:
        """Check if conversation rules match the scenario context"""
        issues = []
        
        learner_role = template_data.get("assess_mode", {}).get("learner_role", "")
        archetype = persona.archetype
        
        conv_rules = persona.conversation_rules
        opening = conv_rules.get("opening_behavior", "")
        response_style = conv_rules.get("response_style", "")
        
        # Check for PERSUASION archetype issues
        if archetype == "PERSUASION":
            # Should NOT mention patient care
            if "patient" in opening.lower() or "patient" in response_style.lower():
                if learner_role and "patient" not in learner_role.lower():
                    issues.append("Conversation rules mention 'patient' but learner is not a patient - likely confusion between patient care and sales pitch")
        
        return issues
    
    @staticmethod
    def auto_fix(persona: PersonaInstance, issues: List[str]) -> PersonaInstance:
        """
        Attempt to auto-fix common issues.
        Returns fixed persona.
        """
        
        # Fix 1: Location consistency
        if any("Location mismatch" in issue for issue in issues):
            main_city = persona.location.city
            main_state = persona.location.state
            
            # Fix professional_context location
            if "professional_context" in persona.detail_categories:
                persona.detail_categories["professional_context"]["location"] = f"{main_city}, {main_state}, India"
        
        return persona
```

**Use the validator:**

```python
# In persona_generator_v2.py

async def generate_persona(
    self,
    template_data: Dict[str, Any],
    mode: str,
    gender: Optional[str] = None,
    custom_prompt: Optional[str] = None
) -> PersonaInstance:
    """
    Main entry point with validation!
    """
    
    # ... existing generation code ...
    
    # NEW: Validate generated persona
    from core.persona_validator import PersonaValidator
    
    issues = PersonaValidator.validate(persona, template_data)
    
    if issues:
        print(f"[VALIDATION] Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Try to auto-fix
        persona = PersonaValidator.auto_fix(persona, issues)
        
        # Re-validate
        remaining_issues = PersonaValidator.validate(persona, template_data)
        if remaining_issues:
            print(f"[VALIDATION] {len(remaining_issues)} issues remain after auto-fix")
    else:
        print("[VALIDATION] Persona looks good! ✅")
    
    return persona
```

---

## 📋 Implementation Checklist

### Phase 1: Archetype Fix
- [ ] Add `determine_correct_archetype()` function
- [ ] Add `validate_and_correct_archetype()` function
- [ ] Call validation after extraction
- [ ] Improve archetype classification prompt
- [ ] Test: Pharma sales should be PERSUASION

### Phase 2: Category Selection Fix
- [ ] Add `_get_scenario_required_categories()` method
- [ ] Update `_determine_relevant_categories()` to use required categories
- [ ] Test: Pharma sales includes time_constraints, sales_rep_history

### Phase 3: Generation Context Fix
- [ ] Add `_build_interaction_context()` method
- [ ] Update `_generate_single_category()` to use context
- [ ] Update `_generate_conversation_rules()` to use context
- [ ] Test: Conversation rules focus on FSO interaction, not patient care

### Phase 4: Validation
- [ ] Create `core/persona_validator.py`
- [ ] Add validation call in `generate_persona()`
- [ ] Add auto-fix for location consistency
- [ ] Test: All validations pass

---

## 🧪 Testing

**Test Case: Pharma Sales Scenario**

```python
# Test extraction + persona generation with fixes
extractor = ScenarioExtractorV2(client)
template_data = await extractor.extract_scenario_info(pharma_doc)

# Check extraction
assert template_data["archetype_classification"]["primary_archetype"] == "PERSUASION"
print("✅ Archetype correct")

# Generate persona
generator = PersonaGenerator(client)
persona = await generator.generate_persona(template_data, "assess_mode")

# Validate
assert persona.archetype == "PERSUASION"
print("✅ Persona archetype correct")

assert "time_constraints" in persona.detail_categories_included
print("✅ time_constraints included")

assert "sales_rep_history" in persona.detail_categories_included
print("✅ sales_rep_history included")

# Check conversation context
conv_rules = persona.conversation_rules
assert "patient" not in conv_rules["opening_behavior"].lower()
print("✅ Conversation context correct (no patient care confusion)")

# Check location consistency
main_city = persona.location.city
prof_location = persona.detail_categories.get("professional_context", {}).get("location", "")
assert main_city in prof_location
print("✅ Location consistent")

print("\n🎉 All fixes verified!")
```

---

## 📊 Expected Results After Fixes

### Before Fixes:
```json
{
  "archetype": "HELP_SEEKING",  // ❌
  "detail_categories_included": [
    "professional_context",
    "medical_philosophy",
    "decision_criteria"
    // Missing: time_constraints, sales_rep_history
  ],
  "conversation_rules": {
    "opening_behavior": "patient's well-being...",  // ❌
    "behavioral_triggers": {
      "what_ends_conversation": ["patient affordability"]  // ❌
    }
  },
  "location": {"city": "Mumbai"},
  "detail_categories": {
    "professional_context": {
      "location": "Bangalore"  // ❌ Inconsistent
    }
  }
}
```

### After Fixes:
```json
{
  "archetype": "PERSUASION",  // ✅
  "detail_categories_included": [
    "professional_context",
    "medical_philosophy",
    "decision_criteria",
    "time_constraints",        // ✅ Added
    "sales_rep_history"        // ✅ Added
  ],
  "conversation_rules": {
    "opening_behavior": "Brief greeting, asks what FSO wants",  // ✅
    "behavioral_triggers": {
      "what_ends_conversation": ["Disrespect", "Off-topic questions"]  // ✅
    }
  },
  "location": {"city": "Mumbai"},
  "detail_categories": {
    "professional_context": {
      "location": "Mumbai, Maharashtra, India"  // ✅ Consistent
    }
  }
}
```

---

## 🎯 Summary

**4 Fixes Needed:**
1. ✅ Correct archetype (PERSUASION for sales)
2. ✅ Add required categories (time_constraints, sales_rep_history)
3. ✅ Fix generation context (sales pitch, not patient care)
4. ✅ Validate consistency (location, archetype, context)

**Implementation order:**
1. Archetype fix (easiest, high impact)
2. Category selection (medium difficulty, high impact)
3. Generation context (medium difficulty, medium impact)
4. Validation (easy, prevents future issues)

**All fixes are backwards compatible - no breaking changes!** ✅
