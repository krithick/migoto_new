from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException, Depends

from fastapi import FastAPI, HTTPException, Depends, Form
from pydantic import BaseModel,Field
from typing import Dict, List, Optional
from datetime import datetime

from uuid import UUID , uuid4

# FastAPI Models
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()
    usage: Optional[dict] = None

class ChatSession(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    extra: str
    session_id: str
    scenario_name: str
    avatar_interaction: str
    avatar_id :str
    language_id : str
    conversation_history: List[Message]
    usage: Optional[dict] = None
    created_at: datetime = datetime.now()
    last_updated: datetime = datetime.now()

class ChatRequest(BaseModel):
    message: str = Form(...)
    session_id: Optional[str] = Form(default=None)
    scenario_name: Optional[str] = Form(default=None)

class ChatResponse(BaseModel):
    session_id: str
    response: str
    emotion:Optional[str]
    complete:bool
    # audio_chunk: Optional[str]
    conversation_history: List[Message]
    correct:Optional[bool]
    correct_answer:Optional[str]
    

class ChatReport(BaseModel):
    session_id: str
    conversation_id: str
    timestamp: datetime = datetime.now()
    overall_score: float
    category_scores: Dict[str, float]
    detailed_feedback: Dict[str, List[str]]
    recommendations: List[str]

class ChatReport(BaseModel):
    session_id: str
    conversation_id: str
    timestamp: datetime = datetime.now()
    overall_score: float
    category_scores: Dict[str, float]
    detailed_feedback: Dict[str, List[str]]
    recommendations: List[str]
    
class BotConfig(BaseModel):
    """
    Represents the configuration for a bot stored in MongoDB
    """
    bot_id: str
    bot_name: str
    bot_description: str
    bot_role:str
    bot_role_alt:str
    system_prompt: str
    # roleplay_summary: str
    # character_core_rules: str
    # character_background: str
    # conversation_flow: str
    # scenario_content: str
    # extra_instructions: Optional[str] = None
    is_active: bool = True
    bot_class: Optional[str] = None
    llm_model: str

class BotConfigAnalyser(BaseModel):
    """
    Represents the configuration for a analyser bot stored in MongoDB
    """
    bot_id: str
    bot_name: str
    bot_description: str
    bot_schema:str
    system_prompt:str
    is_active: bool = True
    llm_model:str
    instructions:str
    responseFormat:str
    guidelines:str

class Children(BaseModel):
    hasChildren: bool = False
    numberOfChildren: Optional[int] = None

class Income(BaseModel):
    amount: Optional[float] = None
    frequency: Optional[str] = None

class ClientProfile(BaseModel):
    name: str = ""
    age: Optional[int] = None
    maritalStatus: str = ""
    children: Children
    occupation: str = ""
    income: Income
    location: str = ""

class FinancialStatus(BaseModel):
    existingPolicies: List[str] = Field(default_factory=list)
    otherInvestments: List[str] = Field(default_factory=list)
    loans: List[str] = Field(default_factory=list)
    monthlySavingCapacity: Optional[float] = None
    riskAppetite: str = ""

class ClientNeeds(BaseModel):
    primaryConcerns: List[str] = Field(default_factory=list)
    shortTermGoals: List[str] = Field(default_factory=list)
    longTermGoals: List[str] = Field(default_factory=list)
    lifeEvents: List[str] = Field(default_factory=list)
    retirementPlans: List[str] = Field(default_factory=list)
    educationPlans: List[str] = Field(default_factory=list)

class RecommendedPlan(BaseModel):
    planName: str = ""
    planType: str = ""
    reasonForRecommendation: str = ""

class InsuranceDiscussion(BaseModel):
    recommendedPlans: List[RecommendedPlan] = Field(default_factory=list)
    clientReactions: List[str] = Field(default_factory=list)
    concernsRaised: List[str] = Field(default_factory=list)
    questionsAsked: List[str] = Field(default_factory=list)

class FollowUp(BaseModel):
    pendingInformation: List[str] = Field(default_factory=list)
    clarificationNeeded: List[str] = Field(default_factory=list)
    nextSteps: List[str] = Field(default_factory=list)
    preferredContactMethod: str = ""

class ConversationMetrics(BaseModel):
    informationGatheringScore: Optional[float] = None
    criticalMissingInformation: List[str] = Field(default_factory=list)
    conversationQuality: str = ""

class ChatReport_(BaseModel):
    session_id: str
    conversation_id: str
    timestamp: datetime
    clientProfile: ClientProfile
    financialStatus: FinancialStatus
    clientNeeds: ClientNeeds
    insuranceDiscussion: InsuranceDiscussion
    followUp: FollowUp
    conversationMetrics: ConversationMetrics



class EvaluationMeta(BaseModel):
    derived_customer_persona: str
    correct_scheme: str
    recommended_scheme: str


class RecommendationAccuracy(BaseModel):
    correct_scheme_recommended: str
    score: float
    notes: str


class SchemePresentation(BaseModel):
    feature_accuracy_score: float
    benefit_alignment_score: float
    transparency_score: float
    overall_score: float
    key_features_covered: List[str]
    key_features_missed: List[str]


class CommunicationQuality(BaseModel):
    clarity_score: float
    completeness_score: float
    responsiveness_score: float
    overall_score: float


class OverallEvaluation(BaseModel):
    total_score: float
    performance_category: str
    strengths: List[str]
    areas_for_improvement: List[str]
    critical_gaps: List[str]


class Recommendations(BaseModel):
    recommendations: list[str]


class Evaluation(BaseModel):
    session_id: str
    conversation_id: str
    evaluation_meta: EvaluationMeta
    recommendation_accuracy: RecommendationAccuracy
    scheme_presentation: SchemePresentation
    communication_quality: CommunicationQuality
    overall_evaluation: OverallEvaluation
    recommendations: list[str]
    timestamp:datetime = datetime.now()

class PersonaConfig(BaseModel):
    """
    Represents a persona configuration stored in MongoDB
    """
    persona_id: str
    persona_name: str
    persona_description: str
    background_info: str
    response_style: str
    is_active: bool = True
