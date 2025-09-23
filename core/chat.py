"""
Enhanced Chat Routes for FastAPI

Routes for handling chat functionality with dynamic avatar interactions and personas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Form, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import json
import re

# Import models and dependencies
from models_old import Message, ChatSession, ChatResponse
from database import get_db
from models.user_models import UserDB , UserRole
from core.user import get_current_user
# Import the new dynamic chat loader system
from dynamic_chat import (
    get_chat_factory,
    initialize_chat_session,
    get_chat_session,
    update_chat_session
)
from core.simple_token_logger import log_token_usage
# Create router
router = APIRouter(tags=["Chat"])

@router.get("/chat/demo", response_class=HTMLResponse)
async def chat_demo():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .word.current { background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px; }
            .play-btn { margin: 10px 0; padding: 8px 16px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
            #chat-container { padding: 20px; font-family: Arial; }
        </style>
    </head>
    <body>
        <div id="chat-container">Loading...</div>
        
        <script>
            let textBuffer = "";
            let audioData = null;
            
            const eventSource = new EventSource('/api/chat/stream?id=1668e186-c86e-456b-a7fc-b3033411c039');
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log(data)
                if (data.complete && data.audio) {
    console.log("Audio received, length:", data.audio.length);
    audioData = data.audio;
} else if (data.complete) {
    console.log("Complete but no audio data");
}
                if (data.response) {
                    textBuffer = data.response;
                    document.getElementById('chat-container').innerHTML = 
                        `<div class="message">${textBuffer}</div>`;
                }
                
                if (data.complete && data.audio) {
                    audioData = data.audio;
                    document.getElementById('chat-container').innerHTML += 
                        `<button class="play-btn" onclick="playSynced()">🔊 Play Synced</button>`;
                    eventSource.close();
                }
            };
            
            function playSynced() {
                const audio = new Audio(`data:audio/wav;base64,${audioData}`);
                const words = textBuffer.split(' ');
                
                audio.addEventListener('loadedmetadata', () => {
                    const timePerWord = audio.duration / words.length;
                    
                    const container = document.getElementById('chat-container');
                    container.innerHTML = words.map((word, i) => 
                        `<span class="word" data-index="${i}">${word}</span>`
                    ).join(' ');
                    
                    audio.play();
                    
                    words.forEach((word, i) => {
                        setTimeout(() => {
                            document.querySelectorAll('.word').forEach(w => w.classList.remove('current'));
                            const current = document.querySelector(`[data-index="${i}"]`);
                            if (current) current.classList.add('current');
                        }, i * timePerWord * 1000);
                    });
                });
                
                audio.load();
            }
        </script>
    </body>
    </html>
    """

# Chat Routes
@router.post("/chat/initialize")
async def initialize_chat(
    avatar_interaction_id: UUID = Form(...),
    mode: str = Form(...),  # "learn_mode", "try_mode", or "assess_mode"
    persona_id: Optional[UUID] = Form(None),
    avatar_id: Optional[UUID] = Form(None),
    language_id: Optional[UUID] = Form(None),
    db: Any = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)  # Add this dependency
):
    """
    Initialize a new chat session for a specific avatar interaction and mode.
    
    - avatar_interaction_id: ID of the avatar interaction to use
    - mode: Which mode to use (learn_mode, try_mode, assess_mode)
    - persona_id: Optional persona to use for this session
    - language_id: Optional language settings to use
    """
    
    # Validate mode
    if mode not in ["learn_mode", "try_mode", "assess_mode"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Must be 'learn_mode', 'try_mode', or 'assess_mode'"
        )
    
    # If user is not admin/superadmin, check for assignment
    if current_user.role == UserRole.USER:
        # Find the scenario this avatar interaction belongs to
        scenario = None
        # print(current_user)
        # Check learn mode
        learn_mode_scenarios = await db.scenarios.find({
            "learn_mode.avatar_interaction": str(avatar_interaction_id)
        }).to_list(length=1)
        if learn_mode_scenarios:
            scenario = learn_mode_scenarios[0]
            
        # Check try mode if not found
        if not scenario:
            try_mode_scenarios = await db.scenarios.find({
                "try_mode.avatar_interaction": str(avatar_interaction_id)
            }).to_list(length=1)
            if try_mode_scenarios:
                scenario = try_mode_scenarios[0]
        
        # Check assess mode if not found
        if not scenario:
            assess_mode_scenarios = await db.scenarios.find({
                "assess_mode.avatar_interaction": str(avatar_interaction_id)
            }).to_list(length=1)
            if assess_mode_scenarios:
                scenario = assess_mode_scenarios[0]
        
        # If scenario found, check if user is assigned
        if scenario:
            scenario_id = scenario["_id"]
            
            # Check if scenario is assigned to user
            assignment = await db.user_scenario_assignments.find_one({
                "user_id": str(current_user.id),
                "scenario_id": scenario_id
            })
            
            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not assigned to this scenario"
                )
            
            # Check if mode is assigned
            assigned_modes = assignment.get("assigned_modes", [])
            if mode not in assigned_modes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You are not assigned to the {mode} of this scenario"
                )
    
    # Initialize chat session
    session = await initialize_chat_session(db, avatar_interaction_id=avatar_interaction_id, mode=mode, persona_id=persona_id,avatar_id=avatar_id, language_id=language_id,current_user=current_user.id)
    
    # Return session information
    return {
        "id":session.id,
        "scenario_name": session.scenario_name,
        "avatar_interaction_id": str(avatar_interaction_id),
        "mode": mode,
        "persona_id": str(persona_id) if persona_id else None,
        "avatar_id": str(avatar_id) if avatar_id else None,
        "language_id": str(language_id) if language_id else None,
        "created_at": session.created_at
    }



