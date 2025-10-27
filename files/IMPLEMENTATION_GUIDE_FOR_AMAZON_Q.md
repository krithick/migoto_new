# Implementation Guide: Dynamic Persona Generation System

## 🎯 Overview

Build a system where:
1. **Base persona fields** are always present (name, age, gender, role, location)
2. **LLM analyzes scenario** and decides what additional detail categories are needed
3. **LLM generates** rich, realistic details for those categories
4. **Persona is flexible** - different scenarios get different details

---

## 📋 System Architecture

```
Scenario Document
    ↓
Extract template_data (existing extraction)
    ↓
LLM analyzes: What persona details does THIS scenario need?
    ↓
LLM decides: ["professional_context", "time_constraints", "past_experiences"]
    ↓
LLM generates: Rich details for ONLY those categories
    ↓
PersonaInstance created with base + dynamic details
    ↓
Generate system prompt using this persona
```

---

## 🗂️ File Structure to Create/Modify

```
project/
├── models/
│   └── persona_models.py          # NEW: Persona data models
├── core/
│   ├── detail_category_library.py  # NEW: Category definitions
│   ├── persona_generator.py        # NEW: Main persona generation logic
│   └── prompt_generator.py         # MODIFY: Use new persona structure
└── services/
    └── enhanced_scenario_generator.py  # MODIFY: Integration point
```

---

## 📝 TASK 1: Create Detail Category Library

**File:** `core/detail_category_library.py`

**Purpose:** Define all possible detail categories that can be added to personas.

**Implementation:**

