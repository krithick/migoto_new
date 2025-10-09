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
from core.azure_search_manager import FactCheckResult

# Import your existing models
from models.avatarInteraction_models import AvatarInteractionDB
from models.persona_models import PersonaDB
from models_old import Message, ChatSession
from database import get_db

# LLM client import
from openai import AsyncAzureOpenAI
import os
from models.language_models import LanguageDB
from core.azure_search_manager import AzureVectorSearchManager, EnhancedFactChecker

from core.simple_token_logger import log_token_usage
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
        self.vector_search = AzureVectorSearchManager()
        self.fact_checker = EnhancedFactChecker(self.vector_search, llm_client)
        self.knowledge_base_id = None
        self.fact_checking_enabled = False
    async def initialize_fact_checking(self, session_id: str,coaching_rules: Dict = None):
        """Initialize fact-checking if this session supports it"""
        print(coaching_rules,"coaching_rulessssssss")
        try:
            # Get knowledge base ID from session
            knowledge_base_id = await self._get_knowledge_base_for_session(session_id)
            print("checkkkk",knowledge_base_id)
            
            # Get language instructions
            language_instructions = await self._get_language_instructions()
            
            # Initialize fact checker with or without knowledge base
            print(f"Initializing fact checker with language instructions: {language_instructions[:50] if language_instructions else 'None'}...")
            self.fact_checker = EnhancedFactChecker(
                self.vector_search, 
                self.llm_client,
                coaching_rules=coaching_rules or {},  # Pass coaching rules here
                language_instructions=language_instructions  # Pass language instructions
            )
            
            avatar_interaction = await self.db.avatar_interactions.find_one(
                {"_id": str(self.config.avatar_interaction_id)}
            )
            
            # Enable fact-checking for try_mode and learn_mode, even without knowledge base
            self.fact_checking_enabled = (
                avatar_interaction and 
                avatar_interaction.get("mode") in ["try_mode", "learn_mode"]
            )
            
            if knowledge_base_id:
                self.knowledge_base_id = knowledge_base_id
            else:
                self.knowledge_base_id = None
                print("No knowledge base - coaching will work without document search")
                
            print("self.fact_checking_enabled",self.fact_checking_enabled)
            
        except Exception as e:
            print(f"Error initializing fact-checking: {e}")
            self.fact_checking_enabled = False
    
    # async def _get_knowledge_base_for_session(self, session_id: str) -> Optional[str]:
    #     """Get knowledge base ID from session"""
    #     try:
    #         session = await self.db.sessions.find_one({"_id": session_id})
    #         # print("session",session)
    #         if not session:
    #             return None
            
    #         avatar_interaction_id = session.get("avatar_interaction")
    #         print(avatar_interaction_id,"avatar_interaction_id")
    #         if not avatar_interaction_id:
    #             return None
    #         # Find scenario containing this avatar interaction
    #         avatar_interaction_str = str(avatar_interaction_id)
    #         print(type(avatar_interaction_str))
             
    #         scenario = await self.db.scenarios.find_one({
    #             "$or": [
    #                 {"learn_mode.avatar_interaction": avatar_interaction_str},
    #                 {"try_mode.avatar_interaction": avatar_interaction_str},
    #                 {"assess_mode.avatar_interaction": avatar_interaction_str}
    #             ]
    #         })
    #         print('scenariossssssss',scenario)
    #         template = await self.db.templates.find_one({"id":scenario.get("template_id")})
    #         print("session",template)
    #         if not template:
    #             print("no template found")
                
    #         return template.get("knowledge_base_id") if template else None
            
    #     except Exception as e:
    #         print(f"Error getting knowledge base: {e}")
    #         return None           
    # async def _get_knowledge_base_for_session(self, session_id: str) -> Optional[str]:
    #     """Get knowledge base ID from session"""
    #     try:
    #         session = await self.db.sessions.find_one({"_id": session_id})
    #         print(f"🔍 Session found: {session is not None}")
        
    #         if not session:
    #             return None
        
    #         avatar_interaction_id = session.get("avatar_interaction")
    #         print(f"🔍 Avatar interaction ID: {avatar_interaction_id} (type: {type(avatar_interaction_id)})")
        
    #         if not avatar_interaction_id:
    #             return None
        
    #         # Convert to string if it's not already
    #         avatar_interaction_str = str(avatar_interaction_id)
    #         print(f"🔍 Looking for scenario with avatar_interaction: {avatar_interaction_str}")
        
    #         # Try multiple query patterns to debug
    #         queries_to_try = [
    #             # Pattern 1: Direct string match
    #             {
    #                 "$or": [
    #                 {"learn_mode.avatar_interaction": avatar_interaction_str},
    #                 {"try_mode.avatar_interaction": avatar_interaction_str},
    #                 {"assess_mode.avatar_interaction": avatar_interaction_str}
    #                 ]
    #             },
    #             # Pattern 2: Without string conversion
    #             {
    #                 "$or": [
    #                 {"learn_mode.avatar_interaction": avatar_interaction_id},
    #                 {"try_mode.avatar_interaction": avatar_interaction_id},
    #                 {"assess_mode.avatar_interaction": avatar_interaction_id}
    #                 ]
    #             },
    #             # Pattern 3: Check if it's stored as ObjectId
    #             {
    #                 "$or": [
    #                 {"learn_mode.avatar_interaction": {"$in": [avatar_interaction_str, avatar_interaction_id]}},
    #                 {"try_mode.avatar_interaction": {"$in": [avatar_interaction_str, avatar_interaction_id]}},
    #                 {"assess_mode.avatar_interaction": {"$in": [avatar_interaction_str, avatar_interaction_id]}}
    #                 ]
    #             }
    #         ]
        
    #         scenario = None
    #         for i, query in enumerate(queries_to_try):
    #             print(f"🔍 Trying query pattern {i+1}")
    #             scenario = await self.db.scenarios.find_one(query)
    #             if scenario:
    #                 print(f"✅ Found scenario with pattern {i+1}: {scenario.get('_id')}")
    #                 break
    #             else:
    #                 print(f"❌ Pattern {i+1} found no results")
        
    #         if not scenario:
    #             print("❌ No scenario found with any pattern")
            
    #             # DEBUG: Let's see what scenarios actually exist
    #             all_scenarios = await self.db.scenarios.find({}).to_list(length=5)
    #             print(f"📊 Total scenarios in DB: {len(all_scenarios)}")
    #             for s in all_scenarios[:2]:  # Show first 2 scenarios
    #                 print(f"   Scenario {s.get('_id')}: learn={s.get('learn_mode', {}).get('avatar_interaction')}, try={s.get('try_mode', {}).get('avatar_interaction')}, assess={s.get('assess_mode', {}).get('avatar_interaction')}")
            
    #             return None
        
    #         # Get template from scenario
    #         template_id = scenario.get("template_id")
    #         print(f"🔍 Template ID from scenario: {template_id}")

    #         if not template_id:
    #             print("❌ No template_id in scenario")
    #             return None
            
    #         template = await self.db.templates.find_one({"id": template_id})
    #         print(f"🔍 Template found: {template is not None}")
        
    #         if not template:
    #             print("❌ Template not found in database")
    #         return None
        
    #         knowledge_base_id = template.get("knowledge_base_id")
    #         print(f"🔍 Knowledge base ID: {knowledge_base_id}")
        
    #         return knowledge_base_id
        
    #     except Exception as e:
    #         print(f"Error getting knowledge base: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return None     
    
    async def _get_knowledge_base_for_session(self, session_id: str) -> Optional[str]:
        """Get knowledge base ID from session - UPDATED for your models"""
        try:
            from uuid import UUID
        
            # Get session
            session = await self.db.sessions.find_one({"_id": session_id})
            if not session:
                print("❌ Session not found")
                return None
        
            # Get avatar_interaction_id from session
            avatar_interaction_id = session.get("avatar_interaction")
            if not avatar_interaction_id:
                print("❌ No avatar_interaction in session")
                return None
        
            # Convert to UUID for querying (your models use UUID)
            if isinstance(avatar_interaction_id, str):
                try:
                    avatar_interaction_uuid = UUID(avatar_interaction_id)
                except ValueError:
                    avatar_interaction_uuid = None
            else:
                avatar_interaction_uuid = avatar_interaction_id
        
            avatar_interaction_str = str(avatar_interaction_id)
        
            print(f"🔍 Looking for scenario with avatar_interaction: {avatar_interaction_str}")
        
            # Query scenarios that reference this avatar_interaction in any mode
            # Based on your ScenarioDB model structure
            query_conditions = []
        
            # Add both string and UUID formats since you had the mismatch issue
            for mode in ["learn_mode", "try_mode", "assess_mode"]:
                query_conditions.extend([
                    {f"{mode}.avatar_interaction": avatar_interaction_str},
                    {f"{mode}.avatar_interaction": avatar_interaction_uuid} if avatar_interaction_uuid else {}
                ])
        
            # Remove empty conditions
            query_conditions = [q for q in query_conditions if q]
        
            scenario = await self.db.scenarios.find_one({"$or": query_conditions})
        
            if not scenario:
                print("❌ No scenario found")
                return None
        
            print(f"✅ Found scenario: {scenario.get('_id')}")
        
            # Get template_id from scenario
            template_id = scenario.get("template_id")
            if not template_id:
                print("❌ No template_id in scenario")
                return None
        
            print(f"🔍 Looking for template: {template_id}")
        
            # Get template
            template = await self.db.templates.find_one({"id": template_id})
            if not template:
                print("❌ Template not found")
                return None
        
            print("✅ Template found")
        
            # Get knowledge_base_id from template
            knowledge_base_id = template.get("knowledge_base_id")
            print(f"🔍 Knowledge base ID: {knowledge_base_id}")
        
            return knowledge_base_id
        
        except Exception as e:
            print(f"Error getting knowledge base: {e}")
            import traceback
            traceback.print_exc()
            return None 
    async def process_message(self, message: str, conversation_history: List[Message], name: Optional[str] = None) -> AsyncGenerator:
        """Enhanced process_message with fact-checking for try_mode"""
        self.last_used = datetime.now()
        
        # Format conversation for LLM
        contents = await self.format_conversation(conversation_history)
        contents.append({"role": "user", "content": message})
        
        try:
            # Get streaming response from LLM
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o",
                messages=contents,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            log_token_usage(response, "process_message")
            if self.config.mode == "try_mode" and self.fact_checking_enabled:
                # TRY MODE: Fact-check AI responses for accuracy (works with or without knowledge base)
                return await self._process_with_fact_checking(response,message,conversation_history, name)
            elif self.config.mode == "learn_mode" and self.knowledge_base_id:
                # LEARN MODE: Enhance responses with knowledge base
                return await self._process_with_knowledge_base(response, message, conversation_history, name)
            else:
                # ASSESS MODE: Simple natural responses
                return await self._process_normal_stream(response, name)
                
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    


    async def _process_with_fact_checking(self, response, user_message: str,conversation_history: List[Message], name: Optional[str]):
        """Process response with fact-checking - ensure final response has complete data"""
    
        # Fact-check the user's message
        coaching_feedback = await self._check_user_response_accuracy(user_message,conversation_history, self.knowledge_base_id)
        print("coaching_feedback",coaching_feedback)
        # Collect AI's full response
        full_response = ""
        usage_info = None

        async for chunk in response:
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        
            if hasattr(chunk, 'usage') and chunk.usage:
                usage_info = chunk.usage
    
        # Stream with complete coaching data
        async def fact_checked_generator():
            if name:
                final_response = self.replace_name(full_response, name)
            else:
                final_response = full_response
        
            # Add coaching feedback if needed
            if coaching_feedback:
                final_response = f"{final_response} [CORRECT] {coaching_feedback} [CORRECT]"
        
            # Stream in chunks ensuring final chunk has complete data
            words = final_response.split()
            current_text = ""
        
            for i, word in enumerate(words):
                current_text += word + " "
            
                if i % 3 == 0 or i == len(words) - 1:
                    is_final = i == len(words) - 1
                
                    # For final chunk, include all metadata
                    if is_final:
                        yield {
                        "chunk": current_text.strip(),
                        "finish": "stop",
                        "usage": usage_info,
                        "fact_check_summary": {
                            "user_response_checked": True,
                            "coaching_provided": coaching_feedback is not None,
                            "coaching_content": coaching_feedback  # ✅ Include the actual coaching
                        }
                    }
                    else:
                        yield {
                        "chunk": current_text.strip(),
                        "finish": None,
                        "usage": None
                    }
                
                    if is_final:
                        break
    
        return fact_checked_generator() 