@router.post("/chat")
async def chat(
    message: str = Form(...),
    id: str = Form(...),
    name: Optional[str] = Form(None),
    db: Any = Depends(get_db)
):
    """
    Send a message to the chat system and prepare for streaming response.
    """
    # Get existing session
    session = await get_chat_session(db, id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get the chat factory
    chat_factory = await get_chat_factory()
    
    # Extract avatar_interaction_id from session
    avatar_interaction_id = session.avatar_interaction
    
    # If persona_id is in the request, we'll use it, otherwise check if it's in the session
    persona_id = None
    if hasattr(session, "persona_id") and session.persona_id:
        persona_id = session.persona_id
        # print("self.config.persona_idsss",persona_id)
    # Get the appropriate chat handler - use the mode from the avatar_interaction document
    # You'll need to fetch the avatar_interaction to determine the mode
    persona_id=await db.avatars.find_one({"_id": session.avatar_id})
    # print(persona_id["_id"],"self.config.persona_idasdasdsd")
    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    mode = avatar_interaction["mode"] if avatar_interaction else "try_mode"  # Default to try_mode
    language_id=session.language_id
    # print(persona_id,"self.config.persona_idsss")
    handler = await chat_factory.get_chat_handler(
        avatar_interaction_id=UUID(avatar_interaction_id),
        mode=mode,
        persona_id=UUID(persona_id["_id"]) if persona_id else None,
        language_id=language_id 
    )
    
    # Add user message to conversation history
    user_message = Message(
        role=handler.config.bot_role_alt,
        content=message,
        timestamp=datetime.now()
    )
    
    # Initialize conversation_history if it doesn't exist
    if not hasattr(session, "conversation_history") or session.conversation_history is None:
        session.conversation_history = []
    
    session.conversation_history.append(user_message)
    
    # Update session in database
    await update_chat_session(db, session)
    
    # Return a simple acknowledgment
    return {
        "message": "Message received, processing...",
        "id": id
    }




@router.get("/chat/stream")
async def chat_stream(
    id: str = Query(...),
    name: Optional[str] = Query(None),
    voice_id: Optional[str] = Query(default="ar-SA-HamedNeural"), 
    db: Any = Depends(get_db),
    # current_user: UserDB = Depends(get_current_user)  # Add this dependency
):
    """
    Stream the response for a chat message.
    """
    # Get session
    session = await get_chat_session(db, id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Get the chat factory
    chat_factory = await get_chat_factory()
    
    # Extract avatar_interaction_id and mode from session
    avatar_interaction_id = session.avatar_interaction
    
    # Fetch avatar_interaction to get mode
    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    
    mode = avatar_interaction["mode"] if avatar_interaction else "try_mode"  # Default to try_mode
    print("avatar_interaction",mode)
    # Extract persona_id if available
    avatar = await db.avatars.find_one({"_id": session.avatar_id})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    persona_id = avatar["persona_id"][0]
    language_id = session.language_id
    
    # Get the appropriate chat handler
    handler = await chat_factory.get_chat_handler(
        avatar_interaction_id=UUID(avatar_interaction_id),
        mode=mode,
        persona_id=UUID(persona_id) if persona_id else None,
        language_id=language_id 
    )
    # await handler.initialize_fact_checking(id)
    # Get template data for coaching rules
    try:
        # Get scenario to find template_id
        session = await get_chat_session(db, id)
        if not session or not session.avatar_interaction:
            print("Warning: No session or avatar_interaction found")
            await handler.initialize_fact_checking(id, coaching_rules={})
            return
        avatar_interaction = await db.avatar_interactions.find_one({"_id": str(session.avatar_interaction)})
        if not avatar_interaction:
            print("Warning: Avatar interaction not found")
            await handler.initialize_fact_checking(id, coaching_rules={})
            return
        # Find scenario with this avatar interaction
        scenario = None
        avatar_interaction_id = session.avatar_interaction
        avatar_interaction_str = str(session.avatar_interaction)
        try:
            avatar_interaction_uuid = UUID(avatar_interaction_str)
        except ValueError:
            avatar_interaction_uuid = None
        print(f"🔍 Looking for scenario with avatar_interaction: {avatar_interaction_str}")
        query_conditions = []
        for mode_type in ["learn_mode", "try_mode", "assess_mode"]:
            query_conditions.extend([
            {f"{mode_type}.avatar_interaction": avatar_interaction_str},
            {f"{mode_type}.avatar_interaction": avatar_interaction_uuid} if avatar_interaction_uuid else {}
        ])
            query_conditions = [q for q in query_conditions if q]
            scenario = await db.scenarios.find_one({"$or": query_conditions})
            print(f"🔍 Scenario found: {scenario is not None}")
            if scenario:
                print(f"✅ Found scenario: {scenario.get('_id')}")
        # Get template data
        coaching_rules = {}
        print("scenario.get",scenario.get("template_id"))
        if scenario and scenario.get("template_id"):
            print("step1",scenario.get("template_id"))
            template = await db.templates.find_one({"id": scenario["template_id"]})
            # print("step2",template)
            if template and template.get("template_data"):
                coaching_rules = template["template_data"].get("coaching_rules", {})
                # print("step3",coaching_rules)
    
        await handler.initialize_fact_checking(id, coaching_rules=coaching_rules)
    
    except Exception as e:
        print(f"Warning: Could not load coaching rules: {e}")
        await handler.initialize_fact_checking(id, coaching_rules={})       
    # Get the most recent user message
    if not session.conversation_history:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No conversation history found")
    
    previous_message = session.conversation_history[-1]
    message = previous_message.content
    
    # Process the message and get the response stream
    try:
        response = await handler.process_message(
            message,
            session.conversation_history,
            name
        )
        
        async def stream_chat():
            from core.speech import generate_audio_for_chat
            import base64
            import asyncio
            
            full_text = ""
            audio_task = None
            audio_data = None  # Initialize audio_data
            
            async for chunk in response:
                updated_message = chunk["chunk"]
                full_text = updated_message
                
                # Skip streaming TTS - will generate at the end
                
                # Check if complete
                if chunk["finish"] == "stop" and chunk["usage"] is not None:
                    # Add bot message to conversation history
                    bot_message = Message(
                        role=handler.config.bot_role,
                        content=updated_message,
                        timestamp=datetime.now()
                    )
                    bot_message.usage = chunk["usage"]
                    if chunk.get("fact_check_summary"):
                        bot_message.metadata = {
                            "fact_check_summary": chunk["fact_check_summary"]
                        }
                                        
                    session.conversation_history.append(bot_message)
                    await update_chat_session(db, session)
                    
                    # Generate TTS for complete response (remove [FINISH] tag)
                    try:
                        print(f"🔊 Generating TTS for: '{full_text[:50]}...'")
                        from core.speech import generate_audio_for_chat
                        # Remove [FINISH] tag before generating audio
                        clean_text = full_text.replace("[FINISH]", "").strip()
                        audio_data = await generate_audio_for_chat(clean_text, voice_id)
                        print(f"🔊 TTS result: {len(audio_data) if audio_data else 0} bytes")
                    except Exception as e:
                        print(f"TTS generation failed: {e}")
                        audio_data = None
                
                # Parse for correct formatting tags
                result = re.split(r"\[CORRECT\]", updated_message)
                correct_answer = ''
                if len(result) >= 3:
                    correct_answer = result[1]
                    answer = result[0]
                else:
                    emotion = "neutral"  # Default emotion if parsing fails
                    answer = re.sub(r"\[CORRECT\]","",updated_message)
                
                # Check if this is the end of the conversation
                is_finished = "[FINISH]" in updated_message
                if is_finished:
                    answer = updated_message.replace("[FINISH]", " ")
                    complete = True
                    
                    # Update mode completion
                    try:
                        # Find the scenario that has this avatar interaction
                        scenario_query = {}
                        
                        if mode == "learn_mode":
                            scenario_query = {"learn_mode.avatar_interaction": avatar_interaction_id}
                        elif mode == "try_mode":
                            scenario_query = {"try_mode.avatar_interaction": avatar_interaction_id}
                        elif mode == "assess_mode":
                            scenario_query = {"assess_mode.avatar_interaction": avatar_interaction_id}
                        
                        scenarios = await db.scenarios.find(scenario_query).to_list(length=1)
                        
                        if scenarios:
                            scenario_id = scenarios[0]["_id"]
                            
                            # Update mode completion
                            # await db.user_scenario_assignments.update_one(
                            #     {
                            #         "user_id": str(current_user.id),
                            #         "scenario_id": scenario_id
                            #     },
                            #     {
                            #         "$set": {
                            #             f"mode_progress.{mode}.completed": True,
                            #             f"mode_progress.{mode}.completed_date": datetime.now()
                            #         }
                            #     }
                            # )
                            
                            # # Check if all assigned modes are now completed
                            # assignment = await db.user_scenario_assignments.find_one({
                            #     "user_id": str(current_user.id),
                            #     "scenario_id": scenario_id
                            # })
                            
                            # if assignment:
                            #     # Check if all modes are completed
                            #     assigned_modes = assignment.get("assigned_modes", [])
                            #     mode_progress = assignment.get("mode_progress", {})
                                
                            #     all_modes_completed = True
                            #     for assigned_mode in assigned_modes:
                            #         if assigned_mode not in mode_progress or not mode_progress.get(assigned_mode, {}).get("completed", False):
                            #             all_modes_completed = False
                            #             break
                                
                                # If all modes are completed, mark scenario as completed
                                # if all_modes_completed:
                                #     await db.user_scenario_assignments.update_one(
                                #         {
                                #             "user_id": str(current_user.id),
                                #             "scenario_id": scenario_id
                                #         },
                                #         {
                                #             "$set": {
                                #                 "completed": True,
                                #                 "completed_date": datetime.now()
                                #             }
                                #         }
                                #     )
                                    
                                    # Update module completion
                                    # from core.module_assignment import update_module_completion_status
                                    # await update_module_completion_status(
                                    #     db, 
                                    #     current_user.id, 
                                    #     UUID(assignment.get("module_id"))
                                    # )
                    except Exception as e:
                        print(f"Error updating mode completion: {e}")
                else:
                    complete = False
                
                # Check if correction is needed
                if "[CORRECT]" in updated_message:
                    correct = False
                else:
                    correct = True
                
                # Format the response as a ChatResponse
                chat_response = ChatResponse(
                    id=session.id,
                    response=answer,
                    emotion=emotion if 'emotion' in locals() else "neutral",
                    complete=complete,
                    correct=correct,
                    correct_answer=correct_answer,
                    conversation_history=session.conversation_history
                )
                
                response_data = {
                    "response": chat_response.response,
                    "emotion": getattr(chat_response, 'emotion', 'neutral'),
                    "complete": chat_response.complete,
                    "correct": getattr(chat_response, 'correct', True),
                    "correct_answer": getattr(chat_response, 'correct_answer', ''),
                    "fact_check_summary": getattr(chat_response, 'fact_check_summary', None),
                    "finish": "stop" if chat_response.complete else None
                }
                
                # Add audio data if available and streaming is finished
                if chunk["finish"] == "stop" and audio_data and len(audio_data) > 0:
                    response_data["audio"] = base64.b64encode(audio_data).decode('utf-8')
                    response_data["audio_format"] = "wav"

                if chunk.get("fact_check_summary"):
                    print("chunk.get("")",chunk.get("fact_check_summary"))
                    chat_response.fact_check_summary = chunk["fact_check_summary"]                
                
                yield f"data: {json.dumps(response_data)}\n\n"

                
        return StreamingResponse(stream_chat(), media_type="text/event-stream")
        
    except Exception as e:
        print(f"Error in chat stream: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.get("/chat/history/{id}")
async def get_chat_history(
    id: str,
    db: Any = Depends(get_db)
):
    """
    Get the conversation history for a chat session.
    
    - id: ID of the chat session
    """
    # Get session
    session = await get_chat_session(db, id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return {
        "id":session.id,
        "scenario_name": session.scenario_name,
        # "persona_id": session.persona_id,
        "conversation_history": [msg.dict() for msg in session.conversation_history],
        "created_at": session.created_at,
        "last_updated": session.last_updated
    }


@router.put("/chat/persona/{id}")
async def update_session_persona(
    id: str,
    persona_id: UUID = Body(...),
    db: Any = Depends(get_db)
):
    """
    Update the persona used in a chat session.
    
    - id: ID of the chat session
    - persona_id: ID of the new persona to use
    """
    # Get session
    session = await get_chat_session(db, id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Verify persona exists
    persona = await db.personas.find_one({"_id": str(persona_id)})
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    
    # Update session with new persona
    session.persona_id = str(persona_id)
    await update_chat_session(db, session)
    
    return {
        "id":session.id,
        "persona_id": str(persona_id),
        "message": "Persona updated successfully"
    }


@router.delete("/chat/session/{id}")
async def delete_chat_session(
    id: str,
    db: Any = Depends(get_db)
):
    """
    Delete a chat session.
    
    - id: ID of the chat session to delete
    """
    # Verify session exists
    session = await get_chat_session(db, id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Delete the session
    result = await db.sessions.delete_one({"id": id})
    
    return {
        "success": result.deleted_count > 0,
        "id": id
    }

from uuid import uuid4
import json

# @router.post("/chat/evaluate/{session_id}")
# async def evaluate_conversation(
#     session_id: str,
#     db: Any = Depends(get_db),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """Generate assessment report and update assignment progress"""
    
#     try:
#         # Get session
#         session = await get_chat_session(db, session_id)
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")
        
#         # Get avatar interaction and scenario
#         avatar_interaction_id = session.avatar_interaction
#         avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
        
#         if not avatar_interaction:
#             raise HTTPException(status_code=404, detail="Avatar interaction not found")
        
#         # Find the scenario
#         scenario_query = {}
#         mode = "assess_mode"  # Default
        
#         # Check which mode this avatar interaction belongs to
#         for mode_type in ["learn_mode", "try_mode", "assess_mode"]:
#             scenarios = await db.scenarios.find({f"{mode_type}.avatar_interaction": avatar_interaction_id}).to_list(length=1)
#             if scenarios:
#                 scenario = scenarios[0]
#                 mode = mode_type
#                 break
#         else:
#             raise HTTPException(status_code=404, detail="Scenario not found")
        
#         # Get template data for evaluation criteria
#         template_id = scenario.get("template_id")
#         template = await db.templates.find_one({"id": template_id}) if template_id else None
#         knowledge_base_id = template.get("knowledge_base_id")    
#         # Generate assessment report
#         evaluation_result = await analyze_conversation_with_factcheck(
#             session.conversation_history,
#             template.get("evaluation_metrics", {}) if template else {},
#             knowledge_base_id
#         )
        
#         # Store evaluation result
#         evaluation_record = {
#             "_id": str(uuid4()),
#             "session_id": session_id,
#             "user_id": str(current_user.id),
#             "scenario_id": scenario["_id"],
#             "mode": mode,
#             "evaluation_result": evaluation_result,
#             "evaluated_at": datetime.now(),
#             "evaluated_by": str(current_user.id)
#         }
        
#         await db.analysis.insert_one(evaluation_record)
        
#         # Update assignment with evaluation data
#         assignment_updated = False
#         try:
#             result = await db.user_scenario_assignments.update_one(
#                 {
#                     "user_id": str(current_user.id),
#                     "scenario_id": scenario["_id"]
#                 },
#                 {
#                     "$set": {
#                         f"mode_progress.{mode}.evaluation_completed": True,
#                         f"mode_progress.{mode}.evaluation_date": datetime.now(),
#                         f"mode_progress.{mode}.latest_score": evaluation_result.get("overall_score", 0),
#                         f"mode_progress.{mode}.performance_category": evaluation_result.get("performance_category", "Needs Assessment"),
#                         f"mode_progress.{mode}.evaluation_id": evaluation_record["_id"]
#                     }
#                 }
#             )
#             assignment_updated = result.modified_count > 0
#         except Exception as e:
#             print(f"Error updating assignment: {e}")
        
#         # Update module completion if applicable
#         try:
#             from core.module_assignment import update_module_completion_status
#             # Find module that contains this scenario
#             modules = await db.modules.find({"scenarios": scenario["_id"]}).to_list(length=1)
#             if modules:
#                 module_id = modules[0]["_id"]
#                 await update_module_completion_status(db, current_user.id, UUID(module_id))
#         except Exception as e:
#             print(f"Error updating module completion: {e}")
        
#         return {
#             "session_id": session_id,
#             "evaluation": evaluation_result,
#             "evaluation_id": evaluation_record["_id"],
#             "assignment_updated": assignment_updated,
#             "score": evaluation_result.get("overall_score", 0),
#             "mode": mode
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Error in evaluate_conversation: {e}")
#         raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")



async def analyze_conversation_with_factcheck(
    conversation_history: List[Message],
    evaluation_metrics: Dict[str, Any],
    knowledge_base_id: Optional[str]
) -> Dict[str, Any]:
    """Single prompt analysis + enhanced fact-checking with template coaching rules"""
    
    try:
        from openai import AsyncAzureOpenAI
        import os
        
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        # Build conversation text (your existing code)
        conversation_text = ""
        for msg in conversation_history:
            role = "Learner" if msg.role != "assistant" else "Customer"
            conversation_text += f"{role}: {msg.content}\n"
        
        # Get relevant knowledge for fact-checking (your existing code)
        knowledge_context = ""
        fact_check_results = []  # ✅ ADD: Store detailed fact-check results
        
        if knowledge_base_id:
            from core.azure_search_manager import AzureVectorSearchManager, EnhancedFactChecker
            vector_search = AzureVectorSearchManager()
            
            # ✅ ENHANCED: Initialize fact-checker with empty coaching rules for evaluation
            # (We're not doing real-time coaching here, just thorough analysis)
            fact_checker = EnhancedFactChecker(vector_search, openai_client, coaching_rules={})
            
            # ✅ ADD: Detailed fact-checking of learner responses
            try:
                # Get learner responses (not customer responses)
                learner_responses = [
                    msg.content for msg in conversation_history 
                    if msg.role != "assistant"  # assistant = customer, others = learner
                ]
                
                # Fact-check the last few learner responses
                for response in learner_responses[-3:]:  # Check last 3 learner responses
                    if len(response.strip()) > 10:  # Skip very short responses
                        verifications = await fact_checker.verify_response_claims(
                            response, 
                            knowledge_base_id, 
                            conversation_history=conversation_history  # ✅ Pass conversation context
                        )
                        
                        # Store detailed results
                        for verification in verifications:
                            fact_check_results.append({
                                "claim": verification.claim.get("claim_text", ""),
                                "result": verification.result.value,
                                "confidence": verification.confidence_score,
                                "explanation": verification.explanation,
                                "coaching_feedback": getattr(verification, 'coaching_feedback', None)
                            })
                        
            except Exception as fact_error:
                print(f"Detailed fact-checking error: {fact_error}")
            
            # Your existing search logic (keep this)
            search_results = await vector_search.vector_search(
                conversation_text[:500], knowledge_base_id, top_k=5, openai_client=openai_client
            )
            
            if search_results:
                knowledge_context = "OFFICIAL INFORMATION FOR FACT-CHECKING:\n"
                for result in search_results:
                    knowledge_context += f"- {result['content']}\n"
        
        # ✅ ENHANCED: Build fact-check summary for evaluation prompt
        fact_check_summary = ""
        if fact_check_results:
            fact_errors = [fc for fc in fact_check_results if fc["result"] in ["INCORRECT", "PARTIALLY_CORRECT"]]
            fact_check_summary = f"""
DETAILED FACT-CHECK RESULTS:
- Total claims analyzed: {len(fact_check_results)}
- Factual errors found: {len(fact_errors)}
- Key issues: {[fc["explanation"] for fc in fact_errors[:3]]}
"""
        
        # ✅ ENHANCED: Evaluation prompt with fact-check integration
        evaluation_prompt = f"""
        Analyze this customer service conversation and provide a comprehensive assessment.
        
        CONVERSATION:
        {conversation_text}
        
        {knowledge_context}
        
        {fact_check_summary}
        
        EVALUATION CRITERIA:
        {json.dumps(evaluation_metrics, indent=2) if evaluation_metrics else "Use standard customer service metrics"}
        
        Provide assessment in JSON format:
        {{
            "overall_score": 0-100,
            "performance_category": "Excellent/Good/Satisfactory/Needs Improvement",
            "factual_accuracy": 0-100,
            "metric_scores": {{
                "knowledge_accuracy": 0-100,
                "communication_quality": 0-100,
                "customer_service_skills": 0-100,
                "professionalism": 0-100
            }},
            "strengths": ["strength 1", "strength 2"],
            "areas_for_improvement": ["area 1", "area 2"],
            "recommendations": ["recommendation 1", "recommendation 2"],
            "fact_check_summary": "Summary of any factual errors found",
            "conversation_summary": "Brief summary of what happened"
        }}
        
        IMPORTANT: 
        - Use the detailed fact-check results above to assess factual accuracy
        - If factual errors were found, reflect this in the knowledge_accuracy score
        - Include specific fact-checking findings in your recommendations
        - Focus on practical, actionable feedback
        """
        
        # Your existing LLM call (keep this)
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert training evaluator who provides comprehensive but concise assessments."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        log_token_usage(response, "analyse")
        # Your existing JSON parsing (keep this)
        result_text = response.choices[0].message.content.strip()
        print(f"🔍 LLM Response: {result_text[:200]}...")
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                # Your existing fallback (keep this)
                result = {
                    "overall_score": 50,
                    "performance_category": "Needs Assessment",
                    "factual_accuracy": 50,
                    "metric_scores": {
                        "knowledge_accuracy": 50,
                        "communication_quality": 50,
                        "customer_service_skills": 50,
                        "professionalism": 50
                    },
                    "strengths": ["Assessment could not be completed"],
                    "areas_for_improvement": ["Please try evaluation again"],
                    "recommendations": ["Review conversation and retry assessment"],
                    "fact_check_summary": "Could not analyze due to parsing error",
                    "conversation_summary": "Analysis incomplete",
                    "parsing_error": True,
                    "raw_response": result_text[:500]
                }
        
        # ✅ ENHANCED: Add detailed fact-check data to result
        result["evaluation_method"] = "single_prompt_with_enhanced_factcheck"
        result["knowledge_base_used"] = knowledge_base_id is not None
        result["conversation_length"] = len(conversation_history)
        result["detailed_fact_checks"] = fact_check_results  # ✅ ADD: Detailed fact-check results
        result["fact_check_stats"] = {
            "total_claims": len(fact_check_results),
            "factual_errors": len([fc for fc in fact_check_results if fc["result"] in ["INCORRECT", "PARTIALLY_CORRECT"]]),
            "accuracy_percentage": round(
                (len([fc for fc in fact_check_results if fc["result"] == "CORRECT"]) / len(fact_check_results) * 100) 
                if fact_check_results else 100, 2
            )
        }
        
        return result
        
    except Exception as e:
        print(f"Error in conversation analysis: {e}")
        return {
            "overall_score": 0,
            "error": f"Analysis failed: {str(e)}",
            "conversation_length": len(conversation_history)
        }
        
        
"""
Enhanced Conversation Evaluation System
Provides comprehensive analysis using template success metrics and coaching rules
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

async def enhanced_conversation_evaluation(
    session_id: str,
    db: Any,
    current_user,
    conversation_history: List[Message],
    evaluation_metrics: Dict[str, Any],
    knowledge_base_id: Optional[str],
    template_coaching_rules: Dict = None
) -> Dict[str, Any]:
    """
    Comprehensive conversation evaluation using template success metrics
    """
    
    try:
        from openai import AsyncAzureOpenAI
        import os
        
        openai_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        # Build conversation text
        conversation_text = ""
        learner_responses = []
        customer_responses = []
        
        for msg in conversation_history:
            role = "Learner" if msg.role != "assistant" else "Customer"
            conversation_text += f"{role}: {msg.content}\n"
            
            if msg.role != "assistant":  # Learner responses
                learner_responses.append(msg.content)
            else:  # Customer responses
                customer_responses.append(msg.content)
        
        # Initialize evaluation components
        knowledge_context = ""
        detailed_fact_checks = []
        template_compliance_analysis = {}
        success_metrics_analysis = {}
        
        # ===== ENHANCED FACT-CHECKING WITH COACHING RULES =====
        if knowledge_base_id:
            from core.azure_search_manager import AzureVectorSearchManager, EnhancedFactChecker
            vector_search = AzureVectorSearchManager()
            
            # ✅ FIX: Initialize with template coaching rules
            fact_checker = EnhancedFactChecker(
                vector_search, 
                openai_client, 
                coaching_rules=template_coaching_rules or {}
            )
            
            # Get knowledge context for evaluation
            try:
                search_results = await vector_search.vector_search(
                    conversation_text[:500], knowledge_base_id, top_k=5, openai_client=openai_client
                )
                
                if search_results:
                    knowledge_context = "OFFICIAL INFORMATION FOR EVALUATION:\n"
                    for result in search_results:
                        knowledge_context += f"- {result['content']}\n"
            except Exception as search_error:
                print(f"Knowledge search error: {search_error}")
            
            # ===== DETAILED FACT-CHECKING OF LEARNER RESPONSES =====
            try:
                for i, response in enumerate(learner_responses[-5:]):  # Check last 5 responses
                    if len(response.strip()) > 10:  # Skip very short responses
                        
                        # Use enhanced verification with conversation context
                        if fact_checker.has_coaching_rules:
                            verification = await fact_checker.verify_response_with_coaching(
                                response, conversation_history, knowledge_base_id
                            )
                        else:
                            # Fallback to basic verification
                            verifications = await fact_checker.verify_response_claims(
                                response, knowledge_base_id, conversation_history=conversation_history
                            )
                            verification = verifications[0] if verifications else None
                        
                        if verification:
                            detailed_fact_checks.append({
                                "response_index": len(learner_responses) - 5 + i,
                                "response_text": response[:100] + "..." if len(response) > 100 else response,
                                "claim": verification.claim.get("claim_text", response[:50]),
                                "result": verification.result.value if hasattr(verification.result, 'value') else str(verification.result),
                                "confidence": verification.confidence_score,
                                "explanation": verification.explanation,
                                "coaching_feedback": getattr(verification, 'coaching_feedback', None),
                                "suggested_correction": verification.suggested_correction
                            })
                        
            except Exception as fact_check_error:
                print(f"Detailed fact-checking error: {fact_check_error}")
        
        # ===== TEMPLATE SUCCESS METRICS ANALYSIS =====
        if evaluation_metrics and "success_metrics" in evaluation_metrics:
            success_metrics_analysis = await analyze_success_metrics(
                conversation_history, 
                evaluation_metrics["success_metrics"],
                template_coaching_rules,
                openai_client
            )
        
        # ===== TEMPLATE COMPLIANCE ANALYSIS =====
        if template_coaching_rules:
            template_compliance_analysis = await analyze_template_compliance(
                conversation_history,
                template_coaching_rules,
                openai_client
            )
        
        # ===== BUILD COMPREHENSIVE EVALUATION PROMPT =====
        fact_check_summary = ""
        if detailed_fact_checks:
            errors = [fc for fc in detailed_fact_checks if fc["result"] in ["INCORRECT", "PARTIALLY_CORRECT"]]
            violations = [fc for fc in detailed_fact_checks if "VIOLATION" in fc["result"]]
            
            fact_check_summary = f"""
DETAILED FACT-CHECK RESULTS:
- Total responses analyzed: {len(detailed_fact_checks)}
- Factual errors found: {len(errors)}
- Process violations found: {len(violations)}
- Key coaching insights: {[fc.get("coaching_feedback", "None") for fc in detailed_fact_checks[:3] if fc.get("coaching_feedback")]}
"""
        
        template_summary = ""
        if template_compliance_analysis:
            template_summary = f"""
TEMPLATE COMPLIANCE ANALYSIS:
- Process adherence: {template_compliance_analysis.get('process_adherence_score', 'N/A')}%
- Customer context alignment: {template_compliance_analysis.get('customer_context_score', 'N/A')}%
- Methodology compliance: {template_compliance_analysis.get('methodology_compliance', 'Not evaluated')}
"""
        
        success_metrics_summary = ""
        if success_metrics_analysis:
            success_metrics_summary = f"""
SUCCESS METRICS EVALUATION:
{json.dumps(success_metrics_analysis, indent=2)}
"""
        
        # ===== COMPREHENSIVE EVALUATION PROMPT =====
        evaluation_prompt = f"""
        You are an expert training evaluator. Analyze this conversation comprehensively using ALL available information.
        
        CONVERSATION:
        {conversation_text}
        
        {knowledge_context}
        
        {fact_check_summary}
        
        {template_summary}
        
        {success_metrics_summary}
        
        EVALUATION CRITERIA:
        {json.dumps(evaluation_metrics, indent=2) if evaluation_metrics else "Use comprehensive customer service training metrics"}
        
        Provide a detailed assessment in JSON format:
        {{
            "overall_score": 0-100,
            "performance_category": "Excellent/Good/Satisfactory/Needs Improvement",
            "template_success_metrics": {{
                "response_accuracy": 0-100,
                "pitching_time_efficiency": 0-100,
                "customer_engagement_score": 0-100,
                "conversion_confidence_level": 0-100,
                "objection_handling_effectiveness": 0-100
            }},
            "detailed_metric_scores": {{
                "factual_accuracy": 0-100,
                "process_adherence": 0-100,
                "customer_context_alignment": 0-100,
                "communication_quality": 0-100,
                "professionalism": 0-100
            }},
            "template_compliance": {{
                "methodology_followed": true/false,
                "process_sequence_correct": true/false,
                "customer_matching_appropriate": true/false
            }},
            "conversation_analysis": {{
                "total_exchanges": "number",
                "discovery_questions_asked": 0-10,
                "packages_mentioned": ["list"],
                "objections_handled": 0-5,
                "closing_attempted": true/false
            }},
            "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
            "critical_areas_for_improvement": ["specific area 1", "specific area 2", "specific area 3"],
            "actionable_recommendations": ["specific action 1", "specific action 2", "specific action 3"],
            "fact_check_summary": "Summary of factual accuracy and knowledge application",
            "coaching_insights": "Key insights from template-specific coaching rules",
            "conversation_summary": "Brief summary of what transpired and outcomes"
        }}
        
        IMPORTANT INSTRUCTIONS:
        - Use the detailed fact-check results to assess factual accuracy
        - Consider template compliance in your scoring
        - If success metrics data is available, use it to inform your evaluation
        - Provide specific, actionable feedback based on the template methodology
        - Focus on both content accuracy AND process adherence
        - Include coaching insights from the template rules
        """
        
        # ===== GET COMPREHENSIVE EVALUATION =====
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert training evaluator who provides comprehensive, data-driven assessments using all available information including template-specific success metrics and coaching insights."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        log_token_usage(response,"evalute")
        # ===== PARSE EVALUATION RESULT =====
        result_text = response.choices[0].message.content.strip()
        print(f"🔍 Evaluation LLM Response: {result_text[:300]}...")
        
        try:
            # Try to parse JSON
            if result_text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise json.JSONDecodeError("Could not extract JSON from markdown", result_text, 0)
            else:
                result = json.loads(result_text)
                
        except json.JSONDecodeError:
            # Enhanced fallback with available data
            print(f"❌ JSON parsing failed. Creating structured fallback...")
            
            # Calculate basic scores from available data
            factual_accuracy = 100
            if detailed_fact_checks:
                correct_count = len([fc for fc in detailed_fact_checks if fc["result"] == "CORRECT"])
                factual_accuracy = round((correct_count / len(detailed_fact_checks)) * 100, 2)
            
            process_adherence = template_compliance_analysis.get('process_adherence_score', 50)
            
            result = {
                "overall_score": round((factual_accuracy + process_adherence) / 2),
                "performance_category": "Needs Assessment",
                "template_success_metrics": {
                    "response_accuracy": factual_accuracy,
                    "pitching_time_efficiency": 50,
                    "customer_engagement_score": 50,
                    "conversion_confidence_level": 50,
                    "objection_handling_effectiveness": 50
                },
                "detailed_metric_scores": {
                    "factual_accuracy": factual_accuracy,
                    "process_adherence": process_adherence,
                    "customer_context_alignment": 50,
                    "communication_quality": 50,
                    "professionalism": 50
                },
                "strengths": ["Assessment completed with available data"],
                "critical_areas_for_improvement": ["Review conversation for detailed feedback"],
                "actionable_recommendations": ["Retry evaluation for comprehensive analysis"],
                "fact_check_summary": f"Analyzed {len(detailed_fact_checks)} responses",
                "conversation_summary": "Evaluation completed with parsing fallback",
                "parsing_error": True,
                "raw_response": result_text[:500]
            }
        
        # ===== ENHANCE RESULT WITH DETAILED DATA =====
        result["evaluation_metadata"] = {
            "evaluation_method": "enhanced_template_based_evaluation",
            "knowledge_base_used": knowledge_base_id is not None,
            "template_coaching_rules_used": template_coaching_rules is not None,
            "conversation_length": len(conversation_history),
            "learner_responses_count": len(learner_responses),
            "evaluated_at": datetime.now().isoformat(),
            "evaluator": "enhanced_system_v2"
        }
        
        result["detailed_fact_checks"] = detailed_fact_checks
        result["template_compliance_analysis"] = template_compliance_analysis
        result["success_metrics_analysis"] = success_metrics_analysis
        
        # Calculate enhanced statistics
        if detailed_fact_checks:
            fact_errors = len([fc for fc in detailed_fact_checks if fc["result"] in ["INCORRECT", "PARTIALLY_CORRECT"]])
            process_violations = len([fc for fc in detailed_fact_checks if "VIOLATION" in fc["result"]])
            
            result["enhanced_statistics"] = {
                "total_claims_analyzed": len(detailed_fact_checks),
                "factual_errors_found": fact_errors,
                "process_violations_found": process_violations,
                "accuracy_percentage": round(((len(detailed_fact_checks) - fact_errors) / len(detailed_fact_checks) * 100), 2) if detailed_fact_checks else 100,
                "process_adherence_percentage": round(((len(detailed_fact_checks) - process_violations) / len(detailed_fact_checks) * 100), 2) if detailed_fact_checks else 100
            }
        
        return result
        
    except Exception as e:
        print(f"Error in enhanced conversation evaluation: {e}")
        return {
            "overall_score": 0,
            "error": f"Enhanced evaluation failed: {str(e)}",
            "conversation_length": len(conversation_history),
            "fallback_used": True,
            "evaluated_at": datetime.now().isoformat()
        }


async def analyze_success_metrics(
    conversation_history: List[Message],
    success_metrics: Dict[str, Any],
    template_coaching_rules: Dict,
    openai_client
) -> Dict[str, Any]:
    """Analyze conversation against template-specific success metrics"""
    
    try:
        # Build conversation for analysis
        conversation_text = "\n".join([
            f"{'Learner' if msg.role != 'assistant' else 'Customer'}: {msg.content}"
            for msg in conversation_history
        ])
        
        success_metrics_prompt = f"""
        Analyze this conversation against specific success metrics:
        
        CONVERSATION:
        {conversation_text}
        
        SUCCESS METRICS TO EVALUATE:
        {json.dumps(success_metrics, indent=2)}
        
        Provide detailed analysis in JSON format:
        {{
            "response_accuracy_analysis": {{
                "package_recommendations_appropriate": true/false,
                "customer_context_understood": true/false,
                "score": 0-100
            }},
            "pitching_time_analysis": {{
                "discovery_completed_before_pitch": true/false,
                "time_efficiency_rating": "Excellent/Good/Needs Improvement",
                "score": 0-100
            }},
            "engagement_analysis": {{
                "two_way_conversation_maintained": true/false,
                "repetitive_questioning_avoided": true/false,
                "score": 0-100
            }},
            "confidence_analysis": {{
                "confident_tone_demonstrated": true/false,
                "clear_closing_provided": true/false,
                "score": 0-100
            }},
            "objection_handling_analysis": {{
                "concerns_acknowledged_empathetically": true/false,
                "appropriate_responses_provided": true/false,
                "score": 0-100
            }}
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You analyze conversations against specific success metrics."},
                {"role": "user", "content": success_metrics_prompt}
            ],
            temperature=0.1,
            max_tokens=800
        )
        log_token_usage(response,"evalute")
        result_text = response.choices[0].message.content.strip()
        
        try:
            if result_text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            else:
                return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Could not parse success metrics analysis", "raw_response": result_text[:200]}
            
    except Exception as e:
        print(f"Success metrics analysis error: {e}")
        return {"error": str(e)}


async def analyze_template_compliance(
    conversation_history: List[Message],
    template_coaching_rules: Dict,
    openai_client
) -> Dict[str, Any]:
    """Analyze how well the conversation follows template-specific rules"""
    
    try:
        process_reqs = template_coaching_rules.get("process_requirements", {})
        customer_context = template_coaching_rules.get("customer_context_from_document", {})
        mistakes = template_coaching_rules.get("document_specific_mistakes", [])
        
        conversation_text = "\n".join([
            f"{'Learner' if msg.role != 'assistant' else 'Customer'}: {msg.content}"
            for msg in conversation_history
        ])
        
        compliance_prompt = f"""
        Analyze conversation compliance with template rules:
        
        CONVERSATION:
        {conversation_text}
        
        TEMPLATE REQUIREMENTS:
        - Methodology: {process_reqs.get("mentioned_methodology", "N/A")}
        - Required Steps: {process_reqs.get("required_steps", "N/A")}
        - Customer Type: {customer_context.get("target_customer_description", "N/A")}
        - Common Mistakes to Avoid: {[m.get("mistake_pattern", "") for m in mistakes]}
        
        Return compliance analysis as JSON:
        {{
            "methodology_compliance": "Followed/Partially Followed/Not Followed",
            "process_adherence_score": 0-100,
            "customer_context_score": 0-100,
            "mistakes_avoided": true/false,
            "specific_violations": ["violation 1", "violation 2"],
            "compliance_summary": "Overall assessment"
        }}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You analyze template compliance in training conversations."},
                {"role": "user", "content": compliance_prompt}
            ],
            temperature=0.1,
            max_tokens=600
        )
        log_token_usage(response,"evalute")
        result_text = response.choices[0].message.content.strip()
        
        try:
            if result_text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            else:
                return json.loads(result_text)
        except json.JSONDecodeError:
            return {"error": "Could not parse compliance analysis", "raw_response": result_text[:200]}
            
    except Exception as e:
        print(f"Template compliance analysis error: {e}")
        return {"error": str(e)}


# ===== UPDATED EVALUATION ENDPOINT =====
@router.post("/chat/evaluate/{session_id}")
async def enhanced_evaluate_conversation(
    session_id: str,
    db: Any = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Generate comprehensive assessment report with template-based evaluation"""
    
    try:
        # ===== GET SESSION AND CONVERSATION =====
        session = await get_chat_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # ===== GET AVATAR INTERACTION AND SCENARIO (FIX DATABASE ACCESS) =====
        avatar_interaction_id = session.avatar_interaction
        avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
        
        if not avatar_interaction:
            raise HTTPException(status_code=404, detail="Avatar interaction not found")
        
        # ===== FIND SCENARIO (PROPER SEARCH LOGIC) =====
        scenario = None
        mode = "assess_mode"  # Default
        
        # Check all modes to find the scenario
        for mode_type in ["learn_mode", "try_mode", "assess_mode"]:
            try:
                scenarios = await db.scenarios.find({f"{mode_type}.avatar_interaction": avatar_interaction_id}).to_list(length=1)
                if scenarios:
                    scenario = scenarios[0]
                    mode = mode_type
                    print(f"✅ Found scenario in {mode_type}: {scenario['_id']}")
                    break
            except Exception as search_error:
                print(f"Error searching {mode_type}: {search_error}")
                continue
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # ===== GET TEMPLATE DATA AND COACHING RULES (SAFE ACCESS) =====
        template_id = scenario.get("template_id")
        template = None
        knowledge_base_id = None
        evaluation_metrics = {}
        template_coaching_rules = {}
        
        if template_id:
            try:
                template = await db.templates.find_one({"id": template_id})
                if template:
                    print(f"✅ Template found: {template_id}")
                    
                    # Safe access to template data
                    template_data = template.get("template_data", {})
                    knowledge_base_id = template.get("knowledge_base_id")
                    evaluation_metrics = template_data.get("evaluation_metrics", {})
                    template_coaching_rules = template_data.get("coaching_rules", {})
                    
                    print(f"✅ Knowledge base ID: {knowledge_base_id}")
                    print(f"✅ Has coaching rules: {bool(template_coaching_rules)}")
                else:
                    print(f"❌ Template not found: {template_id}")
            except Exception as template_error:
                print(f"Error accessing template: {template_error}")
        
        # ===== GENERATE COMPREHENSIVE ASSESSMENT =====
        evaluation_result = await enhanced_conversation_evaluation(
            session_id=session_id,
            db=db,
            current_user=current_user,
            conversation_history=session.conversation_history,
            evaluation_metrics=evaluation_metrics,
            knowledge_base_id=knowledge_base_id,
            template_coaching_rules=template_coaching_rules
        )
        
        # ===== STORE EVALUATION RESULT =====
        evaluation_record = {
            "_id": str(uuid4()),
            "session_id": session_id,
            "user_id": str(current_user.id),
            "scenario_id": scenario["_id"],
            "template_id": template_id,
            "mode": mode,
            "evaluation_result": evaluation_result,
            "evaluation_type": "enhanced_template_based",
            "evaluated_at": datetime.now(),
            "evaluated_by": str(current_user.id)
        }
        
        await db.analysis.insert_one(evaluation_record)
        
        # ===== UPDATE ASSIGNMENT WITH ENHANCED DATA =====
        assignment_updated = False
        try:
            update_data = {
                f"mode_progress.{mode}.evaluation_completed": True,
                f"mode_progress.{mode}.evaluation_date": datetime.now(),
                f"mode_progress.{mode}.latest_score": evaluation_result.get("overall_score", 0),
                f"mode_progress.{mode}.performance_category": evaluation_result.get("performance_category", "Needs Assessment"),
                f"mode_progress.{mode}.evaluation_id": evaluation_record["_id"],
                f"mode_progress.{mode}.template_compliance": evaluation_result.get("template_compliance", {}),
                f"mode_progress.{mode}.success_metrics_scores": evaluation_result.get("template_success_metrics", {})
            }
            
            result = await db.user_scenario_assignments.update_one(
                {
                    "user_id": str(current_user.id),
                    "scenario_id": scenario["_id"]
                },
                {"$set": update_data}
            )
            assignment_updated = result.modified_count > 0
        except Exception as e:
            print(f"Error updating assignment: {e}")
        
        # ===== UPDATE MODULE COMPLETION =====
        try:
            from core.module_assignment import update_module_completion_status
            modules = await db.modules.find({"scenarios": scenario["_id"]}).to_list(length=1)
            if modules:
                module_id = modules[0]["_id"]
                await update_module_completion_status(db, current_user.id, UUID(module_id))
        except Exception as e:
            print(f"Error updating module completion: {e}")
        
        return {
            "session_id": session_id,
            "evaluation": evaluation_result,
            "evaluation_id": evaluation_record["_id"],
            "assignment_updated": assignment_updated,
            "score": evaluation_result.get("overall_score", 0),
            "mode": mode,
            "template_used": template_id,
            "enhancement_features": {
                "template_coaching_rules_applied": bool(template_coaching_rules),
                "success_metrics_evaluated": bool(evaluation_metrics),
                "detailed_fact_checking": True,
                "template_compliance_analysis": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in enhanced evaluate_conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced evaluation failed: {str(e)}")
