"""
Archetype System Models
Defines the 5 core training scenario archetypes and their requirements
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4


class ScenarioArchetype(str, Enum):
    """5 core training scenario patterns"""
    HELP_SEEKING = "HELP_SEEKING"
    PERSUASION = "PERSUASION"
    CONFRONTATION = "CONFRONTATION"
    INVESTIGATION = "INVESTIGATION"
    NEGOTIATION = "NEGOTIATION"


class ConversationPattern(str, Enum):
    """Who initiates the conversation"""
    LEARNER_INITIATES = "learner_initiates"  # Learner starts (sales, confrontation)
    CHARACTER_INITIATES = "character_initiates"  # Character starts (help-seeking, victim)
    MUTUAL = "mutual"  # Both can start (negotiation)


class PersonaComplexity(str, Enum):
    """Persona detail level"""
    BASIC = "basic"  # Name, role, basic traits
    STANDARD = "standard"  # + Background, motivations
    DETAILED = "detailed"  # + Psychological profile, decision patterns
    EXPERT = "expert"  # + Hidden agendas, complex behaviors


# ============= PERSONA SCHEMAS BY ARCHETYPE =============

class HelpSeekingPersonaSchema(BaseModel):
    """Schema for help-seeking archetype personas"""
    # Required fields
    problem_description: str
    emotional_state: str  # "Frustrated", "Confused", "Anxious"
    desired_outcome: str
    patience_level: str  # "High", "Medium", "Low"
    
    # Optional detailed fields
    technical_knowledge: Optional[str] = None  # "Novice", "Intermediate", "Expert"
    previous_attempts: Optional[List[str]] = None
    urgency_level: Optional[str] = None
    communication_style: Optional[str] = None


class PersuasionPersonaSchema(BaseModel):
    """Schema for persuasion/sales archetype personas"""
    # Required fields
    current_position: str  # What they currently believe/use
    satisfaction_level: str  # "Very satisfied", "Neutral", "Dissatisfied"
    knowledge_gaps: List[str]  # What they don't know
    
    # Objection library
    objection_library: List[Dict[str, str]] = Field(default_factory=list)
    # Format: [{"objection": "Too expensive", "underlying_concern": "Budget", "counter_strategy": "ROI data"}]
    
    decision_criteria: List[str]  # ["Evidence quality", "Cost-benefit", "Ease of use"]
    personality_type: str  # "Analytical", "Relationship-driven", "Results-focused"
    
    # Optional detailed fields
    time_pressure: Optional[str] = None  # "Urgent", "Moderate", "No rush"
    authority_level: Optional[str] = None  # "Decision maker", "Influencer", "Gatekeeper"
    buying_signals: Optional[List[str]] = None
    competitive_preferences: Optional[str] = None


class ConfrontationPersonaSchema(BaseModel):
    """Schema for confrontation archetype personas"""
    sub_type: str  # "PERPETRATOR", "VICTIM", "BYSTANDER"
    
    # Perpetrator-specific
    awareness_level: Optional[str] = None  # "Unaware", "Minimizing", "Defensive", "Hostile"
    defensive_mechanisms: Optional[List[str]] = None  # ["Denial", "Deflection", "Justification"]
    escalation_triggers: Optional[List[str]] = None
    de_escalation_opportunities: Optional[List[str]] = None
    
    # Victim-specific
    emotional_state: Optional[str] = None  # "Hurt", "Angry", "Fearful", "Numb"
    trust_level: Optional[str] = None  # "Low", "Guarded", "Cautiously open"
    needs: Optional[List[str]] = None  # ["Validation", "Safety", "Action plan"]
    barriers_to_reporting: Optional[List[str]] = None
    
    # Bystander-specific
    internal_conflict: Optional[str] = None
    knowledge_gaps_intervention: Optional[List[str]] = None
    empowerment_needs: Optional[List[str]] = None
    
    # Common fields
    power_dynamics: Optional[str] = None  # "Senior", "Peer", "Junior"
    conversation_arc: Optional[str] = None


class InvestigationPersonaSchema(BaseModel):
    """Schema for investigation/discovery archetype personas"""
    information_completeness: str  # "Full", "Partial", "Fragmented"
    communication_barriers: List[str]  # ["Medical jargon", "Trauma", "Language"]
    reliability_factors: List[str]  # ["Memory gaps", "Emotional state", "Bias"]
    motivation_to_share: str  # "High", "Moderate", "Reluctant"
    
    # Optional detailed fields
    hidden_information: Optional[str] = None  # What they're not saying initially
    revelation_triggers: Optional[List[str]] = None  # What makes them open up
    information_accuracy: Optional[str] = None


class NegotiationPersonaSchema(BaseModel):
    """Schema for negotiation/mediation archetype personas"""
    BATNA: str  # Best Alternative To Negotiated Agreement
    non_negotiables: List[str]  # Must-haves
    flexible_points: List[str]  # Areas open to trade-offs
    hidden_interests: str  # What they really want
    
    # Optional detailed fields
    emotional_triggers: Optional[List[str]] = None  # ["Fairness", "Respect"]
    concession_patterns: Optional[str] = None
    relationship_importance: Optional[str] = None  # "One-time" vs "Long-term"
    power_position: Optional[str] = None


# ============= ARCHETYPE DEFINITION =============

class ArchetypeDefinition(BaseModel):
    """Master definition for each archetype"""
    id: str = Field(alias="_id")  # "HELP_SEEKING", "PERSUASION", etc.
    name: str
    description: str
    conversation_pattern: ConversationPattern
    
    # Persona requirements
    persona_schema_type: str  # Which schema to use
    required_persona_fields: List[str]
    optional_persona_fields: List[str]
    persona_complexity_default: PersonaComplexity
    
    # Sub-archetypes (if any)
    sub_archetypes: Optional[List[str]] = None
    
    # Extraction guidance
    extraction_keywords: List[str]  # Keywords that indicate this archetype
    extraction_patterns: List[str]  # Patterns to look for
    
    # Prompt templates
    system_prompt_template: str  # Base template with placeholders
    coaching_rules_template: Dict[str, Any]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True


# ============= ENHANCED PERSONA MODEL =============

class PersonaArchetypeData(BaseModel):
    """Archetype-specific persona data"""
    archetype: ScenarioArchetype
    sub_archetype: Optional[str] = None
    
    # Store archetype-specific schema data
    help_seeking_data: Optional[HelpSeekingPersonaSchema] = None
    persuasion_data: Optional[PersuasionPersonaSchema] = None
    confrontation_data: Optional[ConfrontationPersonaSchema] = None
    investigation_data: Optional[InvestigationPersonaSchema] = None
    negotiation_data: Optional[NegotiationPersonaSchema] = None


class EnhancedPersonaDB(BaseModel):
    """Enhanced persona with archetype support"""
    id: UUID = Field(default_factory=uuid4, alias="_id")
    
    # Basic persona info (existing fields)
    name: str
    description: str
    persona_type: str
    gender: str
    age: int
    character_goal: str
    location: str
    persona_details: str
    situation: str
    business_or_personal: str
    background_story: Optional[str] = None
    
    # Archetype-specific data
    archetype_data: PersonaArchetypeData
    
    # Complexity level
    complexity_level: PersonaComplexity = PersonaComplexity.STANDARD
    
    # Metadata
    template_id: Optional[str] = None  # Which template this persona was generated from
    avatar_interaction_id: Optional[UUID] = None  # Which avatar_interaction this is for
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Full persona JSON (for backward compatibility)
    full_persona: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: str}


# ============= ARCHETYPE CLASSIFICATION =============

class ArchetypeClassificationResult(BaseModel):
    """Result of archetype classification"""
    primary_archetype: ScenarioArchetype
    sub_archetype: Optional[str] = None
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    conversation_pattern: ConversationPattern
    persona_schema_needed: str
    
    # Alternative archetypes with confidence scores
    alternative_archetypes: Dict[str, float] = Field(default_factory=dict)
    
    # Extraction guidance
    detected_keywords: List[str] = Field(default_factory=list)
    detected_patterns: List[str] = Field(default_factory=list)
    
    # Alias for backward compatibility
    @property
    def confidence(self) -> float:
        return self.confidence_score
    
    @property
    def sub_type(self) -> Optional[str]:
        return self.sub_archetype


# ============= TEMPLATE ARCHETYPE METADATA =============

class TemplateArchetypeMetadata(BaseModel):
    """Archetype metadata stored in template"""
    archetype: ScenarioArchetype
    sub_archetypes: Optional[List[str]] = None  # For multi-variant scenarios
    conversation_pattern: ConversationPattern
    persona_schema_type: str
    
    # Variant configuration (for scenarios with multiple sub-types)
    requires_multiple_avatar_interactions: bool = False
    avatar_interaction_variants: Optional[List[Dict[str, str]]] = None
    # Format: [{"sub_type": "PERPETRATOR", "conversation_pattern": "learner_initiates"}]
    
    # Classification metadata
    classification_confidence: float
    classification_reasoning: str


# ============= SCENARIO VARIANT CONFIGURATION =============

class ScenarioVariantConfig(BaseModel):
    """Configuration for scenario variants (e.g., PERPETRATOR, VICTIM, BYSTANDER)"""
    variant_type: str  # "PERPETRATOR", "VICTIM", "BYSTANDER"
    avatar_interaction_id: UUID
    conversation_pattern: ConversationPattern
    persona_count: int = 5  # How many personas to generate for this variant
    
    # Variant-specific prompt adjustments
    system_prompt_additions: Optional[str] = None
    coaching_rules_additions: Optional[Dict[str, Any]] = None


class ScenarioArchetypeConfig(BaseModel):
    """Complete archetype configuration for a scenario"""
    archetype: ScenarioArchetype
    template_id: str
    
    # Single variant or multiple variants
    is_multi_variant: bool = False
    variants: Optional[List[ScenarioVariantConfig]] = None
    
    # Default avatar_interaction (for single-variant scenarios)
    default_avatar_interaction_id: Optional[UUID] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