# 

#     async def _check_user_response_accuracy(self, user_message: str,conversation_history: List[Message], knowledge_base_id: str) -> Optional[str]:
#         """Simple fact-checking against Cloudnine documents"""
    
#         try:
#             if len(conversation_history) <= 1:
#                 return None
#             language_instructions = await self._get_language_instructions()
#             # Search for relevant info in documents
#         # ✅ ENHANCED: Use fact-checker with coaching rules if available
#             if hasattr(self, 'fact_checker') and self.fact_checker.has_coaching_rules:
#                 # Use contextual verification with template coaching rules
#                 verification = await self.fact_checker.verify_response_with_coaching(
#                     user_message, conversation_history, knowledge_base_id
#                 )
            
#                 if verification.result != FactCheckResult.CORRECT:
#                     # Use coaching feedback from template if available
#                     if verification.coaching_feedback:
#                         return f"Dear Learner, {verification.coaching_feedback}"
#                     else:
#                         return f"Dear Learner, {verification.explanation}"
            
#                 return None  # No correction needed
                        
#             search_results = await self.vector_search.vector_search(
#             user_message, knowledge_base_id, top_k=3, openai_client=self.llm_client
#             )
        
#             if not search_results:
#                 return None
#             print(conversation_history[0],'conversation_history')
#             # Build context from search results
#             context = "\n".join([result['content'] for result in search_results])
#             convo_context = ""
#             for msg in conversation_history[-4:]:  # Last 4 messages for context
#                 role = "Customer" if msg.role == self.config.bot_role else "Learner"
#                 convo_context += f"{role}: {msg.content}\n"

