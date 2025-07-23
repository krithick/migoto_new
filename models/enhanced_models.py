"""
Phase 1: Enhanced Models and Database Schema
New data models for enhanced scenarios with knowledge base support
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
import json

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, Enum):
    PRODUCT_CATALOG = "product_catalog"
    PRICING_GUIDE = "pricing_guide"
    POLICY_DOCUMENT = "policy_document"
    FAQ_DATABASE = "faq_database"
    TRAINING_MANUAL = "training_manual"
    COMPLIANCE_GUIDE = "compliance_guide"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    OTHER = "other"

class JobType(str, Enum):
    TEMPLATE_PROCESSING = "template_processing"
    DOCUMENT_PROCESSING = "document_processing"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    VECTOR_INDEXING = "vector_indexing"

class FactCheckResult(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    UNSUPPORTED = "unsupported"
    UNCLEAR = "unclear"

# Template Form Data Models
class TemplateBasicInfo(BaseModel):
    company_name: str
    primary_contact_name: str
    primary_contact_email: str
    scenario_title: str
    training_domain: str
    number_of_learners: int
    preferred_language: str = "English"

class LearningObjective(BaseModel):
    objective: str
    priority: str = Field(..., pattern="^(High|Medium|Low)$")
    success_criteria: str

class LearnerProfile(BaseModel):
    job_roles: str
    experience_level: str = Field(..., pattern="^(New|Experienced|Expert)$")
    current_challenges: str

class AIPersona(BaseModel):
    role: str
    background: str
    key_skills: List[str]
    behavioral_traits: List[str]
    goal: str

class ScenarioMode(BaseModel):
    ai_persona: AIPersona
    teaching_style: Optional[List[str]] = None
    difficulty_level: str = Field(..., pattern="^(Easy|Moderate|Challenging|Mixed)$")

class ConversationExample(BaseModel):
    customer_says: str
    learner_should_respond: str
    if_wrong_response: str
    correct_response: str

class KnowledgeRequirement(BaseModel):
    information_type: str
    is_required: bool
    details: str

class CommonSituation(BaseModel):
    situation: str
    correct_response: str
    source_document: Optional[str] = None

class AssessmentCriteria(BaseModel):
    correction_tone: str = Field(..., pattern="^(Gentle coaching|Direct correction|Educational explanation)$")
    correction_timing: str = Field(..., pattern="^(Immediately|End of conversation|Summary report)$")
    correction_method: str = Field(..., pattern="^(Explain what's wrong|Show correct answer|Ask them to try again)$")

class SuccessMetric(BaseModel):
    metric_name: str
    target_value: str
    measurement_method: str

class TemplateFormData(BaseModel):
    """Complete template form data structure"""
    basic_info: TemplateBasicInfo
    learning_objectives: List[LearningObjective]
    learner_profile: LearnerProfile
    learn_mode: ScenarioMode
    assess_mode: ScenarioMode
    conversation_examples: List[ConversationExample]
    knowledge_requirements: List[KnowledgeRequirement]
    common_situations: List[CommonSituation]
    assessment_criteria: AssessmentCriteria
    success_metrics: List[SuccessMetric]
    
    # Approval section
    approved_by: Dict[str, str]  # {"project_owner": "name", "sme": "name", etc.}
    submission_date: datetime = Field(default_factory=datetime.now)

# Enhanced Scenario Models
class EnhancedScenario(BaseModel):
    """Enhanced scenario that links to knowledge base"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    base_scenario_id: Optional[str] = None  # Links to existing scenario if upgraded
    template_data: TemplateFormData
    knowledge_base_id: Optional[str] = None
    fact_checking_enabled: bool = True
    enhancement_status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    
    class Config:
        use_enum_values = True

class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    knowledge_base_id: str
    filename: str
    original_filename: str
    document_type: DocumentType
    file_size: int
    content_type: str
    description: Optional[str] = None
    processed_at: Optional[datetime] = None
    chunk_count: int = 0
    chunk_ids: List[str] = []
    extraction_method: str = "auto"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True

