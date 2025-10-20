# Full Archetype System - Implementation Plan

## Overview
Transform scenario generation from one-size-fits-all to archetype-aware system supporting 5 distinct training patterns.

## Phase 1: Database Setup ✅ COMPLETE

### Collections Created
1. **archetype_definitions** - Master archetype configurations
2. **Enhanced personas collection** - Personas with archetype_data field

### Seed Data
Run on startup:
```python
from core.archetype_definitions import seed_archetype_definitions
await seed_archetype_definitions(db)
```

---

## Phase 2: Update Scenario Generator (NEXT)

### File: `scenario_generator.py`

#### Step 1: Add Archetype Classification
```python
from core.archetype_classifier import ArchetypeClassifier
from core.archetype_extractors import ArchetypeExtractorFactory

async def extract_scenario_info(self, scenario_document: str):
    # 1. Classify archetype
    classifier = ArchetypeClassifier(self.llm_client, self.db)
    classification = await classifier.classify(scenario_document)
    
    # 2. Get archetype definition
    archetype_def = await self.db.archetype_definitions.find_one(
        {"_id": classification.primary_archetype.value.upper()}
    )
    
    # 3. Use archetype-specific extractor
    extractor = ArchetypeExtractorFactory.get_extractor(
        classification.primary_archetype.value.upper(),
        self.llm_client
    )
    template_data = await extractor.extract(scenario_document, archetype_def)
    
    # 4. Add archetype metadata
    template_data["archetype_metadata"] = {
        "archetype": classification.primary_archetype.value,
        "sub_archetype": classification.sub_archetype,
        "conversation_pattern": classification.conversation_pattern.value,
        "persona_schema_type": classification.persona_schema_needed,
        "classification_confidence": classification.confidence,
        "classification_reasoning": classification.reasoning
    }
    
    return template_data
```

#### Step 2: Update Template Storage
```python
# In analyze-template-with-docs endpoint
template_record = {
    "id": str(uuid4()),
    "name": template_name,
    "template_data": template_data,  # Now includes archetype_metadata
    "knowledge_base_id": knowledge_base_id,
    "archetype": template_data["archetype_metadata"]["archetype"],  # NEW: Top-level field
    "sub_archetypes": template_data["archetype_metadata"].get("sub_archetype"),  # NEW
    "created_at": datetime.now().isoformat()
}
```

---

## Phase 3: Multi-Variant Scenario Creation

### File: `core/scenario.py` (or new `core/archetype_scenario_builder.py`)

```python
async def create_scenario_with_archetypes(
    template_id: str,
    scenario_data: Dict,
    db: Any,
    current_user: UserDB
):
    """Create scenario with archetype-aware avatar_interactions"""
    
    # Get template
    template = await db.templates.find_one({"id": template_id})
    archetype_metadata = template["template_data"]["archetype_metadata"]
    archetype = archetype_metadata["archetype"]
    
    # Check if multi-variant scenario
    if archetype == "CONFRONTATION":
        # Create 3 avatar_interactions: PERPETRATOR, VICTIM, BYSTANDER
        avatar_interactions = {}
        
        for sub_type in ["PERPETRATOR", "VICTIM", "BYSTANDER"]:
            ai = await create_avatar_interaction_for_archetype(
                template_data=template["template_data"],
                archetype="CONFRONTATION",
                sub_archetype=sub_type,
                mode="assess_mode",
                db=db,
                current_user=current_user
            )
            avatar_interactions[sub_type] = ai
        
        # Create scenario with variants
        scenario = ScenarioDB(
            title=scenario_data["title"],
            description=scenario_data.get("description"),
            thumbnail_url=scenario_data["thumbnail_url"],
            learn_mode=learn_mode_ai,
            try_mode=try_mode_ai,
            assess_mode=avatar_interactions["PERPETRATOR"]["_id"],  # Default
            template_id=template_id,
            company_id=current_user.company_id,
            created_by=current_user.id
        )
        
        # Store variants in scenario metadata
        scenario.content = {
            "archetype": "CONFRONTATION",
            "assess_mode_variants": [
                {
                    "type": "PERPETRATOR",
                    "avatar_interaction_id": str(avatar_interactions["PERPETRATOR"]["_id"]),
                    "description": "Practice confronting the person who committed bias"
                },
                {
                    "type": "VICTIM",
                    "avatar_interaction_id": str(avatar_interactions["VICTIM"]["_id"]),
                    "description": "Practice supporting the person who experienced bias"
                },
                {
                    "type": "BYSTANDER",
                    "avatar_interaction_id": str(avatar_interactions["BYSTANDER"]["_id"]),
                    "description": "Practice empowering a witness to take action"
                }
            ]
        }
    else:
        # Single avatar_interaction (existing flow)
        scenario = ScenarioDB(...)
    
    await db.scenarios.insert_one(scenario.dict(by_alias=True))
    return scenario


async def create_avatar_interaction_for_archetype(
    template_data: Dict,
    archetype: str,
    sub_archetype: str,
    mode: str,
    db: Any,
    current_user: UserDB
) -> Dict:
    """Create avatar_interaction with archetype metadata"""
    
    # Get appropriate system prompt
    if archetype == "CONFRONTATION":
        if sub_archetype == "PERPETRATOR":
            system_prompt = template_data["persona_definitions"]["perpetrator_persona"]["system_prompt"]
            conversation_pattern = "learner_initiates"
        elif sub_archetype == "VICTIM":
            system_prompt = template_data["persona_definitions"]["victim_persona"]["system_prompt"]
            conversation_pattern = "character_initiates"
        else:  # BYSTANDER
            system_prompt = template_data["persona_definitions"]["bystander_persona"]["system_prompt"]
            conversation_pattern = "character_initiates"
    else:
        system_prompt = template_data.get("assess_mode_description", "")
        conversation_pattern = template_data["archetype_metadata"]["conversation_pattern"]
    
    # Create avatar_interaction
    ai = AvatarInteractionDB(
        system_prompt=system_prompt,
        bot_role=template_data["persona_definitions"][f"{sub_archetype.lower()}_persona"]["role"],
        mode=mode,
        archetype=archetype,  # NEW FIELD
        sub_archetype=sub_archetype,  # NEW FIELD
        conversation_pattern=conversation_pattern,  # NEW FIELD
        avatars=[...],  # From scenario_data
        languages=[...],
        bot_voices=[...],
        environments=[...],
        created_by=current_user.id
    )
    
    result = await db.avatar_interactions.insert_one(ai.dict(by_alias=True))
    ai._id = result.inserted_id
    return ai.dict(by_alias=True)
```

