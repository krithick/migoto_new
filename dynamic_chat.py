"""
Dynamic Chat Loader

A system for dynamically loading and managing chat handlers based on AvatarInteraction documents.
This allows handling N number of scenarios with their associated learn, try, and assess modes.
"""

from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from pydantic import BaseModel
import asyncio
import json
import re
from motor.motor_asyncio import AsyncIOMotorClient

# Import your existing models
from models.avatarInteraction_models import AvatarInteractionDB
from models.persona_models import PersonaDB
from models_old import Message, ChatSession
from database import get_db

# LLM client import
from openai import AsyncAzureOpenAI
import os
from models.language_models import LanguageDB
# Cache configuration
CACHE_EXPIRY_MINUTES = 30  # How long to keep inactive handlers in cache


class ChatHandlerConfig(BaseModel):
    """Configuration for a chat handler"""
    avatar_interaction_id: UUID
    mode: str  # "learn_mode", "try_mode", or "assess_mode"
    system_prompt: str
    bot_role: str
    bot_role_alt: str
    persona_id: Optional[UUID] = None
    language_id: Optional[UUID] = None


class DynamicChatHandler:
    """
    A chat handler for a specific avatar interaction and mode.
    Processes messages and generates responses.
    """
    def __init__(self, 
                 config: ChatHandlerConfig, 
                 llm_client: AsyncAzureOpenAI,
                 db: Any):
        self.config = config
        self.llm_client = llm_client
        self.db = db
        self.last_used = datetime.now()
        
    async def process_message(self, 
                              message: str, 
                              conversation_history: List[Message],
                              name: Optional[str] = None) -> AsyncGenerator:
        """Process a message and generate a streaming response"""
        self.last_used = datetime.now()
        
        # Format conversation for LLM
        contents = await self.format_conversation(conversation_history)
        
        # Add the current message
        contents.append({
            "role": "user",
            "content": message
        })
        
        try:
            # Get streaming response from LLM
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # Or use config.llm_model if available
                messages=contents,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            async def generate():
                res = ""
                async for i in response:
                    if len(i.choices) > 0:
                        chunk_text = i.choices[0].delta.content
                        finish_reason = i.choices[0].finish_reason
                        
                        if chunk_text:
                            res += chunk_text
                            # Apply name replacement if provided
                            if name:
                                updated_text = self.replace_name(res, name)
                            else:
                                updated_text = res
                                
                            yield {"chunk": updated_text, "finish": None, "usage": None}
                            
                        if finish_reason == "stop":
                            if res.strip():
                                if name:
                                    updated_text = self.replace_name(res, name)
                                else:
                                    updated_text = res
                                yield {"chunk": updated_text, "finish": "stop", "usage": None}
                    
                    # Handle usage statistics
                    if hasattr(i, 'usage') and i.usage is not None:
                        yield {
                            "chunk": res,
                            "finish": "stop",
                            "usage": {
                                "completion_tokens": i.usage.completion_tokens,
                                "prompt_tokens": i.usage.prompt_tokens,
                                "total_tokens": i.usage.total_tokens
                            }
                        }
            
            return generate()
            
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    
    async def format_conversation(self, conversation_history: List[Message]) -> List[Dict[str, str]]:
        """Format conversation history for the LLM"""
        contents = []
        
        # Add system prompt
        contents.append({"role": "system", "content": self.config.system_prompt})
        # Get persona if available
        print(self.config)
        if self.config.persona_id:
            try:
                persona = await self.db.personas.find_one({"_id": str(self.config.persona_id)})
                language = await self.db.languages.find_one({"_id": str(self.config.language_id)})
                print("language",language)
                if persona:
                    persona_obj = PersonaDB(**persona)
                    language_obj= LanguageDB(**language)
                    persona_context = self.format_persona_context(self.config.system_prompt,persona_obj,language_obj)
                    # Add persona information to system prompt
                    contents[0]["content"] = persona_context
                    print("actual scenariossss",persona_context)
            except Exception as e:
                print(f"Error loading persona: {e}")
        
        # Add conversation history
        for message in conversation_history:
            role = "user" if message.role == self.config.bot_role_alt else "assistant"
            content = {
                "role": role,
                "content": message.content
            }
            contents.append(content)
            
        return contents
    
    def format_persona_context(self,scenario_prompt: str, persona: PersonaDB,language:LanguageDB) -> str:
        """
        Replace the persona placeholder with details from a persona document
        """
        # Format persona details as markdown
        persona_markdown = f"""
    - Name: {persona.name}
    - Type: {persona.persona_type}
    - Gender: {persona.gender}
    - Age: {persona.age}
    - Goal: {persona.character_goal}
    - Location: {persona.location}
    - Description: {persona.description}
    - Details: {persona.persona_details}
    - Current situation: {persona.situation}
    - Context: {persona.business_or_personal}
    """
        language_markdown = f"""
- Primary language: {language.name}
- Language instructions: {language.prompt}

"""
        # Add background story if available
        if persona.background_story:
            persona_markdown += f"- Background: {persona.background_story}\n"
    # Replace placeholders
        scenario_prompt = scenario_prompt.replace("[LANGUAGE_PLACEHOLDER]", language_markdown)
        scenario_prompt = scenario_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)    
        return scenario_prompt
    
    def replace_name(self, original_text: str, name: str) -> str:
        """Replace [Your Name] with the provided name"""
        if "[Your Name]" in original_text:
            return original_text.replace("[Your Name]", name)
        return original_text


