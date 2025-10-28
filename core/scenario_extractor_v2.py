"""
Scenario Extractor V2
Enhanced multi-pass extraction system for training scenarios.
Extracts ALL context needed for dynamic persona generation and rich prompts.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class ScenarioExtractorV2:
    """
    V2 Extraction System: 4-pass parallel extraction
    Extracts mode descriptions, persona types, domain knowledge, and coaching rules
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
    
    async def extract_scenario_info(self, scenario_document: str) -> Dict[str, Any]:
        """
        Main extraction method: 4 parallel LLM calls for comprehensive extraction
        """
        print("[V2 EXTRACTION] Starting 4-pass extraction...")
        
        # Run 4 extractions in parallel
        results = await asyncio.gather(
            self._extract_mode_descriptions(scenario_document),
            self._extract_persona_types(scenario_document),
            self._extract_domain_knowledge(scenario_document),
            self._extract_coaching_evaluation(scenario_document),
            return_exceptions=True
        )
        
        # Combine results
        mode_descriptions = results[0] if not isinstance(results[0], Exception) else {}
        persona_types = results[1] if not isinstance(results[1], Exception) else {}
        domain_knowledge = results[2] if not isinstance(results[2], Exception) else {}
        coaching_evaluation = results[3] if not isinstance(results[3], Exception) else {}
        
        print(f"[V2 EXTRACTION] Completed: modes={bool(mode_descriptions)}, personas={bool(persona_types)}, domain={bool(domain_knowledge)}, coaching={bool(coaching_evaluation)}")
        
        # Merge into unified structure
        template_data = self._merge_extraction_results(
            mode_descriptions,
            persona_types,
            domain_knowledge,
            coaching_evaluation,
            scenario_document
        )
        
        # FIX #1: Validate and correct archetype
        template_data = self._validate_and_correct_archetype(template_data)
        
        return template_data
    
    async def _extract_mode_descriptions(self, document: str) -> Dict[str, Any]:
        """Pass 1: Extract what happens in each mode"""
        prompt = f"""
Analyze this training scenario and extract mode descriptions.

DOCUMENT:
{document[:3000]}

Extract in JSON format:
{{
    "learn_mode": {{
        "what_happens": "What happens in learn mode",
        "ai_bot_role": "Who is the AI (trainer, expert, instructor)",
        "learner_role": "Who is the learner",
        "teaching_focus": "What's being taught",
        "methods": ["Named methodologies if any (IMPACT, SPIN, KYC, etc.)"],
        "uses_vector_db": true/false
    }},
    "assess_mode": {{
        "what_happens": "What happens in assess mode",
        "learner_role": "Who is the learner",
        "context": "Where/when this happens",
        "ai_bot_role": "Who is the AI character"
    }},
    "try_mode": {{
        "same_as_assess": true/false,
        "coaching_enabled": true/false
    }}
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract mode descriptions from training scenarios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(result_text)
        except Exception as e:
            print(f"[WARN] Mode extraction failed: {e}")
            return {}
    
    async def _extract_persona_types(self, document: str) -> Dict[str, Any]:
        """Pass 2: Extract persona TYPES (not specific instances)"""
        prompt = f"""
Analyze this training scenario and extract persona TYPES (categories, not specific people).

DOCUMENT:
{document[:3000]}

Extract in JSON format:
{{
    "persona_types": [
        {{
            "type": "Category name (e.g., 'Experienced Gynecologist', 'First-time Mother')",
            "description": "What defines this type",
            "use_case": "Why this type is used in training",
            "key_characteristics": {{
                "specialty": "Professional specialty if applicable",
                "decision_style": "How they make decisions",
                "time_availability": "Time constraints",
                "current_solution": "What they currently use/do",
                "pain_points": ["Key frustrations or concerns"]
            }}
        }}
    ]
}}