# #             fact_check_prompt = f"""
# # {language_instructions}

# # You are a customer service training coach. Evaluate the learner's response using this EXACT priority order:

# # RECENT CONVERSATION:
# # {convo_context}
# # LEARNER'S LATEST RESPONSE: "{user_message}"
# # OFFICIAL COMPANY INFORMATION:
# # {context}

# # EVALUATION STEPS (check in this order):

# # 1. FIRST: Is this response a reasonable customer service approach?
# #    - Asking clarifying questions = ALWAYS GOOD
# #    - Showing empathy/acknowledgment = ALWAYS GOOD  
# #    - Requesting details to help better = ALWAYS GOOD

# # 2. SECOND: If giving company information, is it factually correct?
# #    - Check against the official company information above
# #    - Only flag if there's clear contradiction with company docs

# # 3. THIRD: Does it address what the customer actually asked about?

# # RESPOND WITH EXACTLY ONE OF THESE:

# # [CORRECT] 
# # (if the response is appropriate customer service behavior)

# # "Dear Learner, you provided incorrect information about [specific topic]. According to our company information: [correct facts]. Please respond with: [better response]."
# # (only if factually wrong company information was given)

# # "Dear Learner, the customer was asking about [specific need], but your response doesn't help with that. You should [specific action] to address their [specific concern]."
# # (only if completely ignoring customer's question)

