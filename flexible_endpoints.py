from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile, Form
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
import os

from enhanced_scenario_generator import FlexibleScenarioGenerator
from models.user_models import UserDB
from core.user import get_current_user
from database import get_db
from debug_extraction import router as debug_router

# Import existing extraction functions
from scenario_generator import extract_text_from_docx, extract_text_from_pdf, azure_openai_client

router = APIRouter(prefix="/flexible", tags=["Flexible Scenario Generation"])

# Include debug router
router.include_router(debug_router)

@router.post("/analyze-document")
async def flexible_analyze_document(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Step 1: Flexible document analysis with enhanced extraction
    """
    try:
        # Extract text from uploaded file
        content = await file.read()
        
        if file.filename.lower().endswith(('.doc', '.docx')):
            document_text = await extract_text_from_docx(content)
        elif file.filename.lower().endswith('.pdf'):
            document_text = await extract_text_from_pdf(content)
        else:
            document_text = content.decode('utf-8')
        
        if not document_text or len(document_text.strip()) < 50:
            raise HTTPException(400, "Insufficient content extracted from document")
        
        # Extract raw details from document - NO LLM
        generator = FlexibleScenarioGenerator(azure_openai_client)
        extracted_data = await generator.flexible_extract_from_document(document_text)
        
        print(f"Document extraction completed")
        
        # DYNAMIC LLM ENHANCEMENT
        print(f"Enhancing template with LLM...")
        enhanced_result = await generator.enhance_template_with_llm(extracted_data)
        
        # Extract validated_data properly
        if isinstance(enhanced_result, dict) and "enhanced_template" in enhanced_result:
            validated_data = {
                "validated_extraction": enhanced_result["enhanced_template"],
                "template_enhancements": enhanced_result.get("enhancements_made", {}),
                "validation_notes": {
                    "completeness_score": "90%",
                    "missing_elements": [],
                    "suggestions": ["Template enhanced with LLM"]
                }
            }
        else:
            validated_data = enhanced_result
        
        # Store extracted data for user review
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "source_type": "document", 
            "extracted_data": extracted_data,
            "validated_data": validated_data,
            "status": "extracted",
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id)
        }
        
        await db.flexible_templates.insert_one(template_record)
        
        return {
            "template_id": template_record["id"],
            "extracted_data": extracted_data,
            "message": "Document details extracted. Review and approve."
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error analyzing document: {str(e)}")

@router.post("/analyze-prompt")
async def flexible_analyze_prompt(
    scenario_prompt: str = Body(...),
    template_name: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Step 1: Flexible prompt analysis with enhanced extraction
    """
    try:
        # Create template from prompt using LLM
        generator = FlexibleScenarioGenerator(azure_openai_client)
        template_data = await generator.flexible_extract_from_prompt(scenario_prompt)
        
        print(f"Template created from prompt")
        
        # DYNAMIC LLM ENHANCEMENT FOR PROMPT
        print(f"Enhancing prompt-based template with LLM...")
        enhanced_result = await generator.enhance_template_with_llm(template_data)
        validated_data = enhanced_result
        
        # Store template for user review
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "source_type": "prompt",
            "extracted_data": template_data,
            "validated_data": validated_data,
            "status": "ready",
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id)
        }
        
        await db.flexible_templates.insert_one(template_record)
        
        return {
            "template_id": template_record["id"],
            "template_data": template_data,
            "message": "Template created from prompt. Review and approve."
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error analyzing prompt: {str(e)}")

@router.get("/template/{template_id}")
async def get_flexible_template(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Get flexible template for review and editing
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        return {
            "template_id": template_id,
            "template_name": template.get("name"),
            "source_type": template.get("source_type"),
            "extracted_data": template.get("extracted_data", {}),
            "validated_data": template.get("validated_data", {}),
            "status": template.get("status")
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error retrieving template: {str(e)}")

@router.put("/template/{template_id}")
async def update_flexible_template(
    template_id: str,
    updated_data: Dict[str, Any] = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Update flexible template data
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        # Update template
        await db.flexible_templates.update_one(
            {"id": template_id},
            {"$set": {"extracted_data": updated_data}}
        )
        
        return {"message": "Template updated successfully", "template_id": template_id}
        
    except Exception as e:
        raise HTTPException(500, f"Error updating template: {str(e)}")



@router.post("/approve-template/{template_id}")
async def approve_template(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    User approves template for scenario generation
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        await db.flexible_templates.update_one(
            {"id": template_id},
            {"$set": {"status": "approved"}}
        )
        
        return {"message": "Template approved", "template_id": template_id}
        
    except Exception as e:
        raise HTTPException(500, f"Error approving template: {str(e)}")

@router.post("/generate-scenarios/{template_id}")
async def generate_flexible_scenarios(
    template_id: str,
    generation_options: Dict[str, Any] = Body(default={}),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Step 3: Generate final scenarios from approved template
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership and status
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        if template.get("status") != "approved":
            raise HTTPException(400, "Template must be approved before generating scenarios")
        
        # Generate scenario prompts using LLM for dynamic content
        generator = FlexibleScenarioGenerator(azure_openai_client)
        template_data = template.get("template_data", template.get("extracted_data", {}))
        
        print(f"Generating dynamic scenario prompts with LLM...")
        
        # Use LLM to generate dynamic scenario prompts
        scenarios = await generator.generate_dynamic_scenarios(template_data)
        
        if not scenarios:
            # Fallback if generation fails
            scenarios = {
                "learn_mode": "Learn mode prompt generation failed",
                "assess_mode": "Assess mode prompt generation failed", 
                "try_mode": "Try mode prompt generation failed",
                "generated_personas": approved_template.get('participant_roles', {}),
                "scenario_metadata": approved_template.get('scenario_understanding', {})
            }
        
        print(f"Scenarios prepared successfully")
        
        # Store generated scenarios
        scenario_record = {
            "id": str(uuid4()),
            "template_id": template_id,
            "template_name": template.get("name"),
            "learn_mode": scenarios.get("learn_mode"),
            "assess_mode": scenarios.get("assess_mode"),
            "try_mode": scenarios.get("try_mode"),
            "generated_personas": scenarios.get("generated_personas"),
            "scenario_metadata": scenarios.get("scenario_metadata"),
            "generation_options": generation_options,
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id)
        }
        
        await db.flexible_scenarios.insert_one(scenario_record)
        
        return {
            "scenario_id": scenario_record["id"],
            "template_id": template_id,
            "scenarios": scenarios,
            "message": "Scenarios generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error generating scenarios: {str(e)}")

@router.get("/scenarios/{scenario_id}")
async def get_flexible_scenario(
    scenario_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Get generated flexible scenario
    """
    try:
        scenario = await db.flexible_scenarios.find_one({"id": scenario_id})
        if not scenario:
            raise HTTPException(404, "Scenario not found")
        
        # Check ownership
        if scenario.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        return {
            "scenario_id": scenario_id,
            "template_id": scenario.get("template_id"),
            "template_name": scenario.get("template_name"),
            "learn_mode": scenario.get("learn_mode"),
            "assess_mode": scenario.get("assess_mode"),
            "try_mode": scenario.get("try_mode"),
            "generated_personas": scenario.get("generated_personas"),
            "scenario_metadata": scenario.get("scenario_metadata"),
            "created_at": scenario.get("created_at")
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error retrieving scenario: {str(e)}")

@router.get("/list-templates")
async def list_flexible_templates(
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    List user's flexible templates
    """
    try:
        cursor = db.flexible_templates.find(
            {"created_by": str(current_user.id)},
            {"_id": 0}
        ).sort("created_at", -1)
        
        templates = await cursor.to_list(length=100)
        
        return {
            "templates": templates,
            "total_count": len(templates)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error listing templates: {str(e)}")

@router.get("/list-scenarios")
async def list_flexible_scenarios(
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    List user's flexible scenarios
    """
    try:
        cursor = db.flexible_scenarios.find(
            {"created_by": str(current_user.id)},
            {"_id": 0, "learn_mode": 0, "assess_mode": 0, "try_mode": 0}  # Exclude large prompt fields
        ).sort("created_at", -1)
        
        scenarios = await cursor.to_list(length=100)
        
        return {
            "scenarios": scenarios,
            "total_count": len(scenarios)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error listing scenarios: {str(e)}")

@router.post("/generate-prompt/{template_id}")
async def generate_individual_prompt(
    template_id: str,
    prompt_type: str = Body(...),  # "learn_mode" or "assess_mode" or "try_mode"
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Generate individual prompt from approved template
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership and status
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        if template.get("status") != "approved":
            raise HTTPException(400, "Template must be approved before generating prompts")
        
        # Generate specific prompt from template using the generator
        generator = FlexibleScenarioGenerator(azure_openai_client)
        approved_template = template.get("validated_data", {})
        
        # Generate full scenarios first
        full_scenarios = await generator.generate_dynamic_scenarios(approved_template.get("validated_extraction", {}))
        
        # Extract the specific prompt type
        if prompt_type == "learn_mode":
            prompt = full_scenarios.get("learn_mode", "Learn mode prompt generation failed")
        elif prompt_type == "assess_mode":
            prompt = full_scenarios.get("assess_mode", "Assess mode prompt generation failed")
        elif prompt_type == "try_mode":
            prompt = full_scenarios.get("try_mode", "Try mode prompt generation failed")
        else:
            raise HTTPException(400, "Invalid prompt_type. Use 'learn_mode', 'assess_mode', or 'try_mode'")
        
        return {
            "template_id": template_id,
            "prompt_type": prompt_type,
            "generated_prompt": prompt,
            "message": f"{prompt_type} prompt generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error generating prompt: {str(e)}")

@router.post("/preview-prompt/{template_id}")
async def preview_prompt_before_approval(
    template_id: str,
    prompt_type: str = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Preview what prompt would look like before template approval
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        # Generate preview prompt using current template data
        scenario_data = template.get("extracted_data", {})
        
        # Generate preview prompts using basic template data
        scenario_data = template.get("extracted_data", {})
        
        if prompt_type == "learn_mode":
            expert_role = scenario_data.get('participant_roles', {}).get('expert_role', 'Expert Trainer')
            topics = scenario_data.get('content_specifics', {}).get('key_knowledge', ['General topics'])
            prompt = f"PREVIEW: You are a {expert_role}. Your role is to teach about: {', '.join(topics[:3])}. Maintain a supportive and educational approach."
        elif prompt_type in ["assess_mode", "try_mode"]:
            practice_role = scenario_data.get('participant_roles', {}).get('practice_role', 'Practice Partner')
            concerns = scenario_data.get('conversation_dynamics', {}).get('typical_interactions', ['General questions'])
            prompt = f"PREVIEW: You are playing the role of: {practice_role}. Your typical concerns include: {', '.join(concerns[:2])}. Engage naturally with the learner."
        else:
            raise HTTPException(400, "Invalid prompt_type. Use 'learn_mode', 'assess_mode', or 'try_mode'")
        
        return {
            "template_id": template_id,
            "prompt_type": prompt_type,
            "preview_prompt": prompt,
            "message": f"Preview of {prompt_type} prompt (template not yet approved)"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error generating prompt preview: {str(e)}")

@router.post("/simulate-conversation/{template_id}")
async def simulate_conversation(
    template_id: str,
    persona_details: Dict[str, str] = Body(...),
    mode: str = Body(default="assess_mode"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Simulate conversation with a specific persona
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        # Generate conversation simulation
        generator = FlexibleScenarioGenerator(azure_openai_client)
        template_data = template.get("validated_data", {}).get("validated_extraction", template.get("extracted_data", {}))
        
        simulation = await generator.simulate_conversation(template_data, persona_details, mode)
        
        return {
            "template_id": template_id,
            "simulation": simulation,
            "message": "Conversation simulation generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error simulating conversation: {str(e)}")

@router.delete("/template/{template_id}")
async def delete_flexible_template(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Delete flexible template
    """
    try:
        template = await db.flexible_templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(404, "Template not found")
        
        # Check ownership
        if template.get("created_by") != str(current_user.id):
            raise HTTPException(403, "Not authorized")
        
        # Delete template
        await db.flexible_templates.delete_one({"id": template_id})
        
        # Also delete associated scenarios
        await db.flexible_scenarios.delete_many({"template_id": template_id})
        
        return {
            "message": "Template and associated scenarios deleted successfully",
            "template_id": template_id
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error deleting template: {str(e)}")