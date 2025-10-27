"""
V2 Methods for EnhancedScenarioGenerator
Add these methods to the EnhancedScenarioGenerator class in scenario_generator.py
"""


# ============================================================================
# V2 METHODS - Add these to EnhancedScenarioGenerator class
# ============================================================================

async def generate_personas_from_template_v2(
    self,
    template_data: dict,
    gender: str = '',
    context: str = '',
    archetype_classification: dict = None
) -> dict:
    """
    V2 IMPLEMENTATION: Uses PersonaGeneratorV2 with dynamic categories.
    Safe to call - has fallback to v1 if fails.
    """
    try:
        from core.persona_generator_v2 import PersonaGeneratorV2
        
        persona_gen = PersonaGeneratorV2(self.client, self.model)
        
        # Generate assess mode persona
        assess_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender=gender,
            custom_prompt=context
        )
        
        # Generate learn mode persona
        learn_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="learn_mode",
            gender=gender or "Female",
            custom_prompt=None
        )
        
        print(f"[V2] Generated personas with dynamic categories")
        
        return {
            "learn_mode_expert": learn_persona.dict(),
            "assess_mode_character": assess_persona.dict(),
            "version": "v2"
        }
        
    except Exception as e:
        print(f"[WARN] V2 persona generation failed: {e}")
        print("[INFO] Falling back to V1 generation")
        
        # Fallback to existing v1 method
        return await self.generate_personas_from_template(
            template_data, gender, context, archetype_classification
        )


async def generate_assess_mode_from_template_v2(
    self,
    template_data: dict
) -> str:
    """
    V2 IMPLEMENTATION: Uses PromptGeneratorV2 with PersonaInstanceV2.
    Safe to call - has fallback to v1 if fails.
    """
    try:
        from core.persona_generator_v2 import PersonaGeneratorV2
        from core.prompt_generator_v2 import PromptGeneratorV2
        
        # Generate persona
        persona_gen = PersonaGeneratorV2(self.client, self.model)
        persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode"
        )
        
        # Generate prompt from persona
        prompt_gen = PromptGeneratorV2(self.client, self.model)
        system_prompt = await prompt_gen.generate_system_prompt(
            persona=persona,
            template_data=template_data
        )
        
        print(f"[V2] Generated assess mode prompt with {len(persona.detail_categories)} detail categories")
        
        return system_prompt
        
    except Exception as e:
        print(f"[WARN] V2 prompt generation failed: {e}")
        print("[INFO] Falling back to V1 generation")
        
        # Fallback to existing v1 method
        return await self.generate_assess_mode_from_template(template_data)
