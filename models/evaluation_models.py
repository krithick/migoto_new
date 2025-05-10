from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class EvaluationMeta(BaseModel):
    scenario_title: str
    ai_role: str
    conversation_purpose: str
    conversation_dynamics: str


class RoleFulfillment(BaseModel):
    role_effectively_fulfilled: bool
    score: float = Field(ge=0, le=10)
    notes: str


class KnowledgeQuality(BaseModel):
    accuracy_score: float = Field(ge=0, le=10)
    comprehensiveness_score: float = Field(ge=0, le=10)
    relevance_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)
    key_information_provided: List[str]
    key_information_missed: List[str]


class CommunicationQuality(BaseModel):
    clarity_score: float = Field(ge=0, le=10)
    structure_score: float = Field(ge=0, le=10)
    appropriateness_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)


class ConversationQuality(BaseModel):
    flow_score: float = Field(ge=0, le=10)
    coherence_score: float = Field(ge=0, le=10)
    engagement_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)


class OverallEvaluation(BaseModel):
    total_raw_score: float = Field(ge=0, le=40)
    total_percentage_score: float = Field(ge=0, le=100)
    performance_category: str
    strengths: List[str]
    areas_for_improvement: List[str]
    critical_gaps: List[str]


class Evaluation(BaseModel):
    """Main model for storing conversation analysis results in the database"""
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id:str
    session_id: str
    conversation_id: str
    evaluation_meta: EvaluationMeta
    role_fulfillment: RoleFulfillment  # Changed from recommendation_accuracy
    knowledge_quality: KnowledgeQuality  # Changed from scheme_presentation
    communication_quality: CommunicationQuality
    conversation_quality: ConversationQuality  # New field added
    overall_evaluation: OverallEvaluation
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123",
                "conversation_id": "conv456",
                "evaluation_meta": {
                    "scenario_title": "Customer Support Inquiry",
                    "ai_role": "Technical Support Representative",
                    "conversation_purpose": "Resolving a software installation issue",
                    "conversation_dynamics": "Troubleshooting with guided user actions"
                },
                "role_fulfillment": {
                    "role_effectively_fulfilled": True,
                    "score": 8.5,
                    "notes": "Bot successfully identified the issue and provided a solution"
                },
                "knowledge_quality": {
                    "accuracy_score": 9.0,
                    "comprehensiveness_score": 8.5,
                    "relevance_score": 9.0,
                    "overall_score": 8.8,
                    "key_information_provided": [
                        "Installation requirements",
                        "Troubleshooting steps"
                    ],
                    "key_information_missed": [
                        "Alternative installation method"
                    ]
                },
                "communication_quality": {
                    "clarity_score": 9.0,
                    "structure_score": 8.0,
                    "appropriateness_score": 9.0,
                    "overall_score": 8.7
                },
                "conversation_quality": {
                    "flow_score": 8.5,
                    "coherence_score": 9.0,
                    "engagement_score": 8.0,
                    "overall_score": 8.5
                },
                "overall_evaluation": {
                    "total_raw_score": 34.5,
                    "total_percentage_score": 86.25,
                    "performance_category": "Exceptional",
                    "strengths": [
                        "Clear technical explanations",
                        "Effective troubleshooting process"
                    ],
                    "areas_for_improvement": [
                        "Could provide more comprehensive solutions"
                    ],
                    "critical_gaps": []
                },
                "recommendations": [
                    "Include alternative installation methods",
                    "Add follow-up check to ensure issue resolution"
                ]
            }
        }
