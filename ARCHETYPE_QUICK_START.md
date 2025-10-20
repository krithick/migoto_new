# Archetype System - Quick Start Guide

## 🚀 What's New?

Your scenario generation system now automatically classifies training scenarios into 5 archetype types:

1. **HELP_SEEKING** - Character has a problem, needs assistance
2. **PERSUASION** - Character is satisfied, learner must create interest
3. **CONFRONTATION** - Address wrongdoing (3 sub-types: perpetrator/victim/bystander)
4. **INVESTIGATION** - Gather information through questioning
5. **NEGOTIATION** - Find middle ground between competing interests

## 📋 Quick Examples

### HELP_SEEKING
```
"Customer service training where a frustrated customer's laptop broke 
after 2 days. Rep must diagnose, show empathy, and provide solution."
```
**Pattern:** Character has problem → Seeks help → Learner provides solution

---

### PERSUASION
```
"Pharma rep details new diabetes drug to Dr. Archana who is satisfied 
with current treatments. Must present data and overcome objections."
```
**Pattern:** Character has NO problem → Learner creates interest → Overcome objections

---

### CONFRONTATION
```
"Manager addresses team lead making inappropriate disability comments. 
Team lead is defensive. Manager must hold them accountable."
```
**Pattern:** Someone did wrong → Learner addresses behavior → Accountability

**Sub-types:**
- **PERPETRATOR**: Talk to person who did wrong
- **VICTIM**: Support person who was harmed
- **BYSTANDER**: Interview witness

---

### INVESTIGATION
```
"Medical student takes history from patient with vague symptoms. 
Patient has difficulty articulating. Student must ask right questions."
```
**Pattern:** Character has information → Learner extracts through questions → Diagnosis

---

### NEGOTIATION
```
"Employee negotiates 15% raise with manager who has budget constraints. 
Both must find mutually acceptable solution."
```
**Pattern:** Both want different things → Find middle ground → Win-win solution

---

## 🔧 How to Use

### 1. Automatic Classification (Default)

When you create a scenario, classification happens automatically:

```python
POST /scenario/analyze-scenario
{
  "scenario_document": "Your scenario description..."
}
```

Response includes:
```json
{
  "archetype_classification": {
    "primary_archetype": "PERSUASION",
    "confidence_score": 0.85,
    "alternative_archetypes": ["HELP_SEEKING"],
    "reasoning": "Character is satisfied with current solution...",
    "sub_type": null
  }
}
```

---

### 2. Test Classification Only

Quick test without full generation:

```python
POST /scenario/test-archetype-classification
{
  "scenario_document": "Your scenario description..."
}
```

Returns just the classification result.

---

### 3. Check Archetype Definitions

View all archetype configurations:

```python
# In MongoDB
db.archetype_definitions.find()

# Returns 5 documents with:
# - extraction_keywords
# - extraction_patterns
# - system_prompt_templates
# - coaching_rules_templates
```

---

## 🎯 Understanding Confidence Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 0.9 - 1.0 | Very confident | Trust the classification |
| 0.7 - 0.9 | Confident | Good classification |
| 0.5 - 0.7 | Uncertain | Review alternatives |
| < 0.5 | Low confidence | Manual review needed |

---

## 🔍 Troubleshooting

### Classification seems wrong?

**Check the reasoning field:**
```json
"reasoning": "Character explicitly has a problem (broken laptop) and seeks assistance from learner. Matches HELP_SEEKING pattern."
```

**Look at alternatives:**
```json
"alternative_archetypes": ["PERSUASION", "INVESTIGATION"]
```