# # REMEMBER: 
# # - Asking questions to understand customer needs better is ALWAYS correct
# # - Being polite and engaging is ALWAYS correct  
# # - Only mark wrong if giving incorrect company facts or completely ignoring customer
# # """       
#             fact_check_prompt = f"""
# {language_instructions}

# You are a training coach reviewing a learner's response in a customer service conversation.

# RECENT CONVERSATION:
# {convo_context}
# LEARNER'S LATEST RESPONSE: "{user_message}"

# OFFICIAL COMPANY INFORMATION:
# {context}

# EVALUATION PROCESS - FOLLOW THIS EXACT ORDER:

# STEP 1: FACTUAL ACCURACY CHECK (HIGHEST PRIORITY)
# Check if the learner's response contains ANY incorrect information about:
# - Package existence (Cloudnine HAS Economy, Standard, Premium packages)
# - Package pricing (Economy: ₹45,000-₹65,000, Standard: ₹65,000-₹85,000, Premium: ₹85,000-₹1,20,000)
# - Package inclusions/exclusions
# - Insurance partnerships and coverage
# - Booking procedures and policies
# - Any other company facts

# IF ANY FACTUAL ERRORS FOUND:
# "Dear Learner, you said '[wrong information]' but according to our official information: [correct facts]. You should respond: '[specific correct response]'."
# STOP EVALUATION HERE - DO NOT PROCEED TO STEP 2.

# STEP 2: CUSTOMER SERVICE APPROPRIATENESS (ONLY IF STEP 1 PASSES)
# Is this response appropriate customer service behavior?
# - Asking clarifying questions = ALWAYS APPROPRIATE
# - Showing empathy/acknowledgment = ALWAYS APPROPRIATE  
# - Requesting details to provide better help = ALWAYS APPROPRIATE
# - Being polite and professional = ALWAYS APPROPRIATE

# IF APPROPRIATE CUSTOMER SERVICE:
# "[CORRECT]"

# IF INAPPROPRIATE (ignoring customer, being rude, not addressing their question):
# "Dear Learner, the customer was [asking/expressing concern about X], but your response doesn't address their need. You should [specific actions] to properly help them with their [specific concern]."

