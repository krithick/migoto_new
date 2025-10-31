# Frontend Scenario Creation Flow Analysis

## Overview
The frontend scenario creation flow in `migoto-krithick` React application follows a multi-step wizard pattern for creating AI-powered training scenarios with avatar interactions.

---

## Flow Architecture

### Main Entry Points
1. **CreateScenario.jsx** - Root component managing the overall flow
2. **AiScenarioBuilder.jsx** - AI-driven scenario generation interface
3. **EditDocument.jsx** - Template data editing and refinement
4. **DocumentUploadFlow.jsx** - Document/Video upload for Learn Mode
5. **PersonaSelection.jsx** - Persona selection for avatar interactions
6. **LVESelection.jsx** - Language/Voice/Environment configuration

---

## Step-by-Step Flow

### **Step 1: Scenario Creation Mode Selection**
**Component:** `CreateScenario.jsx`

**States:**
- `uploadPage`: Controls which sub-component to display
  - `"Image Upload"` - Traditional manual scenario creation (CourseForm)
  - `"CreateAIScanario"` - AI-powered scenario generation

**User Actions:**
- Click "Create scenario with AI" button → Navigate to AI Scenario Builder
- Or use traditional CourseForm for manual creation

---

### **Step 2: AI Scenario Builder**
**Component:** `AiScenarioBuilder.jsx`

**API Endpoint:** `POST /analyze-scenario-enhanced`

**Form Data Collected:**
```javascript
{
  title: "",              // Scenario title
  description: "",        // Scenario description
  thumbnail_url: "",      // Cover image URL
  supporting_docs: []     // Optional support documents
}
```

**Layout Selection:**
- Radio buttons for Layout 01, 02, or 03
- Stored in `selectedData["Layout"]` and `sessionStorage`

**Process:**
1. User fills scenario title and description
2. Optionally uploads supporting documents via `SupportDocUpload`
3. Uploads cover image (or uses default)
4. Selects layout (1, 2, or 3)
5. Clicks "Generate" button

**Backend Call:**
```javascript
POST /analyze-scenario-enhanced
FormData:
  - scenario_document: description
  - template_name: title
  - supporting_docs: files[]
```

**Response Handling:**
```javascript
// Stores template_id in session and state
setSelectedData("template_id", res.data.template_id)
setSessionStorage("template_id", res.data.template_id)
setSessionStorage("Layout", value)

// Navigate to edit page
navigate("editContent")
setUploadPage("DataEdition")
```

---

### **Step 3: Edit Template Data**
**Component:** `EditDocument.jsx`

**API Endpoints:**
- `GET /load-template-from-db/{template_id}` - Load template
- `POST /add-remove-points` - Add/remove points dynamically
- `PUT /update-template-in-db/{template_id}` - Save changes
- `POST /generate-final-prompts` - Generate mode-specific prompts

**Sidebar Sections:**
1. **General Info** - Basic scenario metadata
2. **Knowledge Base** - Do's, Don'ts, Key Facts, Conversation Topics
3. **Feedback** - Feedback mechanism settings
4. **Context Overview** - Context details
5. **Success Metrics** - KPIs for interaction

**Template Structure (V1 Format):**
```javascript
{
  general_info: {
    scenario_title: "",
    scenario_description: "",
    target_audience: "",
    learning_objectives: ""
  },
  knowledge_base: {
    dos: [],
    donts: [],
    key_facts: [],
    conversation_topics: []
  },
  feedback_mechanism: {
    feedback_type: "",
    feedback_frequency: ""
  },
  context_overview: {
    setting: "",
    situation: ""
  },
  success_metrics: {
    kpis_for_interaction: []
  }
}
```

**User Actions:**
- Edit text fields for General Info, Feedback, Context
- Add/Remove points in Knowledge Base sections using `+` button
- Edit existing points inline
- Click "Save & Upload" to proceed

**Save Process:**
```javascript
// 1. Update template in database
PUT /update-template-in-db/{template_id}
Body: { template_data, template_name }

// 2. Generate final prompts for all modes
POST /generate-final-prompts
Body: { ...template_data }

Response: {
  learn_mode: "...",
  try_mode: "...",
  assess_mode: "..."
}

// 3. Store prompts and navigate
setSelectedData("scenarioResponse", res.data)
setSessionStorage("scenarioResponse", res.data)
navigate("/videoPdf")
```

---

### **Step 4: Document & Video Upload**
**Component:** `DocumentUploadFlow.jsx`

**API Endpoints:**
- `GET /documents/` - Fetch available documents
- `GET /videos/` - Fetch available videos
- `POST /uploads/` - Upload new files

