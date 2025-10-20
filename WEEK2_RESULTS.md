# Week 2 Integration Test Results

## Test Summary
- **Date**: 2025-10-19
- **Total Tests**: 3
- **Passed**: 0
- **Failed**: 3
- **Success Rate**: 0.0%

## Test Results

### ✅ What's Working

1. **Archetype Classification** - EXCELLENT
   - Pharma Sales: PERSUASION (95% confidence) ✅
   - Disability Bias Perpetrator: CONFRONTATION (98% confidence) ✅
   - Disability Bias Victim: CONFRONTATION (90% confidence) ✅
   - All classifications are accurate with high confidence

2. **Basic Persona Generation** - WORKING
   - Personas are being generated successfully
   - Basic fields populated: name, age, gender, role, goal
   - Personas are contextually appropriate (e.g., "Dr. Priya Sharma" for pharma sales)

### ❌ What Needs Fixing

1. **PERSUASION Personas Missing Required Fields**
   - ❌ No objection_library (critical for sales training)
   - ❌ No decision_criteria
   - ❌ No personality_type
   - ❌ No current_position
   - ❌ No satisfaction_level

2. **CONFRONTATION Personas Missing Required Fields**
   - ❌ No sub_type field (PERPETRATOR/VICTIM/BYSTANDER)
   - ❌ No power_dynamics
   - ❌ No awareness_level (for perpetrator)
   - ❌ No defensive_mechanisms (for perpetrator)
   - ❌ No emotional_state (for victim)
   - ❌ No trust_level (for victim)

## Root Cause Analysis

The `generate_personas_from_template` function in `scenario_generator.py` is **archetype-agnostic**. It generates generic personas without considering:
1. Which archetype the scenario belongs to
2. What archetype-specific fields are required
3. The persona schemas defined in `archetype_models.py`

## Required Changes

### 1. Update Persona Generation Prompt
The persona generation prompt needs to:
- Accept archetype classification as input
- Include archetype-specific schema requirements
- Generate fields based on persona type (PersuasionPersonaSchema, ConfrontationPersonaSchema, etc.)

### 2. Enhance `generate_personas_from_template` Function
```python
async def generate_personas_from_template(
    self, 
    template_data, 
    gender='', 
    context='',
    archetype_classification=None  # ADD THIS
):
    # Use archetype info to generate appropriate persona fields
    archetype = archetype_classification.get("primary_archetype")
    sub_type = archetype_classification.get("sub_type")
    
    # Include archetype-specific schema in prompt
    # Generate objection_library for PERSUASION
    # Generate defensive_mechanisms for CONFRONTATION, etc.
```

### 3. Map to Archetype Persona Schemas
The generated personas should map to:
- `PersuasionPersonaSchema` for PERSUASION archetype
- `ConfrontationPersonaSchema` for CONFRONTATION archetype
- `HelpSeekingPersonaSchema` for HELP_SEEKING archetype
- etc.

## Next Steps (Priority Order)

### High Priority
1. ✅ **Pass archetype classification to persona generator**
   - Modify `generate_personas_from_template` to accept archetype info
   - Update all callers to pass classification data

2. ✅ **Enhance persona generation prompt**
   - Add archetype-specific field requirements
   - Include examples of objection libraries, defensive mechanisms, etc.
   - Use archetype definitions from `core/archetype_definitions.py`

3. ✅ **Validate generated personas against schemas**
   - Create validation function that checks required fields
   - Return validation errors if fields are missing

### Medium Priority
4. **Create archetype-aware persona factory**
   - Separate persona generation logic by archetype
   - Use different prompts for different archetypes
   - Ensure all required fields are populated

5. **Add persona quality scoring**
   - Score objection library quality (specificity, relevance)
   - Score defensive mechanism realism
   - Provide feedback for improvement

### Low Priority
6. **Create persona variation generator**
   - Generate multiple personas with different difficulty levels
   - Create persona libraries for common scenarios
   - Allow persona customization and editing

## Code Changes Needed

### File: `scenario_generator.py`

```python
# Line ~XXX: Update generate_personas_from_template signature
async def generate_personas_from_template(
    self, 
    template_data, 
    gender='', 
    context='',
    archetype_classification=None  # NEW PARAMETER
):
    # Get archetype info
    archetype = None
    sub_type = None
    if archetype_classification:
        archetype = archetype_classification.get("primary_archetype")
        sub_type = archetype_classification.get("sub_type")
    
    # Build archetype-specific prompt
    archetype_requirements = self._get_archetype_persona_requirements(archetype, sub_type)
    
    persona_prompt = f"""
    Generate personas for {archetype} archetype.
    
    ARCHETYPE-SPECIFIC REQUIREMENTS:
    {archetype_requirements}
    
    For PERSUASION archetype, include:
    - objection_library: Array of objections with underlying_concern and counter_strategy
    - decision_criteria: List of what influences their decisions
    - personality_type: Analytical/Relationship-driven/Results-focused
    - current_position: What they currently believe/use
    - satisfaction_level: How satisfied they are with current solution
    
    For CONFRONTATION archetype, include:
    - sub_type: PERPETRATOR/VICTIM/BYSTANDER
    - power_dynamics: Senior/Peer/Junior
    
    If PERPETRATOR:
    - awareness_level: Unaware/Minimizing/Defensive/Hostile
    - defensive_mechanisms: [Denial, Deflection, Justification]
    - escalation_triggers: What makes them more defensive
    - de_escalation_opportunities: What helps them open up
    
    If VICTIM:
    - emotional_state: Hurt/Angry/Fearful/Numb
    - trust_level: Low/Guarded/Cautiously open
    - needs: [Validation, Safety, Action plan]
    - barriers_to_reporting: What prevents them from speaking up
    
    [Rest of existing prompt...]
    """
```

### File: `test_week2_personas.py`

```python
# Line ~XX: Pass archetype classification to persona generator
personas_dict = await generator.generate_personas_from_template(
    template_data,
    archetype_classification=classification  # ADD THIS
)
```

## Validation Criteria for Week 2 Completion

### PERSUASION Archetype
- ✅ Objection library with 3-5 objections
- ✅ Each objection has: objection, underlying_concern, counter_strategy
- ✅ Decision criteria list (3-5 items)
- ✅ Personality type specified
- ✅ Current position described
- ✅ Satisfaction level indicated

### CONFRONTATION Archetype
- ✅ Sub-type clearly specified (PERPETRATOR/VICTIM/BYSTANDER)
- ✅ Power dynamics indicated
- ✅ Perpetrator: awareness_level, defensive_mechanisms, escalation_triggers
- ✅ Victim: emotional_state, trust_level, needs, barriers_to_reporting

## Estimated Effort
- **Persona Generator Enhancement**: 2-3 hours
- **Testing & Validation**: 1 hour
- **Documentation**: 30 minutes
- **Total**: 3.5-4.5 hours

## Success Metrics
- All 3 Week 2 tests pass
- Objection libraries have realistic, domain-specific objections
- Confrontation personas have appropriate defensive/emotional characteristics
- Persona quality score > 80% on manual review

## Notes
- Week 1 (Classification) is working perfectly ✅
- Week 2 (Persona Generation) needs archetype awareness
- The foundation is solid, just needs archetype-specific enhancements
- Once fixed, the system will generate production-ready training personas
