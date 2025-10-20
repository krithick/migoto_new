# Prompt Quality Validation System

## Overview
**Real validation** that tests prompts by running actual conversations with AI personas, not just checking structure.

## How It Works

### 1. Automated Conversation Testing
Tests prompts by simulating real user interactions and evaluating AI responses.

**Test Types**:
- ✅ **Knowledge Accuracy**: Does AI provide correct information from knowledge base?
- ✅ **Persona Consistency**: Does AI stay in character throughout?
- ✅ **Archetype Behavior**: Does AI exhibit archetype-specific behaviors (objections, defensive mechanisms)?
- ✅ **Error Handling**: Does AI handle unclear/inappropriate input gracefully?

### 2. Interactive Testing Facility
Allows manual testing with real conversations before deploying to production.

## API Endpoints

### 1. Automated Quality Test
```http
POST /scenario/test-prompt-quality
Content-Type: application/json

{
  "system_prompt": "You are a customer with concerns...",
  "persona": {
    "name": "Sarah",
    "role": "Concerned Customer",
    "objection_library": [...]
  },
  "template_data": {
    "knowledge_base": {...},
    "archetype_classification": {...}
  },
  "mode": "assess"
}
```

**Response**:
```json
{
  "overall_score": 0.85,
  "test_summary": {
    "passed_tests": 4,
    "total_tests": 5,
    "pass_rate": 80.0
  },
  "conversation_examples": [
    {
      "user": "Can you tell me about your pricing?",
      "ai": "I'm concerned about the cost. From what I understand, the pricing seems high compared to alternatives...",
      "passed": true,
      "evaluation": "Response stays in character and shows appropriate concern"
    },
    {
      "user": "Who are you?",
      "ai": "I'm Sarah, a potential customer evaluating your product. I have some concerns about...",
      "passed": true,
      "evaluation": "Consistent persona with clear background"
    }
  ],
  "strengths": [
    "Strong persona_consistency handling (score: 0.90)",
    "Proper archetype-specific behavior"
  ],
  "weaknesses": [
    "Weak error_handling handling (score: 0.45)"
  ],
  "recommendations": [
    "Improve error_handling by reviewing prompt instructions"
  ]
}
```

### 2. Start Interactive Test
```http
POST /scenario/start-interactive-test
Content-Type: application/json

{
  "system_prompt": "You are a customer...",
  "persona": {...},
  "initial_message": "Hi, I'm interested in your product"
}
```

**Response**:
```json
{
  "conversation_id": "test_a3f2b1c8",
  "persona": "Sarah Johnson",
  "initial_response": "Hi! Thanks for reaching out. I've been looking at your product, but I have some concerns about the pricing and features...",
  "message": "Conversation started. Use continue_test_conversation to continue."
}
```

### 3. Continue Interactive Test
```http
POST /scenario/continue-interactive-test
Content-Type: application/json

{
  "system_prompt": "You are a customer...",
  "user_message": "What specific concerns do you have?",
  "conversation_history": [
    {"role": "user", "content": "Hi, I'm interested in your product"},
    {"role": "assistant", "content": "Hi! Thanks for reaching out..."}
  ]
}
```

**Response**:
```json
{
  "user_message": "What specific concerns do you have?",
  "ai_response": "Well, mainly I'm worried about the cost-benefit ratio. Your product is priced at $500/month, but I'm not sure if it offers enough value compared to competitors at $300/month...",
  "turn_number": 2,
  "conversation_history": [...]
}
```

### 4. Evaluate Test Conversation
```http
POST /scenario/evaluate-test-conversation
Content-Type: application/json

{
  "conversation_history": [...],
  "template_data": {...},
  "persona": {...}
}
```

**Response**:
```json
{
  "evaluation": {
    "overall_score": 0.88,
    "persona_consistency": 0.95,
    "knowledge_accuracy": 0.85,
    "response_quality": 0.90,
    "strengths": [
      "Maintained consistent persona throughout",
      "Used objection library effectively",
      "Showed appropriate emotional state"
    ],
    "issues": [
      "One response was slightly out of character"
    ],
    "recommendations": [
      "Clarify persona's decision criteria in prompt"
    ]
  },
  "conversation_length": 5,
  "message": "Conversation evaluated successfully"
}
```

## Validation Criteria

### Knowledge Accuracy Test
**What it checks**:
- Does AI reference correct information from knowledge base?
- Are facts accurate?
- Does AI avoid making up information?

**Example**:
```
USER: "Can you tell me about your return policy?"
AI: "Our return policy allows 30-day returns with full refund..." ✅
vs
AI: "I think we have some return policy..." ❌
```

### Persona Consistency Test
**What it checks**:
- Does AI maintain character background?
- Is role consistent?
- Are personality traits evident?

**Example**:
```
USER: "Who are you?"
AI: "I'm Sarah, a marketing manager at TechCorp. I'm evaluating solutions for my team..." ✅
vs
AI: "I'm an AI assistant here to help you." ❌
```