# REMEMBER:
# - FACT-CHECKING IS MORE IMPORTANT THAN CONVERSATION FLOW
# - Giving wrong company information is ALWAYS incorrect, regardless of tone
# - Asking questions to understand customer needs better is ALWAYS good customer service
# - Only evaluate conversation appropriateness if all facts are correct

# KEEP YOUR RESPONSE LIMITED TO 20 WORDS.
# """
#             response = await self.llm_client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{"role": "user", "content": fact_check_prompt}],
#             temperature=0.1,
#             max_tokens=200
#             )
        
#             result = response.choices[0].message.content.strip()
#             print("resullttt",result,result.strip()== "[CORRECT]")
#             print("resullttt (repr):", repr(result))
#             if result.strip() == "[CORRECT]":
#                 return None
#             else:
#                 return result
#         except Exception as e:
#             print(f"Fact-checking error: {e}")
#             return None
    # 
    async def _check_user_response_accuracy(self, user_message: str, conversation_history: List[Message], knowledge_base_id: str) -> Optional[str]:
        """Hybrid coaching: Enhanced template coaching + existing verification"""
    
        try:
            # Wait longer before coaching and only flag major issues
            if len(conversation_history) <= 5:
                return None
            
            # Only check for major factual errors if we have a knowledge base
            if not knowledge_base_id:
                return None
            
            language_instructions = await self._get_language_instructions()
        
            # 🔄 HYBRID APPROACH: Try enhanced coaching first, fallback to existing
            enhanced_coaching = None
        
            # TRY: Enhanced contextual coaching if available
            if hasattr(self, 'fact_checker') and self.fact_checker.has_coaching_rules:
                try:
                    print(f"Using enhanced coaching with language: {language_instructions[:50] if language_instructions else 'None'}...")
                    verification = await self.fact_checker.verify_response_with_coaching(
                        user_message, conversation_history, knowledge_base_id, language_instructions
                    )
                
                    if verification.result != FactCheckResult.CORRECT:
                        if verification.coaching_feedback:
                            enhanced_coaching = f"Dear Learner, {verification.coaching_feedback}"
                        elif verification.explanation:
                            enhanced_coaching = f"Dear Learner, {verification.explanation}"
                        
                except Exception as enhanced_error:
                    print(f"Enhanced coaching failed: {enhanced_error}")
                    enhanced_coaching = None
        
            # FALLBACK: Only run existing coaching if enhanced failed
            if not enhanced_coaching or enhanced_coaching == "Dear Learner, ":
                existing_coaching = await self._run_existing_coaching_logic(
                    user_message, conversation_history, knowledge_base_id, language_instructions
                )
                if existing_coaching:
                    print("✅ Using existing coaching logic")
                    return existing_coaching
            else:
                print("✅ Using enhanced template coaching")
                return enhanced_coaching
            
            return None
            
        except Exception as e:
            print(f"Fact-checking error: {e}")
            return None

    async def _run_existing_coaching_logic(self, user_message: str, conversation_history: List[Message], 
                                     knowledge_base_id: str, language_instructions: str) -> Optional[str]:
        """Your existing coaching logic - UNCHANGED"""
    
        # Search for relevant info in documents (skip if no knowledge base)
        search_results = []
        if knowledge_base_id:
            search_results = await self.vector_search.vector_search(
                user_message, knowledge_base_id, top_k=3, openai_client=self.llm_client
            )
    
        # Continue with coaching even without search results
        context = ""
        if search_results:
            context = "\n".join([result['content'] for result in search_results])
        else:
            context = "No specific company information available - provide general customer service coaching based on best practices."
        
        # Context already built above
        convo_context = ""
        for msg in conversation_history[-4:]:  # Last 4 messages for context
            role = "Customer" if msg.role == self.config.bot_role else "Learner"
            convo_context += f"{role}: {msg.content}\n"

        # Much more restrictive coaching - only major factual errors
        fact_check_prompt = f"""
{language_instructions}

You are reviewing a learner's response. ONLY flag MAJOR factual errors.

LEARNER'S RESPONSE: "{user_message}"
COMPANY INFORMATION: {context}

ONLY flag if the learner stated:
- Completely wrong product/service names
- Wildly incorrect prices (off by >50%)
- Non-existent services/features
- Clearly false company policies

DO NOT flag:
- Spelling/grammar errors
- Different conversation styles
- Step-by-step questioning
- Not mentioning everything at once
- General customer service approaches

IF MAJOR FACTUAL ERROR:
"Dear Learner, [specific wrong fact] is incorrect. The correct information is [right fact]."

OTHERWISE:
"[CORRECT]"
"""
    
        print(f"Using language instructions: {language_instructions[:50]}...")
        response = await self.llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a training coach. CRITICAL: You must respond in the exact same language as these instructions: {language_instructions}"},
            {"role": "user", "content": fact_check_prompt}
        ],
        temperature=0.1,
        max_tokens=200
    )
        log_token_usage(response, "_run_existing_coaching_logic")
        result = response.choices[0].message.content.strip()
        print("existing coaching result:", result)
    
        if result.strip() == "[CORRECT]":
            return None
        else:
            return result    
    # 
    async def _get_language_instructions(self) -> str:
        """Get language instructions from session"""
        try:
            if not hasattr(self, 'config') or not self.config.language_id:
                print("No language_id found, using default")
                return "Respond in English. Provide coaching feedback in clear, professional language."
        
            # Get language from database
            language = await self.db.languages.find_one({"_id": str(self.config.language_id)})
        
            if language and language.get("prompt"):
                instructions = language["prompt"]
                print(f"Language instructions retrieved: {instructions[:100]}...")
                return instructions
            else:
                print("No language prompt found, using default")
                return "Respond in English. Provide coaching feedback in clear, professional language."
            
        except Exception as e:
            print(f"Error getting language instructions: {e}")
            return "Respond in English. Provide coaching feedback in clear, professional language."    
