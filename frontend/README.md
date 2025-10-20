# Scenario Creator React Component

## Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your credentials:
```
REACT_APP_API_BASE=http://localhost:9000
REACT_APP_BEARER_TOKEN=your_actual_bearer_token
REACT_APP_MODULE_ID=your_actual_module_id
```

3. Import and use in your React app:
```jsx
import ScenarioCreator from './ScenarioCreator';

function App() {
  return <ScenarioCreator />;
}
```

## Workflow with Validation

### Step 1: Input Scenario
- Enter template name
- Describe training scenario
- Click "Analyze & Create Template"
- Calls `/analyze-scenario-enhanced` API
- **Auto-validates** extracted template data

### Step 2: Edit & Validate Template
- **Real-time Validation Score** (0-100)
- Shows issues (blocking) and warnings (non-blocking)
- **Completeness Checklist**:
  - ✅ Context Overview (title, description)
  - ✅ Knowledge Base (conversation topics, facts)
  - ✅ Learning Objectives
  - ✅ Archetype Classification
- Edit all template fields
- Validation updates as you edit
- "Save Template" - saves changes
- "Generate Prompts" - only enabled when validation passes

### Step 3: Review Generated Prompts
- Shows all 3 mode prompts (learn, try, assess)
- Shows generated personas with archetype-specific fields
- Review persona details (objection_library, defensive_mechanisms, etc.)
- Click "Create Scenario with 3 Avatars"

### Step 4: Success
- Shows created scenario ID
- Shows 3 avatar interaction IDs
- Option to create another scenario

## Validation Module

### Template Validation Rules
- **Issues (20 points each)**: Missing title, missing description
- **Warnings (5 points each)**: No conversation topics, no objectives, no archetype

### Validation Score
- 100 = Perfect template
- 80-99 = Good with minor warnings
- 60-79 = Needs improvement
- <60 = Critical issues

### Completeness Check
- Context: Title + Description required
- Knowledge: Conversation topics recommended
- Objectives: Primary objectives recommended
- Archetype: Auto-classified (informational)

## API Flow

1. `POST /analyze-scenario-enhanced` → Get template_id + template_data + **validate**
2. User edits → **Real-time validation**
3. `PUT /templates/{template_id}` → Save edited template
4. `POST /generate-prompts-from-template` → Generate personas + prompts
5. User reviews prompts and personas
6. `POST /avatar-interactions` (x3) → Create 3 avatars with preset
7. `POST /scenarios` → Create scenario with avatars + archetype data

## Features

✅ Real-time validation with scoring
✅ Completeness checklist
✅ Separate prompt generation step
✅ Review generated prompts before creating scenario
✅ View persona details with archetype-specific fields
✅ Archetype classification display
✅ Error handling with user-friendly messages