```python
"""
Detail Category Library
Defines all possible persona detail categories.
LLM will choose from these based on scenario.
"""

from typing import Dict, List, Any
from pydantic import BaseModel


class DetailCategory(BaseModel):
    """Definition of a detail category"""
    name: str
    description: str
    example_fields: List[str]
    when_relevant: str
    

class DetailCategoryLibrary:
    """
    Library of all possible detail categories.
    LLM chooses from these based on scenario analysis.
    """
    
    CATEGORIES = {
        "professional_context": DetailCategory(
            name="professional_context",
            description="Work-related details for professionals (doctors, lawyers, managers, etc.)",
            example_fields=[
                "practice_type", "organization_type", "years_experience",
                "client_load", "patient_load", "specialization", "reputation",
                "daily_routine", "business_pressures", "professional_network"
            ],
            when_relevant="When persona is a professional (doctor, lawyer, manager) and their work context matters"
        ),
        
        "medical_philosophy": DetailCategory(
            name="medical_philosophy",
            description="How medical professionals make treatment decisions",
            example_fields=[
                "treatment_approach", "evidence_requirements", "prescription_philosophy",
                "patient_care_values", "risk_tolerance", "innovation_vs_tradition"
            ],
            when_relevant="When persona is a medical professional making clinical decisions"
        ),
        
        "family_context": DetailCategory(
            name="family_context",
            description="Family composition and how family influences decisions",
            example_fields=[
                "marital_status", "spouse_details", "children", "extended_family",
                "living_situation", "family_dynamics", "who_influences_decisions",
                "family_needs", "family_pressures"
            ],
            when_relevant="When family plays a role in decisions (buying for family, family healthcare, etc.)"
        ),
        
        "health_context": DetailCategory(
            name="health_context",
            description="Health status, medical history, and health concerns",
            example_fields=[
                "current_health_status", "medical_conditions", "past_medical_history",
                "medications", "health_anxieties", "specific_concerns", "treatment_history"
            ],
            when_relevant="When persona is a patient or health is relevant to scenario"
        ),
        
        "financial_context": DetailCategory(
            name="financial_context",
            description="Budget, income, and financial decision-making",
            example_fields=[
                "income_level", "budget_constraints", "financial_priorities",
                "current_obligations", "decision_authority", "spending_philosophy",
                "financial_pressures", "investment_capacity"
            ],
            when_relevant="When scenario involves purchasing, budgeting, or financial decisions"
        ),
        
        "time_constraints": DetailCategory(
            name="time_constraints",
            description="Schedule pressures and time availability",
            example_fields=[
                "typical_day_schedule", "current_time_pressure", "available_time",
                "competing_priorities", "urgency_factors", "time_sensitive_commitments"
            ],
            when_relevant="When persona is time-pressured or busy"
        ),
        
        "sales_rep_history": DetailCategory(
            name="sales_rep_history",
            description="Past experiences with sales representatives",
            example_fields=[
                "frequency_of_rep_visits", "past_interactions", "trust_level",
                "positive_experiences", "negative_experiences", "time_given_to_reps",
                "decision_factors", "skepticism_level"
            ],
            when_relevant="When scenario involves sales pitch and persona has history with sales reps"
        ),
        
        "past_experiences": DetailCategory(
            name="past_experiences",
            description="Relevant past experiences that shape current behavior",
            example_fields=[
                "similar_situations", "outcomes_from_past", "lessons_learned",
                "trust_issues_origin", "success_stories", "failure_stories",
                "what_makes_them_cautious"
            ],
            when_relevant="When past experiences significantly influence current behavior"
        ),
        
        "social_context": DetailCategory(
            name="social_context",
            description="Social pressures, peer influence, and status concerns",
            example_fields=[
                "peer_influence", "social_aspirations", "status_concerns",
                "community_expectations", "cultural_factors", "social_circle",
                "what_others_think_matters"
            ],
            when_relevant="When social factors or peer opinions influence decisions"
        ),
        
        "lifestyle_context": DetailCategory(
            name="lifestyle_context",
            description="Daily life patterns, habits, and lifestyle needs",
            example_fields=[
                "daily_routine", "commute_patterns", "hobbies", "interests",
                "lifestyle_priorities", "life_stage", "typical_activities"
            ],
            when_relevant="When lifestyle or daily patterns affect needs (e.g., car for commute)"
        ),
        
        "anxiety_factors": DetailCategory(
            name="anxiety_factors",
            description="Worries, fears, and sources of anxiety",
            example_fields=[
                "main_fears", "worst_case_scenarios", "anxiety_level",
                "past_trauma", "what_keeps_them_up", "coping_mechanisms"
            ],
            when_relevant="When persona has significant worries or fears affecting behavior"
        ),
        
        "work_relationships": DetailCategory(
            name="work_relationships",
            description="Workplace dynamics and relationships",
            example_fields=[
                "team_dynamics", "manager_relationship", "peer_relationships",
                "power_dynamics", "office_politics", "collaboration_style"
            ],
            when_relevant="When scenario involves workplace interactions (DEI training, HR scenarios)"
        ),
        
        "incident_context": DetailCategory(
            name="incident_context",
            description="Details about a specific incident or event",
            example_fields=[
                "what_happened", "when_it_happened", "who_was_involved",
                "immediate_impact", "ongoing_effects", "witness_presence"
            ],
            when_relevant="When scenario involves a specific incident (bias event, complaint, etc.)"
        ),
        
        "emotional_state": DetailCategory(
            name="emotional_state",
            description="Current emotional condition and triggers",
            example_fields=[
                "primary_emotion", "emotional_intensity", "emotional_triggers",
                "emotional_regulation", "mood_affecting_factors", "emotional_needs"
            ],
            when_relevant="When emotional state significantly affects interactions"
        ),
        
        "decision_criteria": DetailCategory(
            name="decision_criteria",
            description="Factors that influence their decisions",
            example_fields=[
                "must_haves", "nice_to_haves", "deal_breakers",
                "evaluation_factors", "priority_order", "trade_offs_willing_to_make"
            ],
            when_relevant="When persona needs to make a decision (PERSUASION archetype always needs this)"
        ),
        
        "research_behavior": DetailCategory(
            name="research_behavior",
            description="How they gather information and make informed decisions",
            example_fields=[
                "information_sources", "research_methods", "due_diligence_level",
                "who_they_consult", "online_vs_offline", "depth_of_research"
            ],
            when_relevant="When persona is well-researched or actively seeking information"
        )
    }
    
    @classmethod
    def get_category_definition(cls, category_name: str) -> DetailCategory:
        """Get definition for a category"""
        return cls.CATEGORIES.get(category_name)
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, DetailCategory]:
        """Get all available categories"""
        return cls.CATEGORIES
    
    @classmethod
    def get_category_names(cls) -> List[str]:
        """Get list of all category names"""
        return list(cls.CATEGORIES.keys())
```

---

## 📝 TASK 2: Create Persona Models

**File:** `models/persona_models.py`

