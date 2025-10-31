# Frontend V2 Integration - Quick Start Guide

## For Developers Starting V2 Frontend Work

---

## Current Flow (V1) - What Works Now

```
1. AiScenarioBuilder → User enters title, description, uploads image
   ↓ API: POST /analyze-scenario-enhanced
   ↓ Stores: template_id in session

2. EditDocument → User edits hardcoded V1 sections
   ↓ Sections: General Info, Knowledge Base, Feedback, Context, Success Metrics
   ↓ API: PUT /update-template-in-db/{template_id}
   ↓ API: POST /generate-final-prompts
   ↓ Stores: scenarioResponse (learn/try/assess prompts)

3. DocumentUploadFlow → User uploads PDFs and videos
   ↓ API: POST /uploads/
   ↓ Stores: Document[], Video[]

4. PersonaSelection → User selects pre-created personas
   ↓ API: GET /personas/
   ↓ Stores: PersonaSelection[]

5. LVESelection → User configures Language/Voice/Environment
   ↓ Creates 3 avatar interactions (learn, try, assess)
   ↓ API: POST /avatar-interactions/ (3x)
   ↓ API: POST /modules/{moduleId}/scenarios
   ↓ Result: Scenario created with 3 modes
```

---

## What Needs to Change for V2

### **Critical Changes**

1. **EditDocument.jsx** - Must support V2 dynamic sections
2. **PersonaSelection.jsx** - Replace with PersonaGeneration.jsx
3. **LVESelection.jsx** - Link V2 personas to avatar interactions

### **New Components Needed**

1. **ModeDescriptionEditor.jsx** - Edit mode methodology
2. **PersonaTypeEditor.jsx** - Edit persona types
3. **DomainKnowledgeEditor.jsx** - Edit domain knowledge
4. **CoachingRulesEditor.jsx** - Edit coaching rules
5. **EvaluationCriteriaEditor.jsx** - Edit evaluation criteria
6. **PersonaGeneration.jsx** - Generate personas from template
7. **PersonaEditor.jsx** - Edit generated personas

---

## V2 Template Structure - What You'll Work With

```javascript
{
  // V1 sections (still present)
  general_info: { ... },
  feedback_mechanism: { ... },
  context_overview: { ... },
  
  // NEW V2 sections
  mode_descriptions: {
    learn_mode: {
      objective: "",
      methodology: ["step1", "step2"],
      success_indicators: [],
      interaction_style: ""
    },
    try_mode: { ... },
    assess_mode: { ... }
  },
  
  persona_types: {
    learn_mode: [
      {
        type_name: "Expert Trainer",
        archetype: "Mentor",
        core_characteristics: [],
        behavioral_patterns: [],
        communication_style: "",
        expertise_areas: []
      }
    ],
    try_mode: [ ... ],
    assess_mode: [ ... ]
  },
  
  domain_knowledge: {
    subject_matter: {
      industry: "",
      domain: "",
      specialization: ""
    },
    key_concepts: [],
    terminology: [],
    best_practices: [],
    common_pitfalls: []
  },
  
  coaching_rules: {
    guidance_principles: [],
    correction_patterns: [
      {
        trigger: "",
        response: ""
      }
    ],
    encouragement_strategies: [],
    feedback_timing: ""
  },
  
  evaluation_criteria: [
    {
      criterion_name: "",
      weight: 0.3,
      description: "",
      scoring_rubric: [
        { level: "Excellent", score: 5, description: "" }
      ],
      measurement_method: ""
    }
  ]
}
```

---

## V2 Persona Structure - What Gets Generated

```javascript
{
  name: "Dr. Sarah Mitchell",
  age: 45,
  gender: "female",
  mode: "learn_mode",
  persona_type: "Expert Trainer",
  
  // Dynamic categories (varies by scenario)
  detail_categories: {
    professional_background: {
      title: "Senior Medical Director",
      experience_years: 20,
      specialization: "Pharmaceutical Sales Training"
    },
    time_constraints: {
      availability: "Flexible schedule",
      session_duration: "45-60 minutes"
    },
    medical_philosophy: {
      approach: "Evidence-based practice",
      priorities: ["Patient safety", "Efficacy"]
    }
  },
  
  archetype: {
    primary: "Mentor",
    secondary: "Expert",
    traits: ["Supportive", "Knowledgeable"]
  },
  
  conversation_rules: {
    tone: "Professional yet approachable",
    language_style: "Clear medical terminology",
    interaction_patterns: ["Ask probing questions", "Provide examples"]
  }
}
```

---

## Key Files to Modify

### **1. EditDocument.jsx** (MAJOR CHANGES)

**Current Code:**
```javascript
// Hardcoded sidebar
<div onClick={() => setSelected("General Info")}>General Info</div>
<div onClick={() => setSelected("Knowledge Base")}>Knowledge Base</div>
```

