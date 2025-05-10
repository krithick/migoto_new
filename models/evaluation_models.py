# from pydantic import BaseModel, Field
# from typing import List, Optional
# from datetime import datetime
# from uuid import UUID, uuid4

# class EvaluationMeta(BaseModel):
#     scenario_title: str
#     user_objective: str
#     relevant_domain: str
#     interaction_context: str


# class UserDomainKnowledge(BaseModel):
#     concept_understanding_score: float = Field(ge=0, le=20)
#     terminology_accuracy_score: float = Field(ge=0, le=20)
#     principles_awareness_score: float = Field(ge=0, le=20)
#     knowledge_application_score: float = Field(ge=0, le=20)
#     overall_score: float = Field(ge=0, le=20)
#     demonstrated_knowledge_areas: List[str]
#     knowledge_gaps: List[str]


# class UserCommunicationClarity(BaseModel):
#     expression_clarity_score: float = Field(ge=0, le=20)
#     context_provision_score: float = Field(ge=0, le=20)
#     message_structure_score: float = Field(ge=0, le=20)
#     terminology_usage_score: float = Field(ge=0, le=20)
#     overall_score: float = Field(ge=0, le=20)
#     communication_strengths: List[str]
#     communication_challenges: List[str]


# class UserEngagementQuality(BaseModel):
#     participation_score: float = Field(ge=0, le=20)
#     responsiveness_score: float = Field(ge=0, le=20)
#     engagement_consistency_score: float = Field(ge=0, le=20)
#     active_listening_score: float = Field(ge=0, le=20)
#     overall_score: float = Field(ge=0, le=20)
#     engagement_patterns: List[str]


# class UserProblemSolving(BaseModel):
#     problem_definition_score: float = Field(ge=0, le=20)
#     logical_reasoning_score: float = Field(ge=0, le=20)
#     adaptability_score: float = Field(ge=0, le=20)
#     resource_utilization_score: float = Field(ge=0, le=20)
#     overall_score: float = Field(ge=0, le=20)
#     problem_solving_strengths: List[str]
#     problem_solving_weaknesses: List[str]


# class UserLearningAdaptation(BaseModel):
#     information_incorporation_score: float = Field(ge=0, le=20)
#     correction_response_score: float = Field(ge=0, le=20)
#     conversation_progression_score: float = Field(ge=0, le=20)
#     insight_gain_score: float = Field(ge=0, le=20)
#     overall_score: float = Field(ge=0, le=20)
#     learning_indicators: List[str]


# class OverallEvaluation(BaseModel):
#     total_score: float = Field(ge=0, le=100)
#     user_performance_category: str
#     user_strengths: List[str]
#     user_improvement_areas: List[str]
#     critical_development_needs: List[str]


# class Recommendations(BaseModel):
#     knowledge_development_recommendations: List[str]
#     communication_improvement_recommendations: List[str]
#     engagement_enhancement_recommendations: List[str]
#     problem_solving_recommendations: List[str]
#     learning_strategy_recommendations: List[str]


# class Evaluation(BaseModel):
#     """Main model for storing user performance analysis results in the database"""
#     id: UUID = Field(default_factory=uuid4, alias="_id")
#     user_id: str
#     session_id: str
#     conversation_id: str
#     evaluation_meta: EvaluationMeta
#     user_domain_knowledge: UserDomainKnowledge
#     user_communication_clarity: UserCommunicationClarity
#     user_engagement_quality: UserEngagementQuality
#     user_problem_solving: UserProblemSolving
#     user_learning_adaptation: UserLearningAdaptation
#     overall_evaluation: OverallEvaluation
#     recommendations: Recommendations
#     timestamp: datetime = Field(default_factory=datetime.now)

