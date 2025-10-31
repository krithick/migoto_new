"""
Persona Generator V2
Analyzes scenario and generates rich persona with relevant detail categories.
"""

import json
from typing import Dict, Any, List, Optional
from models.persona_models import PersonaInstanceV2, PersonaLocation
from core.detail_category_library import DetailCategoryLibrary


class PersonaGeneratorV2:
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
    ) -> PersonaInstanceV2:
        """
        Main entry point: Generate complete persona for a scenario.
        """
        
        # Step 1: Extract base info from template
        base_persona = self._extract_base_persona(template_data, mode, gender)
        
        # Step 2: LLM decides which detail categories are needed
        relevant_categories = await self._determine_relevant_categories(
            template_data, base_persona, mode
        )
        
        print(f"[PERSONA V2] LLM selected categories: {relevant_categories}")
        
        # Step 3: LLM generates details for those categories
        detail_categories = await self._generate_detail_categories(
            template_data, base_persona, relevant_categories, custom_prompt
        )
        
        # Step 4: Generate realistic name if needed
        if base_persona["name"] == base_persona["role"]:
            base_persona["name"] = await self._generate_realistic_name(
                base_persona["role"], base_persona["gender"], base_persona["age"]
            )
        
        # Step 5: Extract conversation rules
        conversation_rules = await self._generate_conversation_rules(
            template_data, base_persona, detail_categories
        )
        
        # Step 6: Construct final persona
        persona = PersonaInstanceV2(
            template_id=template_data.get("template_id", "unknown"),
            persona_type=base_persona["persona_type"],
            mode=mode,
            scenario_type=template_data.get("general_info", {}).get("domain", "general"),
            name=base_persona["name"],
            age=base_persona["age"],
            gender=base_persona["gender"],
            role=base_persona["role"],
            description=base_persona["description"],
            location=base_persona["location"],
            archetype=template_data.get("archetype_classification", {}).get("primary_archetype", "HELP_SEEKING"),
            archetype_confidence=template_data.get("archetype_classification", {}).get("confidence_score", 0.8),
            archetype_specific_data=base_persona.get("archetype_specific_data", {}),
            detail_categories=detail_categories,
            conversation_rules=conversation_rules,
            detail_categories_included=relevant_categories,
            generation_metadata={"custom_prompt_used": custom_prompt, "gender_specified": gender}
        )
        
        # FIX #4: Validate and auto-fix persona
        from core.persona_validator import PersonaValidator
        
        issues = PersonaValidator.validate(persona, template_data)
        if issues:
            print(f"[VALIDATION] Found {len(issues)} issues:")
            for issue in issues:
                print(f"  - {issue}")
            persona = PersonaValidator.auto_fix(persona, issues)
            remaining = PersonaValidator.validate(persona, template_data)
            if remaining:
                print(f"[VALIDATION] {len(remaining)} issues remain after auto-fix")
        else:
            print("[VALIDATION] Persona looks good! ✅")
        
        return persona
    
    def _extract_base_persona(
        self,
        template_data: Dict[str, Any],
        mode: str,
        gender: Optional[str]
    ) -> Dict[str, Any]:
        """Extract base persona info from V2 extraction format."""
        # V2: Get from mode_descriptions and persona_types
        mode_key = mode if mode in ["learn_mode", "assess_mode", "try_mode"] else "assess_mode"
        mode_desc = template_data.get("mode_descriptions", {}).get(mode_key, {})
        persona_types = template_data.get("persona_types", [])
        first_persona = persona_types[0] if persona_types else {}
        
        # V1 fallback: persona_definitions
        persona_key = f"{mode}_ai_bot" if "mode" in mode else "assess_mode_ai_bot"
        persona_def = template_data.get("persona_definitions", {}).get(persona_key, {})
        
        # Extract name and role (V2 first, then V1 fallback)
        role = first_persona.get("type") or mode_desc.get("ai_bot_role") or persona_def.get("role") or "Character"
        name = persona_def.get("name") or role  # Will be overridden by LLM or caller
        
        # Location
        location_str = persona_def.get("location", "Mumbai, India")
        parts = location_str.split(",")
        city = parts[0].strip() if parts else "Mumbai"
        state = parts[1].strip() if len(parts) > 1 else "Maharashtra"
        
        return {
            "persona_type": role,
            "name": name,
            "age": persona_def.get("age", 35),
            "gender": gender or persona_def.get("gender", "Female"),
            "role": role,
            "description": first_persona.get("description") or persona_def.get("description", ""),
            "location": PersonaLocation(
                city=city,
                state=state,
                current_physical_location=mode_desc.get("context") or persona_def.get("current_situation", "At location"),
                location_type=mode_desc.get("context") or persona_def.get("context", "General"),
                languages_spoken=["English", "Hindi"]
            ),
            "archetype_specific_data": {}
        }
    
    async def _determine_relevant_categories(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        mode: str
    ) -> List[str]:
        """LLM analyzes scenario and decides which detail categories are relevant."""
        
        # FIX #2: Get required categories first
        required_categories = self._get_scenario_required_categories(template_data)
        
        available_categories = self.category_library.get_all_categories()
        category_descriptions = "\n".join([
            f"- {name}: {cat.description} (When: {cat.when_relevant})"
            for name, cat in available_categories.items()
        ])
        
        analysis_prompt = f"""Analyze this scenario and select 3-8 relevant detail categories.

SCENARIO: {template_data.get("context_overview", {}).get("scenario_title", "Training")}
DOMAIN: {template_data.get("general_info", {}).get("domain", "general")}
PERSONA ROLE: {base_persona["role"]}
MODE: {mode}
ARCHETYPE: {template_data.get("archetype_classification", {}).get("primary_archetype", "unknown")}

AVAILABLE CATEGORIES:
{category_descriptions}

REQUIRED CATEGORIES (MUST include): {required_categories}

Task: START with required categories, then add 2-5 MORE relevant ones.
Return JSON array:
["category1", "category2", "category3"]"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You select relevant persona detail categories."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            categories = json.loads(response_text)
            
            # Ensure required categories are included
            for req_cat in required_categories:
                if req_cat not in categories:
                    categories.append(req_cat)
            
            return [cat for cat in categories if cat in available_categories]
            
        except Exception as e:
            print(f"[ERROR] Category selection failed: {e}")
            return required_categories + ["professional_context", "decision_criteria"]
    
    async def _generate_detail_categories(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        relevant_categories: List[str],
        custom_prompt: Optional[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Generate rich details for the selected categories."""
        import asyncio
        
        tasks = [
            self._generate_single_category(
                category_name, template_data, base_persona, custom_prompt
            )
            for category_name in relevant_categories
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            category_name: details
            for category_name, details in zip(relevant_categories, results)
        }
    
    async def _generate_single_category(
        self,
        category_name: str,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        custom_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Generate details for a single category"""
        
        category_def = self.category_library.get_category_definition(category_name)
        
        # FIX #3: Add interaction context
        interaction_context = self._build_interaction_context(template_data, base_persona)
        
        generation_prompt = f"""Generate realistic details for "{category_name}" category.

PERSONA: {base_persona["name"]}, {base_persona["age"]}, {base_persona["role"]}
SCENARIO: {template_data.get("general_info", {}).get("domain", "general")}
CATEGORY: {category_def.description}
EXAMPLE FIELDS: {", ".join(category_def.example_fields)}

{interaction_context}

{f"CUSTOM: {custom_prompt}" if custom_prompt else ""}

Generate detailed JSON with specific, realistic Indian context.
Example: {{"practice_type": "Owns clinic", "years_experience": 15, "patient_load": "40/day"}}

Return JSON only:"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate realistic persona details."},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"[ERROR] Category generation failed for {category_name}: {e}")
            return {"error": f"Failed to generate {category_name}"}
    
    def _get_scenario_required_categories(self, template_data: Dict[str, Any]) -> List[str]:
        """Determine required categories based on scenario type"""
        domain = template_data.get("general_info", {}).get("domain", "")
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        assess_mode = template_data.get("mode_descriptions", {}).get("assess_mode", {})
        what_happens = assess_mode.get("what_happens", "")
        
        required = []
        
        # PERSUASION archetype needs decision_criteria
        if archetype == "PERSUASION":
            required.append("decision_criteria")
        
        # Sales scenarios need these
        if "sales" in domain.lower() or "pharmaceutical" in domain.lower():
            required.extend(["professional_context", "time_constraints", "sales_rep_history"])
        
        # Medical scenarios need medical_philosophy
        if any(keyword in domain.lower() for keyword in ["medical", "pharmaceutical", "healthcare"]):
            required.append("medical_philosophy")
        
        # CONFRONTATION needs these
        if archetype == "CONFRONTATION":
            required.extend(["emotional_state", "incident_context"])
        
        # HELP_SEEKING needs these
        if archetype == "HELP_SEEKING":
            required.append("anxiety_factors")
        
        required = list(set(required))
        print(f"[CATEGORIES] Required for this scenario: {required}")
        return required
    
    async def _generate_conversation_rules(
        self,
        template_data: Dict[str, Any],
        base_persona: Dict[str, Any],
        detail_categories: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate conversation rules and behavioral triggers"""
        
        # FIX #3: Add interaction context
        interaction_context = self._build_interaction_context(template_data, base_persona)
        
        context_summary = "\n".join([
            f"{cat_name}: {json.dumps(details, indent=2)}"
            for cat_name, details in detail_categories.items()
        ])
        
        rules_prompt = f"""Generate conversation rules for this persona.

PERSONA: {base_persona["name"]}, {base_persona["role"]}

{interaction_context}

DETAILS:
{context_summary}

Return JSON:
{{
    "opening_behavior": "How they start conversation",
    "response_style": "Communication style",
    "word_limit": 50,
    "behavioral_triggers": {{
        "what_engages": ["item1", "item2"],
        "what_frustrates": ["item1", "item2"],
        "what_ends_conversation": ["item1", "item2"]
    }}
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate conversation rules."},
                    {"role": "user", "content": rules_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            print(f"[ERROR] Conversation rules generation failed: {e}")
            return {
                "opening_behavior": "Wait for learner",
                "response_style": "Natural",
                "word_limit": 50,
                "behavioral_triggers": {}
            }
    
    async def _generate_realistic_name(self, role: str, gender: str, age: int) -> str:
        """Generate a realistic Indian name for the persona"""
        prompt = f"""Generate ONE realistic Indian name for this character:
Role: {role}
Gender: {gender}
Age: {age}

Return ONLY the name (first and last), nothing else.
Example: Priya Sharma"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate realistic Indian names."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=50
            )
            name = response.choices[0].message.content.strip()
            return name if name else role
        except Exception as e:
            print(f"[ERROR] Name generation failed: {e}")
            return role
    
    def _build_interaction_context(self, template_data: Dict[str, Any], base_persona: Dict[str, Any]) -> str:
        """Build clear context about WHO persona interacts with and HOW"""
        assess_mode = template_data.get("mode_descriptions", {}).get("assess_mode", {})
        learner_role = assess_mode.get("learner_role", "learner")
        ai_bot_role = assess_mode.get("ai_bot_role", base_persona["role"])
        what_happens = assess_mode.get("what_happens", "")
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        
        context = f"""INTERACTION CONTEXT:
- This persona is: {ai_bot_role}
- They interact with: {learner_role}
- What happens: {what_happens}
- Archetype: {archetype}
"""
        
        if archetype == "PERSUASION":
            context += f"""\nThis means:
- The {learner_role} is trying to CONVINCE/SELL to this persona
- Focus on: What convinces them? What frustrates them about sales pitches?
- NOT about patient care - about SALES INTERACTION"""
        elif archetype == "HELP_SEEKING":
            context += f"""\nThis means:
- This persona HAS A PROBLEM and seeks help from {learner_role}
- Focus on: What's their problem? What help do they need?"""
        elif archetype == "CONFRONTATION":
            context += f"""\nThis means:
- There's a conflict or uncomfortable situation
- Focus on: Emotional state, incident details"""
        
        return context
