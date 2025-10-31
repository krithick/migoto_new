"""V2 Prompt Generation with SSE"""
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
from datetime import datetime
import asyncio
import json

from database import get_db
from core.user import get_current_user
from models.user_models import UserDB
from core.prompt_generation_job import PromptGenerationJobManager
from core.system_prompt_generator import SystemPromptGenerator
from core.learn_mode_prompt_generator import LearnModePromptGenerator
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
import os

load_dotenv(".env")

router = APIRouter(prefix="/scenario/v2", tags=["Prompt Generation V2"])

azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)

@router.post("/generate-final-prompts")
async def generate_final_prompts_v2(
    template_id: str = Body(...),
    try_assess_persona_id: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Start async prompt generation (learn sync + try/assess async)"""
    try:
        # Get template for learn mode
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        
        # Generate learn prompt synchronously (no persona)
        learn_prompt_gen = LearnModePromptGenerator(azure_openai_client, model="gpt-4o")
        learn_prompt = await learn_prompt_gen.generate_trainer_prompt(template_data)
        
        # Create job for try/assess persona
        persona_ids = [try_assess_persona_id]
        mode_mapping = {
            try_assess_persona_id: "assess_mode"  # Same prompt for try+assess
        }
        job_id = PromptGenerationJobManager.create_job(template_id, persona_ids)
        
        # Start background task for try/assess
        asyncio.create_task(
            generate_prompts_background(job_id, template_id, persona_ids, mode_mapping, db)
        )
        
        return {
            "job_id": job_id,
            "learn_prompt": learn_prompt,
            "message": "Prompt generation started",
            "status": "processing",
            "sse_endpoint": f"/scenario/v2/prompt-generation-status/{job_id}",
            "persona_count": len(persona_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_prompts_background(
    job_id: str,
    template_id: str,
    persona_ids: List[str],
    mode_mapping: Dict[str, str],
    db: Any
):
    """Background task to generate prompts"""
    try:
        # Get template
        template = await db.templates.find_one({"id": template_id})
        if not template:
            await PromptGenerationJobManager.send_event(job_id, {
                "type": "status_update",
                "status": "failed",
                "error": "Template not found"
            })
            return
        
        template_data = template.get("template_data", {})
        
        # Initialize generators
        system_prompt_gen = SystemPromptGenerator(azure_openai_client, model="gpt-4o")
        learn_prompt_gen = LearnModePromptGenerator(azure_openai_client, model="gpt-4o")
        
        results = {
            "template_id": template_id,
            "template_data": template_data,
            "personas": {},
            "total_personas": len(persona_ids),
            "successful": 0,
            "failed": 0
        }
        
        # Generate prompts for each persona
        for persona_id in persona_ids:
            mode = mode_mapping.get(persona_id, "assess_mode")
            
            # Send progress event
            await PromptGenerationJobManager.send_event(job_id, {
                "type": "persona_progress",
                "persona_id": persona_id,
                "status": "processing"
            })
            
            try:
                # Get persona (check V2 first with _id, then V1 with id)
                persona = await db.personas_v2.find_one({"_id": str(persona_id)})
                if not persona:
                    persona = await db.personas.find_one({"id": str(persona_id)})
                if not persona:
                    raise Exception(f"Persona not found: {persona_id}")
                
                # Convert UUID and datetime objects to strings for JSON serialization
                from datetime import datetime as dt
                def convert_to_json_serializable(obj):
                    if isinstance(obj, dict):
                        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_to_json_serializable(item) for item in obj]
                    elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'UUID':
                        return str(obj)
                    elif isinstance(obj, dt):
                        return obj.isoformat()
                    return obj
                
                persona = convert_to_json_serializable(persona)
                
                # Debug: Check if persona is still a dict
                if not isinstance(persona, dict):
                    raise Exception(f"Persona conversion failed - got {type(persona).__name__} instead of dict")
                
                # Generate prompt based on mode
                if mode == "learn_mode":
                    prompt = await learn_prompt_gen.generate_trainer_prompt(template_data)
                else:
                    prompt = await system_prompt_gen.generate_system_prompt(
                        template_data=template_data,
                        persona_data=persona,
                        mode=mode
                    )
                
                # Save prompt to persona (update in correct collection)
                if "detail_categories" in persona:
                    # V2 persona - use _id
                    await db.personas_v2.update_one(
                        {"_id": persona_id},
                        {"$set": {
                            "system_prompt": prompt,
                            "prompt_mode": mode,
                            "prompt_generated_at": datetime.now().isoformat()
                        }}
                    )
                else:
                    # V1 persona - use id
                    await db.personas.update_one(
                        {"id": persona_id},
                        {"$set": {
                            "system_prompt": prompt,
                            "prompt_mode": mode,
                            "prompt_generated_at": datetime.now().isoformat()
                        }}
                    )
                
                results["personas"][persona_id] = {
                    "status": "completed",
                    "mode": mode,
                    "prompt_length": len(prompt),
                    "persona_name": persona.get("name", "Unknown") if isinstance(persona, dict) else "Unknown"
                }
                results["successful"] += 1
                
                # Send success event
                await PromptGenerationJobManager.send_event(job_id, {
                    "type": "persona_progress",
                    "persona_id": persona_id,
                    "status": "completed"
                })
                
            except Exception as e:
                results["personas"][persona_id] = {
                    "status": "failed",
                    "error": str(e)
                }
                results["failed"] += 1
                
                await PromptGenerationJobManager.send_event(job_id, {
                    "type": "persona_progress",
                    "persona_id": persona_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Get learn prompt from template (already generated)
        template = await db.templates.find_one({"id": template_id})
        learn_prompt_gen = LearnModePromptGenerator(azure_openai_client, model="gpt-4o")
        learn_prompt = await learn_prompt_gen.generate_trainer_prompt(template.get("template_data", {}))
        
        # Send final results
        await PromptGenerationJobManager.send_event(job_id, {
            "type": "results",
            "learn_prompt": learn_prompt,
            "results": results
        })
        
        # Update job status
        PromptGenerationJobManager.update_job(job_id, {
            "status": "completed",
            "results": results
        })
        
    except Exception as e:
        await PromptGenerationJobManager.send_event(job_id, {
            "type": "status_update",
            "status": "failed",
            "error": str(e)
        })
        PromptGenerationJobManager.update_job(job_id, {
            "status": "failed",
            "error": str(e)
        })


@router.get("/prompt-generation-status/{job_id}")
async def prompt_generation_status_sse(job_id: str):
    """SSE endpoint for real-time updates"""
    
    async def event_generator():
        queue = await PromptGenerationJobManager.get_event_queue(job_id)
        if not queue:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Job not found'})}\n\n"
            return
        
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield f"data: {json.dumps(event)}\n\n"
                
                # Close connection after final results
                if event.get("type") == "results":
                    break
                    
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Polling alternative to SSE"""
    job = PromptGenerationJobManager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