**Two-Tab Interface:**
1. **Document & PDF Tab**
   - Upload PDF documents
   - Select from existing documents
   - Stored in `selectedData["Document"]`

2. **Video File Tab**
   - Upload MP4 videos
   - Select from existing videos
   - Stored in `selectedData["Video"]`

**File Upload Process:**
```javascript
// FileCard component handles individual uploads
POST /uploads/
FormData:
  - file: File
  - file_type: "document" | "video"

Response: { id, live_url, ... }
```

**Navigation:**
- "Skip Document >" - Skip to video tab
- "Skip Video >" - Navigate to persona creation
- "< Back" - Return to edit template

**Session Storage:**
```javascript
setSessionStorage("Document", selectedData["Document"])
setSessionStorage("Video", selectedData["Video"])
```

---

### **Step 5: Persona Selection**
**Component:** `PersonaSelection.jsx`

**API Endpoint:** `GET /personas/`

**Features:**
- Display all available personas
- Filter by creator: All, Predefined, Super Admin, Admin, Me
- Click "Create Persona" to build new persona
- Select personas for avatar interactions

**Persona Card Selection:**
- Clicking a persona card stores it in `selectedData["PersonaSelection"]`
- Multiple personas can be selected for different modes

**Navigation:**
- Automatically proceeds to LVE Selection after persona selection

---

### **Step 6: Language, Voice & Environment Selection**
**Component:** `LVESelection.jsx`

**API Endpoints:**
- `GET /languages/` - Fetch available languages
- `GET /bot-voices/` - Fetch bot voices (filtered by language)
- `GET /environments/` - Fetch environments
- `POST /avatar-interactions/` - Create avatar interactions (3x for each mode)
- `POST /modules/{moduleId}/scenarios` - Create final scenario

**Three Sections:**
1. **Language Selection**
   - Select languages for scenario
   - Stored in `selectedData["Language"]` and `localLang`
   - Automatically filters available voices

2. **Voice Selection** (Auto-selected)
   - Voices filtered based on selected languages
   - All matching voices auto-selected
   - Stored in `selectedData["Voice"]`

3. **Environment Selection**
   - Select virtual environments
   - All environments auto-selected by default
   - Stored in `selectedData["Environment"]`

**Final Scenario Creation Process:**

```javascript
// Step 1: Create 3 Avatar Interactions (Learn, Try, Assess)
const modes = ["learn_mode", "try_mode", "assess_mode"]

for each mode:
  POST /avatar-interactions/
  Body: {
    avatars: sessionStorage.avatarSelection,
    languages: localLang,
    bot_voices: selectedData["Voice"],
    environments: selectedData["Environment"],
    layout: sessionStorage.Layout,
    assigned_documents: sessionStorage.Document,
    assigned_videos: sessionStorage.Video,
    system_prompt: scenarioResponse[mode],
    mode: mode,
    bot_role: mode === "learn_mode" ? "trainer" : "employee",
    bot_role_alt: mode === "learn_mode" ? "employee" : "evaluatee"
  }
  
  Response: { id: avatar_interaction_id }

// Step 2: Create Scenario with all 3 interactions
POST /modules/{moduleId}/scenarios
Body: {
  title: scenarioData.title,
  description: scenarioData.description,
  thumbnail_url: scenarioData.thumbnail_url,
  template_id: template_id,
  learn_mode: { avatar_interaction: learn_interaction_id },
  try_mode: { avatar_interaction: try_interaction_id },
  assess_mode: { avatar_interaction: assess_interaction_id }
}

Response: { id: scenario_id }

// Step 3: Assign to Users (if in Create Course flow)
POST /course-assignments/course/{courseId}/assign-with-content
Body: {
  user_ids: [],
  module_ids: [moduleId],
  scenario_mapping: { [moduleId]: [scenario_id] },
  mode_mapping: { [scenario_id]: ["learn_mode", "try_mode", "assess_mode"] }
}
```

---

## Data Flow & State Management

### Zustand Store (`store.js`)
```javascript
useLOIData: {
  selectedData: {
    courseId: "",
    moduleId: "",
    scenarioData: {},
    template_id: "",
    templateResponse: {},
    scenarioResponse: {},
    Layout: 1,
    Document: [],
    Video: [],
    PersonaSelection: [],
    avatarSelection: [],
    Language: [],
    Voice: [],
    Environment: [],
    learn_modeId: "",
    try_modeId: "",
    assess_modeId: "",
    scenarioId: ""
  }
}
```