---

## Phase 4: Archetype-Aware Persona Generation

### New Endpoint: `/scenario/generate-archetype-personas`

```python
@router.post("/generate-archetype-personas")
async def generate_archetype_personas(
    template_id: str = Body(...),
    archetype: str = Body(...),
    sub_archetype: Optional[str] = Body(None),
    count: int = Body(default=5),
    complexity: str = Body(default="detailed"),
    db: Any = Depends(get_db)
):
    """Generate personas with archetype-specific details"""
    
    from core.archetype_persona_generator import ArchetypePersonaGenerator
    
    # Get template
    template = await db.templates.find_one({"id": template_id})
    
    # Generate personas
    generator = ArchetypePersonaGenerator(azure_openai_client, db)
    personas = await generator.generate_personas(
        template_data=template["template_data"],
        archetype=ScenarioArchetype(archetype),
        sub_archetype=sub_archetype,
        count=count,
        complexity=PersonaComplexity(complexity)
    )
    
    # Store in database
    for persona in personas:
        await db.personas.insert_one(persona.dict(by_alias=True))
    
    return {
        "generated_count": len(personas),
        "archetype": archetype,
        "sub_archetype": sub_archetype,
        "personas": [p.dict() for p in personas]
    }
```

---

## Phase 5: Frontend Integration

### Scenario Creation Flow

```typescript
// 1. Upload template → Get archetype classification
const templateResponse = await uploadTemplate(file);
const archetype = templateResponse.archetype_metadata.archetype;

// 2. Show archetype-specific UI
if (archetype === "CONFRONTATION") {
    // Show 3 variant options
    showVariantSelector([
        { type: "PERPETRATOR", label: "Practice confronting perpetrator" },
        { type: "VICTIM", label: "Practice supporting victim" },
        { type: "BYSTANDER", label: "Practice empowering bystander" }
    ]);
} else if (archetype === "PERSUASION") {
    // Show objection library preview
    showObjectionLibrary(templateResponse.persona_definitions.objection_library);
}

// 3. Generate personas for each variant
for (const variant of variants) {
    await generatePersonas({
        template_id: templateId,
        archetype: archetype,
        sub_archetype: variant.type,
        count: 5
    });
}

// 4. Create scenario with variants
await createScenario({
    template_id: templateId,
    title: scenarioTitle,
    variants: variants
});
```

### Chat Session Selection

```typescript
// User selects scenario
const scenario = await getScenario(scenarioId);

// If multi-variant, show variant selector
if (scenario.content?.assess_mode_variants) {
    const selectedVariant = await showVariantSelector(
        scenario.content.assess_mode_variants
    );
    
    // Initialize chat with selected variant
    await initializeChat({
        avatar_interaction_id: selectedVariant.avatar_interaction_id,
        mode: "assess_mode",
        persona_id: randomPersonaForVariant(selectedVariant.type)
    });
} else {
    // Single variant (existing flow)
    await initializeChat({
        avatar_interaction_id: scenario.assess_mode,
        mode: "assess_mode"
    });
}
```

---

## Phase 6: Validation Layer

### File: `core/archetype_validator.py`

