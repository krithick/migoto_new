# Frontend V2 Integration Plan

## Executive Summary

The current frontend scenario creation flow is built exclusively for **V1 template format**. To support the new **V2 extraction system** with dynamic personas, we need significant updates across multiple components.

---

## Current State vs V2 Requirements

### **Current V1 Flow**
```
AI Builder → Edit V1 Template → Upload Media → Select Personas → Configure LVE → Create Scenario
```

### **Required V2 Flow**
```
AI Builder → Edit V2 Template → Generate Personas → Upload Media → Configure LVE → Create Scenario
```

---

## Key Differences: V1 vs V2

| Aspect | V1 (Current) | V2 (Required) |
|--------|--------------|---------------|
| **Template Structure** | Fixed sections (general_info, knowledge_base, etc.) | Dynamic sections (mode_descriptions, persona_types, domain_knowledge, coaching_rules, evaluation_criteria) |
| **Persona Handling** | Pre-created personas from database | Generated dynamically from template persona_types |
| **Mode Descriptions** | Not present | Detailed methodology for each mode |
| **Evaluation** | Simple KPIs | Weighted criteria with scoring rubrics |
| **Coaching** | Not present | Correction patterns and guidance rules |
| **Detail Categories** | Fixed fields (role, background, traits) | Dynamic categories (time_constraints, professional_context, etc.) |

---

## Critical Components Requiring Updates

### **1. AiScenarioBuilder.jsx** ✅ (Minor Changes)
**Current:** Calls `/analyze-scenario-enhanced` and stores `template_id`

**Required Changes:**
- Add version indicator in UI (V1 vs V2)
- Store template version in session storage
- No major changes needed (backend handles V2 extraction)

**Priority:** LOW
**Effort:** 1-2 hours

---

### **2. EditDocument.jsx** 🔴 (Major Overhaul)
**Current:** Hardcoded sidebar with V1 sections

**Required Changes:**

#### **A. Dynamic Sidebar Generation**
```javascript
// Current (Hardcoded)
<div onClick={() => setSelected("General Info")}>General Info</div>
<div onClick={() => setSelected("Knowledge Base")}>Knowledge Base</div>
<div onClick={() => setSelected("Feedback")}>Feedback</div>

// Required (Dynamic)
{Object.keys(templateData).map(section => (
  <div onClick={() => setSelected(section)}>
    {formatSectionName(section)}
  </div>
))}
```

#### **B. Mode Descriptions Editor**
```javascript
// New section for V2
{selected === "mode_descriptions" && (
  <div>
    {["learn_mode", "try_mode", "assess_mode"].map(mode => (
      <ModeDescriptionEditor 
        mode={mode}
        data={templateData.mode_descriptions[mode]}
        onChange={(updated) => updateModeDescription(mode, updated)}
      />
    ))}
  </div>
)}
```

**New Component:** `ModeDescriptionEditor.jsx`
```javascript
// Fields to edit:
- objective
- methodology (array of steps)
- success_indicators (array)
- interaction_style
```

#### **C. Persona Types Editor**
```javascript
// New section for V2
{selected === "persona_types" && (
  <div>
    {Object.entries(templateData.persona_types).map(([mode, personas]) => (
      <PersonaTypeEditor
        mode={mode}
        personas={personas}
        onChange={(updated) => updatePersonaTypes(mode, updated)}
      />
    ))}
  </div>
)}
```

**New Component:** `PersonaTypeEditor.jsx`
```javascript
// For each persona type:
- type_name
- archetype
- core_characteristics (array)
- behavioral_patterns (array)
- communication_style
- expertise_areas (array)
```

#### **D. Domain Knowledge Editor**
```javascript
// Enhanced version of current Knowledge Base
{selected === "domain_knowledge" && (
  <DomainKnowledgeEditor
    data={templateData.domain_knowledge}
    onChange={(updated) => updateDomainKnowledge(updated)}
  />
)}
```

**New Component:** `DomainKnowledgeEditor.jsx`
```javascript
// Sections:
- subject_matter (nested object with multiple fields)
- key_concepts (array)
- terminology (array)
- best_practices (array)
- common_pitfalls (array)
```

