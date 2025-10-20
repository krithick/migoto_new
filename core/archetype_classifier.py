"""
Archetype Classifier - Determines which archetype a scenario belongs to
"""

import json
import re
from typing import Dict, Any
from openai import AsyncAzureOpenAI

from models.archetype_models import (
    ArchetypeClassificationResult,
    ScenarioArchetype,
    ConversationPattern
)


class ArchetypeClassifier:
    """Classifies scenarios into archetypes using LLM"""
    
    def __init__(self, llm_client: AsyncAzureOpenAI, model: str = "gpt-4o"):
        self.llm_client = llm_client
        self.model = model
    
    async def classify_scenario(self, scenario_document: str, template_data: Dict[str, Any] = None) -> ArchetypeClassificationResult:
        """Classify scenario into archetype"""
        
        # Use hardcoded archetype descriptions (no DB dependency)
        from core.archetype_definitions import ARCHETYPE_DEFINITIONS
        archetype_defs = list(ARCHETYPE_DEFINITIONS.values())
        
        # Build classification prompt
        archetype_descriptions = "\n\n".join([
            f"{i+1}. {ad.name.upper()} ({ad.id})\n"
            f"   Description: {ad.description}\n"
            f"   Keywords: {', '.join(ad.extraction_keywords[:5])}\n"
            f"   Patterns: {', '.join(ad.extraction_patterns)}"
            for i, ad in enumerate(archetype_defs)
        ])
        
        classification_prompt = f"""Analyze this training scenario and classify it into ONE archetype.

SCENARIO DOCUMENT:
{scenario_document}

AVAILABLE ARCHETYPES:
{archetype_descriptions}

CLASSIFICATION RULES:
1. HELP_SEEKING: Character explicitly has a problem they want solved
2. PERSUASION: Character has NO problem, learner must CREATE interest
3. CONFRONTATION: Someone did something wrong, needs accountability
4. INVESTIGATION: Character has information, learner must extract it
5. NEGOTIATION: Both parties want different things, must compromise

VALID conversation_pattern VALUES (use EXACTLY these):
- "learner_initiates" (learner starts: sales, confrontation)
- "character_initiates" (character starts: help-seeking, victim)
- "mutual" (both can start: negotiation)

Return ONLY valid JSON:
{{
    "primary_archetype": "PERSUASION",
    "sub_archetype": "PHARMA_SALES" or null,
    "confidence": 0.95,
    "reasoning": "Doctor has no problem, learner must create interest in new medication",
    "conversation_pattern": "learner_initiates",
    "persona_schema_needed": "persuasion",
    "alternative_archetypes": {{"HELP_SEEKING": 0.05}},
    "detected_keywords": ["sales", "pitch", "objections"],
    "detected_patterns": ["Character satisfied with current solution"]
}}
"""
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at classifying training scenarios."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        try:
            if result_text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    result_dict = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from markdown")
            else:
                result_dict = json.loads(result_text)
            
            # Normalize conversation_pattern (handle common variations)
            conv_pattern = result_dict["conversation_pattern"].lower()
            if "mutual" in conv_pattern or "both" in conv_pattern:
                conv_pattern = "mutual"
            elif "learner" in conv_pattern:
                conv_pattern = "learner_initiates"
            elif "character" in conv_pattern:
                conv_pattern = "character_initiates"
            
            # Convert to ArchetypeClassificationResult
            return ArchetypeClassificationResult(
                primary_archetype=ScenarioArchetype(result_dict["primary_archetype"]),
                sub_archetype=result_dict.get("sub_archetype"),
                confidence_score=result_dict["confidence"],
                reasoning=result_dict["reasoning"],
                conversation_pattern=ConversationPattern(conv_pattern),
                persona_schema_needed=result_dict["persona_schema_needed"],
                alternative_archetypes=result_dict.get("alternative_archetypes", {}),
                detected_keywords=result_dict.get("detected_keywords", []),
                detected_patterns=result_dict.get("detected_patterns", [])
            )
            
        except Exception as e:
            print(f"Classification parsing error: {e}")
            # Fallback to HELP_SEEKING
            return ArchetypeClassificationResult(
                primary_archetype=ScenarioArchetype.HELP_SEEKING,
                sub_archetype=None,
                confidence_score=0.5,
                reasoning=f"Classification failed, defaulting to HELP_SEEKING. Error: {str(e)}",
                conversation_pattern=ConversationPattern.CHARACTER_INITIATES,
                persona_schema_needed="help_seeking",
                alternative_archetypes={},
                detected_keywords=[],
                detected_patterns=[]
            )
