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

from models.enhanced_models import DocumentChunk, FactCheckVerification, FactCheckResult

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
    
    def __init__(self, vector_search: AzureVectorSearchManager, openai_client: AsyncAzureOpenAI):
        self.vector_search = vector_search
        self.openai_client = openai_client
    
    async def verify_response_claims(self, response_text: str, scenario_id: str) -> List[FactCheckVerification]:
        """Verify all claims in an AI response"""
        
        # Extract factual claims
        claims = await self._extract_factual_claims(response_text)
        
        # Verify each claim
        verifications = []
        for claim in claims:
            verification = await self._verify_single_claim(claim, scenario_id)
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
                return FactCheckVerification(
                    claim={"claim_text": claim, "claim_type": "unknown", "confidence": 0.0, "extracted_from": "ai_response"},
                    result=FactCheckResult.UNSUPPORTED,
                    confidence_score=0.0,
                    explanation="No relevant information found in knowledge base",
                    supporting_chunks=[],
                    source_documents=[]
                )
            
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