**Purpose:** Define the data structure for personas with flexible detail categories.

**Implementation:**

```python
"""
Persona Data Models
Flexible structure for persona instances with dynamic detail categories.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4


class PersonaLocation(BaseModel):
    """Universal location model"""
    country: str = "India"
    state: Optional[str] = None
    city: str
    region: Optional[str] = None  # "Western suburbs", "Downtown"
    specific_area: Optional[str] = None  # "Andheri West", "MG Road"
    pincode: Optional[str] = None
    
    # Physical place context
    current_physical_location: str  # "At Jawahar Medical nursing home"
    location_type: str  # "Medical facility", "Office", "Home", "Store"
    location_characteristics: Optional[str] = None  # "Busy urban clinic"
    
    # Neighborhood context
    neighborhood_type: Optional[str] = None  # "Middle-class", "Upscale"
    nearby_landmarks: Optional[str] = None
    accessibility: Optional[str] = None  # "Well-connected by metro"
    
    # Cultural context
    regional_culture: Optional[str] = None  # "Urban Mumbai culture"
    languages_spoken: List[str] = ["English", "Hindi"]
    local_customs: Optional[str] = None


class PersonaInstance(BaseModel):
    """
    Flexible persona model with base fields + dynamic detail categories.
    Different scenarios will have different detail categories.
    """
    # ===== META =====
    id: str = Field(default_factory=lambda: str(uuid4()))
    template_id: str
    persona_type: str  # "Experienced Gynecologist", "First-time Mother", etc.
    mode: str  # "learn_mode", "assess_mode", "try_mode"
    scenario_type: str  # "pharma_sales", "maternity_inquiry", etc.
    
    # ===== BASE FIELDS (Always Present) =====
    name: str
    age: int
    gender: str
    role: str
    description: str
    
    # Location (Always Present - Rich Details)
    location: PersonaLocation
    
    # ===== ARCHETYPE (From Classification) =====
    archetype: str  # "PERSUASION", "CONFRONTATION", "HELP_SEEKING", etc.
    archetype_confidence: float
    archetype_specific_data: Dict[str, Any] = Field(default_factory=dict)
    # Examples:
    # PERSUASION: {"current_position": "Uses Dienogest", "satisfaction_level": "Neutral"}
    # CONFRONTATION: {"sub_type": "VICTIM", "incident_details": "..."}
    # HELP_SEEKING: {"problem": "...", "urgency": "High"}
    
    # ===== DYNAMIC DETAIL CATEGORIES (Scenario-Specific) =====
    detail_categories: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # Structure:
    # {
    #     "professional_context": {
    #         "practice_type": "Owns nursing home",
    #         "patient_load": "40 patients/day",
    #         "years_experience": 15,
    #         ...
    #     },
    #     "time_constraints": {
    #         "typical_schedule": "...",
    #         "current_pressure": "Surgery in 1 hour",
    #         ...
    #     }
    # }
    
    # ===== CONVERSATION PARAMETERS =====
    conversation_rules: Dict[str, Any] = Field(default_factory=dict)
    # {
    #     "opening_behavior": "Wait for greeting then...",
    #     "response_style": "Brief and busy",
    #     "word_limit": 50,
    #     "behavioral_triggers": {...}
    # }
    
    # ===== METADATA =====
    detail_categories_included: List[str] = Field(default_factory=list)
    # Track which categories were generated
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
    # Track how it was generated


class PersonaGenerationRequest(BaseModel):
    """Request to generate a persona"""
    template_id: str
    mode: str  # "assess_mode", "learn_mode", "try_mode"
    persona_type: Optional[str] = None  # Pick from template's persona_types
    
    # Optional customization
    gender: Optional[str] = None
    custom_prompt: Optional[str] = None
    variation_id: Optional[int] = None
```

---

## 📝 TASK 3: Create Persona Generator

**File:** `core/persona_generator.py`

**Purpose:** Main logic to analyze scenario and generate persona with relevant details.

**Implementation:**

