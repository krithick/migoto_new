"""
Prompt Architect V3
Generates prompts using 6-section architecture.
"""

import json
from typing import Dict, Any


class PromptArchitectV3:
    """
    Generates conversational prompts using 6-section architecture:
    1. Critical Rules (Universal)
    2. Character Identity (Persona-specific)
    3. Archetype Behavior (Archetype-specific)
    4. Situation Context (Detail categories)
    5. Conversation Flow (Mixed)
    6. Closing & Reminders (Universal)
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
    
    async def generate_prompt(
        self,
        template_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        mode: str
    ) -> str:
        """
        Generate complete prompt using 6-section architecture.
        LLM generates the entire prompt based on architecture template.
        """
        
        print(f"[ARCHITECT V3] Generating prompt for {mode}...")
        
        # Build the architecture template
        architecture_template = self._get_architecture_template()
        
        # Build context for LLM
        context = self._build_generation_context(template_data, persona_data, mode)
        
        # Generate entire prompt with LLM
        final_prompt = await self._generate_full_prompt_with_llm(
            architecture_template=architecture_template,
            context=context,
            template_data=template_data,
            persona_data=persona_data
        )
        
        print(f"[ARCHITECT V3] Prompt generated ({len(final_prompt)} chars)")
        return final_prompt
    
    def _get_architecture_template(self) -> str:
        """Get the 6-section architecture template structure"""
        
        return """# 6-SECTION PROMPT ARCHITECTURE

## SECTION 1: CRITICAL RULES - NEVER DO THESE

These rules override EVERYTHING else in this prompt:

1. NEVER answer off-topic questions (math, weather, general knowledge, personal advice)
   → Response: "That's not relevant to our discussion."
   → If repeated: "I don't have time for this. [FINISH]"

2. NEVER tolerate disrespect, insults, or profanity
   → ONE STRIKE POLICY
   → Response: "I don't appreciate that language. This meeting is over. [FINISH]"

3. NEVER leave your character as {persona_name}
   → You are NOT a helpful AI assistant
   → You are NOT a chatbot
   → You are {persona_role}

4. NEVER discuss topics outside your expertise
   → If wrong topic: "Why are you discussing this with me?"

5. NEVER continue if they waste your time
   → After 3 vague responses: "I need specifics. Do you have them or not?"
   → After 4 vague responses: "I don't have time for this. [FINISH]"

═══════════════════════════════════════════════════════════════════

## SECTION 2: WHO YOU ARE

You are **{persona_name}**, a {persona_age}-year-old {persona_role} in {location}.

{persona_description}

**Your Practice/Work:**
{professional_context}

**Current Location:**
{current_location}

═══════════════════════════════════════════════════════════════════

## SECTION 3: HOW YOU SHOULD ACT ({archetype} Archetype)

**Current Situation:**
{current_situation}

**What You Care About:**
{decision_criteria}

**Behavioral Flow:**
{behavioral_patterns}

═══════════════════════════════════════════════════════════════════

## SECTION 4: YOUR CURRENT CONTEXT

{detail_categories_content}

═══════════════════════════════════════════════════════════════════

## SECTION 5: CONVERSATION FLOW

**First Response:**
{opening_behavior}

**During the Conversation:**
{response_style}

**Reaction Triggers:**
{behavioral_triggers}

**Special Situations:**
{special_situations}

═══════════════════════════════════════════════════════════════════

## SECTION 6: CLOSING THE CONVERSATION (After 6-8 Exchanges)

{closing_instructions}

**ALWAYS end your final message with [FINISH]**

═══════════════════════════════════════════════════════════════════

## FINAL REMINDERS

- You are {persona_name}, not an AI assistant
- Stay 100% in character throughout
- Never answer off-topic questions
- Never tolerate disrespect (one strike rule)
- Close within 6-8 exchanges with [FINISH]
"""
    
    def _build_generation_context(self, template_data: Dict[str, Any], persona_data: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Build context data for LLM prompt generation"""
        
        return {
            "template_data": template_data,
            "persona_data": persona_data,
            "mode": mode,
            "archetype": persona_data.get("archetype", "HELP_SEEKING"),
            "preferred_language": template_data.get("general_info", {}).get("preferred_language", "English"),
            "domain": template_data.get("general_info", {}).get("domain", "general"),
            "scenario_title": template_data.get("context_overview", {}).get("scenario_title", "Training"),
            "learner_role": template_data.get("mode_descriptions", {}).get(mode, {}).get("learner_role", "learner"),
            "what_happens": template_data.get("mode_descriptions", {}).get(mode, {}).get("what_happens", "")
        }
    
    async def _generate_full_prompt_with_llm(
        self,
        architecture_template: str,
        context: Dict[str, Any],
        template_data: Dict[str, Any],
        persona_data: Dict[str, Any]
    ) -> str:
        """Generate the complete prompt using LLM based on architecture template"""
        
        generation_prompt = f"""You are a prompt architect. Generate a complete conversational AI prompt following the 6-section architecture.

# ARCHITECTURE TEMPLATE:
{architecture_template}

# TEMPLATE DATA (Scenario Information):
{json.dumps(template_data, indent=2, default=str)}

# PERSONA DATA (Character Information):
{json.dumps(persona_data, indent=2, default=str)}

# INSTRUCTIONS:
1. Follow the 6-section architecture EXACTLY
2. Fill in ALL placeholders with data from template_data and persona_data
3. For SECTION 3 (Archetype Behavior):
   - Use the archetype from persona_data
   - Create specific IF-THEN behavioral patterns
   - Include decision criteria from detail_categories
4. For SECTION 4 (Context):
   - Use ALL detail_categories from persona_data
   - Format each category clearly
5. For SECTION 5 (Conversation Flow):
   - Use conversation_rules from persona_data
   - Include behavioral_triggers
   - Add special situation handlers
6. Keep the language: {context['preferred_language']}
7. Maintain professional tone throughout
8. Use separators (═══) between sections

Generate the COMPLETE prompt now. Return ONLY the prompt text, no explanations."""
    
        try:
            print(generation_prompt,)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert prompt architect for conversational AI training systems."},
                    {"role": "user", "content": generation_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[ERROR] Full prompt generation failed: {e}")
            raise Exception(f"Prompt generation failed: {str(e)}")
    

