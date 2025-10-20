"""
Archetype-Aware Persona Generator
Generates detailed personas based on archetype requirements
"""

import json
import re
from typing import Dict, Any, List
from uuid import uuid4
from datetime import datetime
from openai import AsyncAzureOpenAI

from models.archetype_models import (
    EnhancedPersonaDB,
    PersonaArchetypeData,
    PersonaComplexity,
    ScenarioArchetype,
    PersuasionPersonaSchema,
    ConfrontationPersonaSchema,
    HelpSeekingPersonaSchema
)


class ArchetypePersonaGenerator:
    """Generates personas with archetype-specific details"""
    
    def __init__(self, llm_client: AsyncAzureOpenAI, db: Any):
        self.llm_client = llm_client
        self.db = db
    
    async def generate_personas(
        self,
        template_data: Dict[str, Any],
        archetype: ScenarioArchetype,
        sub_archetype: str = None,
        count: int = 5,
        complexity: PersonaComplexity = PersonaComplexity.DETAILED
    ) -> List[EnhancedPersonaDB]:
        """Generate multiple personas for an archetype"""
        
        if archetype == ScenarioArchetype.PERSUASION:
            return await self._generate_persuasion_personas(template_data, count, complexity)
        elif archetype == ScenarioArchetype.CONFRONTATION:
            return await self._generate_confrontation_personas(template_data, sub_archetype, count, complexity)
        elif archetype == ScenarioArchetype.HELP_SEEKING:
            return await self._generate_help_seeking_personas(template_data, count, complexity)
        else:
            # Fallback to basic generation
            return await self._generate_basic_personas(template_data, count)
    
    async def _generate_persuasion_personas(
        self,
        template_data: Dict[str, Any],
        count: int,
        complexity: PersonaComplexity
    ) -> List[EnhancedPersonaDB]:
        """Generate persuasion target personas with objection libraries"""
        
        persona_def = template_data.get("persona_definitions", {}).get("assess_mode_ai_bot", {})
        domain = template_data.get("general_info", {}).get("domain", "Sales")
        
        generation_prompt = f"""Generate {count} distinct personas for a {domain} persuasion scenario.

BASE PERSONA TEMPLATE:
{json.dumps(persona_def, indent=2)}

Generate {count} VARIATIONS with different:
- Personality types (Analytical, Relationship-driven, Results-focused, Risk-averse, Innovative)
- Objection styles (Data-driven, Emotional, Time-based, Cost-focused, Competitive)
- Authority levels (Decision maker, Influencer, Gatekeeper)
- Current satisfaction levels

Each persona must have:
1. Unique objection_library (3-5 objections specific to their personality)
2. Distinct decision_criteria
3. Different buying_signals
4. Realistic background and demographics (India-based)

Return JSON array:
[
    {{
        "name": "Dr. Rajesh Sharma",
        "age": 52,
        "gender": "male",
        "description": "Skeptical endocrinologist, very busy, evidence-focused",
        "persona_type": "medical_professional",
        "character_goal": "Provide best care with proven treatments",
        "location": "Mumbai, Maharashtra",
        "persona_details": "Senior doctor, 25 years experience, conservative approach",
        "situation": "Satisfied with current diabetes treatment protocols",
        "business_or_personal": "business",
        "background_story": "Built reputation on evidence-based medicine, skeptical of new drugs",
        
        "archetype_specific": {{
            "current_position": "Uses metformin + glimepiride for most Type 2 patients",
            "satisfaction_level": "High - 85% of patients have good control",
            "knowledge_gaps": ["New GLP-1 cardiovascular data", "Latest outcome trials"],
            "objection_library": [
                {{
                    "objection": "I don't have time for another pharma detail",
                    "underlying_concern": "Sees 40 patients/day, overwhelmed with information",
                    "counter_strategy": "Quick 2-minute value proposition with key data point",
                    "buying_signal": "Asks for specific trial name or patient criteria"
                }},
                {{
                    "objection": "My patients do fine on metformin",
                    "underlying_concern": "Risk aversion, proven track record matters",
                    "counter_strategy": "Show superior A1C reduction in head-to-head trials",
                    "buying_signal": "Asks about specific patient types who might benefit"
                }}
            ],
            "decision_criteria": ["Clinical evidence quality", "Safety profile", "Patient compliance"],
            "personality_type": "Analytical, evidence-driven",
            "time_pressure": "High",
            "authority_level": "Decision maker",
            "buying_signals": ["Asks for trial data", "Mentions specific patient types", "Requests samples"]
        }}
    }}
]

Make each persona psychologically distinct and realistic.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate realistic, psychologically distinct personas for sales training."},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        personas_data = self._parse_json_response(response.choices[0].message.content)
        
        # Convert to EnhancedPersonaDB objects
        personas = []
        for persona_dict in personas_data:
            archetype_specific = persona_dict.pop("archetype_specific", {})
            
            persona = EnhancedPersonaDB(
                _id=uuid4(),
                name=persona_dict["name"],
                description=persona_dict["description"],
                persona_type=persona_dict["persona_type"],
                gender=persona_dict["gender"],
                age=persona_dict["age"],
                character_goal=persona_dict["character_goal"],
                location=persona_dict["location"],
                persona_details=persona_dict["persona_details"],
                situation=persona_dict["situation"],
                business_or_personal=persona_dict["business_or_personal"],
                background_story=persona_dict.get("background_story"),
                archetype_data=PersonaArchetypeData(
                    archetype=ScenarioArchetype.PERSUASION,
                    persuasion_data=PersuasionPersonaSchema(**archetype_specific)
                ),
                complexity_level=complexity,
                template_id=template_data.get("template_id"),
                created_by=uuid4(),  # Will be replaced with actual user
                full_persona=persona_dict
            )
            personas.append(persona)
        
        return personas
    
    async def _generate_confrontation_personas(
        self,
        template_data: Dict[str, Any],
        sub_archetype: str,
        count: int,
        complexity: PersonaComplexity
    ) -> List[EnhancedPersonaDB]:
        """Generate confrontation personas (PERPETRATOR, VICTIM, or BYSTANDER)"""
        
        persona_key = f"{sub_archetype.lower()}_persona"
        persona_def = template_data.get("persona_definitions", {}).get(persona_key, {})
        
        generation_prompt = f"""Generate {count} distinct {sub_archetype} personas for confrontation training.

