from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient


from fastapi import FastAPI, HTTPException, Depends

from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware
import json

from dotenv import load_dotenv

from models import BotConfig,BotConfigAnalyser,ChatReport,ChatRequest,ChatResponse,ChatSession,Message 
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, Field
import logging
# 
from openai import AzureOpenAI,AsyncAzureOpenAI
from dataclasses import dataclass

from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    List,
    Optional,
    TypedDict,
    cast,
)
import os
load_dotenv(".env")

# search imports
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorQuery
from azure.search.documents.models import (
    QueryCaptionResult,
    QueryType,
    VectorizedQuery,
    VectorQuery,
)
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk
api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
subscription =  os.getenv("subscription")
AzureSearch =  os.getenv("AzureSearch")
@dataclass
class Document:
    id: Optional[str]
    content: Optional[str]
    embedding: Optional[List[float]]
    image_embedding: Optional[List[float]]
    category: Optional[str]
    sourcepage: Optional[str]
    sourcefile: Optional[str]
    oids: Optional[List[str]]
    groups: Optional[List[str]]
    captions: List[QueryCaptionResult]
    score: Optional[float] = None
    reranker_score: Optional[float] = None
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class BaseLLMBot(ABC):
    """
    Abstract base class for LLM bots
    """
    def __init__(self, config: BotConfig,llm_client):
        """
        Initialize bot with configuration and LLM client
        
        :param config: Bot configuration from database
        :param llm_client: Initialized LLM client
        """
        self.bot_id = config.bot_id
        self.bot_name = config.bot_name
        self.bot_description = config.bot_description
        self.bot_role=config.bot_role
        self.bot_role_alt=config.bot_role_alt
        self.system_prompt = config.system_prompt
        self.is_active = config.is_active
        self.llm_model = config.llm_model
        self.model=self._initialize_llm_model(config)
        self.search_client=SearchClient(endpoint="https://novacimmerz-search-aivr-dev.search.windows.net",index_name="vector-1739857098131",
                                        credential=AzureKeyCredential(AzureSearch))

        self.speech_config=speechsdk.SpeechConfig(endpoint=f"wss://centralindia.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                       subscription=subscription)
        self.speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        properties = dict()
        properties["SpeechSynthesis_FrameTimeoutInterval"]="100000000"
        properties["SpeechSynthesis_RtfTimeoutThreshold"]="10"
        self.speech_config.set_properties_by_name(properties)
    def _initialize_llm_model(self, config: BotConfig):
        """
        Initialize the LLM model for the bot
        
        :param config: Bot configuration
        :return: Initialized generative model
        """
        try:
            # Configure the generative model with system instruction
            return AsyncAzureOpenAI(api_key = api_key,azure_endpoint = endpoint,api_version =  api_version
# Your Azure OpenAI resource's endpoint value.
)
        except Exception as e:
            print(f"Error initializing LLM for {config.bot_name}: {e}")
            raise
        
    @abstractmethod
    async def load_scenarios(self):
        """
        Load and preprocess scenarios specific to the bot type
        """
        pass
    async def retrieve_relevant_docs(self, query, top=3):
        """
        Retrieve relevant documents from Azure AI Search
        """
        results = await self.search_client.search(
            search_text=query,
            # select=[ "content", "title"],
            top=top
        )
        print(results)
        documents = []
        async for document in results:
            documents.append(document)
        
        return documents
    
    def format_retrieved_context(self, documents):
        """
        Format retrieved documents into context for the LLM
        """
        if not documents:
            return ""
        
        context = "Here is some relevant information:\n\n"
        for doc in documents:
            context += f"Title: {doc.get('title', 'No title')}\n"
            context += f"Content: {doc.get('content', 'No content')}\n\n"
        
        return context
    
    def format_conversation(self, conversation_history, context=""):
        """
        Format the conversation history into a list of `Content` objects.
        Now includes retrieved context.
        """
        contents = []
        
        # Add system prompt with context
        system_content = self.system_prompt
        if context:
            system_content += f"\n\n{context}\n\nPlease use the above information to inform your responses."
        
        contents.append({"role": "system", "content": system_content})
        
        for message in conversation_history:
            role = "user" if message.role == self.bot_role_alt else "system"
            content = {
                "role": role,
                "content": message.content
            }
            contents.append(content)
        print(contents)
        return contents
    
    async def get_llm_response(self,
                            officer_question: str,
                            conversation_history: List[Message]) -> str:
        
        # First, retrieve relevant documents from Azure AI Search
        # documents = await self.retrieve_relevant_docs(officer_question)
        # print("%c Line:181 🍻 documents", "color:#ed9ec7", documents)
        
        # # Format the retrieved documents into context
        # context = self.format_retrieved_context(documents)
        # print(context)
        tts_request = speechsdk.SpeechSynthesisRequest(input_type = speechsdk.SpeechSynthesisRequestInputType.TextStream)
        tts_task = self.speech_synthesizer.speak_async(tts_request)
        # Format conversation with the retrieved context
        contents = self.format_conversation(conversation_history, "context")
        # contents = self.format_conversation(conversation_history, context)
        contents.append({
            "role": "user",
            "content": officer_question
        })
        
        try:
            response = await self.model.chat.completions.create(
                model="gpt-4o-mini",
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
                            # tts_request.input_stream.write(chunk_text)
                            yield {"chunk": res, "finish": None, "usage": None}
                        if finish_reason == "stop":
                            if res.strip():
                                # tts_request.input_stream.close()
                                yield {"chunk": res, "finish": "stop", "usage": None}
            
                    # Handle usage statistics after content is complete
                    if hasattr(i, 'usage') and i.usage is not None:
                        # print(i.usage, 'yeahhhh')
                        yield {
                            "chunk": res,
                            "finish": "stop",
                            "usage": {
                                "completion_tokens": i.usage.completion_tokens,
                                "prompt_tokens": i.usage.prompt_tokens,
                                "total_tokens": i.usage.total_tokens
                            }
                        }
            # result = tts_task.get()
            # print("[TTS END]", result)
            return generate()
        
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            raise

    # def format_conversation(self, conversation_history: List[Message]) :
    #     """
    #     Format the conversation history into a list of `Content` objects.

    #     :param conversation_history: List of Message objects
    #     :return: List of `Content` objects
    #     """
    #     contents = []
    #     contents.append({"role":"system","content":self.system_prompt})
    #     for message in conversation_history:
    #         role = "user" if message.role == self.bot_role_alt else "system"
    #         content = {
    #             "role":role,
    #             "content":message.content
    #         }
    #         contents.append(content)
    #     return contents
   
    # async def get_llm_response(self,
    #                               officer_question: str,
                            
    #                               conversation_history: List[Message]) -> str:

        
    #     contents = self.format_conversation(conversation_history)
    #     contents.append({
    #             "role":"user",
    #             "content":officer_question
    #         })
    #     try:
    #         response = await self.model.chat.completions.create(model="gpt-4o-mini", # model = "deployment_name".
    #     messages=contents,
    #     temperature=0.7,
    #     max_tokens=1000,stream=True,stream_options={"include_usage": True})
            
    #         async def generate():
    #             res = ""
    #             async for i in response:
    #                 if len(i.choices) > 0:
    #                     chunk_text = i.choices[0].delta.content
    #                     finish_reason = i.choices[0].finish_reason
            
    #                     if chunk_text:
    #                         res += chunk_text
    #                         yield {"chunk": res, "finish": None,"usage":None}
    #                     if finish_reason == "stop":
    #                         if res.strip():
    #                             yield {"chunk": res, "finish": "stop","usage":None}
        
    #                 # Handle usage statistics after content is complete
    #                 if hasattr(i, 'usage') and i.usage is not None:
    #                     print(i.usage,'yeahhhh')
    #                     yield {
    #                         "chunk": res,
    #                         "finish": "stop",
    #                         "usage": {
    #                             "completion_tokens": i.usage.completion_tokens,
    #                             "prompt_tokens": i.usage.prompt_tokens,
    #                             "total_tokens": i.usage.total_tokens
    #                         }
    #         }            

    #         return generate()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

    async def get_rag_answer(self, query, conversation_history: List[Message], use_grounding=True):
        """
        Retrieves a RAG answer for the given query.

        Args:
            query (str): The user's query.
            use_grounding (bool, optional): Whether to use grounding. Defaults to True.

        Returns:
            str: The RAG answer.
        """
        print(query)
        return query
    async def search(
        self,
        top: int,
        query_text: Optional[str],
        filter: Optional[str],
        vectors: List[VectorQuery],
        use_text_search: bool,
        use_vector_search: bool,
        use_semantic_ranker: bool,
        use_semantic_captions: bool,
        minimum_search_score: Optional[float],
        minimum_reranker_score: Optional[float],
    ) -> List[Document]:
        search_text = query_text if use_text_search else ""
        search_vectors = vectors if use_vector_search else []

        results = await self.search_client.search(
                search_text=search_text,
                filter=filter,
                top=top,
                vector_queries=search_vectors,
            )

        documents = []
        async for page in results.by_page():
            async for document in page:
                documents.append(
                    Document(
                        id=document.get("id"),
                        content=document.get("content"),
                        embedding=document.get("embedding"),
                        image_embedding=document.get("imageEmbedding"),
                        category=document.get("category"),
                        sourcepage=document.get("sourcepage"),
                        sourcefile=document.get("sourcefile"),
                        oids=document.get("oids"),
                        groups=document.get("groups"),
                        captions=cast(List[QueryCaptionResult], document.get("@search.captions")),
                        score=document.get("@search.score"),
                        reranker_score=document.get("@search.reranker_score"),
                    )
                )

            qualified_documents = [
                doc
                for doc in documents
                if (
                    (doc.score or 0) >= (minimum_search_score or 0)
                    and (doc.reranker_score or 0) >= (minimum_reranker_score or 0)
                )
            ]

        return qualified_documents
       
class BaseAnalyserBot(ABC):
    def __init__(self,config:BotConfigAnalyser,llm_client):
        self.bot_id = config.bot_id
        self.bot_name = config.bot_name
        self.bot_description = config.bot_description    
        self.bot_schema = config.bot_schema    
        self.system_prompt = config.system_prompt
        self.is_active = config.is_active
        self.llm_model = config.llm_model
        self.model=self._initialize_llm_model(config)
        self.instructions=config.instructions   
        self.responseFormat=config.responseFormat
        self.guidelines=config.guidelines    
    def _initialize_llm_model(self, config: BotConfig):
        """
        Initialize the LLM model for the bot
        
        :param config: Bot configuration
        :return: Initialized generative model
        """
        try:
            # Configure the generative model with system instruction
            return AsyncAzureOpenAI(api_key = api_key,azure_endpoint = endpoint,api_version =  api_version
# Your Azure OpenAI resource's endpoint value.
)
        except Exception as e:
            print(f"Error initializing LLM for {config.bot_name}: {e}")
            raise

    def _create_analysis_prompt(self, conversation: str) -> str:
        print(self.bot_name)
        """Create the analysis prompt for Gemini."""
        prompt = fprompt = f"""
 # Bank Scheme Recommendation Evaluation Framework

## Purpose
Evaluate bank representatives' performance when discussing current account options with customers, with specific focus on whether they correctly recommend the designated optimal scheme and how effectively they communicate its benefits.

## Input Requirements
- **Correct Scheme**: {self.bot_name}
- **Conversation Transcript**: {conversation}

## Evaluation Process

### Step 1: Persona Identification
- Analyze the conversation to identify the customer's profile and needs
- Determine the customer persona based on details shared about:
  - Business type and size
  - Banking needs and priorities
  - Financial situation
  - Growth stage and aspirations
  - Transaction patterns

### Step 2: Scheme Recommendation Assessment
- Identify which scheme(s) the bank representative recommended
- Compare against the provided "correct scheme" that should have been recommended
- Evaluate the alignment between the customer's derived persona and the recommended scheme

### Step 3: Comprehensive Evaluation
Assess the following dimensions:

#### 1. Scheme Recommendation Accuracy (0-10)
- Was the correct scheme recommended? (Yes/No)
- How well did the representative explain why this scheme fits the customer's needs?
- If multiple schemes were discussed, was appropriate reasoning provided?
- Was the recommendation proactive or only after specific questioning?

#### 2. Scheme Knowledge Accuracy (0-10)
- Were all key features of the scheme accurately described?
- Were the scheme benefits connected to the specific customer's needs?
- Were limitations or conditions transparently disclosed?
- Were all stated facts correct when compared to reference materials?

#### 3. Response Quality (0-10)
- How effectively were specific questions about the scheme answered?
- Was the appropriate level of detail provided?
- Was information presented in clear, easy-to-understand language?
- Were all aspects of customer inquiries addressed fully?

#### 4. Customer Experience (0-10)
- How well was the scheme presentation tailored to the customer's specific situation?
- Did the representative ask questions to understand needs before recommending?
- Did the representative demonstrate patience in explaining scheme details?
- Was empathy shown regarding the customer's business context?

## Output Format
```json
{{
  "session_id:"sessionID",
  "conversation_id":"conversation_id",
  "evaluation_meta": {{
    "derived_customer_persona": "Detailed description of customer persona identified from conversation",
    "correct_scheme": "Scheme name that should have been recommended (from input)",
    "recommended_scheme": "Scheme(s) actually recommended by representative"
  }},
  "recommendation_accuracy": {{
    "correct_scheme_recommended": "true/false",
    "score": 0,
    "notes": "Specific observations about recommendation accuracy"
  }},
  "scheme_presentation": {{
    "feature_accuracy_score": 0,
    "benefit_alignment_score": 0,
    "transparency_score": 0,
    "overall_score": 0,
    "key_features_covered": [
      "Feature 1",
      "Feature 2"
    ],
    "key_features_missed": [
      "Missing feature 1",
      "Missing feature 2"
    ]
  }},
  "communication_quality": {{
    "clarity_score": 0, 
    "completeness_score": 0,
    "responsiveness_score": 0,
    "overall_score": 0
  }},
  "overall_evaluation": {{
    "total_score": 0,
    "performance_category": "Exceptional/Strong/Adequate/Needs Improvement/Poor",
    "strengths": [
      "Specific strength 1",
      "Specific strength 2"
    ],
    "areas_for_improvement": [
      "Specific area 1",
      "Specific area 2"
    ],
    "critical_gaps": [
      "Critical gap 1",
      "Critical gap 2"
    ]
  }},
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ]
}}
```

## Scoring Guidelines
- **Exceptional (85-100%)**: Perfect or near-perfect recommendation with comprehensive, accurate explanations aligned to customer needs
- **Strong (70-84%)**: Correct recommendation with good explanations and minor omissions
- **Adequate (55-69%)**: Correct recommendation but with notable gaps in explanation or alignment
- **Needs Improvement (40-54%)**: Incorrect recommendation but with some redeeming qualities in communication
- **Poor (0-39%)**: Incorrect recommendation with significant gaps in knowledge and communication

## Usage Instructions
1. Provide the conversation transcript and the name of the correct scheme
2. The evaluation will first identify the customer persona from the conversation
3. Then assess whether the correct scheme was recommended
4. Evaluate how well the scheme was presented and explained
5. Generate detailed feedback and scoring
6. Output results in the specified JSON format

here is some context about the {self.bot_name} scheme to check verify the conversation with 
{self.system_prompt}

Make sure the answers given by the bank employee is correct and assess the marks accordingly 
 """
        
        # prompt=f"""{self.system_prompt} """
        print(prompt)
        return prompt

    def _format_conversation_for_analysis(self, conversation_data: dict) -> str:
        """
        Convert the JSON conversation format into a readable string format for analysis.
        
        Args:
            conversation_data (dict): Conversation in JSON format
            
        Returns:
            str: Formatted conversation text
        """
        formatted_conversation = []
        
        for message in conversation_data["conversation_history"]:
            role = message["role"].replace("_", " ").title()
            content = message["content"]
            formatted_conversation.append(f"{role}: {content}")
            
        return "\n".join(formatted_conversation)
    
    async def analyze_conversation(self, conversation_data: dict) :
        """
        Analyze a conversation using Gemini and return structured feedback.
        
        Args:
            conversation_data (dict): Conversation in JSON format
            
        Returns:
            Dict[str, Any]: Analysis results in JSON format
        """
        try:
            # Validate input
            if not isinstance(conversation_data, dict) or "conversation_history" not in conversation_data:
                raise ValueError("Invalid conversation format. Expected dict with 'conversation_history' key")
            
            # Format conversation for analysis
            formatted_conversation = self._format_conversation_for_analysis(conversation_data)
            contents = []
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(formatted_conversation)
            content = {
                "role": "system",
                "content": prompt
            }
            
            contents.append(content)
            # Get response from Gemini
            # response = self.model.generate_content(prompt)
            response = await self.model.chat.completions.create(
                model="gpt-4o-mini",
                messages=contents,
                temperature=0.7,
                max_tokens=1000,
                # stream=True,
                # stream_options={"include_usage": True}
            )
            print(response.choices[0].message.content)
            # # Clean and parse the response
            cleaned_json_text = self._clean_gemini_response(response.choices[0].message.content)
            print(cleaned_json_text)
            try:
                analysis_result = json.loads(cleaned_json_text)
            except json.JSONDecodeError:
                print("Failed to parse JSON. Raw response:", response.text)
                raise Exception("Invalid JSON response from Gemini")
            
            # Add timestamp if not present
            if 'timestamp' not in analysis_result:
                analysis_result['timestamp'] = datetime.utcnow().isoformat()
                
            return analysis_result
            # return response
            
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            print("Raw response:", response.text if 'response' in locals() else "No response generated")
            raise
   
   

    def _clean_gemini_response(self, response_text: str) -> str:
        """
    Clean the Gemini response text to extract pure JSON.
    
    Args:
        response_text (str): Raw response text from Gemini
        
    Returns:
        str: Cleaned JSON text
    """
    # Remove code block markers if present
        cleaned_text = response_text.replace('```json', '').replace('```', '')
    
    # Remove leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
    
        return cleaned_text

    