"""
Template Utilities

Utility functions for working with scenario templates and personas.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel
from models.persona_models import PersonaDB
import re
import json


def extract_json_template(template_content: str) -> Dict[str, Any]:
    """
    Extract JSON template from OpenAI response
    """
    json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
    template_json = {}
    
    if json_match:
        try:
            template_json = json.loads(json_match.group(1))
            
            # Ensure persona and language placeholders exist
            if "PERSONA_PLACEHOLDER" not in template_json:
                template_json["PERSONA_PLACEHOLDER"] = "[PERSONA_DETAILS]"
            if "LANGUAGE_PLACEHOLDER" not in template_json:
                template_json["LANGUAGE_PLACEHOLDER"] = "[LANGUAGE_INSTRUCTIONS]"
        except json.JSONDecodeError:
            raise ValueError("Failed to parse template JSON")
    
    return template_json


def extract_markdown_template(template_content: str) -> str:
    """
    Extract Markdown template from OpenAI response
    """
    markdown_match = re.search(r'```markdown\s*(.*?)\s*```', template_content, re.DOTALL)
    template_markdown = ""
    
    if markdown_match:
        template_markdown = markdown_match.group(1)
        
        # Ensure markdown contains the placeholders
        if "[PERSONA_PLACEHOLDER]" not in template_markdown:
            # Try to find where to insert the placeholder
            if "## Character Details" in template_markdown:
                template_markdown = template_markdown.replace(
                    "## Character Details", 
                    "## Character Details\n\n[PERSONA_PLACEHOLDER]"
                )
            elif "## Character Background" in template_markdown:
                template_markdown = template_markdown.replace(
                    "## Character Background", 
                    "## Character Background\n\n[PERSONA_PLACEHOLDER]"
                )
            else:
                # Insert after Core Character Rules section
                rules_pattern = r"(## Core Character Rules.*?)(##)"
                replacement = r"\1\n\n## Character Details\n\n[PERSONA_PLACEHOLDER]\n\n\2"
                template_markdown = re.sub(rules_pattern, replacement, template_markdown, flags=re.DOTALL)
        
        if "[LANGUAGE_PLACEHOLDER]" not in template_markdown:
            if "## Language Instructions" in template_markdown:
                template_markdown = template_markdown.replace(
                    "## Language Instructions", 
                    "## Language Instructions\n\n[LANGUAGE_PLACEHOLDER]"
                )
            else:
                # Insert after Character Details section
                details_pattern = r"(## Character Details.*?)(##)"
                replacement = r"\1\n\n## Language Instructions\n\n[LANGUAGE_PLACEHOLDER]\n\n\2"
                template_markdown = re.sub(details_pattern, replacement, template_markdown, flags=re.DOTALL)
    
    return template_markdown


def inject_persona(scenario_prompt: str, persona: PersonaDB) -> str:
    """
    Replace the persona placeholder with details from a persona document
    """
    # Format persona details as markdown
    persona_markdown = f"""
- Name: {persona.name}
- Type: {persona.persona_type}
- Gender: {persona.gender}
- Goal: {persona.character_goal}
- Location: {persona.location}
- Description: {persona.description}
- Details: {persona.persona_details}
- Current situation: {persona.situation}
- Context: {persona.business_or_personal}
"""
    
    # Add background story if available
    if persona.background_story:
        persona_markdown += f"- Background: {persona.background_story}\n"
    
    return scenario_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)


def inject_language_info(scenario_prompt: str, language_data: Dict[str, Any]) -> str:
    """
    Replace the language placeholder with language information
    """
    language_markdown = f"""
- Primary language: {language_data.get('name', 'English')}
- Language code: {language_data.get('code', 'en')}
"""
    
    return scenario_prompt.replace("[LANGUAGE_PLACEHOLDER]", language_markdown)


def convert_template_to_markdown(template: Dict[str, Any]) -> str:
    """
    Convert a template dictionary to markdown format, preserving placeholders
    """
    # Basic template structure
    markdown = f"""# {template.get("SCENARIO_NAME", "[SCENARIO_NAME]")} Bot - Role Play Scenario

## Core Character Rules