```python
"""
Persona Generator
Analyzes scenario and generates rich persona with relevant detail categories.
"""

import json
from typing import Dict, Any, List, Optional
from models.persona_models import PersonaInstance, PersonaLocation
from core.detail_category_library import DetailCategoryLibrary


class PersonaGenerator:
    """
    Generates personas dynamically based on scenario analysis.
    LLM decides which detail categories are relevant.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        self.category_library = DetailCategoryLibrary()
    
    async def generate_persona(
        self,
        template_data: Dict[str, Any],
        mode: str,
        gender: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> PersonaInstance:
        """
        Main entry point: Generate complete persona for a scenario.
        
        Flow:
        1. Get base persona info from template_data
        2. LLM analyzes: What detail categories does this scenario need?
        3. LLM generates: Rich details for those categories
        4. Construct PersonaInstance
        """
        
        # Step 1: Extract base info from template
        base_persona = self._extract_base_persona(template_data, mode, gender)
        
        # Step 2: LLM decides which detail categories are needed
        relevant_categories = await self._determine_relevant_categories(
            template_data, base_persona, mode
        )
        
        print(f"[PERSONA] LLM selected categories: {relevant_categories}")
        
        # Step 3: LLM generates details for those categories
        detail_categories = await self._generate_detail_categories(
            template_data, base_persona, relevant_categories, custom_prompt
        )
        
        # Step 4: Extract conversation rules
        conversation_rules = await self._generate_conversation_rules(
            template_data, base_persona, detail_categories
        )
        
        # Step 5: Construct final persona
        persona = PersonaInstance(
            template_id=template_data.get("template_id", "unknown"),
            persona_type=base_persona["persona_type"],
            mode=mode,
            scenario_type=template_data.get("general_info", {}).get("domain", "general"),
            
            # Base fields
            name=base_persona["name"],
            age=base_persona["age"],
            gender=base_persona["gender"],
            role=base_persona["role"],
            description=base_persona["description"],
            location=base_persona["location"],
            
            # Archetype
            archetype=template_data.get("archetype_classification", {}).get("primary_archetype", "HELP_SEEKING"),
            archetype_confidence=template_data.get("archetype_classification", {}).get("confidence_score", 0.8),
            archetype_specific_data=base_persona.get("archetype_specific_data", {}),
            
            # Dynamic details
            detail_categories=detail_categories,
            conversation_rules=conversation_rules,
            
            # Metadata
            detail_categories_included=relevant_categories,
            generation_metadata={
                "custom_prompt_used": custom_prompt,
                "gender_specified": gender
            }
        )
        
        return persona
    
    def _extract_base_persona(
        self,
        template_data: Dict[str, Any],
        mode: str,
        gender: Optional[str]
    ) -> Dict[str, Any]:
        """
        Extract base persona info from template_data.
        This comes from the extraction phase.
        """
        persona_key = f"{mode}_ai_bot" if "mode" in mode else "assess_mode_ai_bot"
        persona_def = template_data.get("persona_definitions", {}).get(persona_key, {})
        
        # Extract base info
        base = {
            "persona_type": persona_def.get("role", "Character"),
            "name": persona_def.get("name", "Character"),
            "age": persona_def.get("age", 35),
            "gender": gender or persona_def.get("gender", "Female"),
            "role": persona_def.get("role", "Person"),
            "description": persona_def.get("description", ""),
            
            # Build location from extraction
            "location": self._build_location_from_template(persona_def),
            
            # Archetype-specific data
            "archetype_specific_data": self._extract_archetype_data(persona_def, template_data)
        }
        
        return base
    
    def _build_location_from_template(self, persona_def: Dict[str, Any]) -> PersonaLocation:
        """Build PersonaLocation from template data"""
        location_str = persona_def.get("location", "Mumbai, India")
        
        # Parse location string (simple parsing)
        parts = location_str.split(",")
        city = parts[0].strip() if parts else "Mumbai"
        state = parts[1].strip() if len(parts) > 1 else "Maharashtra"
        
        return PersonaLocation(
            city=city,
            state=state,
            current_physical_location=persona_def.get("current_situation", "At location"),
            location_type=persona_def.get("context", "General"),
            languages_spoken=["English", "Hindi"]
        )
    
    def _extract_archetype_data(
        self,
        persona_def: Dict[str, Any],
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract archetype-specific fields from persona definition"""
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        
        archetype_data = {}
        
        if "PERSUASION" in archetype:
            archetype_data = {
                "current_position": persona_def.get("current_position"),
                "satisfaction_level": persona_def.get("satisfaction_level"),
                "decision_criteria": persona_def.get("decision_criteria", []),
                "objection_library": persona_def.get("objection_library", [])
            }
        elif "CONFRONTATION" in archetype:
            archetype_data = {
                "sub_type": persona_def.get("sub_type"),
                "power_dynamics": persona_def.get("power_dynamics"),
                "emotional_state": persona_def.get("emotional_state")
            }
        elif "HELP_SEEKING" in archetype:
            archetype_data = {
                "problem_description": persona_def.get("problem_description"),
                "urgency_level": persona_def.get("urgency_level")
            }
        
        return archetype_data
    
    async def _determine_relevant_categories(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        mode: str
    ) -> List[str]:
        """
        LLM analyzes scenario and decides which detail categories are relevant.
        This is the KEY DYNAMIC DECISION.
        """
        
        # Get all available categories
        available_categories = self.category_library.get_all_categories()
        
        # Build category descriptions for LLM
        category_descriptions = "\n".join([
            f"- **{name}**: {cat.description}\n  When relevant: {cat.when_relevant}"
            for name, cat in available_categories.items()
        ])
        
        analysis_prompt = f"""
You are analyzing a training scenario to determine which persona detail categories are needed.

**Scenario Context:**
{json.dumps(template_data.get("context_overview", {}), indent=2)}

**Domain:** {template_data.get("general_info", {}).get("domain", "general")}
**Archetype:** {template_data.get("archetype_classification", {}).get("primary_archetype", "unknown")}

**Base Persona:**
- Role: {base_persona["role"]}
- Description: {base_persona["description"]}

**Mode:** {mode}

**Available Detail Categories:**
{category_descriptions}

**Task:** Analyze this scenario and select which detail categories are TRULY RELEVANT for this persona.

**Rules:**
1. Only select categories that significantly affect how this persona behaves
2. Don't select everything - be selective
3. Consider the archetype requirements
4. Consider what makes this persona realistic and human
5. Minimum 3 categories, maximum 8 categories

**Output Format:**
Return ONLY a JSON array of category names:
["category1", "category2", "category3"]

**Examples:**
- Pharma sales to doctor: ["professional_context", "medical_philosophy", "time_constraints", "sales_rep_history"]
- Maternity inquiry: ["health_context", "family_context", "financial_context", "anxiety_factors"]
- Car sales: ["family_context", "financial_context", "lifestyle_context", "social_context"]

Respond with ONLY the JSON array of selected categories.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You select relevant persona detail categories based on scenario analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            categories = json.loads(response_text)
            
            # Validate categories
            valid_categories = [
                cat for cat in categories 
                if cat in available_categories
            ]
            
            return valid_categories
            
        except Exception as e:
            print(f"[ERROR] Category selection failed: {e}")
            # Fallback to basic categories
            return ["professional_context", "time_constraints", "decision_criteria"]
    
    async def _generate_detail_categories(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        relevant_categories: List[str],
        custom_prompt: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate rich details for the selected categories.
        Uses parallel generation for efficiency.
        """
        import asyncio
        
        # Generate each category (parallel for speed)
        tasks = [
            self._generate_single_category(
                category_name, template_data, base_persona, custom_prompt
            )
            for category_name in relevant_categories
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combine into dictionary
        detail_categories = {
            category_name: details
            for category_name, details in zip(relevant_categories, results)
        }
        
        return detail_categories
    
    async def _generate_single_category(
        self,
        category_name: str,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        custom_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Generate details for a single category"""
        
        category_def = self.category_library.get_category_definition(category_name)
        
        generation_prompt = f"""
Generate realistic, detailed information for the "{category_name}" category of this persona.

**Category Definition:** {category_def.description}

**Example Fields:** {", ".join(category_def.example_fields)}

**Persona:**
- Name: {base_persona["name"]}
- Age: {base_persona["age"]}
- Role: {base_persona["role"]}
- Location: {base_persona["location"].city}

**Scenario Context:**
{json.dumps(template_data.get("context_overview", {}), indent=2)}

**Domain:** {template_data.get("general_info", {}).get("domain", "general")}

{f"**Custom Instructions:** {custom_prompt}" if custom_prompt else ""}

**Task:** Generate rich, realistic details for this category that make the persona feel human and authentic.

**Requirements:**
1. Use realistic Indian context (names, locations, cultural details)
2. Make details specific and concrete (not generic)
3. Include numeric details where relevant
4. Show depth and nuance
5. Connect details to the scenario

**Output Format:**
Return a JSON object with detailed fields for this category.

Example for "professional_context":
{{
    "practice_type": "Owns Jawahar Medical nursing home",
    "practice_size": "Medium - 20 beds, attached pharmacy",
    "patient_load": "40 OPD patients daily, 2-3 surgeries weekly",
    "years_experience": 15,
    "specialization": "Gynecology with focus on endometriosis and PCOS",
    "reputation": "Well-known in Andheri area, referrals from 3 nearby clinics",
    "daily_routine": "OPD 9am-2pm, surgeries 3pm-6pm, admin work evenings"
}}

Generate detailed JSON for "{category_name}":
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate realistic persona details based on Indian context."},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            details = json.loads(response_text)
            return details
            
        except Exception as e:
            print(f"[ERROR] Category generation failed for {category_name}: {e}")
            return {"error": f"Failed to generate {category_name}"}
    
    async def _generate_conversation_rules(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        detail_categories: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate conversation rules and behavioral triggers"""
        
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        
        # Build context from detail categories
        context_summary = "\n".join([
            f"**{cat_name}:** {json.dumps(details, indent=2)}"
            for cat_name, details in detail_categories.items()
        ])
        
        rules_prompt = f"""
Generate conversation rules and behavioral parameters for this persona.

**Persona:** {base_persona["name"]}, {base_persona["role"]}
**Archetype:** {archetype}

**Detail Categories:**
{context_summary}

**Generate:**
1. opening_behavior: How they start the conversation
2. response_style: How they communicate (brief/detailed, formal/casual)
3. word_limit: Typical response length
4. behavioral_triggers: What engages them, what frustrates them, what ends conversation

**Output JSON:**
{{
    "opening_behavior": "Wait for learner to greet you, then...",
    "response_style": "Brief and professional, time-conscious",
    "word_limit": 50,
    "behavioral_triggers": {{
        "what_engages": ["Specific data", "Evidence-based arguments"],
        "what_frustrates": ["Vague claims", "Time-wasting"],
        "what_escalates": ["Disrespect", "Ignoring concerns"],
        "what_ends_conversation": ["Off-topic questions", "Profanity"]
    }}
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate conversation rules for AI personas."},
                    {"role": "user", "content": rules_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            rules = json.loads(response_text)
            return rules
            
        except Exception as e:
            print(f"[ERROR] Conversation rules generation failed: {e}")
            return {
                "opening_behavior": "Wait for learner",
                "response_style": "Natural",
                "word_limit": 50,
                "behavioral_triggers": {}
            }
```

