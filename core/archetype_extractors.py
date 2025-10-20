"""
Archetype-Specific Extractors
Each archetype has its own extraction logic with specialized schemas
"""

import json
import re
from typing import Dict, Any
from openai import AsyncAzureOpenAI


class ArchetypeExtractorBase:
    """Base class for archetype extractors"""
    
    def __init__(self, llm_client: AsyncAzureOpenAI):
        self.llm_client = llm_client
    
    async def extract(self, scenario_document: str, archetype_definition: Dict) -> Dict[str, Any]:
        """Extract scenario data - to be implemented by subclasses"""
        raise NotImplementedError


class PersuasionExtractor(ArchetypeExtractorBase):
    """Extractor for PERSUASION archetype"""
    
    async def extract(self, scenario_document: str, archetype_definition: Dict) -> Dict[str, Any]:
        extraction_prompt = f"""Extract persuasion/sales scenario data.

SCENARIO: {scenario_document}

Extract in JSON format:
{{
    "general_info": {{
        "domain": "Pharma Sales",
        "target_audience": "Field Sales Officers",
        "preferred_language": "English"
    }},
    "context_overview": {{
        "scenario_title": "Detailing New Diabetes Medication to Endocrinologist",
        "learn_mode_description": "AI expert teaches sales methodology",
        "assess_mode_description": "Practice pitching to skeptical doctor",
        "purpose_of_scenario": "Master objection handling and evidence-based selling"
    }},
    "persona_definitions": {{
        "learn_mode_ai_bot": {{
            "role": "Senior Sales Trainer",
            "background": "15 years pharma sales experience",
            "teaching_style": "Evidence-based, practical"
        }},
        "assess_mode_ai_bot": {{
            "role": "Busy Endocrinologist",
            "current_position": "Satisfied with metformin for Type 2 diabetes",
            "satisfaction_level": "High - patients doing well",
            "knowledge_gaps": [
                "Unaware of new GLP-1 agonist cardiovascular benefits",
                "Doesn't know about recent outcome trials"
            ],
            "objection_library": [
                {{
                    "objection": "I don't have time for another detail",
                    "underlying_concern": "Busy clinic, 40 patients/day",
                    "counter_strategy": "2-minute value proposition with key data",
                    "buying_signal": "Asks for clinical trial details"
                }},
                {{
                    "objection": "My patients do fine on metformin",
                    "underlying_concern": "Risk aversion, status quo bias",
                    "counter_strategy": "Show superior A1C reduction data",
                    "buying_signal": "Asks about specific patient types"
                }}
            ],
            "decision_criteria": ["Clinical evidence quality", "Safety profile", "Patient compliance"],
            "personality_type": "Analytical, evidence-driven",
            "time_pressure": "High - very busy",
            "authority_level": "Decision maker for 200+ diabetes patients"
        }}
    }},
    "knowledge_base": {{
        "dos": ["Present evidence first", "Address objections with data", "Ask about patient types"],
        "donts": ["Push without evidence", "Ignore time constraints", "Dismiss current treatment"],
        "key_facts": ["Product efficacy data", "Safety profile", "Dosing convenience"],
        "conversation_topics": ["Clinical evidence", "Patient outcomes", "Ease of use"]
    }},
    "coaching_rules": {{
        "process_requirements": {{
            "mentioned_methodology": "SPIN Selling" or "Consultative Selling",
            "required_steps": ["Discovery", "Present evidence", "Handle objections", "Close"],
            "sequence_requirements": "Must discover needs before pitching"
        }},
        "document_specific_mistakes": [
            {{
                "mistake_pattern": "Pitching before understanding doctor's patient mix",
                "why_problematic": "Generic pitch doesn't resonate",
                "correct_approach": "Ask about patient demographics first"
            }}
        ]
    }}
}}

Focus on objection_library - make it detailed and realistic.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract persuasion scenario data with detailed objection libraries."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            if text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            return json.loads(text)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return {}


class ConfrontationExtractor(ArchetypeExtractorBase):
    """Extractor for CONFRONTATION archetype"""
    
    async def extract(self, scenario_document: str, archetype_definition: Dict) -> Dict[str, Any]:
        extraction_prompt = f"""Extract confrontation scenario data with 3 sub-types.

