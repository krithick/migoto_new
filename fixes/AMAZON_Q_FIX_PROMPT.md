# PROMPT FOR AMAZON Q - IMPLEMENT FIXES

Copy and paste this to Amazon Q:

---

## Main Prompt:

```
I need you to fix 4 issues in our extraction and persona generation system.

**READ THIS GUIDE FIRST:**
/mnt/user-data/outputs/FIX_GUIDE_ISSUES.md

**ISSUES TO FIX:**

1. Wrong archetype classification (HELP_SEEKING instead of PERSUASION for sales scenarios)
2. Missing required detail categories (time_constraints, sales_rep_history)
3. Wrong conversation context (mentions patient care instead of sales pitch)
4. Location inconsistency (Mumbai vs Bangalore)

**WHAT TO DO:**

Step 1: Fix Archetype
- Add the determine_correct_archetype() function from the guide
- Add validate_and_correct_archetype() function
- Call it after extraction completes
- Make sure pharma sales = PERSUASION archetype

Step 2: Fix Category Selection
- Add _get_scenario_required_categories() method
- Update _determine_relevant_categories() to include required categories
- For sales scenarios, MUST include: time_constraints, sales_rep_history

Step 3: Fix Generation Context
- Add _build_interaction_context() method
- Update _generate_single_category() to use this context
- Update _generate_conversation_rules() to use this context
- Make sure prompts clarify: persona interacts with FSO (sales pitch), NOT patients

Step 4: Add Validation
- Create core/persona_validator.py with PersonaValidator class
- Add validation call in generate_persona()
- Auto-fix location consistency

**TEST AFTER IMPLEMENTING:**
Run the test code from the guide to verify all 4 issues are fixed.

**CRITICAL:**
- Don't break existing functionality
- Add these as enhancements to existing code
- Use the exact code from the guide

Start by reading the guide, then implement step by step.
```

---

## Quick Summary for You:

The guide provides:
✅ Exact code for all 4 fixes
✅ Where to add each fix
✅ Test code to verify fixes work
✅ Before/after examples

Amazon Q just needs to:
1. Read the guide
2. Copy the code snippets
3. Add them to the right files
4. Test that fixes work

Should take 30-60 minutes to implement all 4 fixes.