- You are an AI playing the role of a {template.get("CUSTOMER_ROLE", "[CUSTOMER_ROLE]")}
- NEVER play the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s role - only respond as the customer
- Maintain a natural, conversational tone throughout
- NEVER suggest the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} "reach out to you" - you're the one seeking service
- Keep your responses under {template.get("MAX_RESPONSE_LENGTH", "[MAX_RESPONSE_LENGTH]")} words

## Character Details

[PERSONA_PLACEHOLDER]

## Language Instructions

[LANGUAGE_PLACEHOLDER]

## Conversation Flow

Begin by {template.get("CONVERSATION_STARTER", "[CONVERSATION_STARTER]")}. As the conversation progresses, gradually introduce more details about {template.get("KEY_DETAILS_TO_INTRODUCE", "[KEY_DETAILS_TO_INTRODUCE]")}. Ask about {template.get("INITIAL_INQUIRY", "[INITIAL_INQUIRY]")}.

## Demographic-Specific Context

{template.get("DEMOGRAPHIC_DESCRIPTION", "[DEMOGRAPHIC_DESCRIPTION]")}

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any of these topics (not as a checklist, but as part of an organic conversation):

"""

    # Add topics
    topics = template.get("TOPICS", [])
    for i, topic in enumerate(topics):
        if i < 8:  # Ensure we only add up to 8 topics
            markdown += f"- {topic}\n"
    
    # Add remaining sections
    markdown += f"""
## Fact-Checking the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s Responses

Compare the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s responses with the following facts about the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")}:

### {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")} Facts:

"""

    # Add facts
    facts = template.get("FACTS", [])
    for i, fact in enumerate(facts):
        if i < 8:  # Ensure we only add up to 8 facts
            markdown += f"- {fact}\n"
    
    # Add the rest of the template
    markdown += f"""