### Archetype Behavior Test
**What it checks**:
- **PERSUASION**: Uses objection_library, shows decision criteria
- **CONFRONTATION**: Exhibits defensive_mechanisms, shows emotional_state
- **HELP_SEEKING**: Shows vulnerability, asks for guidance
- **INVESTIGATION**: Asks probing questions, seeks details
- **NEGOTIATION**: Proposes alternatives, seeks compromise

**Example (PERSUASION)**:
```
USER: "Why should you choose our product?"
AI: "I'm not convinced yet. My main concern is the price point - it's 40% higher than competitors. What additional value justifies this cost?" ✅
(Uses objection from objection_library)
```

### Error Handling Test
**What it checks**:
- Handles unclear input gracefully
- Responds professionally to inappropriate messages
- Stays in character even with difficult interactions

**Example**:
```
USER: "xyz random nonsense"
AI: "I'm not sure I understand. Could you clarify what you're asking about?" ✅
vs
AI: "Error: Invalid input" ❌
```

## Scoring System

### Overall Score Calculation
```
overall_score = average(all_test_scores)

Test Score = (
  knowledge_accuracy * 0.3 +
  persona_consistency * 0.3 +
  archetype_behavior * 0.2 +
  error_handling * 0.2
)
```

### Score Interpretation
| Score | Quality | Meaning |
|-------|---------|---------|
| 0.9-1.0 | Excellent | Production ready |
| 0.8-0.89 | Good | Minor improvements recommended |
| 0.7-0.79 | Fair | Review weaknesses |
| 0.6-0.69 | Poor | Significant issues |
| <0.6 | Critical | Major prompt problems |

## Integration with Frontend

### Step 3: Review & Test Prompts (Enhanced)

```jsx
// After generating prompts
const testPromptQuality = async () => {
  const result = await fetch('/scenario/test-prompt-quality', {
    method: 'POST',
    body: JSON.stringify({
      system_prompt: generatedPrompts.assess_mode_prompt,
      persona: generatedPrompts.personas[0],
      template_data: templateData,
      mode: 'assess'
    })
  });
  
  const quality = await result.json();
  
  // Show quality score and conversation examples
  setQualityScore(quality.overall_score);
  setConversationExamples(quality.conversation_examples);
  setRecommendations(quality.recommendations);
};

// Interactive testing
const startInteractiveTest = async () => {
  const result = await fetch('/scenario/start-interactive-test', {
    method: 'POST',
    body: JSON.stringify({
      system_prompt: generatedPrompts.assess_mode_prompt,
      persona: generatedPrompts.personas[0],
      initial_message: "Hi, I need help with something"
    })
  });
  
  const conversation = await result.json();
  setTestConversation(conversation);
};
```

## Example Workflow

### 1. Generate Prompts
```bash
POST /generate-prompts-from-template
→ Returns: learn_mode_prompt, assess_mode_prompt, try_mode_prompt, personas
```

### 2. Automated Quality Test
```bash
POST /test-prompt-quality
→ Runs 5 test conversations automatically
→ Returns: score, examples, strengths, weaknesses
```

### 3. Review Results
```
Score: 0.85 (Good)

Conversation Examples:
✅ Knowledge test: Passed
✅ Persona test: Passed
✅ Archetype test: Passed
⚠️ Error handling: Needs improvement

Recommendations:
- Add clearer instructions for handling unclear input
```

### 4. Interactive Testing (Optional)
```bash
POST /start-interactive-test
→ Start conversation

POST /continue-interactive-test (multiple times)
→ Have full conversation

POST /evaluate-test-conversation
→ Get detailed evaluation
```

### 5. Fix Issues & Retest
```bash
# Edit prompt based on recommendations
# Retest
POST /test-prompt-quality
→ New score: 0.92 (Excellent)
```

### 6. Create Scenario
```bash
POST /scenarios
→ Deploy to production
```

## Benefits

✅ **Real Validation**: Tests actual conversations, not just structure
✅ **Archetype Verification**: Confirms archetype-specific behaviors work
✅ **Quality Assurance**: Catches prompt issues before production
✅ **Interactive Testing**: Manual testing facility for edge cases
✅ **Actionable Feedback**: Specific recommendations for improvement
✅ **Conversation Examples**: See exactly how AI will behave
✅ **Confidence**: Deploy knowing prompts work correctly

## What Gets Validated

### Before (Structure Only)
- ❌ "Prompt exists" ✓
- ❌ "Prompt is long enough" ✓
- ❌ "Persona has required fields" ✓

### Now (Actual Behavior)
- ✅ "AI stays in character" ✓
- ✅ "AI uses objection library correctly" ✓
- ✅ "AI provides accurate information" ✓
- ✅ "AI handles errors gracefully" ✓
- ✅ "AI exhibits archetype behaviors" ✓

This is **real validation** that ensures your prompts will work correctly in production!
