"""
Persona Validator
Validates generated personas for consistency and quality.
"""

from typing import Dict, Any, List
from models.persona_models import PersonaInstanceV2


class PersonaValidator:
    """Validates generated personas and fixes common issues"""
    
    @staticmethod
    def validate(persona: PersonaInstanceV2, template_data: Dict[str, Any]) -> List[str]:
        """Validate persona and return list of issues found"""
        issues = []
        
        # Check 1: Archetype correctness
        expected_archetype = PersonaValidator._get_expected_archetype(template_data)
        if expected_archetype and persona.archetype != expected_archetype:
            issues.append(f"Wrong archetype: got {persona.archetype}, expected {expected_archetype}")
        
        # Check 2: Location consistency
        location_issues = PersonaValidator._check_location_consistency(persona)
        issues.extend(location_issues)
        
        # Check 3: Required categories present
        missing_categories = PersonaValidator._check_required_categories(persona, template_data)
        if missing_categories:
            issues.append(f"Missing required categories: {missing_categories}")
        
        # Check 4: Conversation context appropriate
        context_issues = PersonaValidator._check_conversation_context(persona, template_data)
        issues.extend(context_issues)
        
        return issues
    
    @staticmethod
    def _get_expected_archetype(template_data: Dict[str, Any]) -> str:
        """Determine expected archetype from scenario"""
        domain = template_data.get("general_info", {}).get("domain", "")
        assess_mode = template_data.get("mode_descriptions", {}).get("assess_mode", {})
        what_happens = assess_mode.get("what_happens", "")
        
        if "sales" in domain.lower() or "pitch" in what_happens.lower():
            return "PERSUASION"
        elif "help" in what_happens.lower() or "problem" in what_happens.lower():
            return "HELP_SEEKING"
        elif "bias" in domain.lower() or "conflict" in what_happens.lower():
            return "CONFRONTATION"
        
        return None
    
    @staticmethod
    def _check_location_consistency(persona: PersonaInstanceV2) -> List[str]:
        """Check if location is consistent across all fields"""
        issues = []
        
        main_city = persona.location.city
        main_state = persona.location.state
        
        # Check professional_context if exists
        prof_context = persona.detail_categories.get("professional_context", {})
        if "location" in prof_context:
            prof_location = prof_context["location"]
            if main_city not in prof_location and main_state not in prof_location:
                issues.append(f"Location mismatch: base={main_city}, {main_state} but professional_context={prof_location}")
        
        return issues
    
    @staticmethod
    def _check_required_categories(persona: PersonaInstanceV2, template_data: Dict[str, Any]) -> List[str]:
        """Check if required categories are present"""
        archetype = template_data.get("archetype_classification", {}).get("primary_archetype", "")
        domain = template_data.get("general_info", {}).get("domain", "")
        
        required = []
        
        if archetype == "PERSUASION":
            required.append("decision_criteria")
        
        if "sales" in domain.lower() or "pharmaceutical" in domain.lower():
            required.extend(["time_constraints", "sales_rep_history"])
        
        missing = [cat for cat in required if cat not in persona.detail_categories_included]
        return missing
    
    @staticmethod
    def _check_conversation_context(persona: PersonaInstanceV2, template_data: Dict[str, Any]) -> List[str]:
        """Check if conversation rules match scenario context"""
        issues = []
        
        assess_mode = template_data.get("mode_descriptions", {}).get("assess_mode", {})
        learner_role = assess_mode.get("learner_role", "")
        archetype = persona.archetype
        
        conv_rules = persona.conversation_rules
        opening = conv_rules.get("opening_behavior", "")
        response_style = conv_rules.get("response_style", "")
        
        # Check for PERSUASION archetype issues
        if archetype == "PERSUASION":
            if "patient" in opening.lower() or "patient" in response_style.lower():
                if learner_role and "patient" not in learner_role.lower():
                    issues.append("Conversation mentions 'patient' but learner is not a patient - likely confusion")
        
        return issues
    
    @staticmethod
    def auto_fix(persona: PersonaInstanceV2, issues: List[str]) -> PersonaInstanceV2:
        """Attempt to auto-fix common issues"""
        
        # Fix location consistency
        if any("Location mismatch" in issue for issue in issues):
            main_city = persona.location.city
            main_state = persona.location.state
            
            if "professional_context" in persona.detail_categories:
                persona.detail_categories["professional_context"]["location"] = f"{main_city}, {main_state}, India"
        
        return persona