## When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} provides information that contradicts these facts:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the discrepancy [CORRECT]
4. Example: "{template.get("EXAMPLE_CUSTOMER_RESPONSE", "[EXAMPLE_CUSTOMER_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_CORRECTION", "[EXAMPLE_CORRECTION]")} [CORRECT]"

### If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the issue [CORRECT]
4. Example: "{template.get("EXAMPLE_UNCOOPERATIVE_RESPONSE", "[EXAMPLE_UNCOOPERATIVE_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_UNCOOPERATIVE_CORRECTION", "[EXAMPLE_UNCOOPERATIVE_CORRECTION]")} [CORRECT]"

# Handling Uncooperative {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}

- If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is unhelpful, vague, or unwilling to provide information:
  - First attempt: Politely repeat your request, emphasizing its importance
  - Example: "{template.get("EXAMPLE_POLITE_REPEAT", "[EXAMPLE_POLITE_REPEAT]")}"
  - If still unhelpful:
    - Express disappointment professionally
    - Move to the negative closing for uncooperative staff
    - Example: "{template.get("EXAMPLE_DISAPPOINTMENT_CLOSING", "[EXAMPLE_DISAPPOINTMENT_CLOSING]")} [FINISH]"

## Important Instructions

- When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} recommends a specific {template.get("PRODUCT_TYPE", "[PRODUCT_TYPE]")}:
  - Ask follow-up questions to determine if it suits your {template.get("NEEDS_TYPE", "[NEEDS_TYPE]")}
  - Get clarity on all features, especially focusing on {template.get("KEY_FEATURES", "[KEY_FEATURES]")}
  - Ensure you understand {template.get("IMPORTANT_POLICIES", "[IMPORTANT_POLICIES]")}

## Conversation Closing (Important)

- Positive closing (if you're satisfied with information and service): "{template.get("POSITIVE_CLOSING_TEXT", "[POSITIVE_CLOSING_TEXT]")} [FINISH]"
- Negative closing (if the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE]")} doesn't meet your needs): "{template.get("NEGATIVE_CLOSING_NEEDS_TEXT", "[NEGATIVE_CLOSING_NEEDS_TEXT]")} [FINISH]"
- Negative closing (if {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} was unhelpful/uncooperative): "{template.get("NEGATIVE_CLOSING_SERVICE_TEXT", "[NEGATIVE_CLOSING_SERVICE_TEXT]")} [FINISH]"
- Neutral closing (if you're somewhat satisfied but have reservations): "{template.get("NEUTRAL_CLOSING_TEXT", "[NEUTRAL_CLOSING_TEXT]")} [FINISH]"
"""
    
    return markdown


class TemplateValidator(BaseModel):
    """
    Validator for scenario templates
    """
    template: Dict[str, Any]
    
    def validate(self) -> List[str]:
        """
        Validate the template and return a list of issues
        """
        issues = []
        
        # Check for required fields
        required_fields = [
            "SCENARIO_NAME", 
            "CUSTOMER_ROLE", 
            "SERVICE_PROVIDER_ROLE",
            "MAX_RESPONSE_LENGTH",
            "PERSONA_PLACEHOLDER",
            "LANGUAGE_PLACEHOLDER"
        ]
        
        for field in required_fields:
            if field not in self.template:
                issues.append(f"Missing required field: {field}")
        
        # Check that topics and facts are lists
        if "TOPICS" in self.template and not isinstance(self.template["TOPICS"], list):
            issues.append("TOPICS should be a list")
        
        if "FACTS" in self.template and not isinstance(self.template["FACTS"], list):
            issues.append("FACTS should be a list")
        
        # Check for the presence of closing options
        closing_fields = [
            "POSITIVE_CLOSING_TEXT",
            "NEGATIVE_CLOSING_NEEDS_TEXT",
            "NEGATIVE_CLOSING_SERVICE_TEXT",
            "NEUTRAL_CLOSING_TEXT"
        ]
        
        missing_closings = [field for field in closing_fields if field not in self.template]
        if missing_closings:
            issues.append(f"Missing closing options: {', '.join(missing_closings)}")
        
        return issues


def get_template_fields_for_frontend() -> List[Dict[str, Any]]:
    """
    Return a list of template fields to be used in frontend forms
    """
    return [
        {
            "name": "SCENARIO_NAME",
            "description": "Human-readable name for this scenario",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Bank Account Customer"
        },
        {
            "name": "CUSTOMER_ROLE",
            "description": "Description of who the bot is playing",
            "type": "text",
            "required": True,
            "placeholder": "e.g., customer interested in opening a bank account"
        },
        {
            "name": "SERVICE_PROVIDER_ROLE",
            "description": "Description of who the bot is talking to",
            "type": "text",
            "required": True,
            "placeholder": "e.g., bank staff"
        },
        {
            "name": "MAX_RESPONSE_LENGTH",
            "description": "Maximum response length in words",
            "type": "number",
            "required": True,
            "default_value": "50"
        },
        {
            "name": "CONVERSATION_STARTER",
            "description": "How the conversation begins",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., asking about account options"
        },
        {
            "name": "KEY_DETAILS_TO_INTRODUCE",
            "description": "Important details to gradually introduce",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., your business needs, transaction volume, etc."
        },
        {
            "name": "INITIAL_INQUIRY",
            "description": "First specific question to ask",
            "type": "text",
            "required": True,
            "placeholder": "e.g., account types available for small businesses"
        },
        {
            "name": "DEMOGRAPHIC_DESCRIPTION",
            "description": "Details about the demographic context",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., urban area with diverse banking needs"
        },
        {
            "name": "PRODUCT_OR_SERVICE_NAME",
            "description": "The product or service being discussed",
            "type": "text",
            "required": True,
            "placeholder": "e.g., Business Banking Accounts"
        },
        {
            "name": "PRODUCT_TYPE",
            "description": "Type of product or recommendation",
            "type": "text",
            "required": True,
            "placeholder": "e.g., account type"
        },
        {
            "name": "NEEDS_TYPE",
            "description": "Type of needs or requirements",
            "type": "text",
            "required": True,
            "placeholder": "e.g., business banking needs"
        },
        {
            "name": "KEY_FEATURES",
            "description": "Important features to focus on",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., transaction fees, minimum balance, online banking features"
        },
        {
            "name": "IMPORTANT_POLICIES",
            "description": "Policies to understand",
            "type": "textarea",
            "required": True,
            "placeholder": "e.g., withdrawal limits, account closure conditions"
        }
    ]


def replace_name(original_text: str, name: str) -> str:
    """
    Replace [Your Name] with the provided name
    """
    if "[Your Name]" in original_text:
        return original_text.replace("[Your Name]", name)
    return original_text