---

## 📝 TASK 4: Create Prompt Generator

**File:** `core/prompt_generator.py`

**Purpose:** Generate rich system prompts from PersonaInstance using LLM.

**Implementation:**

```python
"""
Prompt Generator
Generates rich system prompts from PersonaInstance data.
Uses LLM to create natural, context-rich prompts.
"""

import json
from typing import Dict, Any
from models.persona_models import PersonaInstance


class PromptGenerator:
    """
    Generates system prompts from persona data.
    Uses GENERATE approach (LLM creates natural prompt).
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
    
    async def generate_system_prompt(
        self,
        persona: PersonaInstance,
        template_data: Dict[str, Any]
    ) -> str:
        """
        Generate complete system prompt from persona.
        
        The LLM creates a natural, context-rich prompt based on:
        - Base persona fields
        - All detail categories
        - Archetype rules
        - Conversation rules
        """
        
        # Build comprehensive context for LLM
        generation_instructions = self._build_generation_instructions(persona, template_data)
        
        # LLM generates the prompt
        system_prompt = await self._call_llm_for_prompt_generation(generation_instructions)
        
        return system_prompt
    
    def _build_generation_instructions(
        self,
        persona: PersonaInstance,
        template_data: Dict[str, Any]
    ) -> str:
        """Build instructions for LLM to generate prompt"""
        
        # Format persona data
        persona_summary = f"""
**Base Identity:**
- Name: {persona.name}
- Age: {persona.age}
- Gender: {persona.gender}
- Role: {persona.role}

**Location:**
{json.dumps(persona.location.dict(), indent=2)}

**Archetype:** {persona.archetype}
**Archetype-Specific Data:**
{json.dumps(persona.archetype_specific_data, indent=2)}

**Detail Categories:**
{json.dumps(persona.detail_categories, indent=2)}

**Conversation Rules:**
{json.dumps(persona.conversation_rules, indent=2)}
"""
        
        # Get archetype-specific instructions
        archetype_instructions = self._get_archetype_instructions(persona.archetype)
        
        instructions = f"""
You are creating a system prompt for an AI training scenario.

**Mode:** {persona.mode}
**Scenario Type:** {persona.scenario_type}

**Persona Data:**
{persona_summary}

**Archetype-Specific Behavior:**
{archetype_instructions}

**Your Task:**
Generate a complete, natural-language system prompt that:

1. **Introduces the character** with full context (who they are, where they are, what's happening)
2. **Includes ALL relevant details** from the detail categories naturally woven in
3. **Sets behavioral rules** based on archetype
4. **Adds strong guardrails**:
   - DO NOT answer off-topic questions
   - DO NOT leave character
   - DO NOT tolerate disrespect
   - DO NOT discuss topics outside domain
5. **Specifies conversation flow**:
   - How to start
   - How to respond
   - When to escalate/de-escalate
   - How to end

**Critical Requirements:**
- Write in NATURAL language (not just listing fields)
- Make the persona feel REAL and HUMAN
- Include specific situational details that affect behavior
- Add archetype-appropriate reactions
- Keep sections organized but readable
- Use all the persona data provided

**Tone:** Professional, realistic, contextually appropriate

Generate the complete system prompt now.
"""
        
        return instructions
    
    def _get_archetype_instructions(self, archetype: str) -> str:
        """Get archetype-specific prompt generation instructions"""
        
        instructions = {
            "PERSUASION": """
**PERSUASION Archetype Behavior:**
- Start neutral/polite when they approach
- Let THEM explain their product/service
- Be skeptical if they make vague claims without evidence
- Be receptive if they provide strong data
- Raise objections based on your current position
- Use your decision criteria to evaluate
- Close positively if convinced, negatively if not
""",
            "CONFRONTATION": """
**CONFRONTATION Archetype Behavior:**
- Show emotional authenticity (hurt, defensive, or concerned based on sub-type)
- React to how learner approaches you
- Escalate if they're accusatory or dismissive
- Open up if they show genuine empathy
- Your vulnerability depends on their skill
""",
            "HELP_SEEKING": """
**HELP_SEEKING Archetype Behavior:**
- Proactively share your problem/concern
- Be clear about what you need
- Be satisfied if they provide good solution
- Be frustrated if they're unhelpful or vague
- Close positively if helped, negatively if not
""",
            "INVESTIGATION": """
**INVESTIGATION Archetype Behavior:**
- Answer questions honestly but don't volunteer extra info
- Show your communication barriers naturally
- Reward good questioning with more details
- Be brief if they ask poor questions
""",
            "NEGOTIATION": """
**NEGOTIATION Archetype Behavior:**
- State your position clearly
- Protect your non-negotiables firmly
- Be flexible on other points
- Look for win-win solutions
- Reward creative problem-solving
"""
        }
        
        return instructions.get(archetype, "Respond naturally based on your character.")
    
    async def _call_llm_for_prompt_generation(self, instructions: str) -> str:
        """Call LLM to generate the system prompt"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating AI system prompts for training scenarios."},
                    {"role": "user", "content": instructions}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            system_prompt = response.choices[0].message.content.strip()
            return system_prompt
            
        except Exception as e:
            print(f"[ERROR] Prompt generation failed: {e}")
            return self._fallback_prompt_template(instructions)
    
    def _fallback_prompt_template(self, instructions: str) -> str:
        """Fallback if LLM generation fails"""
        return f"""
# Training Scenario

[SYSTEM ERROR: Could not generate full prompt]

{instructions}

Please respond naturally based on the context provided.
"""
```

