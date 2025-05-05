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
    db: Any = Depends(get_db)
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
    
    # Initialize chat session
    session = await initialize_chat_session(db, avatar_interaction_id, mode, persona_id,language_id)
    
    # Return session information
    return {
        "session_id": session.session_id,
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
    session_id: str = Form(...),
    name: Optional[str] = Form(None),
    db: Any = Depends(get_db)
):
    """
    Send a message to the chat system and prepare for streaming response.
    """
    # Get existing session
    session = await get_chat_session(db, session_id)
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
        "session_id": session_id
    }


@router.get("/chat/stream")
async def chat_stream(
    session_id: str = Query(...),
    name: Optional[str] = Query(None),
    db: Any = Depends(get_db)
):
    """
    Stream the response for a chat message.
    """
    # Get session
    session = await get_chat_session(db, session_id)
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
        raise HTTPException(status_code=404, detail="Avatar  not found")
    persona_id=avatar["persona_id"][0]
    language_id=session.language_id
    
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
                    answer = updated_message
                
                # Check if this is the end of the conversation
                if "[FINISH]" in updated_message:
                    answer = updated_message.replace("[FINISH]", " ")
                    complete = True
                else:
                    complete = False
                
                # Check if correction is needed
                if "[CORRECT]" in updated_message:
                    correct = False
                else:
                    correct = True
                
                # Format the response as a ChatResponse
                chat_response = ChatResponse(
                    session_id=session.session_id,
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

@router.get("/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Any = Depends(get_db)
):
    """
    Get the conversation history for a chat session.
    
    - session_id: ID of the chat session
    """
    # Get session
    session = await get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "scenario_name": session.scenario_name,
        "persona_id": session.persona_id,
        "conversation_history": [msg.dict() for msg in session.conversation_history],
        "created_at": session.created_at,
        "last_updated": session.last_updated
    }


@router.put("/chat/persona/{session_id}")
async def update_session_persona(
    session_id: str,
    persona_id: UUID = Body(...),
    db: Any = Depends(get_db)
):
    """
    Update the persona used in a chat session.
    
    - session_id: ID of the chat session
    - persona_id: ID of the new persona to use
    """
    # Get session
    session = await get_chat_session(db, session_id)
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
        "session_id": session.session_id,
        "persona_id": str(persona_id),
        "message": "Persona updated successfully"
    }


@router.delete("/chat/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: Any = Depends(get_db)
):
    """
    Delete a chat session.
    
    - session_id: ID of the chat session to delete
    """
    # Verify session exists
    session = await get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Delete the session
    result = await db.sessions.delete_one({"session_id": session_id})
    
    return {
        "success": result.deleted_count > 0,
        "session_id": session_id
    }