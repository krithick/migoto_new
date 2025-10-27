# Extraction System Structure Discovery

## Current Extraction Location

**File**: `scenario_generator.py`
**Function**: `extract_scenario_info()` (line 907)
**Class**: `EnhancedScenarioGenerator`

## Current Extraction Flow

1. **Input**: `scenario_document` (text from uploaded files or user input)
2. **Processing**: 
   - Cleans document with `_clean_document_for_llm()`
   - Sends to Azure OpenAI with detailed extraction prompt
   - Parses JSON response
   - Classifies archetype using `ArchetypeClassifier`
   - Injects archetype-specific fields
3. **Output**: `template_data` dictionary with structure:
   - `general_info`
   - `context_overview`
   - `persona_definitions`
   - `dialogue_flow`
   - `knowledge_base`
   - `variations_challenges`
   - `success_metrics`
   - `feedback_mechanism`
   - `coaching_rules`
   - `archetype_classification`

## Current Folder Structure

```
migoto_new/
├── core/
│   ├── scenario_generator_v2_methods.py (v2 persona methods)
│   ├── persona_generator_v2.py (v2 persona generation)
│   ├── prompt_generator_v2.py (v2 prompt generation)
│   ├── detail_category_library.py (v2 persona categories)
│   ├── archetype_classifier.py (existing archetype system)
│   ├── document_processor.py (document processing)
│   ├── azure_search_manager.py (vector search)
│   └── ... (40+ other core files)
├── models/
│   ├── persona_models.py (v2 models added)
│   └── ... (20+ other model files)
├── services/
│   └── ... (service integrations)
└── scenario_generator.py (main file with extract_scenario_info)
```

## Existing Extraction Features

### What's Currently Extracted:
- ✅ General scenario info (domain, title, purpose)
- ✅ Persona definitions (learn/assess mode characters)
- ✅ Knowledge base (dos, donts, key facts, conversation topics)
- ✅ Dialogue flow and initial prompts
- ✅ Feedback mechanisms (positive/negative closings)
- ✅ Archetype classification (PERSUASION, CONFRONTATION, etc.)
- ✅ Archetype-specific fields (objections, decision criteria, etc.)
- ✅ Coaching rules (basic structure)
- ✅ Evaluation metrics (via separate function)

### What's Missing (from EXTRACTION_IMPROVEMENTS_GUIDE.md):
- ❌ Mode descriptions (learn/assess/try what happens)
- ❌ Persona TYPES vs instances (currently extracts specific instances)
- ❌ Methodology extraction (IMPACT, SPIN, etc. - partially done in conversation_topics)
- ❌ Domain knowledge structure (methodology steps, subject matter)
- ❌ Evaluation criteria (what to evaluate, scoring weights, common mistakes)
- ❌ Coaching rules (when to coach, what to catch, correction patterns)
- ❌ Multi-pass extraction (currently single LLM call)

## Implementation Plan

### Step 1: Create ScenarioExtractorV2
**File**: `core/scenario_extractor_v2.py`
- 4-pass parallel extraction system
- Extract mode descriptions
- Extract persona TYPES (not instances)
- Extract domain knowledge structure
- Extract evaluation criteria
- Extract coaching rules

### Step 2: Add V2 Function
**File**: `scenario_generator.py`
- ADD `extract_scenario_info_v2()` function (don't replace v1)
- Call ScenarioExtractorV2
- Add fallback to v1 if v2 fails

### Step 3: Test
- Test with sample document
- Compare v1 vs v2 output
- Verify fallback works

## Key Insights

1. **Existing OpenAI Client**: Use `azure_openai_client` from scenario_generator.py
2. **Existing Archetype System**: Keep and integrate with v2
3. **Existing Coaching Rules**: Enhance, don't replace
4. **Database**: MongoDB with async Motor driver
5. **API Pattern**: FastAPI with async/await

## Next Steps

1. ✅ Read guides (DONE)
2. ✅ Discover structure (DONE)
3. ⏳ Create scenario_extractor_v2.py
4. ⏳ Add extract_scenario_info_v2() function
5. ⏳ Test extraction