# 
    async def _process_normal_stream(self, response, name: Optional[str]):
        """Process normal streaming response (learn/assess modes)"""
        async def normal_generator():
            full_response = ""
            
            async for chunk in response:
                if len(chunk.choices) > 0:
                    chunk_text = chunk.choices[0].delta.content
                    finish_reason = chunk.choices[0].finish_reason
                    
                    if chunk_text:
                        full_response += chunk_text
                        
                        # Apply name replacement
                        if name:
                            updated_text = self.replace_name(full_response, name)
                        else:
                            updated_text = full_response
                        
                        yield {"chunk": updated_text, "finish": None, "usage": None}
                    
                    if finish_reason == "stop":
                        if name:
                            final_text = self.replace_name(full_response, name)
                        else:
                            final_text = full_response
                        
                        yield {"chunk": final_text, "finish": "stop", "usage": None}
                
                # Handle usage statistics
                if hasattr(chunk, 'usage') and chunk.usage:
                    yield {
                        "chunk": full_response,
                        "finish": "stop", 
                        "usage": {
                            "completion_tokens": chunk.usage.completion_tokens,
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        }
                    }
        
        return normal_generator()
    
    async def _apply_fact_check_corrections(self, response: str, fact_checks: List) -> str:
        """Apply corrections based on fact-check results"""
        
        incorrect_checks = [
            fc for fc in fact_checks 
            if fc.result in ["INCORRECT", "PARTIALLY_CORRECT"]
        ]
        
        if not incorrect_checks:
            return response
        
        # Build correction prompt
        corrections = []
        for fc in incorrect_checks:
            if hasattr(fc, 'suggested_correction') and fc.suggested_correction:
                corrections.append(f"Issue: {fc.explanation}\nCorrection: {fc.suggested_correction}")
        
        if not corrections:
            return response
        
        correction_prompt = f"""
        The following response contains factual errors. Please provide a corrected version:
        
        ORIGINAL RESPONSE:
        {response}
        
        CORRECTIONS NEEDED:
        {chr(10).join(corrections)}
        
        Provide a corrected response that:
        1. Maintains the same conversational tone
        2. Incorporates the factual corrections
        3. Flows naturally without obvious correction markers
        """
        
        try:
            correction_response = await self.llm_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You provide factually corrected responses while maintaining natural conversation flow."},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            log_token_usage(correction_response, "_apply_fact_check_corrections")
            return correction_response.choices[0].message.content
            
        except Exception as e:
            print(f"Error applying corrections: {e}")
            return response  # Fallback to original
    
    def _calculate_accuracy(self, fact_checks: List) -> float:
        """Calculate accuracy percentage from fact checks"""
        if not fact_checks:
            return 100.0
        
        correct_count = len([fc for fc in fact_checks if fc.result == "CORRECT"])
        return round((correct_count / len(fact_checks)) * 100, 2) 
    
    async def _generate_coaching_if_needed(self, user_message: str, fact_checks: List) -> Optional[str]:
        """Generate coaching feedback if user's response needs correction"""
    
        # Check if user provided unhelpful or incorrect responses
        incorrect_checks = [
        fc for fc in fact_checks 
        if fc.result in ["INCORRECT", "PARTIALLY_CORRECT", "UNCLEAR"]
    ]
    
        # Also check for unhelpful responses (short, dismissive, etc.)
        is_unhelpful = await self._is_response_unhelpful(user_message)
    
        if not incorrect_checks and not is_unhelpful:
            return None  # No coaching needed
    
        # Build coaching feedback
        coaching_parts = []
    
        if incorrect_checks:
            # Address factual errors
            coaching_parts.append("There are some factual inaccuracies in your response.")
        
            for fc in incorrect_checks[:2]:  # Limit to 2 main corrections
                if hasattr(fc, 'suggested_correction') and fc.suggested_correction:
                    coaching_parts.append(f"Regarding {fc.claim.get('claim_text', 'this point')}: {fc.suggested_correction}")
    
        if is_unhelpful:
            # Address unhelpful response patterns
            coaching_parts.append("The response could be more helpful and constructive.")
            coaching_parts.append("Consider providing specific guidance, asking clarifying questions, and showing empathy for the customer's situation.")
    
        # Format final coaching message
        coaching_message = f"Dear learner, {' '.join(coaching_parts)} Please try to provide more comprehensive and accurate guidance."
    
        return coaching_message

    async def _is_response_unhelpful(self, user_message: str) -> bool:
        """Check if user response is unhelpful based on patterns - MORE RESTRICTIVE"""
    
        message_lower = user_message.lower().strip()
    
        # Only flag VERY unhelpful patterns
        unhelpful_patterns = [
        message_lower in ["no", "i don't know", "idk"],  # Removed length check
        "figure it out" in message_lower,
        "not my problem" in message_lower,
        "don't care" in message_lower,
    ]
    
        return any(unhelpful_patterns)    
   
   
    
    async def _process_with_knowledge_base(self, response, user_message: str, conversation_history: List[Message], name: Optional[str]):

        """Process response with knowledge base enhancement for learn mode"""
    
        # For learn mode, we enhance the AI expert's responses with knowledge base info
        # This is simpler than fact-checking - just add relevant context
    
        async def knowledge_enhanced_generator():
            full_response = ""
            usage_info = None

            async for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage_info = chunk.usage
        
        # Apply name replacement
            if name:
                final_response = self.replace_name(full_response, name)
            else:
                final_response = full_response
        
            # Stream the response (could enhance with knowledge base context here)
            words = final_response.split()
            current_text = ""
        
            for i, word in enumerate(words):
                current_text += word + " "
            
                if i % 3 == 0 or i == len(words) - 1:
                    is_final = i == len(words) - 1
                
                    yield {
                    "chunk": current_text.strip(),
                    "finish": "stop" if is_final else None,
                    "usage": usage_info if is_final else None
                }
                
                    if is_final:
                        break
    
        return knowledge_enhanced_generator()
    async def format_conversation(self, conversation_history: List[Message]) -> List[Dict[str, str]]:
        """Format conversation history for the LLM"""
        contents = []
        
        # Add system prompt
        system_content = self.config.system_prompt
        
        # If conversation is empty and mode is try/assess, add explicit wait instruction
        if len(conversation_history) == 0 and self.config.mode in ["try_mode", "assess_mode"]:
            system_content += "\n\nCRITICAL: This is the start of the conversation. DO NOT send any message. WAIT for the user to speak first. Do not greet, do not offer help, do not say anything until the user initiates."
        
        contents.append({"role": "system", "content": system_content})
        # Get persona if available
        # print(self.config)
        if self.config.persona_id:
            try:
                print(self.config.persona_id,"self.config.persona_id")
                persona = await self.db.personas.find_one({"_id": str(self.config.persona_id)})
                language = await self.db.languages.find_one({"_id": str(self.config.language_id)})
                # print("language",language)
                if persona:
                    persona_obj = PersonaDB(**persona)
                    language_obj= LanguageDB(**language)
                    persona_context = self.format_persona_context(scenario_prompt=self.config.system_prompt,persona=persona_obj,language=language_obj)
                    # Add persona information to system prompt
                    contents[0]["content"] = persona_context
                    # print("actual scenariossss",persona_context)
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
        # Add background story if available
        if persona.background_story:
            persona_markdown += f"- Background: {persona.background_story}\n"
        
        # Check if language prompt has [PERSONA_PLACEHOLDER] and inject persona details
        language_prompt = language.prompt
        if "[PERSONA_PLACEHOLDER]" in language_prompt:
            language_prompt = language_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)
        
        language_markdown = f"""
- Primary language: {language.name}
- Language instructions: {language_prompt}

"""
        # Replace placeholders
        scenario_prompt = scenario_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_markdown)
        scenario_prompt = scenario_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)
        return scenario_prompt
    
    def replace_name(self, original_text: str, name: str) -> str:
        """Replace [Your Name] with the provided name"""
        if "[Your Name]" in original_text:
            return original_text.replace("[Your Name]", name)
        return original_text
