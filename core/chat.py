"""
Enhanced Chat Routes for FastAPI

Routes for handling chat functionality with dynamic avatar interactions and personas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body, Form, Query
from fastapi.responses import StreamingResponse
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

# Create router
router = APIRouter(tags=["Chat"])

# Chat Routes
@router.post("/chat/initialize")
async def initialize_chat(
    avatar_interaction_id: UUID = Form(...),
    mode: str = Form(...),  # "learn_mode", "try_mode", or "assess_mode"
    persona_id: Optional[UUID] = Form(None),
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
        print(current_user)
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
    session = await initialize_chat_session(db, avatar_interaction_id=avatar_interaction_id, mode=mode, persona_id=persona_id, language_id=language_id,current_user=current_user.id)
    
    # Return session information
    return {
        "id":session.id,
        "scenario_name": session.scenario_name,
        "avatar_interaction_id": str(avatar_interaction_id),
        "mode": mode,
        "persona_id": str(persona_id) if persona_id else None,
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
    
    # Get the appropriate chat handler - use the mode from the avatar_interaction document
    # You'll need to fetch the avatar_interaction to determine the mode
    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    mode = avatar_interaction["mode"] if avatar_interaction else "try_mode"  # Default to try_mode
    language_id=session.language_id
    handler = await chat_factory.get_chat_handler(
        avatar_interaction_id=UUID(avatar_interaction_id),
        mode=mode,
        persona_id=UUID(persona_id) if persona_id else None,
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
    db: Any = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)  # Add this dependency
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
            res = ""
            async for chunk in response:
                updated_message = chunk["chunk"]
                
                # Check if complete
                if chunk["finish"] == "stop" and chunk["usage"] is not None:
                    # Add bot message to conversation history
                    bot_message = Message(
                        role=handler.config.bot_role,
                        content=updated_message,
                        timestamp=datetime.now()
                    )
                    bot_message.usage = chunk["usage"]
                    session.conversation_history.append(bot_message)
                    await update_chat_session(db, session)
                
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
                            await db.user_scenario_assignments.update_one(
                                {
                                    "user_id": str(current_user.id),
                                    "scenario_id": scenario_id
                                },
                                {
                                    "$set": {
                                        f"mode_progress.{mode}.completed": True,
                                        f"mode_progress.{mode}.completed_date": datetime.now()
                                    }
                                }
                            )
                            
                            # Check if all assigned modes are now completed
                            assignment = await db.user_scenario_assignments.find_one({
                                "user_id": str(current_user.id),
                                "scenario_id": scenario_id
                            })
                            
                            if assignment:
                                # Check if all modes are completed
                                assigned_modes = assignment.get("assigned_modes", [])
                                mode_progress = assignment.get("mode_progress", {})
                                
                                all_modes_completed = True
                                for assigned_mode in assigned_modes:
                                    if assigned_mode not in mode_progress or not mode_progress.get(assigned_mode, {}).get("completed", False):
                                        all_modes_completed = False
                                        break
                                
                                # If all modes are completed, mark scenario as completed
                                if all_modes_completed:
                                    await db.user_scenario_assignments.update_one(
                                        {
                                            "user_id": str(current_user.id),
                                            "scenario_id": scenario_id
                                        },
                                        {
                                            "$set": {
                                                "completed": True,
                                                "completed_date": datetime.now()
                                            }
                                        }
                                    )
                                    
                                    # Update module completion
                                    from core.module_assignment import update_module_completion_status
                                    await update_module_completion_status(
                                        db, 
                                        current_user.id, 
                                        UUID(assignment.get("module_id"))
                                    )
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
                
                yield f"data: {chat_response.json()}\n\n"
                
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