**Required Code:**
```javascript
// Dynamic sidebar based on template version
const getSections = () => {
  if (templateData.version === "v2") {
    return [
      "general_info",
      "mode_descriptions",
      "persona_types",
      "domain_knowledge",
      "coaching_rules",
      "evaluation_criteria",
      "feedback_mechanism",
      "context_overview"
    ]
  }
  return ["general_info", "knowledge_base", "feedback", "context", "success_metrics"]
}

{getSections().map(section => (
  <div onClick={() => setSelected(section)}>
    {formatSectionName(section)}
  </div>
))}
```

**Current Content Rendering:**
```javascript
{selected === "General Info" && 
  Object.entries(General || {}).map(([key, value]) => (
    <input value={value} onChange={...} />
  ))
}
```

**Required Content Rendering:**
```javascript
{selected === "mode_descriptions" && 
  <ModeDescriptionEditor 
    data={templateData.mode_descriptions}
    onChange={(updated) => setTemplateData({...templateData, mode_descriptions: updated})}
  />
}

{selected === "persona_types" && 
  <PersonaTypeEditor 
    data={templateData.persona_types}
    onChange={(updated) => setTemplateData({...templateData, persona_types: updated})}
  />
}
```

---

### **2. Create PersonaGeneration.jsx** (NEW FILE)

**Location:** `src/Pages/AvatarCreation/PersonaGeneration.jsx`

**Basic Structure:**
```javascript
import React, { useState, useEffect } from 'react'
import axios from '../../service'
import { getSessionStorage } from '../../sessionHelper'

function PersonaGeneration() {
  const [templateData, setTemplateData] = useState(null)
  const [generatedPersonas, setGeneratedPersonas] = useState({})
  const [loading, setLoading] = useState({})
  
  useEffect(() => {
    // Load template from session
    const template = getSessionStorage("templateResponse")
    setTemplateData(template)
  }, [])
  
  const handleGeneratePersona = async (mode, personaType) => {
    setLoading(prev => ({ ...prev, [`${mode}_${personaType.type_name}`]: true }))
    
    try {
      const response = await axios.post('/personas/generate-v2', {
        template_data: templateData,
        mode: mode,
        persona_type: personaType.type_name,
        gender: "male", // TODO: Add gender selector
        custom_prompt: "" // TODO: Add custom prompt input
      })
      
      setGeneratedPersonas(prev => ({
        ...prev,
        [mode]: response.data
      }))
    } catch (error) {
      console.error("Persona generation failed:", error)
    } finally {
      setLoading(prev => ({ ...prev, [`${mode}_${personaType.type_name}`]: false }))
    }
  }
  
  return (
    <div>
      <h2>Generate Personas</h2>
      {templateData?.persona_types && 
        Object.entries(templateData.persona_types).map(([mode, types]) => (
          <div key={mode}>
            <h3>{mode.replace('_', ' ').toUpperCase()}</h3>
            {types.map(personaType => (
              <div key={personaType.type_name}>
                <h4>{personaType.type_name}</h4>
                <p>Archetype: {personaType.archetype}</p>
                <button 
                  onClick={() => handleGeneratePersona(mode, personaType)}
                  disabled={loading[`${mode}_${personaType.type_name}`]}
                >
                  {loading[`${mode}_${personaType.type_name}`] 
                    ? "Generating..." 
                    : "Generate Persona"}
                </button>
                
                {generatedPersonas[mode] && (
                  <PersonaPreview persona={generatedPersonas[mode]} />
                )}
              </div>
            ))}
          </div>
        ))
      }
    </div>
  )
}

export default PersonaGeneration
```

---

### **3. Update LVESelection.jsx** (MINOR CHANGES)

**Current Code:**
```javascript
const learnPayload = {
  system_prompt: getSessionStorage("scenarioResponse").learn_mode,
  mode: "learn_mode"
}
```

**Required Code:**
```javascript
const learnPayload = {
  system_prompt: getSessionStorage("scenarioResponse").learn_mode,
  mode: "learn_mode",
  persona_id: getSessionStorage("generatedPersonas").learn_mode.id, // NEW
  template_version: "v2" // NEW
}
```

---

## API Endpoints You'll Use

### **1. Generate V2 Persona**
```javascript
POST /personas/generate-v2
Body: {
  template_data: { ... },
  mode: "learn_mode",
  persona_type: "Expert Trainer",
  gender: "male",
  custom_prompt: ""
}
Response: {
  name: "Dr. Sarah Mitchell",
  detail_categories: { ... },
  archetype: { ... },
  conversation_rules: { ... }
}
```

### **2. Save V2 Persona**
```javascript
POST /personas/
Body: { ...PersonaInstanceV2 }
Response: { id: "uuid", ... }
```

### **3. Load Template (V1 or V2)**
```javascript
GET /load-template-from-db/{template_id}
Response: {
  template_data: { ... },
  version: "v2",
  name: "Template Name"
}
```

---

## Session Storage Keys for V2