### Session Storage Keys
```javascript
"template_id"           // Template ID from backend
"scenarioData"          // Form data from AI builder
"scenarioResponse"      // Generated prompts for all modes
"Layout"                // Selected layout (1, 2, or 3)
"Document"              // Array of document IDs
"Video"                 // Array of video IDs
"avatarSelection"       // Selected avatar IDs
"courseId"              // Parent course ID
"moduleId"              // Parent module ID
"createdUser"           // User IDs for assignment
"personaLimit"          // Persona creation limit
```

---

## Flow Variations

### **1. Create Course Flow**
```
Course → Module → Scenario → User Assignment
```
- After scenario creation, shows "Select User" button
- Opens user selection popup
- Assigns course with scenario to selected users
- Navigates to Dashboard

### **2. CourseManagement Flow**
```
Edit Existing Course → Add Scenario
```
- Loads existing courseId and moduleId from session
- After scenario creation, navigates back to CourseManagement
- No user assignment step

### **3. Create User and Course Flow**
```
User Creation → Course → Module → Scenario → Auto-assign
```
- Users already selected before scenario creation
- Auto-assigns after scenario creation
- Navigates to Dashboard

---

## Key Components & Their Roles

| Component | Purpose | Key APIs |
|-----------|---------|----------|
| `CreateScenario.jsx` | Flow orchestrator | None |
| `AiScenarioBuilder.jsx` | Scenario input form | `/analyze-scenario-enhanced` |
| `EditDocument.jsx` | Template editing | `/load-template-from-db`, `/update-template-in-db`, `/generate-final-prompts` |
| `DocumentUploadFlow.jsx` | Media upload | `/documents/`, `/videos/`, `/uploads/` |
| `PersonaSelection.jsx` | Persona selection | `/personas/` |
| `LVESelection.jsx` | Final configuration | `/languages/`, `/bot-voices/`, `/environments/`, `/avatar-interactions/`, `/modules/{id}/scenarios` |

---

## Navigation Routes

```
/migoto-cms/course/createScenario
  → /migoto-cms/course/createScenario/editContent
  → /migoto-cms/course/createScenario/videoPdf
  → /migoto-cms/course/createScenario/personaCreation
  → /migoto-cms/course/createScenario/lveSelection
  → /migoto-cms/dashboard (on completion)
```

---

## Critical Issues & Limitations

### **1. V1 Template Format Only**
- Frontend only handles V1 template structure
- No support for V2 dynamic fields (`mode_descriptions`, `persona_types`, `domain_knowledge`, etc.)
- EditDocument.jsx hardcodes V1 sections

### **2. Hardcoded Persona Handling**
- No dynamic persona generation from template
- Relies on pre-created personas in database
- No integration with PersonaGeneratorV2

### **3. Missing V2 Features**
- No archetype classification display
- No dynamic detail categories
- No coaching rules or evaluation criteria editing
- No methodology steps visualization

### **4. Template Editing Limitations**
- Can only edit predefined sections
- Cannot add new sections dynamically
- No support for nested structures in V2

### **5. Prompt Generation**
- Uses `/generate-final-prompts` which expects V1 format
- No support for V2 persona types or mode descriptions

---

## Recommendations for V2 Integration

### **Phase 1: Backend Compatibility**
1. Update `/analyze-scenario-enhanced` to return V2 format indicator
2. Ensure `/load-template-from-db` returns both V1 and V2 formats
3. Update `/generate-final-prompts` to handle V2 structure

### **Phase 2: Frontend Template Editor**
1. Create dynamic section renderer for V2 fields
2. Add mode descriptions editor
3. Add persona types editor with dynamic categories
4. Add domain knowledge editor
5. Add coaching rules and evaluation criteria editors

### **Phase 3: Persona Integration**
1. Integrate PersonaGeneratorV2 API calls
2. Display generated personas with dynamic categories
3. Allow editing of persona detail categories
4. Show archetype classifications

### **Phase 4: Enhanced UX**
1. Add visual indicators for V1 vs V2 templates
2. Add migration tool for V1 → V2 conversion
3. Add preview mode for generated personas
4. Add validation for V2 required fields

---

## Next Steps for Implementation

1. **Analyze V2 Template Structure** - Map V2 fields to UI components
2. **Design Dynamic Editor** - Create flexible component for V2 sections
3. **Update API Integration** - Modify API calls to support V2
4. **Create Persona Generator UI** - Build interface for V2 persona generation
5. **Testing & Migration** - Test with existing scenarios and provide migration path

---

## Session Storage Cleanup

The flow uses `clearAllData()` and `clearScenarioData()` functions to clean up session storage after scenario creation:

```javascript
// From sessionHelper.js
clearScenarioData() - Removes scenario-specific data
clearAllData() - Removes all creation flow data
```

Called after successful scenario creation to prevent data leakage between flows.
