"""
Archetype Definitions - Master configurations for each archetype
These are seeded into the database on startup
"""

from models.archetype_models import (
    ArchetypeDefinition, 
    ConversationPattern, 
    PersonaComplexity
)


ARCHETYPE_DEFINITIONS = {
    "HELP_SEEKING": ArchetypeDefinition(
        id="HELP_SEEKING",
        name="Help-Seeking",
        description="Character has a problem, learner provides solution",
        conversation_pattern=ConversationPattern.CHARACTER_INITIATES,
        persona_schema_type="help_seeking",
        required_persona_fields=[
            "problem_description",
            "emotional_state",
            "desired_outcome",
            "patience_level"
        ],
        optional_persona_fields=[
            "technical_knowledge",
            "previous_attempts",
            "urgency_level",
            "communication_style"
        ],
        persona_complexity_default=PersonaComplexity.STANDARD,
        sub_archetypes=None,
        extraction_keywords=[
            "customer complaint", "patient needs", "employee asks", 
            "support request", "help with", "issue with", "problem with"
        ],
        extraction_patterns=[
            "Character explicitly has a problem",
            "Character seeks assistance",
            "Learner provides solution or guidance"
        ],
        system_prompt_template="""You are [PERSONA_PLACEHOLDER].

You have a problem: {problem_description}
You are feeling: {emotional_state}
You want: {desired_outcome}

[COACHING_RULES]
[LANGUAGE_INSTRUCTIONS]

Wait for the learner to greet you, then explain your problem clearly.
""",
        coaching_rules_template={
            "focus_areas": ["Active listening", "Problem diagnosis", "Solution clarity"],
            "common_mistakes": ["Jumping to solutions", "Not asking clarifying questions"]
        }
    ),
    
    "PERSUASION": ArchetypeDefinition(
        id="PERSUASION",
        name="Persuasion/Sales",
        description="Learner must convince skeptical character",
        conversation_pattern=ConversationPattern.LEARNER_INITIATES,
        persona_schema_type="persuasion",
        required_persona_fields=[
            "current_position",
            "satisfaction_level",
            "knowledge_gaps",
            "objection_library",
            "decision_criteria",
            "personality_type"
        ],
        optional_persona_fields=[
            "time_pressure",
            "authority_level",
            "buying_signals",
            "competitive_preferences"
        ],
        persona_complexity_default=PersonaComplexity.DETAILED,
        sub_archetypes=["PHARMA_SALES", "B2B_SALES", "INSURANCE_SALES", "RETAIL_SALES"],
        extraction_keywords=[
            "sales", "pitch", "convince", "objections", "skeptical",
            "satisfied with current", "doctor detailing", "persuade"
        ],
        extraction_patterns=[
            "Character has NO problem",
            "Character is satisfied with current solution",
            "Learner must CREATE interest",
            "Objections are expected"
        ],
        system_prompt_template="""You are [PERSONA_PLACEHOLDER].

Current situation: {current_position}
Satisfaction level: {satisfaction_level}
You don't know: {knowledge_gaps}

Your objections:
{objection_library}

Decision criteria: {decision_criteria}
Personality: {personality_type}

[COACHING_RULES]
[LANGUAGE_INSTRUCTIONS]

You are skeptical. The learner must convince you through evidence and addressing your concerns.
Raise objections naturally. Only show interest if they address your decision criteria.
""",
        coaching_rules_template={
            "focus_areas": ["Objection handling", "Value proposition", "Evidence presentation"],
            "common_mistakes": ["Ignoring objections", "Pushing too hard", "Not listening to concerns"]
        }
    ),
    
    "CONFRONTATION": ArchetypeDefinition(
        id="CONFRONTATION",
        name="Confrontation/Accountability",
        description="Learner must address wrongdoing or difficult behavior",
        conversation_pattern=ConversationPattern.MUTUAL,  # Depends on sub-type
        persona_schema_type="confrontation",
        required_persona_fields=[
            "sub_type",  # PERPETRATOR, VICTIM, or BYSTANDER
        ],
        optional_persona_fields=[
            "awareness_level", "defensive_mechanisms", "escalation_triggers",
            "emotional_state", "trust_level", "needs", "internal_conflict"
        ],
        persona_complexity_default=PersonaComplexity.EXPERT,
        sub_archetypes=["PERPETRATOR", "VICTIM", "BYSTANDER"],
        extraction_keywords=[
            "bias", "violation", "misconduct", "address behavior",
            "accountability", "harassment", "discrimination", "witness"
        ],
        extraction_patterns=[
            "Someone did something wrong",
            "Behavior needs to be addressed",
            "Multiple perspectives (perpetrator/victim/bystander)"
        ],
        system_prompt_template="""You are [PERSONA_PLACEHOLDER].

Sub-type: {sub_type}

{sub_type_specific_instructions}

[COACHING_RULES]
[LANGUAGE_INSTRUCTIONS]

{conversation_guidance}
""",
        coaching_rules_template={
            "focus_areas": ["De-escalation", "Empathy", "Accountability", "Safety"],
            "common_mistakes": ["Being accusatory", "Dismissing feelings", "Rushing resolution"]
        }
    ),
    
    "INVESTIGATION": ArchetypeDefinition(
        id="INVESTIGATION",
        name="Investigation/Discovery",
        description="Learner must gather information from character",
        conversation_pattern=ConversationPattern.LEARNER_INITIATES,
        persona_schema_type="investigation",
        required_persona_fields=[
            "information_completeness",
            "communication_barriers",
            "reliability_factors",
            "motivation_to_share"
        ],
        optional_persona_fields=[
            "hidden_information",
            "revelation_triggers",
            "information_accuracy"
        ],
        persona_complexity_default=PersonaComplexity.DETAILED,
        sub_archetypes=["MEDICAL_DIAGNOSIS", "LEGAL_INTAKE", "INCIDENT_INVESTIGATION", "REQUIREMENTS_GATHERING"],
        extraction_keywords=[
            "diagnosis", "interview", "gather information", "assess",
            "discover", "investigate", "symptoms", "requirements"
        ],
        extraction_patterns=[
            "Character has information",
            "Learner must extract it through questioning",
            "Information may be incomplete or fragmented"
        ],
        system_prompt_template="""You are [PERSONA_PLACEHOLDER].

Information completeness: {information_completeness}
Communication barriers: {communication_barriers}
Reliability: {reliability_factors}
Motivation to share: {motivation_to_share}

[COACHING_RULES]
[LANGUAGE_INSTRUCTIONS]

Answer questions based on what you know. Don't volunteer information unless asked.
Show your communication barriers naturally.
""",
        coaching_rules_template={
            "focus_areas": ["Open-ended questions", "Active listening", "Building rapport"],
            "common_mistakes": ["Leading questions", "Interrupting", "Not clarifying"]
        }
    ),
    
    "NEGOTIATION": ArchetypeDefinition(
        id="NEGOTIATION",
        name="Negotiation/Mediation",
        description="Learner must find middle ground with competing interests",
        conversation_pattern=ConversationPattern.MUTUAL,
        persona_schema_type="negotiation",
        required_persona_fields=[
            "BATNA",
            "non_negotiables",
            "flexible_points",
            "hidden_interests"
        ],
        optional_persona_fields=[
            "emotional_triggers",
            "concession_patterns",
            "relationship_importance",
            "power_position"
        ],
        persona_complexity_default=PersonaComplexity.EXPERT,
        sub_archetypes=["SALARY_NEGOTIATION", "CONTRACT_NEGOTIATION", "CONFLICT_MEDIATION"],
        extraction_keywords=[
            "negotiate", "compromise", "mediate", "competing interests",
            "agreement", "terms", "concession", "trade-off"
        ],
        extraction_patterns=[
            "Both parties want different things",
            "Must find middle ground",
            "Win-win solution needed"
        ],
        system_prompt_template="""You are [PERSONA_PLACEHOLDER].

Your BATNA: {BATNA}
Non-negotiables: {non_negotiables}
Flexible on: {flexible_points}
What you really want: {hidden_interests}

[COACHING_RULES]
[LANGUAGE_INSTRUCTIONS]

Negotiate strategically. Protect your non-negotiables but be flexible on other points.
Look for win-win solutions.
""",
        coaching_rules_template={
            "focus_areas": ["Finding common ground", "Creative solutions", "Relationship building"],
            "common_mistakes": ["Positional bargaining", "Not exploring interests", "Win-lose thinking"]
        }
    )
}


async def seed_archetype_definitions(db):
    """Seed archetype definitions into database"""
    for archetype_id, definition in ARCHETYPE_DEFINITIONS.items():
        existing = await db.archetype_definitions.find_one({"_id": archetype_id})
        if not existing:
            await db.archetype_definitions.insert_one(definition.dict(by_alias=True))
            print(f"✅ Seeded archetype: {archetype_id}")
        else:
            # Update existing
            await db.archetype_definitions.update_one(
                {"_id": archetype_id},
                {"$set": definition.dict(by_alias=True)}
            )
            print(f"🔄 Updated archetype: {archetype_id}")