SUB-TYPE: {sub_archetype}
BASE TEMPLATE: {json.dumps(persona_def, indent=2)}

Generate {count} VARIATIONS with different:
- Awareness levels (if PERPETRATOR)
- Emotional states (if VICTIM)
- Internal conflicts (if BYSTANDER)
- Power dynamics
- Backgrounds and demographics (India-based)

Return JSON array with archetype_specific fields matching the sub-type.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You generate realistic {sub_archetype} personas for confrontation training."},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        personas_data = self._parse_json_response(response.choices[0].message.content)
        
        # Convert to EnhancedPersonaDB
        personas = []
        for persona_dict in personas_data:
            archetype_specific = persona_dict.pop("archetype_specific", {})
            archetype_specific["sub_type"] = sub_archetype
            
            persona = EnhancedPersonaDB(
                _id=uuid4(),
                name=persona_dict["name"],
                description=persona_dict["description"],
                persona_type=persona_dict["persona_type"],
                gender=persona_dict["gender"],
                age=persona_dict["age"],
                character_goal=persona_dict["character_goal"],
                location=persona_dict["location"],
                persona_details=persona_dict["persona_details"],
                situation=persona_dict["situation"],
                business_or_personal=persona_dict["business_or_personal"],
                background_story=persona_dict.get("background_story"),
                archetype_data=PersonaArchetypeData(
                    archetype=ScenarioArchetype.CONFRONTATION,
                    sub_archetype=sub_archetype,
                    confrontation_data=ConfrontationPersonaSchema(**archetype_specific)
                ),
                complexity_level=complexity,
                template_id=template_data.get("template_id"),
                created_by=uuid4(),
                full_persona=persona_dict
            )
            personas.append(persona)
        
        return personas
    
    async def _generate_help_seeking_personas(
        self,
        template_data: Dict[str, Any],
        count: int,
        complexity: PersonaComplexity
    ) -> List[EnhancedPersonaDB]:
        """Generate help-seeking personas (existing logic)"""
        
        # Use existing persona generation logic
        # This is your current default behavior
        personas = []
        # ... existing implementation
        return personas
    
    async def _generate_basic_personas(
        self,
        template_data: Dict[str, Any],
        count: int
    ) -> List[EnhancedPersonaDB]:
        """Fallback basic persona generation"""
        personas = []
        # Basic generation without archetype specifics
        return personas
    
    def _parse_json_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse JSON array from LLM response"""
        try:
            if text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            return json.loads(text)
        except Exception as e:
            print(f"Persona JSON parsing error: {e}")
            return []