```javascript
// Existing keys (keep these)
"template_id"           // Template UUID
"scenarioData"          // Form data from AI builder
"scenarioResponse"      // Generated prompts
"Layout"                // Layout number (1, 2, 3)
"Document"              // Document IDs array
"Video"                 // Video IDs array

// NEW keys for V2
"templateVersion"       // "v1" or "v2"
"generatedPersonas"     // { learn_mode: {...}, try_mode: {...}, assess_mode: {...} }
"personaIds"            // { learn_mode: "uuid", try_mode: "uuid", assess_mode: "uuid" }
```

---

## Component File Structure

```
src/
├── Pages/
│   ├── Course/
│   │   ├── AIScenario/
│   │   │   ├── AiScenarioBuilder.jsx (minor changes)
│   │   │   ├── EditDocument/
│   │   │   │   ├── EditDocument.jsx (MAJOR CHANGES)
│   │   │   │   ├── ModeDescriptionEditor.jsx (NEW)
│   │   │   │   ├── PersonaTypeEditor.jsx (NEW)
│   │   │   │   ├── DomainKnowledgeEditor.jsx (NEW)
│   │   │   │   ├── CoachingRulesEditor.jsx (NEW)
│   │   │   │   └── EvaluationCriteriaEditor.jsx (NEW)
│   │   ├── LVESelection/
│   │   │   └── LVESelection.jsx (minor changes)
│   ├── AvatarCreation/
│   │   ├── PersonaSelection.jsx (DEPRECATED for V2)
│   │   ├── PersonaGeneration.jsx (NEW)
│   │   └── PersonaEditor.jsx (NEW)
├── Components/
│   ├── PersonaPreview.jsx (NEW)
│   ├── DynamicFieldEditor.jsx (NEW)
│   └── TemplateVersionIndicator.jsx (NEW)
```

---

## Testing Checklist

### **Phase 1: Template Editing**
- [ ] Load V2 template successfully
- [ ] Display all V2 sections in sidebar
- [ ] Edit mode descriptions
- [ ] Edit persona types
- [ ] Edit domain knowledge
- [ ] Edit coaching rules
- [ ] Edit evaluation criteria
- [ ] Save V2 template successfully

### **Phase 2: Persona Generation**
- [ ] Display persona types from template
- [ ] Generate persona for learn_mode
- [ ] Generate persona for try_mode
- [ ] Generate persona for assess_mode
- [ ] Preview generated persona
- [ ] Edit generated persona
- [ ] Save persona to personas_v2 collection

### **Phase 3: Integration**
- [ ] Create avatar interactions with V2 personas
- [ ] Create scenario with V2 template
- [ ] Assign scenario to users
- [ ] Verify scenario works in user app

---

## Common Pitfalls to Avoid

1. **Don't break V1 flow** - Always check template version before rendering
2. **Don't hardcode sections** - Use dynamic rendering for V2
3. **Don't forget validation** - V2 has required fields
4. **Don't skip error handling** - Persona generation can fail
5. **Don't forget session cleanup** - Clear V2 data after scenario creation

---

## Debugging Tips

### **Check Template Version**
```javascript
console.log("Template version:", templateData.version)
console.log("Has mode_descriptions:", !!templateData.mode_descriptions)
console.log("Has persona_types:", !!templateData.persona_types)
```

### **Check Generated Personas**
```javascript
console.log("Generated personas:", getSessionStorage("generatedPersonas"))
console.log("Persona IDs:", getSessionStorage("personaIds"))
```

### **Check API Responses**
```javascript
axios.post('/personas/generate-v2', payload)
  .then(res => console.log("Persona generated:", res.data))
  .catch(err => console.error("Generation failed:", err.response?.data))
```

---

## Quick Commands

### **Start Development Server**
```bash
cd migoto-krithick
npm run dev
```

### **Check Current Flow**
```javascript
// In browser console
console.log("Current flow:", localStorage.getItem("flow"))
console.log("Template ID:", sessionStorage.getItem("template_id"))
console.log("Template data:", sessionStorage.getItem("templateResponse"))
```

### **Clear Session Storage**
```javascript
// In browser console
sessionStorage.clear()
localStorage.removeItem("flow")
```

---

## Need Help?

1. **Check backend docs:** `FRONTEND_SCENARIO_FLOW_ANALYSIS.md`
2. **Check integration plan:** `FRONTEND_V2_INTEGRATION_PLAN.md`
3. **Check API docs:** `PERSONA_V2_INTEGRATION_COMPLETE.md`
4. **Check V2 structure:** `extraction_v2_output.json`

---

## Next Steps

1. **Read** `FRONTEND_SCENARIO_FLOW_ANALYSIS.md` for complete flow understanding
2. **Review** `FRONTEND_V2_INTEGRATION_PLAN.md` for detailed implementation plan
3. **Start** with Phase 1: Add template version detection
4. **Create** `TemplateVersionIndicator` component
5. **Test** with existing V1 scenarios to ensure no breakage