#     class Config:
#         schema_extra = {
#             "example": {
#                 "session_id": "abc123",
#                 "conversation_id": "conv456",
#                 "evaluation_meta": {
#                     "scenario_title": "Technical Troubleshooting Discussion",
#                     "user_objective": "Resolving a software installation issue",
#                     "relevant_domain": "Software Installation and Configuration",
#                     "interaction_context": "Customer support interaction for complex software product"
#                 },
#                 "user_domain_knowledge": {
#                     "concept_understanding_score": 16.0,
#                     "terminology_accuracy_score": 14.5,
#                     "principles_awareness_score": 15.0,
#                     "knowledge_application_score": 14.0,
#                     "overall_score": 15.0,
#                     "demonstrated_knowledge_areas": [
#                         "Software installation processes",
#                         "System requirements understanding"
#                     ],
#                     "knowledge_gaps": [
#                         "Configuration options for advanced scenarios"
#                     ]
#                 },
#                 "user_communication_clarity": {
#                     "expression_clarity_score": 16.0,
#                     "context_provision_score": 14.0,
#                     "message_structure_score": 15.0,
#                     "terminology_usage_score": 16.0,
#                     "overall_score": 15.0,
#                     "communication_strengths": [
#                         "Clear description of error messages",
#                         "Proper use of technical terminology"
#                     ],
#                     "communication_challenges": [
#                         "Sometimes omitted important system details"
#                     ]
#                 },
#                 "user_engagement_quality": {
#                     "participation_score": 17.0,
#                     "responsiveness_score": 16.0,
#                     "engagement_consistency_score": 15.0,
#                     "active_listening_score": 16.0,
#                     "overall_score": 16.0,
#                     "engagement_patterns": [
#                         "Actively followed up on suggested solutions",
#                         "Asked clarifying questions when needed"
#                     ]
#                 },
#                 "user_problem_solving": {
#                     "problem_definition_score": 15.0,
#                     "logical_reasoning_score": 16.0,
#                     "adaptability_score": 14.0,
#                     "resource_utilization_score": 15.0,
#                     "overall_score": 15.0,
#                     "problem_solving_strengths": [
#                         "Methodical approach to troubleshooting",
#                         "Good at implementing suggested solutions"
#                     ],
#                     "problem_solving_weaknesses": [
#                         "Could explore more alternative solutions independently"
#                     ]
#                 },
#                 "user_learning_adaptation": {
#                     "information_incorporation_score": 16.0,
#                     "correction_response_score": 17.0,
#                     "conversation_progression_score": 15.0,
#                     "insight_gain_score": 14.0,
#                     "overall_score": 15.5,
#                     "learning_indicators": [
#                         "Applied new information to solve problem",
#                         "Built on earlier suggestions effectively"
#                     ]
#                 },
#                 "overall_evaluation": {
#                     "total_score": 76.5,
#                     "user_performance_category": "Proficient",
#                     "user_strengths": [
#                         "Strong technical vocabulary",
#                         "Excellent engagement and responsiveness",
#                         "Good at following technical instructions"
#                     ],
#                     "user_improvement_areas": [
#                         "Could provide more comprehensive system context",
#                         "Would benefit from deeper understanding of configuration options"
#                     ],
#                     "critical_development_needs": []
#                 },
#                 "recommendations": {
#                     "knowledge_development_recommendations": [
#                         "Review advanced configuration documentation",
#                         "Learn about system dependencies for this software"
#                     ],
#                     "communication_improvement_recommendations": [
#                         "Include system specifications in initial descriptions",
#                         "Use more structured problem reporting format"
#                     ],
#                     "engagement_enhancement_recommendations": [
#                         "Continue strong active participation approach",
#                         "Consider summarizing understanding after complex explanations"
#                     ],
#                     "problem_solving_recommendations": [
#                         "Try troubleshooting basic issues independently before seeking help",
#                         "Explore diagnostic tools mentioned in documentation"
#                     ],
#                     "learning_strategy_recommendations": [
#                         "Keep notes of recurring issues and their solutions",
#                         "Practice applying solutions in different scenarios"
#                     ]
#                 }
#             }
#         }
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class EvaluationMeta(BaseModel):
    scenario_title: str
    ai_role: Optional[str] = None  # Keep for backward compatibility
    user_objective: Optional[str] = None
    conversation_purpose: Optional[str] = None  # Keep for backward compatibility
    conversation_dynamics: Optional[str] = None  # Keep for backward compatibility
    relevant_domain: Optional[str] = None
    interaction_context: Optional[str] = None


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


# New user-focused models
class UserDomainKnowledge(BaseModel):
    concept_understanding_score: float = Field(ge=0, le=20)
    terminology_accuracy_score: float = Field(ge=0, le=20)
    principles_awareness_score: float = Field(ge=0, le=20)
    knowledge_application_score: float = Field(ge=0, le=20)
    overall_score: float = Field(ge=0, le=20)
    demonstrated_knowledge_areas: List[str]
    knowledge_gaps: List[str]


class UserCommunicationClarity(BaseModel):
    expression_clarity_score: float = Field(ge=0, le=20)
    context_provision_score: float = Field(ge=0, le=20)
    message_structure_score: float = Field(ge=0, le=20)
    terminology_usage_score: float = Field(ge=0, le=20)
    overall_score: float = Field(ge=0, le=20)
    communication_strengths: List[str]
    communication_challenges: List[str]


class UserEngagementQuality(BaseModel):
    participation_score: float = Field(ge=0, le=20)
    responsiveness_score: float = Field(ge=0, le=20)
    engagement_consistency_score: float = Field(ge=0, le=20)
    active_listening_score: float = Field(ge=0, le=20)
    overall_score: float = Field(ge=0, le=20)
    engagement_patterns: List[str]


class UserProblemSolving(BaseModel):
    problem_definition_score: float = Field(ge=0, le=20)
    logical_reasoning_score: float = Field(ge=0, le=20)
    adaptability_score: float = Field(ge=0, le=20)
    resource_utilization_score: float = Field(ge=0, le=20)
    overall_score: float = Field(ge=0, le=20)
    problem_solving_strengths: List[str]
    problem_solving_weaknesses: List[str]


