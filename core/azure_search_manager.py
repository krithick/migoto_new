"""
Phase 2: Azure Search Vector Integration
Advanced vector search and knowledge retrieval
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI
import re
from models.enhanced_models import DocumentChunk, FactCheckVerification, FactCheckResult
from core.simple_token_logger import log_token_usage

class AzureVectorSearchManager:
    """Manages Azure Cognitive Search vector operations"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.base_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "enhanced-knowledge-base")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Search configuration missing")
    
    def get_search_client(self, knowledge_base_id: str) -> SearchClient:
        """Get search client for specific scenario index"""
        # index_name = f"{self.base_index_name}-{scenario_id.replace('-', '').lower()[:20]}"
        index_name = self.base_index_name
        return SearchClient(
            endpoint=self.endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(self.api_key)
        )
    
    # async def index_document_chunks(self, chunks: List[DocumentChunk], scenario_id: str) -> bool:
    #     """Index document chunks in Azure Search"""
    #     search_client = self.get_search_client(scenario_id)
        
    #     try:
    #         # Prepare documents for indexing
    #         documents = []
    #         for chunk in chunks:
    #             doc = {
    #                 "id": f"{scenario_id}_{chunk.id}",
    #                 "content": chunk.content,
    #                 "document_id": chunk.document_id,
    #                 "knowledge_base_id": chunk.knowledge_base_id,
    #                 "scenario_id": scenario_id,
    #                 "chunk_index": chunk.chunk_index,
    #                 "word_count": chunk.word_count,
    #                 "section": chunk.section or "",
    #                 "page_number": chunk.page_number or 0,
    #                 "contentVector": chunk.embedding or [],
    #                 "source_file": chunk.metadata.get("source_file", ""),
    #                 "document_type": chunk.metadata.get("document_type", "unknown")
    #             }
    #             documents.append(doc)
            
    #         # Upload in batches
    #         batch_size = 100
    #         for i in range(0, len(documents), batch_size):
    #             batch = documents[i:i + batch_size]
    #             await search_client.upload_documents(batch)
            
    #         return True
            
    #     except Exception as e:
    #         print(f"Error indexing chunks: {e}")
    #         return False
    #     finally:
    #         # Always close the client
    #         await search_client.close()

    async def index_document_chunks(self, chunks: List[DocumentChunk], knowledge_base_id: str) -> bool:
        """Index document chunks in Azure Search"""
        search_client = self.get_search_client(knowledge_base_id)  # Use knowledge_base_id
    
        try:
            documents = []
            for chunk in chunks:
                chunk.knowledge_base_id = knowledge_base_id 
                doc = {
                "id": f"{knowledge_base_id}_{chunk.id}",  # ✅ Use knowledge_base_id
                "content": chunk.content,
                "document_id": chunk.document_id,
                "knowledge_base_id": knowledge_base_id,  # ✅ Use consistent ID
                "scenario_id": knowledge_base_id,  # Keep for backward compatibility
                "chunk_index": chunk.chunk_index,
                "word_count": chunk.word_count,
                "section": chunk.section or "",
                "page_number": chunk.page_number or 0,
                "contentVector": chunk.embedding or [],
                "source_file": chunk.metadata.get("source_file", ""),
                "document_type": chunk.metadata.get("document_type", "unknown")
            }
                documents.append(doc)
        
            # Upload in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                await search_client.upload_documents(batch)
        
            return True
        
        except Exception as e:
            print(f"Error indexing chunks: {e}")
            return False
        finally:
            await search_client.close()     
    
  
    
    # 
    async def vector_search(self, query: str, knowledge_base_id: str, top_k: int = 5,
                        openai_client: AsyncAzureOpenAI = None) -> List[Dict[str, Any]]:
        """Perform vector search with query embedding - SECURE VERSION"""
        search_client = self.get_search_client(knowledge_base_id)
    
        try:
            if openai_client:
                query_embedding = await self._get_query_embedding(query, openai_client)
            else:
                query_embedding = None
        
            search_results = []
        
            # 🔒 CRITICAL: Filter by knowledge_base_id
            filter_expression = f"knowledge_base_id eq '{knowledge_base_id}'"
        
            if query_embedding:
                results = await search_client.search(
                search_text=query,
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_embedding,
                    "fields": "contentVector",
                    "k": top_k
                }],
                filter=filter_expression,  # ✅ This prevents cross-contamination
                select=["id", "content", "document_id", "source_file", "document_type", "chunk_index", "knowledge_base_id"],
                top=top_k
                )
            else:
                results = await search_client.search(
                search_text=query,
                filter=filter_expression,  # ✅ This prevents cross-contamination  
                select=["id", "content", "document_id", "source_file", "document_type", "chunk_index", "knowledge_base_id"],
                top=top_k
                )
        
            async for result in results:
                # Double-check knowledge_base_id matches
                if result.get("knowledge_base_id") == knowledge_base_id:
                    search_results.append({
                    "chunk_id": result["id"],
                    "content": result["content"],
                    "document_id": result["document_id"],
                    "source_file": result.get("source_file", ""),
                    "document_type": result.get("document_type", "unknown"),
                    "chunk_index": result.get("chunk_index", 0),
                    "search_score": result.get("@search.score", 0)
                    })
        
            return search_results
        
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
        finally:
            await search_client.close()     
    # 
    async def _get_query_embedding(self, query: str, openai_client: AsyncAzureOpenAI) -> List[float]:
        """Generate embedding for search query"""
        response = await openai_client.embeddings.create(
            input=[query],
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    # ADD this method to AzureVectorSearchManager class:

    async def validate_knowledge_base_access(self, knowledge_base_id: str, user_company_id: str) -> bool:
        """Validate user has access to this knowledge base"""
        try:
            # Check if knowledge base belongs to user's company or is shared
            kb_record = await self.db.knowledge_bases.find_one({"_id": knowledge_base_id})
        
            if not kb_record:
                return False
            
            # Add your company access logic here
            template_id = kb_record.get("template_id")
            if template_id:
                template = await self.db.templates.find_one({"id": template_id})
                # Add template access validation based on your company hierarchy
            
            return True  # Implement your actual validation logic
        
        except Exception as e:
            print(f"Error validating KB access: {e}")
            return False    
class EnhancedFactChecker:
    """Advanced fact-checking with vector search"""
    
    def __init__(self, vector_search: AzureVectorSearchManager, openai_client: AsyncAzureOpenAI,coaching_rules: Dict = None):
        self.vector_search = vector_search
        self.openai_client = openai_client
        print(coaching_rules,"coaching_rulesin class enchanced fact checker")
        if coaching_rules and isinstance(coaching_rules, dict):
            self.coaching_rules = coaching_rules
            self.has_coaching_rules = True
            print(f"FactChecker initialized with coaching rules from template")
        else:
            self.coaching_rules = {
                "process_requirements": {},
                "document_specific_mistakes": [],
                "customer_context_from_document": {},
                "correction_preferences_from_document": {},
                "domain_specific_validation": {}
            }
            self.has_coaching_rules = False
            print(f"FactChecker initialized with basic fact-checking only")    
    # async def verify_response_claims(self, response_text: str, scenario_id: str) -> List[FactCheckVerification]:
    #     """Verify all claims in an AI response"""
        
    #     # Extract factual claims
    #     claims = await self._extract_factual_claims(response_text)
        
    #     # Verify each claim
    #     verifications = []
    #     for claim in claims:
    #         verification = await self._verify_single_claim(claim, scenario_id)
    #         verifications.append(verification)
        
    #     return verifications
    async def verify_response_claims(self, response_text: str, scenario_id: str, conversation_history: List = None) -> List[FactCheckVerification]:
        """Verify all claims in an AI response"""
    
        # Extract factual claims
        claims = await self._extract_factual_claims(response_text)
    
        # Verify each claim
        verifications = []
        for claim in claims:
            # Use smart verification that chooses contextual or basic
            verification = await self.verify_response_with_coaching(claim, conversation_history or [], scenario_id)
            verifications.append(verification)
    
        return verifications

    
    async def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract verifiable claims from text"""
        print("text",text)
        prompt = f"""
        Extract specific factual claims from this text that can be verified:
        
        {text}
        
        Focus on:
        - Prices, costs, amounts
        - Product features, specifications
        - Policies, procedures, rules
        - Dates, times, schedules
        - Technical details
        - Contact information
        
        Return as JSON array of claim strings.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract verifiable factual claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            log_token_usage(response,"_extract_factual_claims")
            print(",response",response)
            result = response.choices[0].message.content
            print("result",result)
            claims = json.loads(result)
            return claims if isinstance(claims, list) else []
            
        except Exception as e:
            print(f"Error extracting claims manager: {e}")
            return []
    
    async def _verify_single_claim(self, claim: str, scenario_id: str) -> FactCheckVerification:
        """Verify a single claim against knowledge base"""
        
        try:
            # Search for relevant information
            search_results = await self.vector_search.vector_search(
                claim, scenario_id, top_k=3, openai_client=self.openai_client
            )
            
            if not search_results:
                # No knowledge base available - provide general coaching
                return await self._provide_general_coaching(claim, scenario_id)
            
            # Build context from search results
            context = "\n\n".join([
                f"Source: {result['source_file']}\nContent: {result['content']}"
                for result in search_results
            ])
            
            # Verify claim with LLM
            verification_prompt = f"""
            Verify this claim against the knowledge base:
            
            CLAIM: {claim}
            
            KNOWLEDGE BASE:
            {context}
            
            Provide assessment as JSON:
            {{
                "result": "CORRECT|INCORRECT|PARTIALLY_CORRECT|UNSUPPORTED|UNCLEAR",
                "confidence_score": 0.0-1.0,
                "explanation": "Detailed explanation",
                "suggested_correction": "If incorrect, what's the correct information (null if not applicable)"
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise fact-checker."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            log_token_usage(response,"_verify_single_claim")
            result_json = json.loads(response.choices[0].message.content)
            
            return FactCheckVerification(
                claim={"claim_text": claim, "claim_type": "general", "confidence": 1.0, "extracted_from": "ai_response"},
                result=FactCheckResult(result_json["result"]),
                confidence_score=result_json["confidence_score"],
                explanation=result_json["explanation"],
                suggested_correction=result_json.get("suggested_correction"),
                supporting_chunks=[r["chunk_id"] for r in search_results],
                source_documents=[r["source_file"] for r in search_results]
            )
            
        except Exception as e:
            return FactCheckVerification(
                claim={"claim_text": claim, "claim_type": "unknown", "confidence": 0.0, "extracted_from": "ai_response"},
                result=FactCheckResult.UNCLEAR,
                confidence_score=0.0,
                explanation=f"Error during verification: {str(e)}",
                supporting_chunks=[],
                source_documents=[]
            )
    
    # async def _verify_contextual_response(self, claim: str, conversation_history: List, 
    #                                 scenario_id: str) -> FactCheckVerification:
    #     """Enhanced verification with template-specific coaching rules"""
    
    #     try:
    #         # Your existing search logic
    #         search_results = await self.vector_search.vector_search(
    #             claim, scenario_id, top_k=3, openai_client=self.openai_client
    #         )
        
    #         if not search_results:
    #             return FactCheckVerification(
    #             claim={"claim_text": claim, "claim_type": "contextual", "confidence": 0.0, "extracted_from": "ai_response"},
    #             result=FactCheckResult.UNSUPPORTED,
    #             confidence_score=0.0,
    #             explanation="No relevant information found in knowledge base",
    #             supporting_chunks=[],
    #             source_documents=[]
    #             )
        
    #         # Build context from search results
    #         context = "\n\n".join([
    #         f"Source: {result['source_file']}\nContent: {result['content']}"
    #         for result in search_results
    #         ])
        
    #         # Build conversation context (last 5 messages)
    #         conversation_text = "\n".join([
    #         f"{msg.role}: {msg.content}" for msg in conversation_history[-5:]
    #         ]) if conversation_history else "No conversation history"
        
    #         # ADD: Build coaching context from template rules
    #         coaching_context = ""
    #         if self.has_coaching_rules and self.coaching_rules:
    #             try:
    #                 process_reqs = self.coaching_rules.get("process_requirements", {})
    #                 mistakes = self.coaching_rules.get("document_specific_mistakes", [])
    #                 customer_context = self.coaching_rules.get("customer_context_from_document", {})
                
    #                 # Safe field access with defaults
    #                 methodology = process_reqs.get("mentioned_methodology", "No specific process mentioned")
    #                 steps = process_reqs.get("required_steps", "No specific steps defined")
    #                 customer_type = customer_context.get("target_customer_description", "General customer")
    #                 mistake_patterns = [m.get("mistake_pattern", "No pattern") for m in mistakes if isinstance(m, dict)]
                
    #                 coaching_context = f"""
    #                 DOCUMENT-SPECIFIC COACHING RULES:
    #             Required Process: {methodology}
    #             Required Steps: {steps}
    #             Customer Type: {customer_type}
    #             Common Mistakes to Avoid: {mistake_patterns}
    #             """
    #             except Exception as coaching_error:
    #                 print(f"Warning: Could not build coaching context: {coaching_error}")
    #                 coaching_context = "BASIC COACHING: Use professional communication and verify facts against knowledge base."
    #         else:
    #             coaching_context = "BASIC COACHING: Use professional communication and verify facts against knowledge base."
        
    #         # Enhanced verification prompt with template rules
    #         verification_prompt = f"""
    #         Verify this user response in the context of a training scenario:
        
    #         USER RESPONSE TO VERIFY: {claim}
        
    #         CONVERSATION HISTORY:
    #         {conversation_text}
        
    #         KNOWLEDGE BASE CONTEXT:
    #         {context}
        
    #         {coaching_context}
        
    #         Analyze the user response for:
    #         1. FACTUAL ACCURACY: Is the information correct per knowledge base?
    #         2. PROCESS ADHERENCE: Does the response follow the required process/methodology?
    #         3. CUSTOMER APPROPRIATENESS: Is the response suitable for the customer type?
    #         4. COACHING COMPLIANCE: Does it avoid the common mistakes mentioned?
        
    #         Provide assessment as JSON:
    #         {{
    #         "result": "CORRECT|INCORRECT|PARTIALLY_CORRECT|PROCESS_VIOLATION|CUSTOMER_MISMATCH|UNSUPPORTED",
    #         "confidence_score": 0.0-1.0,
    #         "explanation": "Detailed explanation of the assessment",
    #         "coaching_feedback": "Specific guidance based on template coaching rules",
    #         "suggested_correction": "What the correct response should be (if applicable)"
    #         }}
    #         """
        
    #         response = await self.openai_client.chat.completions.create(
    #         model="gpt-4o",
    #         messages=[
    #             {"role": "system", "content": "You are a contextual training coach that provides specific feedback based on document requirements."},
    #             {"role": "user", "content": verification_prompt}
    #         ],
    #         temperature=0.1,
    #         max_tokens=800
    #         )
        
    #         result_text = response.choices[0].message.content
    #         try:
    #             result_text = response.choices[0].message.content.strip()
    
    #             # Try to parse JSON first
    #             result_json = json.loads(result_text)
    #             print(result_json)
    #         except json.JSONDecodeError:
    #             # ❌ JSON parsing failed - extract coaching from raw text
    #             print(f"JSON parsing failed. Raw LLM response: {result_text}")
    
    #             # Try to extract useful coaching from the raw text response
    #             if "incorrect" in result_text.lower() or "wrong" in result_text.lower():
    #                 # LLM found an issue but didn't return proper JSON
    #                 result_json = {
    #         "result": "INCORRECT",
    #         "confidence_score": 0.7,
    #         "explanation": result_text[:200],  # Use the actual LLM response
    #         "coaching_feedback": result_text[:300],  # Use the actual feedback
    #         "suggested_correction": None
    #                 }
    #             else:
    #                 # Truly unclear response
    #                 result_json = {
    #         "result": "UNCLEAR",
    #         "confidence_score": 0.3,
    #         "explanation": f"Could not analyze: {result_text[:100]}",
    #         "coaching_feedback": None,  # ❌ Don't provide generic coaching
    #         "suggested_correction": None
    #                 }

    #         except Exception as e:
    #                 print(f"Error in contextual verification: {e}")
    #                 # Return completely empty result to force fallback to existing logic
    #                 result_json = {
    #                 "result": "UNCLEAR",
    #     "confidence_score": 0.0,
    #     "explanation": f"Verification error: {str(e)}",
    #     "coaching_feedback": None,  # ❌ No generic coaching
    #     "suggested_correction": None
    #                 }               
    
        
    #     except Exception as e:
    #         print(f"Error in contextual verification: {e}")
    #         return FactCheckVerification(
    #         claim={"claim_text": claim, "claim_type": "contextual", "confidence": 0.0, "extracted_from": "ai_response"},
    #         result=FactCheckResult.UNCLEAR,
    #         confidence_score=0.0,
    #         explanation=f"Error during contextual verification: {str(e)}",
    #         supporting_chunks=[],
    #         source_documents=[]
    #         )    
    # 
    async def _verify_contextual_response(self, claim: str, conversation_history: List, 
                                    scenario_id: str) -> FactCheckVerification:
        """Enhanced verification with template-specific coaching rules"""

        try:
            # Your existing search logic
            search_results = await self.vector_search.vector_search(
                claim, scenario_id, top_k=3, openai_client=self.openai_client
            )
    
            if not search_results:
                # No knowledge base available - provide contextual coaching without documents
                return await self._provide_contextual_coaching_without_docs(claim, conversation_history)
    
            # Build context from search results
            context = "\n\n".join([
                f"Source: {result['source_file']}\nContent: {result['content']}"
            for result in search_results
            ])
    
            # Build conversation context (last 5 messages)
            conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in conversation_history[-5:]
            ]) if conversation_history else "No conversation history"
    
            # ADD: Build coaching context from template rules
            coaching_context = ""
            if self.has_coaching_rules and self.coaching_rules:
                try:
                    process_reqs = self.coaching_rules.get("process_requirements", {})
                    mistakes = self.coaching_rules.get("document_specific_mistakes", [])
                    customer_context = self.coaching_rules.get("customer_context_from_document", {})
            
                    # Safe field access with defaults
                    methodology = process_reqs.get("mentioned_methodology", "No specific process mentioned")
                    steps = process_reqs.get("required_steps", "No specific steps defined")
                    customer_type = customer_context.get("target_customer_description", "General customer")
                    mistake_patterns = [m.get("mistake_pattern", "No pattern") for m in mistakes if isinstance(m, dict)]
            
                    coaching_context = f"""
                DOCUMENT-SPECIFIC COACHING RULES:
            Required Process: {methodology}
            Required Steps: {steps}
            Customer Type: {customer_type}
            Common Mistakes to Avoid: {mistake_patterns}
            """
                except Exception as coaching_error:
                    print(f"Warning: Could not build coaching context: {coaching_error}")
                    coaching_context = "BASIC COACHING: Use professional communication and verify facts against knowledge base."
            else:
                coaching_context = "BASIC COACHING: Use professional communication and verify facts against knowledge base."
    
            # Enhanced verification prompt with template rules
            verification_prompt = f"""
        Verify this user response in the context of a training scenario:
    
        USER RESPONSE TO VERIFY: {claim}
    
        CONVERSATION HISTORY:
        {conversation_text}
    
        KNOWLEDGE BASE CONTEXT:
        {context}
    
        {coaching_context}
    
        Analyze the user response for:
        1. FACTUAL ACCURACY: Is the information correct per knowledge base?
        2. PROCESS ADHERENCE: Does the response follow the required process/methodology?
        3. CUSTOMER APPROPRIATENESS: Is the response suitable for the customer type?
        4. COACHING COMPLIANCE: Does it avoid the common mistakes mentioned?
    
        Provide assessment as JSON:
        {{
        "result": "CORRECT|INCORRECT|PARTIALLY_CORRECT|PROCESS_VIOLATION|CUSTOMER_MISMATCH|UNSUPPORTED",
        "confidence_score": 0.0-1.0,
        "explanation": "Detailed explanation of the assessment",
        "coaching_feedback": "Specific guidance based on template coaching rules",
        "suggested_correction": "What the correct response should be (if applicable)"
        }}
        """
    
            response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a contextual training coach that provides specific feedback based on document requirements."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0.1,
            max_tokens=800
            )
            log_token_usage(response,"_verify_contextual_response")
            result_text = response.choices[0].message.content.strip()
        
            try:
                # ✅ FIX: Handle markdown code blocks properly
                if result_text.startswith('```json'):
                    # Extract JSON from markdown code block
                    json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                    if json_match:
                        result_json = json.loads(json_match.group(1))
                    else:
                        raise json.JSONDecodeError("Could not extract JSON from markdown", result_text, 0)
                else:
                    # Direct JSON parsing
                    result_json = json.loads(result_text)
            
                print(f"✅ Successfully parsed JSON: {result_json}")
            
            except json.JSONDecodeError:
                # ❌ JSON parsing failed - extract coaching from raw text
                print(f"JSON parsing failed. Raw LLM response: {result_text}")

                # Try to extract useful coaching from the raw text response
                if "incorrect" in result_text.lower() or "wrong" in result_text.lower():
                    # LLM found an issue but didn't return proper JSON
                    result_json = {
                    "result": "INCORRECT",
                    "confidence_score": 0.7,
                    "explanation": result_text[:200],  # Use the actual LLM response
                    "coaching_feedback": result_text[:300],  # Use the actual feedback
                    "suggested_correction": None
                }
                else:
                    # Truly unclear response
                    result_json = {
                    "result": "UNCLEAR",
                    "confidence_score": 0.3,
                    "explanation": f"Could not analyze: {result_text[:100]}",
                    "coaching_feedback": None,  # ❌ Don't provide generic coaching
                    "suggested_correction": None
                }

            # ✅ ADD: Map LLM results to valid FactCheckResult values
            result_mapping = {
            "CORRECT": "CORRECT",
            "INCORRECT": "INCORRECT", 
            "PARTIALLY_CORRECT": "PARTIALLY_CORRECT",
            "PROCESS_VIOLATION": "INCORRECT",  # ✅ Map this to INCORRECT
            "CUSTOMER_MISMATCH": "INCORRECT",  # ✅ Map this to INCORRECT
            "UNSUPPORTED": "UNSUPPORTED",
            "UNCLEAR": "UNSUPPORTED"
        }

            llm_result = result_json.get("result", "UNSUPPORTED")
            mapped_result = result_mapping.get(llm_result, "UNSUPPORTED")
        
            print(f"🔍 LLM result: {llm_result} → Mapped to: {mapped_result}")
            print(f"🔍 Coaching feedback: {result_json.get('coaching_feedback', 'None')}")

            # ✅ RETURN: Create and return the verification object
            verification_result = FactCheckVerification(
            claim={"claim_text": claim, "claim_type": "contextual", "confidence": 1.0, "extracted_from": "ai_response"},
            result=FactCheckResult(mapped_result),  # ✅ Use mapped result
            confidence_score=result_json.get("confidence_score", 0.5),
            explanation=result_json.get("explanation", "Analysis completed"),
            suggested_correction=result_json.get("suggested_correction"),
            coaching_feedback=result_json.get("coaching_feedback"),  # ✅ This is the key field
            supporting_chunks=[r["chunk_id"] for r in search_results],
            source_documents=[r["source_file"] for r in search_results]
        )
        
            print(f"✅ Returning verification object with result: {verification_result.result}")
            return verification_result
        
        except Exception as e:
            print(f"Error in contextual verification: {e}")
            return FactCheckVerification(
            claim={"claim_text": claim, "claim_type": "contextual", "confidence": 0.0, "extracted_from": "ai_response"},
            result=FactCheckResult.UNSUPPORTED,
            confidence_score=0.0,
            explanation=f"Error during contextual verification: {str(e)}",
            supporting_chunks=[],
            source_documents=[]
        )
    # 
    # async def verify_response_with_coaching(self, claim: str, conversation_history: List, scenario_id: str) -> FactCheckVerification:
    #     """Smart verification that uses contextual coaching if available, falls back to basic fact-checking"""
    
    #     if self.has_coaching_rules:
    #         try:
    #             # Use enhanced contextual verification
    #             return await self._verify_contextual_response(claim, conversation_history, scenario_id)
    #         except Exception as e:
    #             print(f"Contextual verification failed, falling back to basic: {e}")
    #             # Fall through to basic verification
    
    #     # Use existing basic verification as fallback
    #     return await self._verify_single_claim(claim, scenario_id)  
    async def verify_response_with_coaching(self, claim: str, conversation_history: List, scenario_id: str) -> FactCheckVerification:
        """Smart verification that uses contextual coaching if available, falls back to basic fact-checking"""
    
        if self.has_coaching_rules:
            try:
                # Use enhanced contextual verification
                result = await self._verify_contextual_response(claim, conversation_history, scenario_id)
            
                # ✅ FIX: Make sure we return the result, not None
                if result:
                    print(f"✅ Contextual verification succeeded: {result.result}")
                    return result
                else:
                    print("❌ Contextual verification returned None, falling back")
                
            except Exception as e:
                print(f"Contextual verification failed, falling back to basic: {e}")
                # Fall through to basic verification
    
        # Use existing basic verification as fallback
        print("🔄 Using basic fact-checking as fallback")
        return await self._verify_single_claim(claim, scenario_id)
    
    async def _provide_general_coaching(self, claim: str, scenario_id: str) -> FactCheckVerification:
        """Provide general coaching when no knowledge base is available"""
        try:
            coaching_prompt = f"""
            Evaluate this learner response for professional quality:
            
            LEARNER RESPONSE: {claim}
            
            Provide coaching feedback focusing on:
            - Professional communication
            - Appropriateness for the context
            - Helpfulness and clarity
            - Completeness of response
            
            Return as JSON:
            {{
                "result": "CORRECT|NEEDS_IMPROVEMENT",
                "coaching_feedback": "Specific coaching advice",
                "explanation": "Brief explanation"
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional training coach who adapts feedback to any domain or scenario type."},
                    {"role": "user", "content": coaching_prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                if result_text.startswith('```json'):
                    json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                    if json_match:
                        result_json = json.loads(json_match.group(1))
                    else:
                        raise json.JSONDecodeError("Could not extract JSON", result_text, 0)
                else:
                    result_json = json.loads(result_text)
                
                coaching_feedback = result_json.get("coaching_feedback")
                is_correct = result_json.get("result") == "CORRECT"
                
                return FactCheckVerification(
                    claim={"claim_text": claim, "claim_type": "general", "confidence": 1.0, "extracted_from": "ai_response"},
                    result=FactCheckResult.CORRECT if is_correct else FactCheckResult.INCORRECT,
                    confidence_score=0.8,
                    explanation=result_json.get("explanation", "General coaching provided"),
                    coaching_feedback=coaching_feedback,
                    supporting_chunks=[],
                    source_documents=[]
                )
                
            except json.JSONDecodeError:
                # Fallback to basic response
                return FactCheckVerification(
                    claim={"claim_text": claim, "claim_type": "general", "confidence": 1.0, "extracted_from": "ai_response"},
                    result=FactCheckResult.CORRECT,
                    confidence_score=0.5,
                    explanation="Response evaluated for general quality",
                    coaching_feedback=None,
                    supporting_chunks=[],
                    source_documents=[]
                )
                
        except Exception as e:
            print(f"Error in general coaching: {e}")
            return FactCheckVerification(
                claim={"claim_text": claim, "claim_type": "general", "confidence": 0.0, "extracted_from": "ai_response"},
                result=FactCheckResult.CORRECT,
                confidence_score=0.5,
                explanation="Unable to provide coaching",
                supporting_chunks=[],
                source_documents=[]
            )
    
    async def _provide_contextual_coaching_without_docs(self, claim: str, conversation_history: List) -> FactCheckVerification:
        """Provide contextual coaching using template rules but without knowledge base documents"""
        try:
            # Build conversation context
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}" for msg in conversation_history[-5:]
            ]) if conversation_history else "No conversation history"
            
            # Build coaching context from template rules
            coaching_context = ""
            if self.has_coaching_rules and self.coaching_rules:
                try:
                    process_reqs = self.coaching_rules.get("process_requirements", {})
                    mistakes = self.coaching_rules.get("document_specific_mistakes", [])
                    customer_context = self.coaching_rules.get("customer_context_from_document", {})
                    
                    methodology = process_reqs.get("mentioned_methodology", "Professional customer service")
                    steps = process_reqs.get("required_steps", "Listen, understand, respond appropriately")
                    customer_type = customer_context.get("target_customer_description", "General customer")
                    mistake_patterns = [m.get("mistake_pattern", "") for m in mistakes if isinstance(m, dict)]
                    
                    coaching_context = f"""
                    COACHING GUIDELINES:
                    Required Approach: {methodology}
                    Key Steps: {steps}
                    Customer Type: {customer_type}
                    Avoid These Mistakes: {mistake_patterns}
                    """
                except Exception:
                    coaching_context = "BASIC COACHING: Use professional communication and best practices appropriate for the context."
            else:
                coaching_context = "BASIC COACHING: Use professional communication and best practices appropriate for the context."
            
            coaching_prompt = f"""
            Evaluate this learner response in a training context:
            
            LEARNER RESPONSE: {claim}
            
            CONVERSATION CONTEXT:
            {conversation_text}
            
            {coaching_context}
            
            Provide coaching feedback focusing on:
            1. Does the response follow the required approach/methodology?
            2. Is it appropriate for the context and audience?
            3. Does it avoid common mistakes?
            4. Is it professional and effective?
            
            Return as JSON:
            {{
                "result": "CORRECT|NEEDS_IMPROVEMENT",
                "coaching_feedback": "Specific coaching based on the guidelines above",
                "explanation": "Brief explanation of the assessment"
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an adaptive training coach that provides specific feedback based on any domain's training guidelines."},
                    {"role": "user", "content": coaching_prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                if result_text.startswith('```json'):
                    json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                    if json_match:
                        result_json = json.loads(json_match.group(1))
                    else:
                        raise json.JSONDecodeError("Could not extract JSON", result_text, 0)
                else:
                    result_json = json.loads(result_text)
                
                coaching_feedback = result_json.get("coaching_feedback")
                is_correct = result_json.get("result") == "CORRECT"
                
                return FactCheckVerification(
                    claim={"claim_text": claim, "claim_type": "contextual", "confidence": 1.0, "extracted_from": "ai_response"},
                    result=FactCheckResult.CORRECT if is_correct else FactCheckResult.INCORRECT,
                    confidence_score=0.8,
                    explanation=result_json.get("explanation", "Contextual coaching provided"),
                    coaching_feedback=coaching_feedback,
                    supporting_chunks=[],
                    source_documents=[]
                )
                
            except json.JSONDecodeError:
                # Fallback - still provide some coaching
                return FactCheckVerification(
                    claim={"claim_text": claim, "claim_type": "contextual", "confidence": 1.0, "extracted_from": "ai_response"},
                    result=FactCheckResult.CORRECT,
                    confidence_score=0.6,
                    explanation="Response evaluated using training guidelines",
                    coaching_feedback="Continue focusing on professional, helpful communication.",
                    supporting_chunks=[],
                    source_documents=[]
                )
                
        except Exception as e:
            print(f"Error in contextual coaching without docs: {e}")
            return FactCheckVerification(
                claim={"claim_text": claim, "claim_type": "contextual", "confidence": 0.0, "extracted_from": "ai_response"},
                result=FactCheckResult.CORRECT,
                confidence_score=0.5,
                explanation="Unable to provide detailed coaching",
                coaching_feedback="Focus on clear, professional communication appropriate for the context.",
                supporting_chunks=[],
                source_documents=[]
            )  