# Project Structure Discovery - Dynamic Persona System

## 📁 DISCOVERED FOLDER STRUCTURE

```
migoto_new/
├── core/                           ✅ EXISTS - Business logic routers
│   ├── persona.py                  ✅ FOUND - Existing persona endpoints
│   ├── archetype_persona_generator.py  ✅ FOUND - Archetype-based generation
│   └── [40+ other core files]
│
├── models/                         ✅ EXISTS - Pydantic models
│   ├── persona_models.py           ✅ FOUND - Existing persona models
│   ├── archetype_models.py         ✅ FOUND - Archetype models
│   └── [20+ other model files]
│
├── services/                       ✅ EXISTS - External services
│   ├── file_storage.py             ✅ FOUND
│   └── __init__.py
│
├── enhanced_scenario_generator.py  ✅ FOUND - Root level (NOT in services/)
│
└── files/                          ✅ EXISTS - Documentation
    ├── IMPLEMENTATION_GUIDE_FOR_AMAZON_Q.md
    ├── SAFE_IMPLEMENTATION_GUIDE.md
    └── PROJECT_STATUS_SUMMARY.md
```

## 🔍 KEY FINDINGS

### 1. Existing Persona System

**File:** `core/persona.py`
- **Functions Found:**
  - `get_personas()` - List personas
  - `get_persona()` - Get by ID
  - `create_persona()` - Create new persona
  - `generate_persona()` - AI-powered generation (uses Azure OpenAI)
  - `update_persona()` - Update existing
  - `delete_persona()` - Delete persona
  
- **API Endpoints:**
  - `GET /personas/` - List all
  - `GET /personas/{id}` - Get one
  - `POST /personas/` - Create
  - `POST /personas/generate` - AI generate
  - `PUT /personas/{id}` - Update
  - `DELETE /personas/{id}` - Delete

**Current Models:** `models/persona_models.py`
```python
- PersonaBase
- PersonaCreate
- PersonaDB
- PersonaResponse
- PersonaGenerateRequest
- BotGender (Enum)
```

### 2. Archetype System

**File:** `core/archetype_persona_generator.py`
- **Class:** `ArchetypePersonaGenerator`
- **Methods:**
  - `generate_personas()` - Main entry
  - `_generate_persuasion_personas()`
  - `_generate_confrontation_personas()`
  - `_generate_help_seeking_personas()`

**Models:** `models/archetype_models.py`
```python
- EnhancedPersonaDB
- PersonaArchetypeData
- PersuasionPersonaSchema
- ConfrontationPersonaSchema
- HelpSeekingPersonaSchema
- ScenarioArchetype (Enum)
```

### 3. Scenario Generator

**File:** `enhanced_scenario_generator.py` (ROOT LEVEL)
- **Class:** `FlexibleScenarioGenerator`
- **Key Methods:**
  - `flexible_extract_from_document()` - Extract from docs
  - `flexible_extract_from_prompt()` - Extract from prompts
  - `generate_dynamic_scenarios()` - Generate scenarios
  - `simulate_conversation()` - Simulate conversations

### 4. Database Connection

**Pattern Found:**
```python
async def get_database():
    from database import get_db
    return await get_db()
```

### 5. Azure OpenAI Client

**Pattern Found in `core/persona.py`:**
```python
azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)
```

## ⚠️ CRITICAL OBSERVATIONS

### What's Working:
1. ✅ Existing persona system is functional
2. ✅ Archetype system already exists
3. ✅ Azure OpenAI integration working
4. ✅ Database operations use async Motor
5. ✅ FastAPI router pattern established

### What's Missing (for v2 system):
1. ❌ No detail category library
2. ❌ No dynamic persona generation (LLM chooses categories)
3. ❌ No flexible PersonaInstance model
4. ❌ No prompt generator using persona data
5. ❌ No v2 functions alongside v1

## 📋 SAFE IMPLEMENTATION PLAN

### Phase 1: Create NEW Files (No Breaking Changes)

**Where to create:**
```
core/
├── detail_category_library.py      ← NEW (safe)
├── persona_generator_v2.py         ← NEW (safe)
└── prompt_generator_v2.py          ← NEW (safe)

models/
└── persona_models_v2.py            ← NEW (safe, or add to existing)
```

### Phase 2: Add v2 Functions to Existing Files

**File:** `core/persona.py`
- ✅ Keep all existing functions
- ➕ Add `generate_persona_v2()` (NEW function)
- ➕ Add endpoint `/personas/generate-v2` (NEW endpoint)

**File:** `enhanced_scenario_generator.py`
- ✅ Keep all existing methods
- ➕ Add `generate_personas_from_template_v2()` (NEW method)
- ➕ Add `generate_assess_mode_from_template_v2()` (NEW method)

## 🎯 NEXT STEPS

### Step 1: Create Detail Category Library
**File:** `core/detail_category_library.py`
- NEW file, completely safe
- No dependencies on existing code

### Step 2: Create Persona Models v2
**Option A:** Add to `models/persona_models.py` (at bottom)
**Option B:** Create `models/persona_models_v2.py`
- Recommendation: Add to existing file with clear comments

### Step 3: Create Persona Generator v2
**File:** `core/persona_generator_v2.py`
- NEW file, separate from existing
- Uses detail_category_library
- Uses persona_models_v2

### Step 4: Create Prompt Generator v2
**File:** `core/prompt_generator_v2.py`
- NEW file, separate from existing
- Generates prompts from PersonaInstance

### Step 5: Integration (Safe)
**Add to `core/persona.py`:**
```python
# Keep existing generate_persona() function

# Add NEW v2 function
async def generate_persona_v2(...):
    try:
        # Try v2 system
        from core.persona_generator_v2 import PersonaGenerator
        ...
    except Exception as e:
        # Fallback to v1
        return await generate_persona(...)
```

## ✅ SAFETY CHECKLIST

- [x] Found existing folder structure
- [x] Documented existing functions
- [x] Identified integration points
- [x] No files will be replaced
- [x] All new files are separate
- [x] Fallback logic planned
- [x] Existing endpoints remain unchanged

## 🚨 RED FLAGS TO AVOID

❌ DON'T replace `core/persona.py`
❌ DON'T modify existing `generate_persona()` function
❌ DON'T change existing models in `persona_models.py`
❌ DON'T remove any existing endpoints
❌ DON'T modify `archetype_persona_generator.py`

## 📊 COMPARISON: Existing vs V2

### Existing System:
- Single persona generation
- Fixed structure
- No dynamic categories
- Direct prompt creation

### V2 System (To Add):
- Dynamic category selection (LLM decides)
- Flexible persona structure
- 15+ detail categories
- Prompt generation from persona data
- Parallel with v1 (not replacement)

## 🎯 READY TO PROCEED?

**Status:** ✅ Discovery Complete

**Safe to implement:**
1. Detail category library (NEW file)
2. Persona models v2 (ADD to existing)
3. Persona generator v2 (NEW file)
4. Prompt generator v2 (NEW file)
5. Integration functions (ADD to existing)

**Next Action:** Await your approval to proceed with Phase 1
