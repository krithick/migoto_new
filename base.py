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

from models_old import BotConfig,BotConfigAnalyser,Message 
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
    def apply_persona_to_system_prompt(system_prompt: str, persona: dict) -> str:
        """
        Apply persona details to the system prompt
    
        :param system_prompt: Original system prompt with [PERSONA_PLACEHOLDER]
        :param persona: Persona document from database
        :return: Enhanced system prompt
        """
        if not persona:
            return system_prompt
    
        # Format persona details as markdown
        persona_markdown = f"""
    - Name: {persona.get('name', '[Your Name]')}
    - Type: {persona.get('persona_type', '')}
    - Gender: {persona.get('gender', '')}
    - Goal: {persona.get('character_goal', '')}
    - Location: {persona.get('location', '')}
    - Description: {persona.get('description', '')}
    - Details: {persona.get('persona_details', '')}
    - Current situation: {persona.get('situation', '')}
    - Context: {persona.get('business_or_personal', '')}
    """
    
        # Add background story if available
        if persona.get('background_story'):
            persona_markdown += f"- Background: {persona.get('background_story')}\n"

    # Replace placeholder with persona details
        enhanced_prompt = system_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)
    
        return enhanced_prompt    
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

    def _create_analysis_prompt(self, conversation: str,scenario_title: str,scenario_description: str,ai_role: str,key_metrics: str,additional_context: str) -> str:
        print(self.bot_name)
        """Create the analysis prompt for Gemini."""
        prompt  = f"""
Conversation Quality Analysis Framework
Purpose
Evaluate the quality and effectiveness of conversations between an AI/bot and users, covering various roles and interaction types - including advisory, informational, transactional, collaborative, or any other conversational scenario across any domain.
Input Requirements

Scenario Title: {scenario_title}
Scenario Description: {scenario_description}
AI/Bot Role: {ai_role}
Key Success Metrics: {key_metrics}
- **Conversation Transcript**: {conversation}

Evaluation Process
Step 1: Conversation Context Identification

Analyze the conversation to identify the purpose and nature of the interaction
Determine the specific context, topics, and dynamics of the conversation
Identify the roles adopted by both the AI/bot and the user during the exchange

Step 2: Interaction Assessment

Evaluate how effectively the AI/bot fulfilled its intended role in the conversation
Assess the appropriateness of responses given the specified scenario and role
Analyze how well the conversation progressed and evolved throughout the exchange

Step 3: Comprehensive Evaluation
Assess the following dimensions:
1. Role Fulfillment (0-10)

Did the AI/bot effectively fulfill its intended role in the conversation? (Yes/No)
How well did the AI/bot accomplish the objectives appropriate to its role?
Did the conversation achieve its intended purpose?
Was the AI/bot appropriately proactive or reactive based on its role?

2. Knowledge & Accuracy (0-10)

Were all key facts and information accurately presented?
Were explanations comprehensive and correct?
Were appropriate resources or references provided when needed?
Were limitations or uncertainties transparently disclosed?

3. Communication Quality (0-10)

How clear and understandable were the responses?
Was an appropriate level of detail provided?
How well-structured and organized was the information?
Were complex concepts explained effectively?

4. Conversation Quality (0-10)

How natural and appropriate was the flow of the conversation?
Did both participants engage effectively in the exchange?
Was an appropriate tone maintained throughout the conversation?
How efficiently and coherently was the conversation conducted?

Step 4: Improvement Analysis

Identify specific moments where alternative responses would have improved the interaction
Analyze missed opportunities for providing additional value
Evaluate the conversation flow for potential optimization

## Output Format
```json
{{
  "session_id": "sessionID",
  "conversation_id": "conversationID",
  "evaluation_meta": {{
    "scenario_title": "Title describing the conversation scenario",
    "ai_role": "Description of the AI/bot's role in this conversation",
    "conversation_purpose": "Identified purpose and context of the conversation",
    "conversation_dynamics": "Analysis of key interaction patterns observed"
  }},
  "role_fulfillment": {{
    "role_effectively_fulfilled": true,
    "score": 0,
    "notes": "Specific observations about role fulfillment"
  }},
  "knowledge_quality": {{
    "accuracy_score": 0,
    "comprehensiveness_score": 0,
    "relevance_score": 0,
    "overall_score": 0,
    "key_information_provided": [
      "Information 1",
      "Information 2"
    ],
    "key_information_missed": [
      "Missing information 1",
      "Missing information 2"
    ]
  }},
  "communication_quality": {{
    "clarity_score": 0, 
    "structure_score": 0,
    "appropriateness_score": 0,
    "overall_score": 0
  }},
  "conversation_quality": {{
    "flow_score": 0,
    "coherence_score": 0,
    "engagement_score": 0,
    "overall_score": 0
  }},
  "overall_evaluation": {{
    "total_raw_score": 0,
    "total_percentage_score": 0,
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
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3"
  ],
  "timestamp": "2025-05-09T12:34:56.789Z"
}}
```

Corporate Assessment Application
This framework is specifically designed to be applicable in corporate settings for:

Customer service quality evaluation
Sales conversation assessments
Internal communication analysis
Training and onboarding conversation review
Compliance verification in regulated communications
Performance reviews of AI/human representatives

When used in corporate environments, evaluators can:

Compare scores against established benchmarks
Track improvement over time using consistent metrics
Identify training opportunities based on specific gaps
Document compliance with communication standards
Generate evidence-based performance reports

Scoring Calculation
The total score out of 100 is calculated as follows:

Each of the four main evaluation dimensions is scored on a scale of 0-10:

Role Fulfillment (0-10)
Knowledge & Accuracy (0-10)
Communication Quality (0-10)
Conversation Quality (0-10)


For each dimension, the sub-scores are averaged to create the dimension score.
The total raw score is the sum of all four dimension scores (maximum of 40 points).
This raw score is then converted to a percentage by multiplying by 2.5:
Total Score (out of 100) = Sum of all dimension scores × 2.5

This percentage score maps to performance categories as follows:

85-100: Exceptional
70-84: Strong
55-69: Adequate
40-54: Needs Improvement
0-39: Poor



Usage Instructions

Provide the scenario title, description, AI/bot role, key metrics, and conversation transcript
The evaluation will first identify the conversation context and dynamics
Then assess how effectively the AI/bot fulfilled its intended role
Evaluate the quality of information, communication, and overall conversation
Generate detailed feedback and scoring
Output results in the specified JSON format

Additional Context (Optional)
{additional_context}
Ensure the evaluation is objective, constructive, and focused on actionable insights that can improve future conversations.
"""
        
        # prompt=f"""{self.system_prompt} """
        # print(prompt)
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
    
    async def analyze_conversation(self, conversation_data: dict,interaction_details: dict,scenario_name:str) :
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
            
            prompt = self._create_analysis_prompt(formatted_conversation,scenario_title=scenario_name,
                                                  scenario_description="",ai_role=interaction_details["bot_role"],key_metrics="",additional_context="")
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
            # print(response.choices[0].message.content)
            # # Clean and parse the response
            cleaned_json_text = self._clean_gemini_response(response.choices[0].message.content)
            # print(cleaned_json_text)
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

    