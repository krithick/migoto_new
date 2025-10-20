# Backend Validation System

## Overview
Comprehensive validation system for template data and generated prompts to ensure quality before scenario creation.

## Validation Modules

### 1. Template Validator (`core/template_validator.py`)

**Purpose**: Validates template data quality before prompt generation

**Validation Rules**:

#### Context Overview (20 points per error)
- ❌ **ERROR**: Missing scenario title
- ❌ **ERROR**: Missing scenario description
- ⚠️ **WARNING**: Title too short (<5 chars)
- ⚠️ **WARNING**: Description too brief (<20 chars)

#### Knowledge Base (10 points per warning)
- ⚠️ **WARNING**: No conversation topics defined
- ⚠️ **WARNING**: Limited topics (<3)
- ℹ️ **INFO**: No key facts defined

#### Learning Objectives (10 points per warning)
- ⚠️ **WARNING**: No primary objectives defined
- ℹ️ **INFO**: Limited objectives (<2)

#### Archetype Classification (5 points per info)
- ℹ️ **INFO**: No archetype classification
- ℹ️ **INFO**: Low confidence (<70%)

#### Evaluation Metrics (5 points per info)
- ℹ️ **INFO**: No evaluation criteria defined

**Scoring System**:
- Start: 100 points
- Deduct: 20 (error), 10 (warning), 5 (info)
- Bonus: +10 for quality metrics, +10 for completeness
- Range: 0-100

**Quality Metrics**:
- `context_quality`: 0.0-1.0 (title + description completeness)
- `knowledge_base_quality`: 0.0-1.0 (topics + facts density)
- `objectives_quality`: 0.0-1.0 (primary + secondary objectives)
- `evaluation_quality`: 0.0-1.0 (criteria + rubric presence)

**Completeness Check**:
```json
{
  "context": true/false,
  "knowledge_base": true/false,
  "learning_objectives": true/false,
  "archetype": true/false,
  "evaluation_metrics": true/false
}
```

### 2. Prompts Validator (`core/template_validator.py`)

**Purpose**: Validates generated prompts quality before scenario creation

**Validation Rules**:

#### Mode Prompts (25 points per error)
- ❌ **ERROR**: Missing learn_mode_prompt
- ❌ **ERROR**: Missing try_mode_prompt
- ❌ **ERROR**: Missing assess_mode_prompt
- ⚠️ **WARNING**: Prompt too short (<50 chars)

#### Personas (25 points per error)
- ❌ **ERROR**: No personas generated
- ⚠️ **WARNING**: Less than 3 personas
- ❌ **ERROR**: Persona missing name
- ⚠️ **WARNING**: Persona missing role

**Quality Metrics**:
- `learn_mode_prompt_quality`: 0.0-1.0 (length/200)
- `try_mode_prompt_quality`: 0.0-1.0 (length/200)
- `assess_mode_prompt_quality`: 0.0-1.0 (length/200)
- `personas_quality`: 0.0-1.0 (count/3)

## API Endpoints

### 1. Validate Template
```http
POST /scenario/validate-template
Content-Type: application/json

{
  "template_data": {
    "context_overview": {...},
    "knowledge_base": {...},
    "learning_objectives": {...},
    "archetype_classification": {...}
  }
}
```

**Response**:
```json
{
  "valid": true,
  "score": 85.5,
  "issues": [
    {
      "field": "knowledge_base.conversation_topics",
      "severity": "warning",
      "message": "Limited conversation topics",
      "suggestion": "Consider adding more topics (recommended: 3-7)"
    }
  ],
  "completeness": {
    "context": true,
    "knowledge_base": true,
    "learning_objectives": true,
    "archetype": true,
    "evaluation_metrics": false
  },
  "quality_metrics": {
    "context_quality": 0.9,
    "knowledge_base_quality": 0.6,
    "objectives_quality": 0.8,
    "evaluation_quality": 0.0,
    "archetype_confidence": 0.95
  },
  "recommendation": "Ready for prompt generation"
}
```

### 2. Validate Prompts
```http
POST /scenario/validate-prompts
Content-Type: application/json

{
  "learn_mode_prompt": "...",
  "try_mode_prompt": "...",
  "assess_mode_prompt": "...",
  "personas": [...]
}
```