#### **E. Coaching Rules Editor**
```javascript
// New section for V2
{selected === "coaching_rules" && (
  <CoachingRulesEditor
    data={templateData.coaching_rules}
    onChange={(updated) => updateCoachingRules(updated)}
  />
)}
```

**New Component:** `CoachingRulesEditor.jsx`
```javascript
// Fields:
- guidance_principles (array)
- correction_patterns (array of objects with trigger/response)
- encouragement_strategies (array)
- feedback_timing
```

#### **F. Evaluation Criteria Editor**
```javascript
// New section for V2
{selected === "evaluation_criteria" && (
  <EvaluationCriteriaEditor
    data={templateData.evaluation_criteria}
    onChange={(updated) => updateEvaluationCriteria(updated)}
  />
)}
```

**New Component:** `EvaluationCriteriaEditor.jsx`
```javascript
// For each criterion:
- criterion_name
- weight (percentage)
- description
- scoring_rubric (array of levels)
- measurement_method
```

**Priority:** HIGH
**Effort:** 40-60 hours

---

### **3. PersonaSelection.jsx** 🔴 (Complete Replacement)
**Current:** Displays pre-created personas from database

**Required Changes:**

#### **Replace with PersonaGeneration.jsx**
```javascript
// New flow:
1. Display persona_types from template
2. For each persona type, show "Generate Persona" button
3. Call PersonaGeneratorV2 API
4. Display generated persona with dynamic categories
5. Allow editing of generated persona
6. Save to personas_v2 collection
```

**New Component:** `PersonaGeneration.jsx`
```javascript
const PersonaGeneration = () => {
  const [personaTypes, setPersonaTypes] = useState([])
  const [generatedPersonas, setGeneratedPersonas] = useState({})
  
  // Load persona types from template
  useEffect(() => {
    const template = getSessionStorage("templateResponse")
    setPersonaTypes(template.persona_types)
  }, [])
  
  // Generate persona for specific type
  const handleGeneratePersona = async (mode, personaType) => {
    const response = await axios.post('/personas/generate-v2', {
      template_data: getSessionStorage("templateResponse"),
      mode: mode,
      persona_type: personaType.type_name,
      gender: selectedGender,
      custom_prompt: customPrompt
    })
    
    setGeneratedPersonas(prev => ({
      ...prev,
      [`${mode}_${personaType.type_name}`]: response.data
    }))
  }
  
  return (
    <div>
      {Object.entries(personaTypes).map(([mode, types]) => (
        <ModeSection mode={mode}>
          {types.map(personaType => (
            <PersonaTypeCard
              type={personaType}
              onGenerate={() => handleGeneratePersona(mode, personaType)}
              generatedPersona={generatedPersonas[`${mode}_${personaType.type_name}`]}
            />
          ))}
        </ModeSection>
      ))}
    </div>
  )
}
```

**New Component:** `PersonaTypeCard.jsx`
```javascript
// Display:
- Persona type name
- Archetype
- Core characteristics
- "Generate Persona" button
- Generated persona preview (if generated)
- Edit button for generated persona
```

**New Component:** `PersonaEditor.jsx`
```javascript
// Edit generated persona:
- Basic info (name, age, gender)
- Dynamic detail categories (rendered from persona.detail_categories)
- Archetype classification
- Conversation rules
- Save to personas_v2 collection
```

**Priority:** HIGH
**Effort:** 30-40 hours

---

### **4. LVESelection.jsx** ⚠️ (Moderate Changes)
**Current:** Creates 3 avatar interactions with V1 prompts

**Required Changes:**

#### **A. Update Avatar Interaction Payload**
```javascript
// Current
const payload = {
  system_prompt: scenarioResponse.learn_mode, // V1 prompt
  mode: "learn_mode"
}

// Required
const payload = {
  system_prompt: scenarioResponse.learn_mode, // V2 prompt (already generated)
  mode: "learn_mode",
  persona_id: generatedPersonas.learn_mode.id, // Link to V2 persona
  template_version: "v2" // Version indicator
}
```