class KnowledgeBase(BaseModel):
    """Knowledge base for a scenario"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    enhanced_scenario_id: str
    documents: List[DocumentMetadata] = []
    vector_index_name: str  # Azure Search index name
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    total_chunks: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('vector_index_name', always=True)
    def generate_index_name(cls, v, values):
        if not v and 'scenario_id' in values:
            # Create safe index name for Azure Search
            scenario_id = values['scenario_id'].replace('-', '_').lower()
            return f"kb_{scenario_id}_{str(uuid4())[:8]}"
        return v
    
    class Config:
        use_enum_values = True

class ProcessingJob(BaseModel):
    """Background job tracking"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_type: JobType
    scenario_id: str
    enhanced_scenario_id: Optional[str] = None
    knowledge_base_id: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: int = 0
    progress_message: str = "Queued for processing"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True

# Document Chunk Models (for vector storage)
class DocumentChunk(BaseModel):
    """Individual document chunk for vector search"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    knowledge_base_id: str = ""
    document_id: str
    content: str
    chunk_index: int
    word_count: int
    character_count: int
    section: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)

# Fact-Checking Models
class FactCheckClaim(BaseModel):
    """Individual factual claim extracted from conversation"""
    claim_text: str
    claim_type: str  # "pricing", "feature", "policy", "process", etc.
    confidence: float = 0.0
    extracted_from: str  # "user_response" or "ai_response"

class FactCheckVerification(BaseModel):
    """Result of fact-checking a claim"""
    claim: FactCheckClaim
    result: FactCheckResult
    confidence_score: float
    supporting_chunks: List[str] = []  # Chunk IDs that support/contradict
    explanation: str
    suggested_correction: Optional[str] = None
    source_documents: List[str] = []
    verified_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True

class ConversationFactCheck(BaseModel):
    """Fact-checking results for an entire conversation"""
    session_id: str
    scenario_id: str
    enhanced_scenario_id: str
    fact_checks: List[FactCheckVerification] = []
    total_claims: int = 0
    correct_claims: int = 0
    incorrect_claims: int = 0
    accuracy_percentage: float = 0.0
    generated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('accuracy_percentage', always=True)
    def calculate_accuracy(cls, v, values):
        if values.get('total_claims', 0) > 0:
            correct = values.get('correct_claims', 0)
            total = values['total_claims']
            return round((correct / total) * 100, 2)
        return 0.0

# Analytics Models
class KnowledgeGap(BaseModel):
    """Identified knowledge gap from conversations"""
    topic: str
    frequency: int
    example_questions: List[str]
    severity: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    recommended_action: str

class ConversationAnalytics(BaseModel):
    """Analytics for conversation performance"""
    session_id: str
    scenario_id: str
    enhanced_scenario_id: str
    user_id: str
    
    # Fact-checking metrics
    fact_check_summary: ConversationFactCheck
    
    # Performance metrics
    total_exchanges: int
    avg_response_time: float = 0.0
    conversation_duration: int = 0  # seconds
    
    # Knowledge assessment
    knowledge_gaps: List[KnowledgeGap] = []
    strong_areas: List[str] = []
    improvement_recommendations: List[str] = []
    
    # Learning objectives assessment
    objectives_met: List[str] = []
    objectives_missed: List[str] = []
    learning_score: float = 0.0
    
    generated_at: datetime = Field(default_factory=datetime.now)

# API Request/Response Models
class TemplateUploadRequest(BaseModel):
    """Request for uploading template"""
    template_data: TemplateFormData
    create_base_scenario: bool = True  # Whether to create traditional scenario too

class TemplateUploadResponse(BaseModel):
    """Response after template upload"""
    enhanced_scenario_id: str
    base_scenario_id: Optional[str] = None
    processing_job_id: str
    status: ProcessingStatus
    message: str = "Template processed successfully"

class DocumentUploadRequest(BaseModel):
    """Request for uploading documents"""
    enhanced_scenario_id: str
    document_type: DocumentType
    description: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    processing_job_id: str
    status: ProcessingStatus
    message: str = "Document uploaded and queued for processing"

class ProcessingStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str
    job_type: JobType
    status: ProcessingStatus
    progress: int
    progress_message: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class KnowledgeSearchRequest(BaseModel):
    """Request for searching knowledge base"""
    query: str
    scenario_id: str
    top_k: int = Field(default=5, ge=1, le=20)
    document_types: Optional[List[DocumentType]] = None

class KnowledgeSearchResponse(BaseModel):
    """Response from knowledge base search"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time_ms: float

class FactCheckRequest(BaseModel):
    """Request for fact-checking a statement"""
    statement: str
    scenario_id: str
    context: Optional[str] = None

