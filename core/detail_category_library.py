"""
Detail Category Library
Defines all possible persona detail categories.
LLM will choose from these based on scenario.
"""

from typing import Dict, List
from pydantic import BaseModel


class DetailCategory(BaseModel):
    """Definition of a detail category"""
    name: str
    description: str
    example_fields: List[str]
    when_relevant: str


class DetailCategoryLibrary:
    """
    Library of all possible detail categories.
    LLM chooses from these based on scenario analysis.
    """
    
    CATEGORIES = {
        "professional_context": DetailCategory(
            name="professional_context",
            description="Work-related details for professionals",
            example_fields=["practice_type", "years_experience", "client_load", "specialization", "reputation"],
            when_relevant="When persona is a professional and their work context matters"
        ),
        
        "medical_philosophy": DetailCategory(
            name="medical_philosophy",
            description="How medical professionals make treatment decisions",
            example_fields=["treatment_approach", "evidence_requirements", "prescription_philosophy"],
            when_relevant="When persona is a medical professional making clinical decisions"
        ),
        
        "family_context": DetailCategory(
            name="family_context",
            description="Family composition and how family influences decisions",
            example_fields=["marital_status", "children", "family_dynamics", "who_influences_decisions"],
            when_relevant="When family plays a role in decisions"
        ),
        
        "health_context": DetailCategory(
            name="health_context",
            description="Health status, medical history, and health concerns",
            example_fields=["current_health_status", "medical_conditions", "medications", "health_anxieties"],
            when_relevant="When persona is a patient or health is relevant to scenario"
        ),
        
        "financial_context": DetailCategory(
            name="financial_context",
            description="Budget, income, and financial decision-making",
            example_fields=["income_level", "budget_constraints", "financial_priorities", "spending_philosophy"],
            when_relevant="When scenario involves purchasing, budgeting, or financial decisions"
        ),
        
        "time_constraints": DetailCategory(
            name="time_constraints",
            description="Schedule pressures and time availability",
            example_fields=["typical_day_schedule", "current_time_pressure", "competing_priorities"],
            when_relevant="When persona is time-pressured or busy"
        ),
        
        "sales_rep_history": DetailCategory(
            name="sales_rep_history",
            description="Past experiences with sales representatives",
            example_fields=["frequency_of_rep_visits", "past_interactions", "trust_level", "skepticism_level"],
            when_relevant="When scenario involves sales pitch and persona has history with sales reps"
        ),
        
        "past_experiences": DetailCategory(
            name="past_experiences",
            description="Relevant past experiences that shape current behavior",
            example_fields=["similar_situations", "outcomes_from_past", "lessons_learned", "trust_issues_origin"],
            when_relevant="When past experiences significantly influence current behavior"
        ),
        
        "social_context": DetailCategory(
            name="social_context",
            description="Social pressures, peer influence, and status concerns",
            example_fields=["peer_influence", "social_aspirations", "status_concerns", "community_expectations"],
            when_relevant="When social factors or peer opinions influence decisions"
        ),
        
        "lifestyle_context": DetailCategory(
            name="lifestyle_context",
            description="Daily life patterns, habits, and lifestyle needs",
            example_fields=["daily_routine", "hobbies", "lifestyle_priorities", "typical_activities"],
            when_relevant="When lifestyle or daily patterns affect needs"
        ),
        
        "anxiety_factors": DetailCategory(
            name="anxiety_factors",
            description="Worries, fears, and sources of anxiety",
            example_fields=["main_fears", "worst_case_scenarios", "anxiety_level", "coping_mechanisms"],
            when_relevant="When persona has significant worries or fears affecting behavior"
        ),
        
        "work_relationships": DetailCategory(
            name="work_relationships",
            description="Workplace dynamics and relationships",
            example_fields=["team_dynamics", "manager_relationship", "power_dynamics", "collaboration_style"],
            when_relevant="When scenario involves workplace interactions"
        ),
        
        "incident_context": DetailCategory(
            name="incident_context",
            description="Details about a specific incident or event",
            example_fields=["what_happened", "when_it_happened", "who_was_involved", "immediate_impact"],
            when_relevant="When scenario involves a specific incident"
        ),
        
        "emotional_state": DetailCategory(
            name="emotional_state",
            description="Current emotional condition and triggers",
            example_fields=["primary_emotion", "emotional_intensity", "emotional_triggers", "emotional_needs"],
            when_relevant="When emotional state significantly affects interactions"
        ),
        
        "decision_criteria": DetailCategory(
            name="decision_criteria",
            description="Factors that influence their decisions",
            example_fields=["must_haves", "deal_breakers", "evaluation_factors", "trade_offs_willing_to_make"],
            when_relevant="When persona needs to make a decision"
        ),
        
        "research_behavior": DetailCategory(
            name="research_behavior",
            description="How they gather information and make informed decisions",
            example_fields=["information_sources", "research_methods", "who_they_consult", "depth_of_research"],
            when_relevant="When persona is well-researched or actively seeking information"
        )
    }
    
    @classmethod
    def get_category_definition(cls, category_name: str) -> DetailCategory:
        """Get definition for a category"""
        return cls.CATEGORIES.get(category_name)
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, DetailCategory]:
        """Get all available categories"""
        return cls.CATEGORIES
    
    @classmethod
    def get_category_names(cls) -> List[str]:
        """Get list of all category names"""
        return list(cls.CATEGORIES.keys())
