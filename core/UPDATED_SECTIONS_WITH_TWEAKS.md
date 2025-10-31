# Updated Sections with All 3 Tweaks Applied

This file contains the UPDATED code sections with all tweaks applied.
Replace the corresponding sections in your `core/system_prompt_generator.py` file.

---

## TWEAK 1: Updated Section 4 Instructions

### Location in file: Around line 450 in `_build_generation_prompt()` method

### Find the section that starts with:
```
**For EACH detail_category that exists in persona_data:**
```

### Replace the ENTIRE block (from "For EACH detail_category" to "Don't assume which categories exist") with:

```python
**For EACH detail_category that exists in persona_data:**

Create a subsection:
## [Category Name]

Write 120-180 words in rich narrative style with this structure:

1. **Opening statement** (what this aspect is about for this persona)
2. **Specific details** from the data (include numbers, names, examples)
3. **Mini-stories or scenarios** (if past experiences or interactions exist)
4. **Impact on behavior** (how this affects how they act and react)

**USE SUB-BREAKDOWNS when helpful to organize information:**
- For history categories: "Good experiences: ..." / "Bad experiences: ..."
- For criteria categories: "Must-haves: ..." / "Deal-breakers: ..."
- For time categories: "Daily routine: ..." / "When disrupted: ..."
- For relationship categories: "Trust level: ..." / "Skepticism level: ..."

**Example structure for Sales Rep History:**
"You have [trust level] trust but [skepticism level] skepticism. Past interactions:
Good experience - [Product Name]: [what happened, outcome]
Bad experience - [Product Name]: [what happened, outcome]
What convinces you: [list]
What frustrates you: [list]"

This structure makes each category feel complete and immersive.

**Don't assume which categories exist - dynamically use whatever is present!**
```

---

## TWEAK 2: Updated Section 5 Special Situations

### Location in file: Around line 530 in `_build_generation_prompt()` method

### Find the section that starts with:
```
**Special Situations:**
```

### Replace from "**Special Situations:**" down to the line with "**Throughout the conversation:**" with:

```python
**Special Situations with CLEAR ESCALATION:**

Show escalation patterns that build naturally:

- **IF disrespectful/profanity:**
  → ONE STRIKE - end immediately
  → "I don't appreciate that. We're done. [FINISH]"

- **IF off-topic questions:**
  → First time: "That's not relevant to our discussion."
  → Second time: "I need to stay focused. Do you have relevant information?"
  → Third time: "We're done here. [FINISH]"

- **IF wrong product for specialty:**
  → First mention: "I don't treat [wrong_area]. Why are you pitching this to me?"
  → If they continue: "This isn't relevant to my practice. [FINISH]"

- **IF time-wasting with vague responses:**
  → After 2 vague responses: "Can you be more specific? I need concrete information."
  → After 3 vague responses: "I've asked for specifics multiple times. This isn't productive."
  → After 4 vague responses: "I don't have time for this. [FINISH]"

- **IF making good points but time running out:**
  → "This sounds interesting, but I need to see the actual data. Can you send me [relevant materials]? I'll review and get back to you."

- **IF directly addressing concerns with data:**
  → Engage immediately: "That's exactly what I'm concerned about. What were the results?"

Use placeholders like [wrong_area] and [relevant materials] to keep it agnostic.

**Throughout the conversation:**
```

---

## TWEAK 3: Updated Archetype Templates

### Location in file: In `_get_archetype_template()` method

### For each archetype, ADD the "SECTION 4 CATEGORY EMPHASIS" block at the end

---

### PERSUASION Template Update:

Find the end of the PERSUASION template (around line 660), which currently ends with:

```python
4. **Make a decision after 6-8 exchanges:**
   - Convinced (got strong evidence, addressed concerns) = Positive close
   - Uncertain (some info but need more) = Neutral close
   - Not convinced (vague, no evidence, wasted time) = Negative close
""",
```

**Replace with:**

```python
4. **Make a decision after 6-8 exchanges:**
   - Convinced (got strong evidence, addressed concerns) = Positive close
   - Uncertain (some info but need more) = Neutral close
   - Not convinced (vague, no evidence, wasted time) = Negative close

**SECTION 4 CATEGORY EMPHASIS FOR PERSUASION:**

When writing Section 4, give extra depth to these category types:
- **Decision criteria** (150-180 words) - This is CORE! Must-haves, deal-breakers, evaluation factors
- **Time constraints** (150-180 words) - Shows why they're impatient and what frustrates them
- **Past experiences** (150-180 words) - Shows skepticism, what worked/didn't work with examples
- **Sales rep history** (150-180 words) - Trust level, past interactions with outcomes
- Other categories: 120-150 words each

These categories explain WHY they're skeptical and WHAT it takes to convince them.
""",
```

---

### HELP_SEEKING Template Update:

Find the end of the HELP_SEEKING template (around line 720), which currently ends with:

```python
4. **End based on outcome:**
   - Problem solved = Grateful close: "Thank you, this resolves the issue. [FINISH]"
   - Partially helped = Cautious close: "I'll try this and follow up if needed. [FINISH]"
   - Not helped = Frustrated close: "This doesn't address my issue. [FINISH]"
""",
```

**Replace with:**

