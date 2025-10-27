"""
Prompt Generator V2
Generates rich system prompts from PersonaInstance data using LLM.
"""

import json
from typing import Dict, Any
from models.persona_models import PersonaInstanceV2


class PromptGeneratorV2:
    """
    Generates system prompts from persona data.
    Uses LLM to create natural, context-rich prompts.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
    
    async def generate_system_prompt(
        self,
        persona: PersonaInstanceV2,
        template_data: Dict[str, Any]
    ) -> str:
        """Generate complete system prompt from persona."""
        
        generation_instructions = self._build_generation_instructions(persona, template_data)
        system_prompt = await self._call_llm_for_prompt_generation(generation_instructions)
        
        return system_prompt
    
    def _build_generation_instructions(
        self,
        persona: PersonaInstanceV2,
        template_data: Dict[str, Any]
    ) -> str:
        """Build instructions for LLM to generate prompt"""
        
        persona_summary = f"""
**Base Identity:**
- Name: {persona.name}
- Age: {persona.age}
- Gender: {persona.gender}
- Role: {persona.role}

**Location:**
{json.dumps(persona.location.dict(), indent=2)}

**Archetype:** {persona.archetype}

**Detail Categories:**
{json.dumps(persona.detail_categories, indent=2)}

**Conversation Rules:**
{json.dumps(persona.conversation_rules, indent=2)}
"""
        
        archetype_instructions = self._get_archetype_instructions(persona.archetype)
        
        instructions = f"""Create a system prompt for an AI training scenario.

**Mode:** {persona.mode}
**Scenario Type:** {persona.scenario_type}

**Persona Data:**
{persona_summary}

**Archetype Behavior:**
{archetype_instructions}

**Your Task:**
Generate a complete system prompt that:

1. Introduces the character with full context
2. Includes ALL relevant details from detail categories naturally
3. Sets behavioral rules based on archetype
4. Adds guardrails:
   - DO NOT answer off-topic questions
   - DO NOT leave character
   - DO NOT tolerate disrespect
5. Specifies conversation flow

Make the persona feel REAL and HUMAN. Use all provided data.

Generate the complete system prompt now."""
        
        return instructions
    
    def _get_archetype_instructions(self, archetype: str) -> str:
        """Get archetype-specific prompt generation instructions"""
        
        instructions = {
            "PERSUASION": """
- Start neutral/polite
- Let THEM explain their product
- Be skeptical of vague claims
- Be receptive to strong data
- Raise objections based on your position
- Close positively if convinced, negatively if not
""",
            "CONFRONTATION": """
- Show emotional authenticity
- React to how learner approaches you
- Escalate if they're dismissive
- Open up if they show empathy
""",
            "HELP_SEEKING": """
- Proactively share your problem
- Be clear about what you need
- Be satisfied if they help
- Be frustrated if they're unhelpful
""",
            "INVESTIGATION": """
- Answer honestly but don't volunteer extra
- Show communication barriers naturally
- Reward good questioning with details
""",
            "NEGOTIATION": """
- State your position clearly
- Protect non-negotiables firmly
- Be flexible on other points
- Look for win-win solutions
"""
        }
        
        return instructions.get(archetype, "Respond naturally based on your character.")
    
    async def _call_llm_for_prompt_generation(self, instructions: str) -> str:
        """Call LLM to generate the system prompt"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create AI system prompts for training scenarios."},
                    {"role": "user", "content": instructions}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[ERROR] Prompt generation failed: {e}")
            return self._fallback_prompt_template(instructions)
    
    def _fallback_prompt_template(self, instructions: str) -> str:
        """Fallback if LLM generation fails"""
        return f"""# Training Scenario

[SYSTEM ERROR: Could not generate full prompt]

{instructions}

Please respond naturally based on the context provided."""