---

## 📝 TASK 5: Integration Point

**File:** `services/enhanced_scenario_generator.py` (MODIFY existing)

**Purpose:** Integrate new persona generation system.

**Changes Needed:**

```python
# ADD import at top
from core.persona_generator import PersonaGenerator
from core.prompt_generator import PromptGenerator
from models.persona_models import PersonaInstance

# MODIFY the generate_personas_from_template method:

async def generate_personas_from_template(
    self, 
    template_data, 
    gender='', 
    context='', 
    archetype_classification=None
):
    """
    NEW IMPLEMENTATION: Use PersonaGenerator instead of old approach
    """
    try:
        # Initialize generators
        persona_gen = PersonaGenerator(self.client, self.model)
        
        # Generate assess mode persona (main one)
        assess_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender=gender,
            custom_prompt=context
        )
        
        # Generate learn mode persona (simpler)
        learn_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="learn_mode",
            gender=gender or "Female",  # Default for trainer
            custom_prompt=None
        )
        
        # Return in expected format
        return {
            "learn_mode_expert": learn_persona.dict(),
            "assess_mode_character": assess_persona.dict()
        }
        
    except Exception as e:
        print(f"Error in generate_personas_from_template: {str(e)}")
        # Fallback to old implementation if needed
        return self._get_mock_personas(template_data)

# MODIFY the generate_assess_mode_from_template method:

async def generate_assess_mode_from_template(self, template_data):
    """
    NEW IMPLEMENTATION: Use PromptGenerator with PersonaInstance
    """
    try:
        # Step 1: Generate persona
        persona_gen = PersonaGenerator(self.client, self.model)
        persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode"
        )
        
        # Step 2: Generate prompt from persona
        prompt_gen = PromptGenerator(self.client, self.model)
        system_prompt = await prompt_gen.generate_system_prompt(
            persona=persona,
            template_data=template_data
        )
        
        return system_prompt
        
    except Exception as e:
        print(f"Error in generate_assess_mode_from_template: {str(e)}")
        return "Error generating assess mode template"
```