SCENARIO: {scenario_document}

Extract in JSON format with 3 persona definitions (PERPETRATOR, VICTIM, BYSTANDER):
{{
    "general_info": {{
        "domain": "HR/DEI Training",
        "target_audience": "Managers and HR professionals",
        "preferred_language": "English"
    }},
    "context_overview": {{
        "scenario_title": "Addressing Workplace Bias Against Employees with Disabilities",
        "learn_mode_description": "AI expert teaches bias intervention techniques",
        "assess_mode_description": "Practice addressing bias in different roles",
        "purpose_of_scenario": "Master de-escalation, empathy, and accountability"
    }},
    "persona_definitions": {{
        "learn_mode_ai_bot": {{
            "role": "Senior DEI Trainer",
            "background": "10+ years in workplace inclusion",
            "teaching_style": "Empathetic, evidence-based"
        }},
        "perpetrator_persona": {{
            "role": "Manager who made biased comment",
            "sub_type": "PERPETRATOR",
            "awareness_level": "Unaware of harm caused",
            "defensive_mechanisms": ["Denial", "It was just a joke", "Deflection"],
            "escalation_triggers": ["Direct accusations", "Public confrontation", "Threats"],
            "de_escalation_opportunities": ["Private setting", "Focus on impact not intent", "Path to redemption"],
            "power_dynamics": "Senior to learner",
            "conversation_arc": "Defensive → Uncomfortable → Realization → Accountability"
        }},
        "victim_persona": {{
            "role": "Employee with disability who experienced bias",
            "sub_type": "VICTIM",
            "emotional_state": "Hurt, angry, distrustful",
            "trust_level": "Low - fears retaliation",
            "needs": ["Validation", "Action plan", "Safety assurance", "Confidentiality"],
            "barriers_to_reporting": ["Fear of retaliation", "Past dismissals", "Power imbalance"],
            "conversation_arc": "Guarded → Sharing → Hopeful (if handled with empathy)"
        }},
        "bystander_persona": {{
            "role": "Colleague who witnessed bias",
            "sub_type": "BYSTANDER",
            "internal_conflict": "Wants to help but fears consequences",
            "knowledge_gaps_intervention": ["What to say", "How to report", "Will I be protected"],
            "empowerment_needs": ["Permission to act", "Specific language", "Support"],
            "conversation_arc": "Uncertain → Empowered → Committed"
        }}
    }},
    "coaching_rules": {{
        "process_requirements": {{
            "mentioned_methodology": "Restorative Justice" or "Trauma-Informed Approach",
            "required_steps": ["Establish safety", "Listen actively", "Validate experience", "Action plan"],
            "sequence_requirements": "Safety first, then accountability"
        }}
    }}
}}

Make each persona psychologically realistic with authentic emotional responses.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract confrontation scenarios with 3 distinct personas."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        try:
            if text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            return json.loads(text)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return {}


class HelpSeekingExtractor(ArchetypeExtractorBase):
    """Extractor for HELP_SEEKING archetype (your current default)"""
    
    async def extract(self, scenario_document: str, archetype_definition: Dict) -> Dict[str, Any]:
        # Use your existing extraction logic
        extraction_prompt = f"""Extract help-seeking scenario data.

SCENARIO: {scenario_document}

Extract standard template structure with focus on:
- problem_description
- emotional_state
- desired_outcome
- patience_level

Return in your existing template format.
"""
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract help-seeking scenario data."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return self._parse_json_response(response.choices[0].message.content)
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        try:
            if text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            return json.loads(text)
        except Exception as e:
            return {}


# Extractor factory
class ArchetypeExtractorFactory:
    """Factory to get the right extractor for each archetype"""
    
    @staticmethod
    def get_extractor(archetype: str, llm_client: AsyncAzureOpenAI) -> ArchetypeExtractorBase:
        extractors = {
            "PERSUASION": PersuasionExtractor,
            "CONFRONTATION": ConfrontationExtractor,
            "HELP_SEEKING": HelpSeekingExtractor,
            # Add others as needed
        }
        
        extractor_class = extractors.get(archetype, HelpSeekingExtractor)
        return extractor_class(llm_client)