# learn 
    async def _generate_enhanced_expert_response(self, user_message: str, conversation_history: List[Message], enhanced_context: str) -> Any:
        """Generate AI expert response enhanced with specific knowledge base information"""
    
        try:
            # Format conversation for LLM with enhanced knowledge
            contents = await self.format_conversation(conversation_history)
        
            # Add the enhanced knowledge to the system prompt
            if contents and contents[0]["role"] == "system":
                # Inject knowledge into existing system prompt
                original_system = contents[0]["content"]
                enhanced_system = f"{original_system}\n\n{enhanced_context}\n\nUSE THIS SPECIFIC INFORMATION when teaching and answering questions. Provide concrete examples and accurate details from the company information above."
                contents[0]["content"] = enhanced_system
        
            # Add the current user message
            contents.append({"role": "user", "content": user_message})
        
            # Generate enhanced response
            enhanced_response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=contents,
            temperature=0.7,
            max_tokens=1000,
            stream=True,
            stream_options={"include_usage": True}
            )
            log_token_usage(enhanced_response, "_generate_enhanced_expert_response")
            return enhanced_response
        
        except Exception as e:
            print(f"Error generating enhanced response: {e}")
            return None

    async def _stream_enhanced_response(self, enhanced_response, name: Optional[str]):
        """Stream the enhanced expert response"""
    
        if not enhanced_response:
            # Fallback to basic response if enhancement failed
            return self._create_fallback_response(name)
    
        async def enhanced_generator():
            full_response = ""
        
            async for chunk in enhanced_response:
                if len(chunk.choices) > 0:
                    chunk_text = chunk.choices[0].delta.content
                    finish_reason = chunk.choices[0].finish_reason
                
                    if chunk_text:
                        full_response += chunk_text
                    
                        # Apply name replacement
                        if name:
                            updated_text = self.replace_name(full_response, name)
                        else:
                            updated_text = full_response
                    
                        yield {"chunk": updated_text, "finish": None, "usage": None}
                
                    if finish_reason == "stop":
                        if name:
                            final_text = self.replace_name(full_response, name)
                        else:
                            final_text = full_response
                    
                        yield {"chunk": final_text, "finish": "stop", "usage": None}
            
                # Handle usage statistics
                if hasattr(chunk, 'usage') and chunk.usage:
                    yield {
                    "chunk": full_response,
                    "finish": "stop", 
                    "usage": {
                        "completion_tokens": chunk.usage.completion_tokens,
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "total_tokens": chunk.usage.total_tokens
                    },
                    "knowledge_enhancement": {
                        "enhanced_with_documents": True,
                        "knowledge_base_used": self.knowledge_base_id
                    }
                    }
    
        return enhanced_generator()

    async def _create_fallback_response(self, name: Optional[str]):
        """Create a simple fallback response if enhancement fails"""
        async def fallback_generator():
            fallback_text = "I'm here to help you learn. Could you please rephrase your question?"
            if name:
                fallback_text = self.replace_name(fallback_text, name)
        
            yield {"chunk": fallback_text, "finish": "stop", "usage": None}
    
        return fallback_generator() 
# 

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
    avatar_id: Optional[UUID] = None,
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
        avatar_id=str(avatar_id) if avatar_id else None,
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


# async def update_chat_session(db: Any, session: ChatSession):
#     """Update a chat session in the database"""
#     session.last_updated = datetime.now()
#     # await db.sessions.update_one(
#     #     {"_id": str(session.id)},
#     #     {"$set": session.dict()}
#     # )
#     await db.sessions.update_one(
#     {"_id": str(session.id)},
#     {"$set": session.model_dump() if hasattr(session, 'model_dump') else session.dict()}
# )
async def update_chat_session(db: Any, session: ChatSession):
    """Update a chat session in the database"""
    session.last_updated = datetime.now()
    
    await db.sessions.update_one(
        {"_id": str(session.id)},
        {"$set": session.to_mongo_dict()}
    )