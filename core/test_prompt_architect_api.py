"""
Test Prompt Architect API
Temporary endpoint to test new 6-section prompt architecture.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict
import os
from openai import AsyncAzureOpenAI

from core.scenario_extractor_v2 import ScenarioExtractorV2
from core.persona_generator_v2 import PersonaGeneratorV2
from core.prompt_architect_v3 import PromptArchitectV3


router = APIRouter(prefix="/test-prompt-architect", tags=["Test Prompt Architect"])


class TestPromptRequest(BaseModel):
    scenario_description: str
    mode: str = "assess_mode"


class TestPromptResponse(BaseModel):
    template_data: Dict[str, Any]
    persona_data: Dict[str, Any]
    final_prompt: str
    stats: Dict[str, Any]


# Initialize Azure OpenAI client
def get_openai_client():
    return AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)


@router.post("/generate", response_model=TestPromptResponse)
async def test_new_prompt_generation(request: TestPromptRequest):
    """
    Test endpoint for new 6-section prompt architecture.
    
    Flow:
    1. Extract template data from scenario description
    2. Generate persona using template data
    3. Generate prompt using 6-section architecture
    4. Return all data for inspection
    """
    
    try:
        client = get_openai_client()
        
        print(f"\n{'='*60}")
        print(f"[TEST API] Starting new prompt generation")
        print(f"[TEST API] Mode: {request.mode}")
        print(f"{'='*60}\n")
        
        # Step 1: Extract template data
        print("[STEP 1] Extracting template data...")
        extractor = ScenarioExtractorV2(client)
        template_data = await extractor.extract_scenario_info(request.scenario_description)
        print(f"[STEP 1] ✓ Template extracted (archetype: {template_data.get('archetype_classification', {}).get('primary_archetype')})")
        
        # Step 2: Generate persona
        print("\n[STEP 2] Generating persona...")
        persona_generator = PersonaGeneratorV2(client)
        persona = await persona_generator.generate_persona(
            template_data=template_data,
            mode=request.mode
        )
        persona_data = persona.dict()
        print(f"[STEP 2] ✓ Persona generated: {persona_data.get('name')} ({persona_data.get('role')})")
        print(f"[STEP 2]   Detail categories: {persona_data.get('detail_categories_included')}")
        
        # Step 3: Generate prompt using new architecture
        print("\n[STEP 3] Generating prompt with 6-section architecture...")
        architect = PromptArchitectV3(client)
        final_prompt = await architect.generate_prompt(
            template_data=template_data,
            persona_data=persona_data,
            mode=request.mode
        )
        print(f"[STEP 3] ✓ Prompt generated ({len(final_prompt)} characters)")
        
        # Stats
        stats = {
            "template_archetype": template_data.get("archetype_classification", {}).get("primary_archetype"),
            "template_confidence": template_data.get("archetype_classification", {}).get("confidence_score"),
            "persona_name": persona_data.get("name"),
            "persona_role": persona_data.get("role"),
            "detail_categories_count": len(persona_data.get("detail_categories_included", [])),
            "detail_categories": persona_data.get("detail_categories_included", []),
            "prompt_length": len(final_prompt),
            "prompt_sections": 6
        }
        
        print(f"\n{'='*60}")
        print(f"[TEST API] ✓ Generation complete!")
        print(f"[TEST API] Archetype: {stats['template_archetype']}")
        print(f"[TEST API] Persona: {stats['persona_name']}")
        print(f"[TEST API] Categories: {stats['detail_categories_count']}")
        print(f"[TEST API] Prompt length: {stats['prompt_length']} chars")
        print(f"{'='*60}\n")
        
        return TestPromptResponse(
            template_data=template_data,
            persona_data=persona_data,
            final_prompt=final_prompt,
            stats=stats
        )
        
    except Exception as e:
        print(f"[ERROR] Test prompt generation failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Test Prompt Architect API is running"}