If confidence is low, the scenario might be:
- Ambiguous (mix of multiple archetypes)
- Poorly described (needs more detail)
- Edge case (doesn't fit standard patterns)

---

### How to improve classification?

**Be specific in scenario descriptions:**

❌ **Vague:**
```
"Training scenario about customer service"
```

✅ **Specific:**
```
"Customer service rep helps frustrated customer whose laptop broke 
after 2 days. Customer needs replacement. Rep must follow return policy 
and provide solution."
```

**Include key indicators:**
- What problem does the character have? (HELP_SEEKING)
- Is character satisfied or has no problem? (PERSUASION)
- Did someone do something wrong? (CONFRONTATION)
- Does learner need to gather information? (INVESTIGATION)
- Are there competing interests? (NEGOTIATION)

---

## 📊 Archetype Decision Tree

```
Does character have a problem?
├─ YES → Is learner providing solution?
│         ├─ YES → HELP_SEEKING
│         └─ NO → Is learner gathering info?
│                  └─ YES → INVESTIGATION
│
└─ NO → Is learner trying to convince them?
         ├─ YES → PERSUASION
         └─ NO → Is there wrongdoing to address?
                  ├─ YES → CONFRONTATION
                  └─ NO → Are there competing interests?
                           └─ YES → NEGOTIATION
```

---

## 🎨 Archetype Characteristics

### HELP_SEEKING
- **Character state:** Has problem, frustrated/confused
- **Learner role:** Problem solver, helper
- **Conversation flow:** Character initiates, explains problem
- **Success:** Problem resolved, character satisfied

### PERSUASION
- **Character state:** Satisfied, skeptical, has objections
- **Learner role:** Convincer, educator
- **Conversation flow:** Learner initiates, creates interest
- **Success:** Character shows interest, objections addressed

### CONFRONTATION
- **Character state:** Defensive (perpetrator), hurt (victim), uncertain (bystander)
- **Learner role:** Accountability holder, supporter, investigator
- **Conversation flow:** Depends on sub-type
- **Success:** Accountability achieved, support provided, information gathered

### INVESTIGATION
- **Character state:** Has information, may be unclear/emotional
- **Learner role:** Information gatherer, questioner
- **Conversation flow:** Learner asks, character reveals
- **Success:** Complete information gathered

### NEGOTIATION
- **Character state:** Has position, wants outcome
- **Learner role:** Negotiator, mediator
- **Conversation flow:** Back-and-forth, proposals
- **Success:** Mutually acceptable agreement

---

## 🔗 Related Files

- **Full Plan:** `ARCHETYPE_SYSTEM_PLAN.md`
- **Test Scenarios:** `ARCHETYPE_TEST_SCENARIOS.md`
- **Implementation Summary:** `WEEK1_INTEGRATION_SUMMARY.md`
- **Models:** `core/archetype_models.py`
- **Classifier:** `core/archetype_classifier.py`
- **Definitions:** `core/archetype_definitions.py`

---

## 💡 Pro Tips

1. **Use specific language:** "Customer has problem" vs "Customer is satisfied"
2. **Mention the learner's role:** "Rep must convince" vs "Rep must help"
3. **Include emotional states:** "Frustrated customer" vs "Skeptical doctor"
4. **Specify conversation initiator:** "Wait for customer" vs "Approach the doctor"
5. **For CONFRONTATION:** Clearly state who did what to whom

---

## 🎓 Training Your Team

### For Content Creators
- Learn the 5 archetype patterns
- Use the decision tree when writing scenarios
- Test scenarios with `/test-archetype-classification`
- Review confidence scores and reasoning

### For Developers
- Understand archetype data models
- Know how to query by archetype
- Use archetype fields in avatar_interactions
- Monitor classification accuracy

### For Trainers
- Recognize archetype patterns in real situations
- Match training needs to appropriate archetypes
- Use archetype-specific coaching approaches
- Leverage sub-types for nuanced scenarios

---

## ✅ Quick Checklist

Before creating a scenario, ask:

- [ ] Does the character have a problem? (HELP_SEEKING)
- [ ] Is the character satisfied/skeptical? (PERSUASION)
- [ ] Is there wrongdoing to address? (CONFRONTATION)
- [ ] Does the learner need to gather info? (INVESTIGATION)
- [ ] Are there competing interests? (NEGOTIATION)
- [ ] Have I been specific about roles and situations?
- [ ] Have I included emotional states?
- [ ] Is it clear who initiates the conversation?

---

## 🚦 Getting Started

1. **Start the application** - Archetypes seed automatically
2. **Test with sample scenario** - Use `/test-archetype-classification`
3. **Review the result** - Check archetype, confidence, reasoning
4. **Create full scenario** - Use `/analyze-scenario` for complete generation
5. **Verify in database** - Check avatar_interactions have archetype fields

---

## 📞 Need Help?

- **Low confidence scores?** → Add more detail to scenario description
- **Wrong classification?** → Check reasoning field, review decision tree
- **Missing archetypes?** → Verify database seeding in startup logs
- **API errors?** → Check OpenAI credentials in .env file

---

**Ready to create archetype-aware training scenarios!** 🎉