---

## 📝 TASK 6: API Endpoint Updates

**File:** Your API routes file (MODIFY existing endpoints)

**Changes:**

```python
# The /generate-personas endpoint should now return PersonaInstance format
# The /generate-prompts endpoint uses new system

# Example:
@router.post("/generate-personas")
async def generate_personas(
    template_id: str = Body(...),
    persona_type: str = Body(...),
    mode: str = Body(...),
    gender: str = Body(default=""),
    prompt: str = Body(default=""),
    db: Any = Depends(get_db)
):
    """Generate persona using new PersonaGenerator"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        
        # Use new PersonaGenerator
        from core.persona_generator import PersonaGenerator
        persona_gen = PersonaGenerator(azure_openai_client)
        
        persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode=mode,
            gender=gender,
            custom_prompt=prompt
        )
        
        return {
            "template_id": template_id,
            "persona": persona.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## ✅ Testing Instructions

After implementation, test with these scenarios:

### Test 1: Pharma Sales
```python
# Should generate:
# - professional_context
# - medical_philosophy
# - time_constraints
# - sales_rep_history
```

### Test 2: Maternity Inquiry
```python
# Should generate:
# - health_context
# - family_context
# - financial_context
# - anxiety_factors
```

### Test 3: DEI Training
```python
# Should generate:
# - work_relationships
# - incident_context
# - emotional_state
# - organizational_context
```

---

## 🎯 Success Criteria

✅ LLM successfully chooses 3-8 relevant categories per scenario
✅ Generated details are rich, specific, and realistic
✅ System prompts are natural and context-rich
✅ Different scenarios get different detail categories
✅ Personas feel human and authentic
✅ API endpoints return new PersonaInstance format
✅ Old functionality still works (backwards compatible)

---

## 📞 Key Points for Implementation

1. **Keep it dynamic** - LLM decides categories, not hardcoded rules
2. **Rich details** - Each category should have 5-10 fields minimum
3. **Parallel generation** - Use asyncio.gather for speed
4. **Error handling** - Fallbacks if LLM calls fail
5. **Logging** - Print which categories were selected
6. **Testing** - Test with 3-5 different scenario types

---

## 🚀 Implementation Order

1. ✅ Create detail_category_library.py
2. ✅ Create persona_models.py
3. ✅ Create persona_generator.py
4. ✅ Create prompt_generator.py
5. ✅ Modify enhanced_scenario_generator.py
6. ✅ Update API endpoints
7. ✅ Test with multiple scenarios

**Good luck! The system is now fully dynamic with LLM-driven category selection!**