```python
class ArchetypeTemplateValidator:
    """Validates extracted template data matches archetype requirements"""
    
    @staticmethod
    def validate(template_data: Dict, archetype: str) -> Dict:
        """Validate and fix template data"""
        
        if archetype == "PERSUASION":
            # Ensure objection_library exists
            persona = template_data["persona_definitions"]["assess_mode_ai_bot"]
            if "objection_library" not in persona or not persona["objection_library"]:
                raise ValueError("PERSUASION archetype requires objection_library")
            
            # Validate objection structure
            for obj in persona["objection_library"]:
                required = ["objection", "underlying_concern", "counter_strategy"]
                if not all(k in obj for k in required):
                    raise ValueError(f"Objection missing required fields: {required}")
        
        elif archetype == "CONFRONTATION":
            # Ensure all 3 personas exist
            required_personas = ["perpetrator_persona", "victim_persona", "bystander_persona"]
            for persona_key in required_personas:
                if persona_key not in template_data["persona_definitions"]:
                    raise ValueError(f"CONFRONTATION requires {persona_key}")
        
        return template_data
```

---

## Phase 7: Migration Strategy

### Existing Scenarios
```python
async def migrate_existing_scenarios_to_archetypes(db):
    """Add archetype metadata to existing scenarios"""
    
    scenarios = await db.scenarios.find({}).to_list(length=1000)
    
    for scenario in scenarios:
        # Get template
        template = await db.templates.find_one({"id": scenario.get("template_id")})
        
        if template and "archetype_metadata" not in template.get("template_data", {}):
            # Classify existing template
            classifier = ArchetypeClassifier(llm_client, db)
            classification = await classifier.classify(
                template["template_data"].get("context_overview", {}).get("scenario_title", "")
            )
            
            # Update template with archetype
            await db.templates.update_one(
                {"id": template["id"]},
                {"$set": {
                    "archetype": classification.primary_archetype.value,
                    "template_data.archetype_metadata": {
                        "archetype": classification.primary_archetype.value,
                        "confidence": classification.confidence
                    }
                }}
            )
            
            print(f"✅ Migrated scenario {scenario['_id']} to {classification.primary_archetype.value}")
```

---

## Testing Plan

### Test Scenarios

1. **PERSUASION: Pharma Sales**
   - Upload pharma detailing document
   - Verify objection_library extraction
   - Generate 5 doctor personas with different objection styles
   - Test conversation with each persona

2. **CONFRONTATION: Disability Bias**
   - Upload DEI scenario document
   - Verify 3 personas extracted (PERPETRATOR, VICTIM, BYSTANDER)
   - Create scenario with 3 avatar_interactions
   - Generate 5 personas per variant (15 total)
   - Test conversation with each variant

3. **HELP_SEEKING: Customer Service**
   - Upload customer complaint scenario
   - Verify standard extraction (existing flow)
   - Generate 5 customer personas
   - Test conversation

### Validation Checks
- [ ] Archetype classification accuracy > 90%
- [ ] All required persona fields present
- [ ] Objection libraries have 3+ objections
- [ ] Multi-variant scenarios create correct number of avatar_interactions
- [ ] Persona injection works with archetype-specific data
- [ ] Coaching rules reflect archetype requirements

---

## Rollout Plan

### Week 1: Core Infrastructure
- ✅ Create archetype models
- ✅ Seed archetype definitions
- [ ] Add archetype fields to avatar_interaction model
- [ ] Test archetype classification

### Week 2: Extraction & Generation
- [ ] Implement archetype-specific extractors
- [ ] Test PERSUASION extractor with pharma scenario
- [ ] Test CONFRONTATION extractor with DEI scenario
- [ ] Implement archetype persona generator

### Week 3: Scenario Creation
- [ ] Build multi-variant scenario creation
- [ ] Test CONFRONTATION scenario with 3 variants
- [ ] Update scenario endpoints
- [ ] Add validation layer

### Week 4: Frontend & Testing
- [ ] Update frontend for variant selection
- [ ] Test end-to-end flow
- [ ] Migrate existing scenarios
- [ ] Production deployment

---

## Success Metrics

1. **Archetype Coverage**: 80% of scenarios classified into correct archetype
2. **Persona Quality**: Archetype-specific fields populated in 95% of personas
3. **User Satisfaction**: Multi-variant scenarios used by 60% of users
4. **Conversation Quality**: Objection handling accuracy improves by 40%
5. **System Adoption**: 5 archetypes actively used within 2 months

---

## Future Enhancements

### Phase 8: Advanced Features
- Dynamic archetype mixing (e.g., PERSUASION + NEGOTIATION)
- Persona evolution (personas learn from conversations)
- Archetype-specific evaluation metrics
- Custom archetype creation by admins
- Multi-language archetype support

### Phase 9: AI Improvements
- Fine-tune extraction models per archetype
- Persona consistency scoring
- Automatic objection library expansion
- Real-time archetype adaptation

---

## Documentation

### For Developers
- Archetype system architecture diagram
- API documentation for new endpoints
- Database schema changes
- Migration scripts

### For Users
- Archetype selection guide
- Best practices per archetype
- Persona generation tips
- Troubleshooting guide