**Response**:
```json
{
  "valid": true,
  "score": 92.0,
  "issues": [],
  "completeness": {
    "learn_mode_prompt": true,
    "try_mode_prompt": true,
    "assess_mode_prompt": true,
    "personas": true
  },
  "quality_metrics": {
    "learn_mode_prompt_quality": 0.95,
    "try_mode_prompt_quality": 0.90,
    "assess_mode_prompt_quality": 0.92,
    "personas_quality": 1.0
  },
  "recommendation": "Ready for scenario creation"
}
```

### 3. Generate Prompts with Validation
```http
POST /scenario/generate-prompts-from-template
Content-Type: application/json

{
  "template_id": "template_123",
  "modes": ["learn", "try", "assess"],
  "validate_before_generation": true
}
```

**Response** (if validation fails):
```json
{
  "error": "Template validation failed",
  "validation": {
    "valid": false,
    "score": 45.0,
    "issues": [
      {
        "field": "context_overview.scenario_title",
        "severity": "error",
        "message": "Scenario title is required",
        "suggestion": "Provide a clear, descriptive title"
      }
    ]
  },
  "message": "Fix template errors before generating prompts"
}
```

**Response** (if validation passes):
```json
{
  "template_id": "template_123",
  "prompts": {
    "learn_mode_prompt": "...",
    "try_mode_prompt": "...",
    "assess_mode_prompt": "...",
    "personas": [...]
  },
  "template_validation": {
    "score": 88.5,
    "completeness": {...}
  },
  "prompts_validation": {
    "valid": true,
    "score": 95.0,
    "issues": [],
    "quality_metrics": {...}
  },
  "message": "Prompts generated and validated successfully"
}
```

## Integration with Frontend

The React component already uses this validation:

**Step 2: Edit Template**
- Calls `/validate-template` on every edit
- Shows real-time validation score
- Displays issues and warnings
- Blocks "Generate Prompts" if invalid

**Step 3: Review Prompts**
- Automatically validates generated prompts
- Shows quality metrics
- Allows review before scenario creation

## Validation Severity Levels

| Severity | Impact | Blocks Generation |
|----------|--------|-------------------|
| **error** | Critical issue | ✅ Yes |
| **warning** | Quality concern | ❌ No |
| **info** | Suggestion | ❌ No |

## Score Interpretation

| Score | Quality | Action |
|-------|---------|--------|
| 90-100 | Excellent | Ready to generate |
| 75-89 | Good | Minor improvements recommended |
| 60-74 | Fair | Review warnings |
| 45-59 | Poor | Fix issues |
| 0-44 | Critical | Fix errors before proceeding |

## Example Validation Flow

```python
# 1. User edits template
template_data = {
    "context_overview": {
        "scenario_title": "Sales Training",
        "scenario_description": "Learn sales techniques"
    },
    "knowledge_base": {
        "conversation_topics": ["Prospecting", "Closing"],
        "key_facts": []
    }
}

# 2. Validate template
validation = TemplateValidator.validate_template(template_data)
# Result: score=75, warnings about limited topics and no facts

# 3. User adds more content
template_data["knowledge_base"]["conversation_topics"].extend([
    "Objection Handling", "Relationship Building", "Follow-up"
])
template_data["knowledge_base"]["key_facts"] = [
    "80% of sales require 5+ follow-ups",
    "Listening is more important than talking"
]

# 4. Re-validate
validation = TemplateValidator.validate_template(template_data)
# Result: score=92, ready for generation

# 5. Generate prompts
prompts = await generator.generate_prompts_from_template(template_data)

# 6. Validate prompts
prompts_validation = PromptsValidator.validate_prompts(prompts)
# Result: score=95, ready for scenario creation
```

## Benefits

✅ **Quality Assurance**: Ensures templates meet minimum standards
✅ **User Guidance**: Provides actionable suggestions
✅ **Error Prevention**: Catches issues before generation
✅ **Consistency**: Standardized validation across all templates
✅ **Transparency**: Clear scoring and feedback
✅ **Flexibility**: Warnings don't block, errors do