class DynamicChatFactory:
    """
    Factory for creating and managing chat handlers on demand.
    Maintains a cache of handlers to avoid recreating them for each message.
    """
    def __init__(self, db: Any):
        self.db = db
        self.handlers: Dict[str, DynamicChatHandler] = {}
        self.llm_client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            azure_endpoint=os.getenv("endpoint"),
            api_version=os.getenv("api_version")
        )
        
        # Start background cleanup task
        asyncio.create_task(self._cleanup_inactive_handlers())
        
    async def get_chat_handler(self, 
                               avatar_interaction_id: UUID, 
                               mode: str,
                               persona_id: Optional[UUID] = None,
                               language_id: Optional[UUID] = None) -> DynamicChatHandler:
        """Get or create a chat handler for the specified avatar interaction and mode"""
        # Create a unique key for this handler configuration
        handler_key = f"{avatar_interaction_id}:{mode}:{persona_id}:{language_id}"
        
        # Check if handler exists in cache
        if handler_key in self.handlers:
            handler = self.handlers[handler_key]
            handler.last_used = datetime.now()  # Update last used time
            return handler
            
        # Load avatar interaction from database
        avatar_interaction = await self.db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
        if not avatar_interaction:
            raise HTTPException(status_code=404, detail="Avatar interaction not found")
        
        ai_obj = AvatarInteractionDB(**avatar_interaction)
        
        # Create handler config
        config = ChatHandlerConfig(
            avatar_interaction_id=avatar_interaction_id,
            mode=mode,
            system_prompt=ai_obj.system_prompt,
            bot_role=ai_obj.bot_role,
            bot_role_alt=ai_obj.bot_role_alt or ai_obj.bot_role,
            persona_id=persona_id,
            language_id=language_id
        )
        
        # Create new handler
        handler = DynamicChatHandler(config, self.llm_client, self.db)
        
        # Cache the handler
        self.handlers[handler_key] = handler
        
        return handler
    
    async def _cleanup_inactive_handlers(self):
        """Background task to remove inactive handlers from cache"""
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = datetime.now()
            expired_keys = []
            
            for key, handler in self.handlers.items():
                # If handler hasn't been used for CACHE_EXPIRY_MINUTES, mark for removal
                if (current_time - handler.last_used) > timedelta(minutes=CACHE_EXPIRY_MINUTES):
                    expired_keys.append(key)
                    
            # Remove expired handlers
            for key in expired_keys:
                del self.handlers[key]
                
            print(f"Cleaned up {len(expired_keys)} inactive chat handlers. Active: {len(self.handlers)}")


# Create a singleton factory instance
_chat_factory = None

async def get_chat_factory():
    """Get the singleton chat factory instance"""
    global _chat_factory
    if _chat_factory is None:
        db = await get_db()
        _chat_factory = DynamicChatFactory(db)
    return _chat_factory


# Helper functions for session management
async def initialize_chat_session(
    db: Any,
    avatar_interaction_id: UUID,
    mode: str,
    current_user : UUID,
    persona_id: Optional[UUID] = None,
    language_id : Optional[UUID] = None,
    
) -> ChatSession:
    """Initialize a new chat session for the specified avatar interaction and mode"""
    # Get avatar interaction to get scenario name
    avatar_interaction = await db.avatar_interactions.find_one({"_id": str(avatar_interaction_id)})
    if not avatar_interaction:
        raise HTTPException(status_code=404, detail="Avatar interaction not found")
    
    ai_obj = AvatarInteractionDB(**avatar_interaction)
    
    # Determine scenario name based on mode and avatar interaction
    scenario_name = f"{ai_obj.bot_role} - {mode}"
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
                        
    session = ChatSession(
        extra=str(uuid4()),
        scenario_name=scenario_name,
        avatar_interaction=str(avatar_interaction_id),  # Add this line
        avatar_id=str(avatar_interaction.get("avatars", [""])[0]),
        persona_id=str(persona_id) if persona_id else None,
        user_id=str(current_user),
        # persona_settings={
        #     "avatar_interaction_id": str(avatar_interaction_id),
        #     "mode": mode
        # },
        language_id = str(language_id),# Add this line
     
        conversation_history=[],
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    session_dict = session.dict(by_alias=True)
    if "_id" in session_dict:
        session_dict["_id"] = str(session_dict["_id"])    
    # Save to database
    await db.sessions.insert_one(session_dict)
    
    return session


async def get_chat_session(db: Any, id: str) -> Optional[ChatSession]:
    """Get a chat session by ID"""
    session_data = await db.sessions.find_one({"_id": str(id)})
    if session_data:
        return ChatSession(**session_data)
    return None


async def update_chat_session(db: Any, session: ChatSession):
    """Update a chat session in the database"""
    session.last_updated = datetime.now()
    await db.sessions.update_one(
        {"_id": str(session.id)},
        {"$set": session.dict()}
    )