class FactCheckResponse(BaseModel):
    """Response from fact-checking"""
    statement: str
    verification: FactCheckVerification
    supporting_evidence: List[Dict[str, Any]]

# Database Collection Names
class Collections:
    """MongoDB collection names"""
    ENHANCED_SCENARIOS = "enhanced_scenarios"
    KNOWLEDGE_BASES = "knowledge_bases"
    DOCUMENT_METADATA = "document_metadata"
    PROCESSING_JOBS = "processing_jobs"
    CONVERSATION_ANALYTICS = "conversation_analytics"
    FACT_CHECK_RESULTS = "fact_check_results"

# Utility functions for model conversion
def convert_objectid_to_str(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB ObjectId to string"""
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document

def prepare_for_mongodb(model: BaseModel) -> Dict[str, Any]:
    """Prepare Pydantic model for MongoDB storage"""
    data = model.dict(by_alias=True)
    if "_id" not in data and "id" in data:
        data["_id"] = data.pop("id")
    return data

def load_from_mongodb(data: Dict[str, Any], model_class) -> BaseModel:
    """Load Pydantic model from MongoDB document"""
    if "_id" in data and "id" not in data:
        data["id"] = str(data.pop("_id"))
    return model_class(**data)

# Example usage and validation
if __name__ == "__main__":
    # Example template data
    template_data = TemplateFormData(
        basic_info=TemplateBasicInfo(
            company_name="Cloudnine Hospitals",
            primary_contact_name="Dr. Sarah Mitchell",
            primary_contact_email="sarah.mitchell@cloudnine.com",
            scenario_title="Pitch Perfect - Maternity Sales",
            training_domain="Healthcare",
            number_of_learners=50,
            preferred_language="English"
        ),
        learning_objectives=[
            LearningObjective(
                objective="Master SPIN selling techniques for maternity packages",
                priority="High",
                success_criteria="Use SPIN questioning in 80% of interactions"
            )
        ],
        learner_profile=LearnerProfile(
            job_roles="Customer Care Executive",
            experience_level="Experienced",
            current_challenges="Difficulty handling price objections"
        ),
        learn_mode=ScenarioMode(
            ai_persona=AIPersona(
                role="Senior maternity sales trainer",
                background="15+ years in healthcare sales",
                key_skills=["SPIN selling", "objection handling"],
                behavioral_traits=["supportive", "patient", "knowledgeable"],
                goal="Improve learner confidence in package sales"
            ),
            teaching_style=["Interactive", "Scenario-based"],
            difficulty_level="Moderate"
        ),
        assess_mode=ScenarioMode(
            ai_persona=AIPersona(
                role="Expecting mother",
                background="First-time parent, educated, budget-conscious",
                key_skills=["asking detailed questions", "comparing options"],
                behavioral_traits=["curious", "analytical", "concerned about cost"],
                goal="Find the best maternity package for family needs"
            ),
            difficulty_level="Moderate"
        ),
        conversation_examples=[
            ConversationExample(
                customer_says="What's included in your premium package?",
                learner_should_respond="Let me understand your specific needs first. Are you expecting your first child?",
                if_wrong_response="Premium package costs ₹1,20,000 and includes...",
                correct_response="Use SPIN questioning to understand needs before presenting package"
            )
        ],
        knowledge_requirements=[
            KnowledgeRequirement(
                information_type="Package pricing",
                is_required=True,
                details="Current rates for all maternity packages"
            )
        ],
        common_situations=[
            CommonSituation(
                situation="Customer asks about premium package pricing",
                correct_response="Premium package ranges from ₹85,000 to ₹1,20,000 depending on specific selections",
                source_document="pricing_guide_2024.pdf"
            )
        ],
        assessment_criteria=AssessmentCriteria(
            correction_tone="Gentle coaching",
            correction_timing="Immediately",
            correction_method="Explain what's wrong"
        ),
        success_metrics=[
            SuccessMetric(
                metric_name="Price accuracy",
                target_value=">95%",
                measurement_method="Fact-checking against pricing documents"
            )
        ],
        approved_by={"project_owner": "Dr. Sarah Mitchell", "sme": "Sales Manager"}
    )
    
    print("✅ Template data model validation passed!")
    print(f"Template for: {template_data.basic_info.company_name}")
    print(f"Scenario: {template_data.basic_info.scenario_title}")
    print(f"Learning objectives: {len(template_data.learning_objectives)}")
    print(f"Knowledge requirements: {len(template_data.knowledge_requirements)}")