#### **B. Validate V2 Personas**
```javascript
// Before creating avatar interactions, ensure personas are generated
const validatePersonas = () => {
  const requiredModes = ["learn_mode", "try_mode", "assess_mode"]
  for (const mode of requiredModes) {
    if (!generatedPersonas[mode]) {
      throw new Error(`Persona not generated for ${mode}`)
    }
  }
}
```

**Priority:** MEDIUM
**Effort:** 4-6 hours

---

### **5. New Components Required**

#### **A. TemplateVersionIndicator.jsx**
```javascript
// Display template version badge
<Badge color={isV2 ? "blue" : "gray"}>
  {isV2 ? "V2 Template" : "V1 Template"}
</Badge>
```

#### **B. DynamicFieldEditor.jsx**
```javascript
// Generic component for editing nested objects/arrays
const DynamicFieldEditor = ({ data, schema, onChange }) => {
  // Recursively render fields based on data type
  // Support: string, number, array, object
}
```

#### **C. PersonaPreview.jsx**
```javascript
// Preview generated persona with all dynamic categories
const PersonaPreview = ({ persona }) => {
  return (
    <div>
      <h3>{persona.name}</h3>
      <p>Archetype: {persona.archetype}</p>
      {Object.entries(persona.detail_categories).map(([category, details]) => (
        <CategorySection category={category} details={details} />
      ))}
    </div>
  )
}
```

#### **D. MigrationTool.jsx**
```javascript
// Tool to convert V1 templates to V2
const MigrationTool = ({ templateId }) => {
  const handleMigrate = async () => {
    await axios.post(`/templates/${templateId}/migrate-to-v2`)
    // Reload template
  }
  
  return <Button onClick={handleMigrate}>Migrate to V2</Button>
}
```

---

## Implementation Phases

### **Phase 1: Foundation (Week 1-2)**
**Goal:** Support both V1 and V2 templates without breaking existing functionality

**Tasks:**
1. Add template version detection in `EditDocument.jsx`
2. Create `TemplateVersionIndicator` component
3. Update session storage to include version
4. Add V2 API endpoints to service layer
5. Create base components: `DynamicFieldEditor`, `PersonaPreview`

**Deliverables:**
- V1 templates continue to work
- V2 templates load but show "Coming Soon" message
- Version indicator visible in UI

---

### **Phase 2: Template Editing (Week 3-5)**
**Goal:** Enable editing of V2 template sections

**Tasks:**
1. Create `ModeDescriptionEditor` component
2. Create `PersonaTypeEditor` component
3. Create `DomainKnowledgeEditor` component
4. Create `CoachingRulesEditor` component
5. Create `EvaluationCriteriaEditor` component
6. Update `EditDocument.jsx` to render V2 sections dynamically
7. Update save logic to handle V2 structure

**Deliverables:**
- Full V2 template editing capability
- All V2 sections editable
- Save/load works for V2

---

### **Phase 3: Persona Generation (Week 6-7)**
**Goal:** Replace persona selection with persona generation

**Tasks:**
1. Create `PersonaGeneration.jsx` component
2. Create `PersonaTypeCard.jsx` component
3. Create `PersonaEditor.jsx` component
4. Integrate PersonaGeneratorV2 API
5. Update navigation flow to skip old PersonaSelection
6. Add persona validation before LVE selection

**Deliverables:**
- Dynamic persona generation from template
- Editable generated personas
- Personas saved to personas_v2 collection

---

### **Phase 4: Integration & Testing (Week 8)**
**Goal:** Complete end-to-end V2 flow

**Tasks:**
1. Update `LVESelection.jsx` to use V2 personas
2. Add V2 validation throughout flow
3. Create migration tool for V1 → V2
4. Comprehensive testing of V2 flow
5. Update documentation

**Deliverables:**
- Complete V2 scenario creation flow
- Migration tool for existing scenarios
- Updated user documentation

---

## API Integration Points

### **New API Calls Required**