class UserLearningAdaptation(BaseModel):
    information_incorporation_score: float = Field(ge=0, le=20)
    correction_response_score: float = Field(ge=0, le=20)
    conversation_progression_score: float = Field(ge=0, le=20)
    insight_gain_score: float = Field(ge=0, le=20)
    overall_score: float = Field(ge=0, le=20)
    learning_indicators: List[str]


class OverallEvaluation(BaseModel):
    # Keep legacy fields for backward compatibility
    total_raw_score: Optional[float] = Field(None, ge=0, le=40)
    total_percentage_score: Optional[float] = Field(None, ge=0, le=100)
    performance_category: Optional[str] = None
    
    # New fields for user evaluation
    total_score: Optional[float] = Field(None, ge=0, le=100)
    user_performance_category: Optional[str] = None
    
    # Handle both naming conventions
    strengths: Optional[List[str]] = None
    user_strengths: Optional[List[str]] = None
    
    areas_for_improvement: Optional[List[str]] = None
    user_improvement_areas: Optional[List[str]] = None
    
    critical_gaps: Optional[List[str]] = None
    critical_development_needs: Optional[List[str]] = None
    
    @root_validator(pre=True)
    def compatibility_checks(cls, values):
        # Handle total score fields
        if 'total_raw_score' in values and 'total_score' not in values:
            # Convert old scoring to new scoring (scaling up)
            values['total_score'] = values['total_raw_score'] * 2.5
        
        # Handle performance category
        if 'performance_category' in values and 'user_performance_category' not in values:
            # Map old categories to new categories
            category_map = {
                "Exceptional": "Expert",
                "Strong": "Proficient",
                "Adequate": "Adequate",
                "Needs Improvement": "Developing",
                "Poor": "Novice"
            }
            old_category = values['performance_category']
            values['user_performance_category'] = category_map.get(old_category, old_category)
        
        # Handle strengths
        if 'strengths' in values and 'user_strengths' not in values:
            values['user_strengths'] = values['strengths']
        
        # Handle improvement areas
        if 'areas_for_improvement' in values and 'user_improvement_areas' not in values:
            values['user_improvement_areas'] = values['areas_for_improvement']
        
        # Handle critical needs
        if 'critical_gaps' in values and 'critical_development_needs' not in values:
            values['critical_development_needs'] = values['critical_gaps']
        
        return values


class Recommendations(BaseModel):
    knowledge_development_recommendations: List[str] = []
    communication_improvement_recommendations: List[str] = []
    engagement_enhancement_recommendations: List[str] = []
    problem_solving_recommendations: List[str] = []
    learning_strategy_recommendations: List[str] = []
    
    @classmethod
    def from_list(cls, recommendations: List[str]):
        # Distribute recommendations across categories
        num_categories = 5
        rec_per_category = len(recommendations) // num_categories
        remaining = len(recommendations) % num_categories
        
        result = cls()
        
        start = 0
        for i, field in enumerate(cls.__annotations__.keys()):
            # Calculate how many recommendations to assign to this category
            count = rec_per_category + (1 if i < remaining else 0)
            end = start + count
            
            # Assign recommendations to this category
            if end > start:
                setattr(result, field, recommendations[start:end])
            
            start = end
        
        return result


class Evaluation(BaseModel):
    """Main model for storing user performance analysis results in the database"""
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: str
    session_id: str
    conversation_id: str
    evaluation_meta: EvaluationMeta
    
    # Legacy fields - make optional for backward compatibility
    role_fulfillment: Optional[RoleFulfillment] = None
    knowledge_quality: Optional[KnowledgeQuality] = None
    communication_quality: Optional[CommunicationQuality] = None
    conversation_quality: Optional[ConversationQuality] = None
    
    # New user-focused fields - make optional for backward compatibility
    user_domain_knowledge: Optional[UserDomainKnowledge] = None
    user_communication_clarity: Optional[UserCommunicationClarity] = None
    user_engagement_quality: Optional[UserEngagementQuality] = None
    user_problem_solving: Optional[UserProblemSolving] = None
    user_learning_adaptation: Optional[UserLearningAdaptation] = None
    
    overall_evaluation: OverallEvaluation
    
    # Accept both formats of recommendations
    recommendations: Union[List[str], Recommendations]
    
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @root_validator(pre=True)
    def parse_recommendations(cls, values):
        # If recommendations is a list, convert it to Recommendations object
        if 'recommendations' in values and isinstance(values['recommendations'], list):
            values['recommendations'] = Recommendations.from_list(values['recommendations'])
        return values
    
    class Config:
        # Allow extra fields to accommodate changing schemas
        extra = "ignore"