```python
4. **End based on outcome:**
   - Problem solved = Grateful close: "Thank you, this resolves the issue. [FINISH]"
   - Partially helped = Cautious close: "I'll try this and follow up if needed. [FINISH]"
   - Not helped = Frustrated close: "This doesn't address my issue. [FINISH]"

**SECTION 4 CATEGORY EMPHASIS FOR HELP_SEEKING:**

When writing Section 4, give extra depth to these category types:
- **Problem description** (150-180 words) - This is CORE! What's wrong, urgency, impact
- **Anxiety factors** (150-180 words) - What worries them, emotional state
- **Past attempts** (150-180 words) - What they tried, why it didn't work
- **Help expectations** (150-180 words) - What they need, what would satisfy them
- Other categories: 120-150 words each

These categories explain WHAT they need help with and HOW frustrated/anxious they are.
""",
```

---

### CONFRONTATION Template Update:

Find the end of the CONFRONTATION template (around line 780), which currently ends with:

```python
4. **End based on outcome:**
   - Issue acknowledged/resolved = Satisfied close: "I appreciate you taking this seriously. [FINISH]"
   - Partial acknowledgment = Cautious close: "I hope this will be addressed properly. [FINISH]"
   - Dismissed/not resolved = Frustrated close: "I don't feel heard. I'll need to escalate this. [FINISH]"
""",
```

**Replace with:**

```python
4. **End based on outcome:**
   - Issue acknowledged/resolved = Satisfied close: "I appreciate you taking this seriously. [FINISH]"
   - Partial acknowledgment = Cautious close: "I hope this will be addressed properly. [FINISH]"
   - Dismissed/not resolved = Frustrated close: "I don't feel heard. I'll need to escalate this. [FINISH]"

**SECTION 4 CATEGORY EMPHASIS FOR CONFRONTATION:**

When writing Section 4, give extra depth to these category types:
- **Incident context** (150-180 words) - This is CORE! What happened, when, who was involved
- **Emotional state** (150-180 words) - How they feel, defensiveness level, anxiety
- **Power dynamics** (150-180 words) - Relationship context, who has power
- **Work relationships** (150-180 words) - Team dynamics, history with others
- Other categories: 120-150 words each

These categories explain WHAT happened and HOW they feel about it.
""",
```

---

### INVESTIGATION Template Update:

Find the end of the INVESTIGATION template (around line 840), which currently ends with:

```python
3. **End based on outcome:**
   - Satisfied with process = Cooperative close: "I've shared what I can. [FINISH]"
   - Concerns about fairness = Guarded close: "I think that's all I should say. [FINISH]"
   - Feel attacked = Defensive close: "I'm not continuing this without representation. [FINISH]"
""",
```

**Replace with:**

```python
3. **End based on outcome:**
   - Satisfied with process = Cooperative close: "I've shared what I can. [FINISH]"
   - Concerns about fairness = Guarded close: "I think that's all I should say. [FINISH]"
   - Feel attacked = Defensive close: "I'm not continuing this without representation. [FINISH]"

**SECTION 4 CATEGORY EMPHASIS FOR INVESTIGATION:**

When writing Section 4, give extra depth to these category types:
- **Incident knowledge** (150-180 words) - What they know, their involvement level
- **Cooperation level** (150-180 words) - How willing/reluctant they are
- **Protection concerns** (150-180 words) - What they're guarding, why they're cautious
- **Rights awareness** (150-180 words) - What boundaries they set
- Other categories: 120-150 words each

These categories explain WHAT they know and HOW cooperative they'll be.
""",
```

---

### NEGOTIATION Template Update:

Find the end of the NEGOTIATION template (around line 900), which currently ends with:

```python
3. **End based on outcome:**
   - Deal reached = Satisfied close: "I think we have an agreement. [FINISH]"
   - Partial agreement = Conditional close: "I'll need to think about this. [FINISH]"
   - No agreement = Walk away: "We're too far apart. Thank you for your time. [FINISH]"
"""
```

**Replace with (NOTE: this one has THREE quotes at the end, not a comma!):**

```python
3. **End based on outcome:**
   - Deal reached = Satisfied close: "I think we have an agreement. [FINISH]"
   - Partial agreement = Conditional close: "I'll need to think about this. [FINISH]"
   - No agreement = Walk away: "We're too far apart. Thank you for your time. [FINISH]"

**SECTION 4 CATEGORY EMPHASIS FOR NEGOTIATION:**

When writing Section 4, give extra depth to these category types:
- **Position and priorities** (150-180 words) - What they want, what's most important
- **Bottom line** (150-180 words) - Walk-away point, non-negotiables
- **Leverage** (150-180 words) - What power they have, alternatives available
- **Trade-offs** (150-180 words) - What they're willing to compromise on
- Other categories: 120-150 words each

These categories explain WHAT they want and HOW they'll negotiate.
"""
```

---

## Summary of All Changes:

✅ **Tweak 1:** Section 4 instructions now specify 120-180 words per category with structured approach
✅ **Tweak 2:** Section 5 special situations now show clear 3-step escalation patterns
✅ **Tweak 3:** All 5 archetype templates now have "SECTION 4 CATEGORY EMPHASIS" blocks

**Expected Result:** Generated prompts should now be 3500-4000 words with Section 4 at 1000-1200 words.

---

## How to Apply These Changes:

1. Open your `core/system_prompt_generator.py` file
2. Find each section mentioned above (use Ctrl+F to search for the text)
3. Replace with the updated version
4. Save the file
5. Test with: `await generate_system_prompt(client, template_data, persona_data, "assess_mode")`

Done! 🚀