Focus on TYPES/CATEGORIES, not specific named individuals.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract persona types from training scenarios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(result_text)
        except Exception as e:
            print(f"[WARN] Persona type extraction failed: {e}")
            return {}
    
    async def _extract_domain_knowledge(self, document: str) -> Dict[str, Any]:
        """Pass 3: Extract domain knowledge structure"""
        prompt = f"""
Analyze this training scenario and extract domain knowledge structure.

DOCUMENT:
{document[:4000]}

Extract in JSON format:
{{
    "methodology": {{
        "name": "Named methodology if exists (IMPACT, SPIN, KYC, etc.) or null",
        "steps": ["Step 1", "Step 2", "..."]
    }},
    "subject_matter": {{
        "type": "pharmaceutical_product / policy / service / process",
        "name": "Name of product/policy/service",
        "main_points": ["Key point 1", "Key point 2"],
        "key_benefits": ["Benefit 1", "Benefit 2"],
        "evidence": ["Evidence 1", "Evidence 2"]
    }},
    "key_facts": ["Fact 1", "Fact 2", "..."],
    "dos": ["Do 1", "Do 2", "..."],
    "donts": ["Don't 1", "Don't 2", "..."],
    "conversation_topics": ["Topic 1", "Topic 2", "..."]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract domain knowledge from training scenarios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            result_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(result_text)
        except Exception as e:
            print(f"[WARN] Domain knowledge extraction failed: {e}")
            return {}
    
    async def _extract_coaching_evaluation(self, document: str) -> Dict[str, Any]:
        """Pass 4: Extract coaching rules and evaluation criteria"""
        prompt = f"""
Analyze this training scenario and extract coaching rules and evaluation criteria.

DOCUMENT:
{document[:4000]}