```javascript
// 1. Generate V2 Persona
POST /personas/generate-v2
Body: {
  template_data: {},
  mode: "learn_mode",
  persona_type: "Expert Trainer",
  gender: "male",
  custom_prompt: ""
}
Response: PersonaInstanceV2

// 2. Save V2 Persona
POST /personas/
Body: PersonaInstanceV2
Response: { id, ... }

// 3. Load V2 Template
GET /load-template-from-db/{template_id}
Response: {
  template_data: V2Structure,
  version: "v2"
}

// 4. Update V2 Template
PUT /update-template-in-db/{template_id}
Body: {
  template_data: V2Structure,
  template_name: ""
}

// 5. Generate V2 Prompts
POST /generate-final-prompts
Body: V2Structure
Response: {
  learn_mode: "",
  try_mode: "",
  assess_mode: ""
}
```

---

## UI/UX Considerations

### **1. Version Indicator**
- Clear badge showing V1 vs V2
- Tooltip explaining differences
- Migration button for V1 templates

### **2. Dynamic Sections**
- Collapsible sections for better organization
- Search/filter for large templates
- Validation indicators for required fields

### **3. Persona Generation**
- Loading states during generation
- Preview before saving
- Regenerate option if unsatisfied
- Gender selection UI
- Custom prompt textarea

### **4. Error Handling**
- Clear error messages for V2 validation failures
- Fallback to V1 if V2 generation fails
- Retry mechanisms for API failures

### **5. Progressive Disclosure**
- Show basic fields first
- "Advanced" toggle for detailed editing
- Tooltips explaining V2 concepts

---

## Testing Strategy

### **Unit Tests**
- Component rendering for V2 data
- Dynamic field editor logic
- Persona generation flow
- Template version detection

### **Integration Tests**
- Complete V2 scenario creation flow
- V1 → V2 migration
- Persona generation and editing
- Avatar interaction creation with V2 data

### **User Acceptance Tests**
- Create V2 scenario from scratch
- Edit existing V2 template
- Generate and customize personas
- Complete scenario with V2 flow

---

## Risk Mitigation

### **Risk 1: Breaking Existing V1 Flow**
**Mitigation:** 
- Maintain separate code paths for V1 and V2
- Extensive regression testing
- Feature flag for V2 features

### **Risk 2: Complex V2 UI**
**Mitigation:**
- Progressive disclosure
- Guided wizard for first-time users
- Video tutorials

### **Risk 3: API Failures**
**Mitigation:**
- Graceful degradation
- Local caching of generated data
- Retry mechanisms

### **Risk 4: Performance Issues**
**Mitigation:**
- Lazy loading of sections
- Pagination for large arrays
- Debounced API calls

---

## Success Metrics

1. **Functionality:** 100% of V2 features accessible in UI
2. **Compatibility:** V1 scenarios continue to work without issues
3. **Performance:** V2 scenario creation < 30 seconds
4. **Usability:** Users can create V2 scenario without documentation
5. **Adoption:** 80% of new scenarios use V2 within 1 month

---

## Estimated Timeline

| Phase | Duration | Team Size | Total Hours |
|-------|----------|-----------|-------------|
| Phase 1: Foundation | 2 weeks | 2 devs | 160 hours |
| Phase 2: Template Editing | 3 weeks | 2 devs | 240 hours |
| Phase 3: Persona Generation | 2 weeks | 2 devs | 160 hours |
| Phase 4: Integration & Testing | 1 week | 3 devs | 120 hours |
| **Total** | **8 weeks** | **2-3 devs** | **680 hours** |

---

## Next Immediate Steps

1. **Review this plan** with team and stakeholders
2. **Prioritize features** - Which V2 features are MVP?
3. **Assign developers** to each phase
4. **Set up development environment** with V2 backend
5. **Create detailed component specs** for Phase 1
6. **Begin implementation** of TemplateVersionIndicator

---

## Questions to Resolve

1. Should we support editing V1 templates in V2 format?
2. Can users switch between V1 and V2 for same scenario?
3. What happens to existing V1 scenarios - auto-migrate or manual?
4. Should persona generation be optional or mandatory?
5. How to handle partial V2 data (some sections missing)?

---

## Conclusion

The V2 integration requires significant frontend work but provides a much more powerful and flexible scenario creation system. The phased approach ensures we don't break existing functionality while progressively adding V2 capabilities.

**Key Success Factor:** Maintaining backward compatibility with V1 while building robust V2 features.