Extract in JSON format:
{{
    "evaluation_criteria": {{
        "what_to_evaluate": ["Criterion 1", "Criterion 2", "..."],
        "scoring_weights": {{
            "methodology_adherence": 30,
            "objection_handling": 20,
            "factual_accuracy": 25,
            "communication_skills": 25
        }},
        "common_mistakes": ["Mistake 1", "Mistake 2", "..."]
    }},
    "coaching_rules": {{
        "when_coach_appears": ["After methodology violation", "After factual error"],
        "coaching_style": "Gentle and supportive / Direct / Educational",
        "what_to_catch": ["Methodology violations", "Factual inaccuracies"],
        "correction_patterns": {{
            "skipped_step": "Correction message pattern",
            "vague_claim": "Correction message pattern",
            "wrong_fact": "Correction message pattern"
        }}
    }}
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract coaching and evaluation rules from training scenarios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2500
            )
            
            result_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(result_text)
        except Exception as e:
            print(f"[WARN] Coaching/evaluation extraction failed: {e}")
            return {}
    
    def _merge_extraction_results(
        self,
        mode_descriptions: Dict,
        persona_types: Dict,
        domain_knowledge: Dict,
        coaching_evaluation: Dict,
        original_document: str
    ) -> Dict[str, Any]:
        """Merge all extraction results into unified template_data structure"""
        
        # Extract basic info
        learn_mode = mode_descriptions.get("learn_mode", {})
        assess_mode = mode_descriptions.get("assess_mode", {})
        try_mode = mode_descriptions.get("try_mode", {})
        
        methodology = domain_knowledge.get("methodology", {})
        subject_matter = domain_knowledge.get("subject_matter", {})
        
        # Build unified structure
        template_data = {
            "general_info": {
                "domain": subject_matter.get("type", "General Training"),
                "title": subject_matter.get("name", "Training Scenario"),
                "purpose_of_ai_bot": f"{learn_mode.get('ai_bot_role', 'Trainer')} / {assess_mode.get('ai_bot_role', 'Character')}",
                "target_audience": learn_mode.get("learner_role", "Trainees"),
                "preferred_language": "English"
            },
            
            "context_overview": {
                "scenario_title": subject_matter.get("name", "Training Scenario"),
                "learn_mode_description": learn_mode.get("what_happens", "Expert teaches methodology"),
                "assess_mode_description": assess_mode.get("what_happens", "Learner practices skills"),
                "try_mode_description": "Same as assess mode with coaching" if try_mode.get("coaching_enabled") else "Same as assess mode",
                "purpose_of_scenario": f"Learn {methodology.get('name', 'skills')} and practice application"
            },
            
            "mode_descriptions": {
                "learn_mode": learn_mode,
                "assess_mode": assess_mode,
                "try_mode": try_mode
            },
            
            "persona_types": persona_types.get("persona_types", []),
            
            "domain_knowledge": {
                "methodology": methodology.get("name"),
                "methodology_steps": methodology.get("steps", []),
                "subject_matter": subject_matter,
                "key_facts": domain_knowledge.get("key_facts", []),
                "dos": domain_knowledge.get("dos", []),
                "donts": domain_knowledge.get("donts", []),
                "conversation_topics": domain_knowledge.get("conversation_topics", []),
                "evaluation_criteria": coaching_evaluation.get("evaluation_criteria", {}),
                "coaching_rules": coaching_evaluation.get("coaching_rules", {})
            },
            
            # Keep compatibility with v1 structure
            "knowledge_base": {
                "key_facts": domain_knowledge.get("key_facts", []),
                "dos": domain_knowledge.get("dos", []),
                "donts": domain_knowledge.get("donts", []),
                "conversation_topics": domain_knowledge.get("conversation_topics", [])
            },
            
            "coaching_rules": coaching_evaluation.get("coaching_rules", {}),
            "evaluation_criteria": coaching_evaluation.get("evaluation_criteria", {}),
            
            # Placeholder for v1 compatibility
            "persona_definitions": {},
            "dialogue_flow": {},
            "variations_challenges": {},
            "success_metrics": {},
            "feedback_mechanism": {},
            
            # Metadata
            "extraction_version": "v2",
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        return template_data
    
    def _determine_correct_archetype(self, template_data: Dict[str, Any]) -> Optional[str]:
        """Determine correct archetype based on scenario context"""
        domain = template_data.get("general_info", {}).get("domain", "")
        assess_mode = template_data.get("mode_descriptions", {}).get("assess_mode", {})
        ai_bot_role = assess_mode.get("ai_bot_role", "")
        what_happens = assess_mode.get("what_happens", "")
        
        # PERSUASION: Sales, pitching scenarios
        if any(keyword in domain.lower() for keyword in ["sales", "pharmaceutical", "product"]):
            if any(keyword in what_happens.lower() for keyword in ["pitch", "sell", "convince", "present product"]):
                return "PERSUASION"
        
        # PERSUASION: Customer/client being sold to
        if any(role in ai_bot_role.lower() for role in ["customer", "client", "doctor", "buyer"]):
            if "pitch" in what_happens.lower() or "sell" in what_happens.lower():
                return "PERSUASION"
        
        # HELP_SEEKING: Customer seeking help
        if any(keyword in what_happens.lower() for keyword in ["seeks help", "needs assistance", "has problem"]):
            return "HELP_SEEKING"
        
        # CONFRONTATION: Conflict, bias scenarios
        if any(keyword in domain.lower() for keyword in ["dei", "bias", "conflict", "complaint"]):
            return "CONFRONTATION"
        
        return None
    
    def _validate_and_correct_archetype(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate archetype and correct if wrong"""
        current_archetype = template_data.get("archetype_classification", {}).get("primary_archetype")
        correct_archetype = self._determine_correct_archetype(template_data)
        
        if correct_archetype and current_archetype != correct_archetype:
            print(f"[ARCHETYPE FIX] Correcting {current_archetype} → {correct_archetype}")
            template_data["archetype_classification"] = {
                "primary_archetype": correct_archetype,
                "confidence_score": 0.95,
                "corrected": True,
                "original_archetype": current_archetype
            }
        
        return template_data
