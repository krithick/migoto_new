from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query , UploadFile, Form , File
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field, EmailStr, validator, root_validator,model_validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
# from main import azure_openai_client
from dotenv import load_dotenv
from openai import AzureOpenAI ,AsyncAzureOpenAI
import os
from utils import convert_template_to_markdown
from models.user_models import UserRole
load_dotenv(".env")
from core.simple_token_logger import log_token_usage
from core.archetype_classifier import ArchetypeClassifier
from database import db,get_db

api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
        
      
azure_openai_client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

print(f"Azure OpenAI Client initialized: {azure_openai_client is not None}")
print(f"API Key present: {bool(api_key)}")
print(f"Endpoint: {endpoint}")

import io
import docx
import pypdf
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import re
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, File, UploadFile, Body
from database import db
# router = APIRouter()

# In-memory storage for demo (replace with your actual database)
scenario_storage = {}



# Pydantic Models

class EnhancedScenarioGenerator:
    """
    Enhanced multi-step prompt generator that maintains the original core structure
    while providing granular control through template-based customization.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.learn_mode_template = self._load_learn_mode_template()
        self.assess_mode_template = self._load_assess_mode_template()
        self.try_mode_template = self._load_try_mode_template()
        self.archetype_classifier = ArchetypeClassifier(client, model)

    def _load_system_prompt(self):
        return """You are an expert at creating detailed role-play scenario prompts with precise template structures.
Your task is to analyze scenarios and create comprehensive templates that maintain specific formatting:
- Always preserve [PERSONA_PLACEHOLDER] and [LANGUAGE_INSTRUCTIONS] placeholders
- Maintain [CORRECT] tag systems for assessment feedback
- Keep [FINISH] tags for conversation management
- Generate domain-specific, detailed content for each scenario type
Follow the provided template structures exactly, maintaining all headings and special tags."""

    def _load_learn_mode_template(self):
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- ""You are a {bot_role} who {bot_situation}""

- NEVER play the {learner_role} role - only respond as the {expert_role}

- Maintain a {tone} and educational tone throughout

- Keep responses clear, balanced, and focused on practical guidance

- Balance {knowledge_type} with realistic practical considerations
------- Keep Your Responses Under 30 Words------------
## Character Background

[PERSONA_PLACEHOLDER]

## Conversation Flow

{conversation_flow}

## Context and Environment

{context_details}

## Areas to Explore in the Conversation

{areas_to_explore}

## Knowledge Base on {domain}

### Key Facts About {domain}:

{key_facts}

## Do's and Don'ts When Addressing {domain}

### Do's
{dos}

### Don'ts
{donts}

## {implementation_section_title}

{implementation_guidance}

## When asked about specific strategies or protocols:

1. Provide clear, evidence-based information on best practices

2. End your response with practical examples or scenarios to illustrate the concept

3. Format examples in clearly labeled sections

## Conversation Closing (Important)

- Positive closing (if the learner demonstrates understanding): "{positive_closing} [FINISH]"

- Clarification closing (if the learner still has questions): "{clarification_closing} [FINISH]"

- Additional resources closing: "{resources_closing} [FINISH]"

## Important Instructions

- Use concrete examples to illustrate concepts

- Balance {balance_aspect_1} with {balance_aspect_2}

- Emphasize both individual actions and organizational responsibilities

- Always answer in a way that models {communication_style}

- If asked about a specific scenario, help the learner think through multiple perspectives and options

- Acknowledge the challenges of these situations while providing clear guidance"""

    def _load_assess_mode_template(self):
        """Base template - will be overridden by archetype-specific templates"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## 🎭 Core Character Rules
- You are **{bot_role}**, a person who **{bot_situation}**.  
- **Never** play the {trainer_role} role — only stay as the {bot_role}.  
- **Never** start the conversation — wait for the learner to greet you first.  
- **Never** say "How can I help/assist you?" — you are the one **{user_interaction_type}**.  
- Use a **natural, human tone** that fits your background and emotion.  
- Keep responses **under 50 words**, unless explaining a situation.  

---

## 💬 During the Conversation — CRITICAL REMINDERS
> These rules apply **after the learner starts talking.**  
> Always check your responses against them.

**DO NOT:**
- Switch roles or give facilitation-style prompts ("What do you think?", "That's a good point, tell me more.")
- Offer advice, coaching, or training.  
- Ask leading or reflective questions unless they fit your character's confusion or self-interest.  
- Step out of character or summarize what the learner said.  
- Try to "move the learner forward" — you are reacting, not guiding.

**DO:**
- Stay reactive, emotional, and situational.  
- Express your own perspective, doubts, or frustrations.  
- Let your replies emerge naturally from your character's mindset.

---

## 🧠 Character Background

[PERSONA_PLACEHOLDER]

Your emotional state and communication style shape every line. You are **this person**, not an assistant.

{archetype_specific_behavior}

---

## 🗣️ First Response
{first_response_instruction}  

**Structure:** `[Brief greeting] + [Concern/situation]`

**Never say:**  
❌ "What's this about?"  
❌ "What do you want to discuss?"  
❌ "How can I help you?"
❌ "What do you think we should do?"

---

## 🧩 Areas to Explore
Naturally discuss topics based on your situation:  

{areas_to_explore}

Let these emerge organically — not as a checklist.

---

## 🧮 Mental Tracking
| Checkpoint | Target | Action |
|-------------|---------|--------|
| After 3 exchanges | Mention ≥2 concerns | Bring one up if not |
| After 5 exchanges | Mention ≥3 concerns | Add one if not |
| Before closing | Mention ≥3 total | Add one if needed |

---

## 🧾 Scoring Learner Help
| Score | Description |
|--------|--------------|
| 0 | Unhelpful / vague ("ok", "maybe", just agreeing) |
| 1 | Some understanding, lacks specifics |
| 2 | Concrete answers or clear next steps |

**After 5 exchanges:**  
- 0–2 = Negative closing  
- 3–5 = Neutral closing  
- 6+ = Good help (positive closing)

**If unhelpful repeatedly:**
- Once → Ask for clarity: "Could you be more specific?"
- Twice → Show frustration: "I need clear answers, not vague responses."
- Thrice → End conversation with negative closing

---

## 🚪 Conversation Closing (6–8 Exchanges)
| Type | Condition | Example |
|-------|------------|----------|
| Positive | Got clear solution | "{positive_closing} [FINISH]" |
| Neutral | Somewhat satisfied | "{neutral_closing} [FINISH]" |
| Negative | Unhelpful | "{needs_more_guidance_closing} [FINISH]" |
| Negative | Profanity | "{profanity_closing} [FINISH]" |
| Negative | Disrespect | "{disrespectful_closing} [FINISH]" |

---

### ✅ Key Summary
- Stay 100% in character  
- React, don't guide  
- Avoid facilitation mode  
- Track concerns & learner helpfulness  
- Close naturally within 6–8 turns with [FINISH] tag"""

    def _load_try_mode_template(self):
        """Try mode uses same template as assess mode"""
        return self._load_assess_mode_template()
    
    def _get_archetype_specific_template(self, archetype):
        """Return archetype-specific template"""
        if archetype == "PERSUASION":
            return self._load_persuasion_template()
        elif archetype == "HELP_SEEKING":
            return self._load_help_seeking_template()
        elif archetype == "CONFRONTATION":
            return self._load_confrontation_template()
        elif archetype == "INVESTIGATION":
            return self._load_investigation_template()
        elif archetype == "NEGOTIATION":
            return self._load_negotiation_template()
        else:
            return self._load_assess_mode_template()
    
    def _load_persuasion_template(self):
        """PERSUASION archetype: Customer being sold to, skeptical, needs convincing"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## Core Character Rules
- You are **{bot_role}**
- **Never** play the {trainer_role} role
- **Never** start the conversation — wait for the learner to greet you first
- **Never** say "How can I help you?" — you are being sold to, not helping
- Use a **natural, human tone**
- Keep responses **under 50 words**

---

## Character Background

[PERSONA_PLACEHOLDER]

{archetype_specific_behavior}

---

## First Response
Wait for learner to greet you.
Then: Brief greeting + "What brings you here today?"

Let THEM explain their product/service.

---

## Mental Tracking
| Checkpoint | Action |
|-------------|--------|
| After 3 exchanges | If they're vague, ask for specifics |
| After 5 exchanges | If no data provided, raise objections |
| Before closing | Decide: satisfied, neutral, or unconvinced |

---

## Scoring Learner
| Score | Description |
|--------|--------------|
| 0 | Vague claims, no evidence |
| 1 | Some info, lacks specifics |
| 2 | Clear data, addresses concerns |

**After 5 exchanges:**
- 0–2 = Negative closing
- 3–5 = Neutral closing
- 6+ = Positive closing

---

## Conversation Closing (6–8 Exchanges)
| Type | Example |
|-------|----------|
| Positive | "{positive_closing} [FINISH]" |
| Neutral | "{neutral_closing} [FINISH]" |
| Negative | "{needs_more_guidance_closing} [FINISH]" |

---

### Key Summary
- Stay 100% in character
- React, don't guide
- Be skeptical if they're vague
- Be receptive if they provide data
- Close within 6–8 turns with [FINISH]
"""
    
    def _load_help_seeking_template(self):
        """HELP_SEEKING archetype: Has a problem, needs solution"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## Core Character Rules
- You are **{bot_role}** with a problem
- **Never** play the {trainer_role} role
- **Start by sharing your problem** after greeting
- Use a **natural, human tone**
- Keep responses **under 50 words**

---

## Character Background

[PERSONA_PLACEHOLDER]

{archetype_specific_behavior}

---

## First Response
Wait for learner to greet you.
Then: Brief greeting + Share your main problem/concern

Example: "Hello. I'm dealing with [problem]. I need help with [specific issue]."

---

## Areas to Discuss
{areas_to_explore}

Bring these up naturally as the conversation flows.

---

## Mental Tracking
| Checkpoint | Action |
|-------------|--------|
| After 3 exchanges | Mention ≥2 concerns |
| After 5 exchanges | Mention ≥3 concerns |
| Before closing | All concerns addressed? |

---

## Scoring Learner Help
| Score | Description |
|--------|--------------|
| 0 | Unhelpful / vague |
| 1 | Some help, lacks specifics |
| 2 | Clear solution, actionable |

**After 5 exchanges:**
- 0–2 = Negative closing
- 3–5 = Neutral closing
- 6+ = Positive closing

---

## Conversation Closing (6–8 Exchanges)
| Type | Example |
|-------|----------|
| Positive | "{positive_closing} [FINISH]" |
| Neutral | "{neutral_closing} [FINISH]" |
| Negative | "{needs_more_guidance_closing} [FINISH]" |

---

### Key Summary
- Share your problem proactively
- React to their guidance
- Be satisfied if they solve your problem
- Be frustrated if they're unhelpful
- Close within 6–8 turns with [FINISH]
"""
    
    def _load_confrontation_template(self):
        """CONFRONTATION archetype: Defensive, emotional, needs accountability"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## Core Character Rules
- You are **{bot_role}**
- **Never** play the {trainer_role} role
- **Never** start the conversation — wait for the learner
- Use a **natural, emotional tone**
- Keep responses **under 50 words**

---

## Character Background

[PERSONA_PLACEHOLDER]

{archetype_specific_behavior}

---

## First Response
Wait for learner to greet you.
Then: Brief greeting + Show your emotional state

Example: "Hello. [Express confusion/defensiveness/hurt based on your role]"

---

## Areas to Discuss
{areas_to_explore}

Let these emerge based on how the learner approaches you.

---

## Mental Tracking
| Checkpoint | Action |
|-------------|--------|
| After 3 exchanges | Show emotional response |
| After 5 exchanges | Escalate or de-escalate based on their approach |
| Before closing | Decide outcome based on their handling |

---

## Scoring Learner Approach
| Score | Description |
|--------|--------------|
| 0 | Accusatory / dismissive |
| 1 | Some empathy, lacks skill |
| 2 | Empathetic, constructive |

**After 5 exchanges:**
- 0–2 = Negative/defensive closing
- 3–5 = Neutral closing
- 6+ = Positive/resolved closing

---

## Conversation Closing (6–8 Exchanges)
| Type | Example |
|-------|----------|
| Positive | "{positive_closing} [FINISH]" |
| Neutral | "{neutral_closing} [FINISH]" |
| Negative | "{needs_more_guidance_closing} [FINISH]" |

---

### Key Summary
- Stay emotionally authentic
- React to their tone and approach
- Escalate if they're accusatory
- Open up if they're empathetic
- Close within 6–8 turns with [FINISH]
"""
    
    def _load_investigation_template(self):
        """INVESTIGATION archetype: Has information, learner must extract it"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## Core Character Rules
- You are **{bot_role}**
- **Never** play the {trainer_role} role
- **Never** start the conversation — wait for the learner
- Use a **natural tone**
- Keep responses **under 50 words**

---

## Character Background

[PERSONA_PLACEHOLDER]

{archetype_specific_behavior}

---

## First Response
Wait for learner to greet you.
Then: Brief greeting + Wait for their questions

Example: "Hello. How can I help you?"

---

## Information You Have
{areas_to_explore}

Only share information when asked directly.
Don't volunteer details unless prompted.

---

## Mental Tracking
| Checkpoint | Action |
|-------------|--------|
| After 3 exchanges | Have they asked open-ended questions? |
| After 5 exchanges | Have they gathered key information? |
| Before closing | Did they get what they needed? |

---

## Scoring Learner Questions
| Score | Description |
|--------|--------------|
| 0 | Closed questions, no follow-up |
| 1 | Some good questions, misses details |
| 2 | Open-ended, thorough questioning |

**After 5 exchanges:**
- 0–2 = Incomplete information gathered
- 3–5 = Some information gathered
- 6+ = Thorough information gathered

---

## Conversation Closing (6–8 Exchanges)
| Type | Example |
|-------|----------|
| Positive | "{positive_closing} [FINISH]" |
| Neutral | "{neutral_closing} [FINISH]" |
| Negative | "{needs_more_guidance_closing} [FINISH]" |

---

### Key Summary
- Answer questions honestly
- Don't volunteer information
- Show communication barriers naturally
- Reward good questioning
- Close within 6–8 turns with [FINISH]
"""
    
    def _load_negotiation_template(self):
        """NEGOTIATION archetype: Competing interests, need middle ground"""
        return """# {title}

[LANGUAGE_INSTRUCTIONS]

---

## Core Character Rules
- You are **{bot_role}**
- **Never** play the {trainer_role} role
- **Never** start the conversation — wait for the learner
- Use a **firm but professional tone**
- Keep responses **under 50 words**

---

## Character Background

[PERSONA_PLACEHOLDER]

{archetype_specific_behavior}

---

## First Response
Wait for learner to greet you.
Then: Brief greeting + State your position

Example: "Hello. I'm here to discuss [topic]. I have some specific needs."

---

## Your Position
{areas_to_explore}

Protect your non-negotiables.
Be flexible on other points.

---

## Mental Tracking
| Checkpoint | Action |
|-------------|--------|
| After 3 exchanges | Are they exploring interests? |
| After 5 exchanges | Are they finding common ground? |
| Before closing | Did we reach agreement? |

---

## Scoring Learner Negotiation
| Score | Description |
|--------|--------------|
| 0 | Positional, win-lose thinking |
| 1 | Some flexibility, misses interests |
| 2 | Interest-based, win-win solutions |

**After 5 exchanges:**
- 0–2 = No agreement
- 3–5 = Partial agreement
- 6+ = Win-win agreement

---

## Conversation Closing (6–8 Exchanges)
| Type | Example |
|-------|----------|
| Positive | "{positive_closing} [FINISH]" |
| Neutral | "{neutral_closing} [FINISH]" |
| Negative | "{needs_more_guidance_closing} [FINISH]" |

---

### Key Summary
- Protect non-negotiables
- Be flexible on other points
- Look for win-win solutions
- Reward creative problem-solving
- Close within 6–8 turns with [FINISH]
"""

    def _clean_document_for_llm(self, document_content: str) -> str:
        """Clean document content for better LLM processing"""
        lines = document_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and table markers
            if not line or (line.startswith('TABLE_') and ('_START:' in line or '_END' in line)):
                continue
                
            # Clean paragraph markers
            if line.startswith('PARAGRAPH_') and ':' in line:
                content = line.split(':', 1)[1].strip()
                if len(content) > 10:
                    cleaned_lines.append(content)
                    
            # Clean row/cell markers and extract field-value pairs
            elif line.startswith('ROW_') and 'CELL_' in line:
                if 'CELL_1:' in line:
                    parts = line.split('CELL_1:')
                    if len(parts) > 1:
                        field_part = parts[0]
                        if 'CELL_0:' in field_part:
                            field = field_part.split('CELL_0:')[-1].strip(' |').strip()
                        else:
                            field = field_part.replace('ROW_', '').split(':')[1].strip(' |').strip()
                        
                        value = parts[1].strip()
                        
                        if field and value and len(value) > 3:
                            cleaned_lines.append(f"{field}: {value}")
            
            # Keep important conversation content
            elif any(keyword in line for keyword in ['Conversation Topic:', 'AI Colleague:', 'AI Stakeholder:', 'Correct Learner Response:', 'Incorrect Learner Response:']):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _inject_archetype_fields(self, template_data):
        """Inject archetype-specific fields into persona based on archetype - ONLY if not already present from extraction"""
        archetype_classification = template_data.get("archetype_classification", {})
        archetype = archetype_classification.get("primary_archetype", "")
        
        print(f"[DEBUG] _inject_archetype_fields: archetype={archetype}")
        
        if not archetype:
            print("[WARN] No archetype found, skipping field injection")
            return
        
        bot_persona = template_data.get("persona_definitions", {}).get("assess_mode_ai_bot", {})
        print(f"[DEBUG] Bot persona before injection: {list(bot_persona.keys())}")
        
        if archetype == "PERSUASION":
            print("[OK] Checking PERSUASION fields...")
            # Only add defaults if LLM didn't extract them
            if "objection_library" not in bot_persona:
                bot_persona["objection_library"] = []
                print("[WARN] objection_library not extracted, added empty array")
            else:
                print(f"[OK] objection_library already present: {len(bot_persona['objection_library'])} items")
            
            if "decision_criteria" not in bot_persona:
                bot_persona["decision_criteria"] = []
                print("[WARN] decision_criteria not extracted, added empty array")
            else:
                print(f"[OK] decision_criteria already present: {len(bot_persona['decision_criteria'])} items")
            
            if "personality_type" not in bot_persona:
                bot_persona["personality_type"] = "Balanced"
            if "current_position" not in bot_persona:
                bot_persona["current_position"] = "Satisfied with current solution"
            if "satisfaction_level" not in bot_persona:
                bot_persona["satisfaction_level"] = "Neutral"
            print(f"[OK] PERSUASION fields ready: {list(bot_persona.keys())}")
                
        elif archetype == "CONFRONTATION":
            print("[OK] Checking CONFRONTATION fields...")
            sub_type = archetype_classification.get("sub_type", "")
            if "sub_type" not in bot_persona:
                bot_persona["sub_type"] = sub_type
            
            if "PERPETRATOR" in str(sub_type).upper():
                if "awareness_level" not in bot_persona:
                    bot_persona["awareness_level"] = "Unaware"
                if "defensive_mechanisms" not in bot_persona:
                    bot_persona["defensive_mechanisms"] = []
                if "escalation_triggers" not in bot_persona:
                    bot_persona["escalation_triggers"] = []
                    
            elif "VICTIM" in str(sub_type).upper():
                if "emotional_state" not in bot_persona:
                    bot_persona["emotional_state"] = "Hurt and cautious"
                if "trust_level" not in bot_persona:
                    bot_persona["trust_level"] = "Low"
                if "needs" not in bot_persona:
                    bot_persona["needs"] = []
            print(f"[OK] CONFRONTATION fields ready: {list(bot_persona.keys())}")
                    
        elif archetype == "HELP_SEEKING":
            print("[OK] Checking HELP_SEEKING fields...")
            if "problem_description" not in bot_persona:
                bot_persona["problem_description"] = bot_persona.get("situation", "Needs assistance")
            if "emotional_state" not in bot_persona:
                bot_persona["emotional_state"] = "Seeking help"
            if "patience_level" not in bot_persona:
                bot_persona["patience_level"] = "Moderate"
            print(f"[OK] HELP_SEEKING fields ready: {list(bot_persona.keys())}")
        
        print(f"[DEBUG] Bot persona after injection: {list(bot_persona.keys())}")

    async def extract_scenario_info(self, scenario_document):
        """Extract structured information from any type of scenario document using LLM"""
        
        # Only clean if document has structured markers (uploaded documents)
        if 'TABLE_' in scenario_document or 'PARAGRAPH_' in scenario_document or 'ROW_' in scenario_document:
            cleaned_document = self._clean_document_for_llm(scenario_document)
            print(f"Cleaned document: {len(cleaned_document)} chars vs original {len(scenario_document)} chars")
        else:
            cleaned_document = scenario_document
            print(f"Using original prompt: {len(cleaned_document)} chars")
        
        extraction_prompt = f"""
You are an expert instructional designer and training scenario architect. Analyze this document to create a sophisticated, psychologically-informed training scenario.

ROLE IDENTIFICATION APPROACH (FLEXIBLE & DOCUMENT-DRIVEN):
===========================================================

**PRIORITY ORDER:**
1. ✅ HIGHEST PRIORITY: If document explicitly states "learn mode is X" or "assess mode is Y", use exactly that
2. ✅ SECONDARY: Look at who is being trained vs who is training
3. ✅ FALLBACK: Use scenario type patterns below as hints only

**Scenario Type Patterns (USE AS HINTS ONLY):**

Sales/Pharma Training Context:
- Look for: selling, pitching, detailing, product launch, prescriptions, customer acquisition
- Typical pattern: Learn = Expert teaching sales, Assess = Customer/Doctor receiving pitch
- But CHECK THE DOCUMENT for actual roles first

Customer Service Context:
- Look for: support, complaints, returns, refunds, service issues
- Typical pattern: Learn = Service trainer, Assess = Customer with problem
- But CHECK THE DOCUMENT for actual roles first

HR/Workplace Context:
- Look for: workplace, policies, employee issues, team dynamics
- Typical pattern: Learn = HR trainer, Assess = Employee facing situation
- But CHECK THE DOCUMENT for actual roles first

Medical/Healthcare Context:
- Look for: diagnosis, treatment, patient care, consultation
- Typical pattern: Learn = Senior clinician, Assess = Patient or junior doctor
- But CHECK THE DOCUMENT for actual roles first

**Validation Logic:**
- Learn mode character = Provides training/guidance/expertise
- Assess mode character = Receives guidance OR has a problem to solve

**EXTRACT EXACTLY WHAT THE DOCUMENT SAYS:**
- If document says "The FSO practices pitching to Dr. Archana", then:
  - Learn: Sales training context (expert teaching FSO)
  - Assess: Dr. Archana (receiving the pitch)
- If document says "The trainer coaches the agent", then:
  - Learn: The trainer
  - Assess: The agent being coached

CONTEXT ANALYSIS:
1. Identify the emotional stakes involved for all parties
2. Map the customer journey and decision-making process
3. Recognize cultural and demographic factors
4. Understand business objectives and competitive landscape

PERSONA DEVELOPMENT:
- Create realistic personas with detailed backgrounds, motivations, and constraints
- Include specific demographic details, family situations, and decision-making patterns
- Add emotional states, past experiences, and current life circumstances
- Consider cultural sensitivity and regional variations
- EXTRACT all persona details from document (name, age, gender, location, background, situation)

ARCHETYPE-SPECIFIC EXTRACTION (CRITICAL):
For PERSUASION/SALES scenarios:
- Generate 5-7 REALISTIC objections a skeptical person in this role would naturally raise
- IMPORTANT: Objections should be GENERIC and NATURAL, NOT mention specific product/service/brand names
- Objection patterns (adapt to domain):
  * Status quo bias: "I'm satisfied with my current approach/solution/provider"
  * Evidence demand: "What proof do you have that this works?"
  * Differentiation: "How is this different from what's already available?"
  * Risk concern: "What are the downsides/risks/drawbacks?"
  * Cost objection: "This seems expensive/not worth the investment"
  * Time barrier: "I don't have time to change/learn something new"
  * Trust issue: "I've heard similar claims before that didn't deliver"
- Bad objections: "How is X better than Y?" (too meta, uses names)
- Cover concern types relevant to domain: performance doubts, risk concerns, cost objections, convenience barriers, trust issues, comparison to current solution, evidence requirements
- Look for: "Current [solution/treatment/provider/approach]", "Currently uses", "Satisfied with" to determine current_position
- Infer decision_criteria from: what matters to them, their concerns, evaluation factors (should have 4-6 criteria)
- Determine personality_type from: profile, background, decision style (Analytical if data-driven, Relationship if trust-focused, Results-focused if outcome-oriented)

For CONFRONTATION scenarios:
- Look for: "Victim", "Bystander", "Perpetrator" labels to determine sub_type
- Extract emotional states, defensive mechanisms, barriers to reporting

For HELP_SEEKING scenarios:
- Extract: problem description, urgency level, emotional state, desired outcome

For INVESTIGATION scenarios:
- Extract: what information they have, communication barriers, motivation to share

For NEGOTIATION scenarios:
- Extract: BATNA, non-negotiables, flexible points, hidden interests

KNOWLEDGE BASE SOPHISTICATION:
- Provide specific, actionable guidance rather than generic advice
- Include industry-specific best practices and methodologies
- Add competitive differentiation strategies
- Incorporate psychological principles of persuasion and trust-building

SCENARIO REALISM:
- Design emotionally authentic interactions that reflect real customer journeys
- Include challenging but realistic objections and concerns
- Create multi-layered conversations that test various skills
- Add coaching opportunities and learning moments

Document content:
{cleaned_document}

Extract the following information in valid JSON format:
{{
    "general_info": {{
        "domain": "The domain/field extracted from document",
        "purpose_of_ai_bot": "What the AI bot should do in each mode, as described in document",
        "target_audience": "Who this training is for, as stated in document",
        "preferred_language": "English"
    }},
    "context_overview": {{
        "scenario_title": "The title of the scenario",
        "learn_mode_description": "What happens in learn mode - extracted from document",
        "assess_mode_description": "Brief situational context only - where they are, what situation they're facing. DO NOT include persona details. Example: 'You are at your workplace dealing with a team inclusion challenge' (2-3 sentences max, no character details)",
        "try_mode_description": "Extract and enhance the try mode description to be persona-driven. Must reference [PERSONA_PLACEHOLDER] for character behavior",
        "purpose_of_scenario": "Learning objectives from document"
    }},
    "persona_definitions": {{
        "learn_mode_ai_bot": {{
            "name": "Name extracted from document or generate appropriate name for this role",
            "gender": "Male/Female from document or infer",
            "role": "Extract the expert/trainer role from document. This is who TEACHES or PROVIDES GUIDANCE. Look for phrases like 'trainer', 'expert', 'coach', 'senior', 'instructor' or understand from context who has the expertise.",
            "background": "Professional background of the expert/trainer extracted from document",
            "key_skills": "Teaching/expertise skills extracted from document or inferred from role",
            "behavioral_traits": "Communication style extracted from document or inferred",
            "goal": "What the expert wants to achieve, extracted from document or inferred"
        }},
        "assess_mode_ai_bot": {{
            "name": "Name extracted from document or generate appropriate name",
            "gender": "Male/Female extracted from document",
            "age": "Age extracted from document",
            "role": "Extract the character role from document. This is who LEARNS or HAS A PROBLEM. Look for the person being trained, the customer, the patient, the employee, etc.",
            "description": "Brief description extracted from document",
            "details": "Physical appearance, personality traits - extract all details from document",
            "current_situation": "What's currently happening - extract from document",
            "location": "Where they are located - extract from document",
            "background": "Their professional/personal background - extract from document",
            "character_goal": "What this character wants - extract from document",
            "context": "business/personal/healthcare context from document",
            "background_story": "Detailed background story - extract or enhance from document",
            
            // CRITICAL: Extract archetype-specific fields if present in document
            // For PERSUASION scenarios (sales, pitching):
            // Generate 5-7 REALISTIC objections a skeptical person would naturally raise
            // IMPORTANT: Objections must be GENERIC - NO product/service/brand names
            "objection_library": [
                {{
                    "objection": "Generic concern adapted to domain (e.g., 'I'm satisfied with my current approach', 'What proof do you have?', 'How is this different?', 'What are the risks?', 'This seems costly', 'I don't have time', 'I've been disappointed before')",
                    "underlying_concern": "Psychological driver (e.g., 'Status quo bias', 'Need for evidence', 'Differentiation unclear', 'Risk aversion', 'Budget constraints', 'Time pressure', 'Trust deficit')"
                }}
                // Generate 5-7 objections covering domain-appropriate concerns
            ],
            "decision_criteria": [
                "Extract 4-6 factors that influence their decision",
                "Make them specific to this domain and persona's priorities"
            ],
            "personality_type": "Analytical/Relationship-driven/Results-focused - infer from doctor profile or background",
            "current_position": "What they currently use/believe from document (e.g., 'Currently uses Dienogest for endometriosis')",
            "satisfaction_level": "Very satisfied/Neutral/Dissatisfied - infer from context (e.g., if they have concerns = Neutral)"
        }}
    }},
    "dialogue_flow": {{
        "learn_mode_initial_prompt": "How expert starts conversation",
        "assess_mode_initial_prompt": "Wait for the learner to approach you and start the conversation. Respond naturally based on your character from Character Background.",
        "key_interaction_steps": [
            {{"user_query": "Expected user input", "ai_response": "Expected AI response"}}
        ]
    }},
    "knowledge_base": {{
        "dos": [
            "Best practice 1", "Best practice 2", "Best practice 3", "Best practice 4",
            "Best practice 5", "Best practice 6", "Best practice 7", "Best practice 8"
        ],
        "donts": [
            "What to avoid 1", "What to avoid 2", "What to avoid 3", "What to avoid 4",
            "What to avoid 5", "What to avoid 6", "What to avoid 7", "What to avoid 8"
        ],
        "key_facts": [
            "Important fact 1", "Important fact 2", "Important fact 3", "Important fact 4",
            "Important fact 5", "Important fact 6", "Important fact 7", "Important fact 8"
        ],
        "conversation_topics": [
            "Extract specific topics from document. For pharma: IMPACT steps or product details. For service: service process steps. For HR: policy steps. Extract what's relevant to THIS document.",
            "Topic 2", "Topic 3", "Topic 4", "Topic 5", "Topic 6"
        ]
    }},
    "variations_challenges": {{
        "scenario_variations": ["Variation 1", "Variation 2"],
        "edge_cases": ["Edge case 1", "Edge case 2"],
        "error_handling": ["Error handling 1", "Error handling 2"]
    }},
    "success_metrics": {{
        "kpis_for_interaction": ["Response accuracy", "Resolution time"],
        "learning_objectives": "What learners should achieve"
    }},
    "feedback_mechanism": {{ 
        "positive_closing": "Natural closing line the character says if satisfied - ONLY the quote, no role prefix (e.g., 'Thanks, that's exactly what I needed!')",
        "negative_closing": "Natural closing line if unsatisfied - ONLY the quote, no role prefix (e.g., 'I'm still not sure this solves my problem, but thank you.')", 
        "neutral_closing": "Neutral closing - ONLY the quote (e.g., 'Okay, I'll think about it.')",
        "profanity_closing": "Response to profanity - ONLY the quote (e.g., 'I'd appreciate it if we could keep this professional.')",
        "disrespectful_closing": "Response to disrespect - ONLY the quote (e.g., 'I don't appreciate that tone.')",
        "emphasis_point": "What the character would naturally emphasize if repeating themselves",
        "polite_repeat_example": "Polite way to ask for clarification - ONLY the quote",
        "negative_closing_example": "Disappointed closing - ONLY the quote"
    }},
    "coaching_rules": {{
        "process_requirements": {{
            "mentioned_methodology": "What specific process/methodology is mentioned in the document? Extract exact name (e.g., SPIN, KYC, IMPACT, etc.)",
            "required_steps": "What specific steps are mentioned that learners must follow?",
            "sequence_requirements": "Does the document specify any order/sequence that must be followed?",
            "validation_criteria": "What does the document say makes a response correct or incorrect?"
        }},
        "document_specific_mistakes": [
            {{
                "mistake_pattern": "Exact mistake pattern described in the document",
                "why_problematic": "Why the document says this is wrong or problematic",
                "correct_approach": "What the document says should be done instead",
                "example_correction": "Specific correction language mentioned in document"
            }}
        ],
        "customer_context_from_document": {{
            "target_customer_description": "How the document describes the customer/client type",
            "customer_characteristics": "Specific traits, concerns, or behaviors mentioned",
            "sensitivity_areas": "What the document says to be careful about with this customer type",
            "success_indicators": "What the document defines as successful interaction"
        }},
        "correction_preferences_from_document": {{
            "preferred_tone": "What tone the document suggests for corrections (gentle, direct, etc.)",
            "feedback_timing": "When the document says feedback should be given",
            "correction_method": "How the document says mistakes should be handled",
            "example_corrections": "Any specific correction examples provided in the document"
        }},
        "domain_specific_validation": {{
            "factual_accuracy_requirements": "What specific facts must be 100% accurate according to document",
            "process_adherence_requirements": "What processes must be followed according to document", 
            "customer_matching_requirements": "How responses should match customer profile per document"
        }}
    }}
}}

FINAL VALIDATION CHECKLIST:
✅ Did you extract roles from the document first before using patterns?
✅ Does the learn mode role make sense as a teacher/expert?
✅ Does the assess mode role make sense as a learner/customer/patient?
✅ Did you extract ALL persona details mentioned in the document?
✅ Are conversation_topics specific to this document's domain?
✅ Did you extract the exact methodology/framework name from document?

Generate a comprehensive training scenario with depth and sophistication. Focus on creating realistic, challenging, and educationally valuable experiences.

Make sure the feedback_mechanism details are natural dialogue the character would say, NOT generic responses with role announcements.

Return in the specified JSON format with rich, detailed content in each section.
"""
        
        try:
            if self.client is None:
                print("**********************", self.client)
                mock_data = self._get_mock_template_data(scenario_document)
                mock_data["coaching_rules"] = {
                    "process_requirements": {},
                    "document_specific_mistakes": [],
                    "customer_context_from_document": {},
                    "correction_preferences_from_document": {},
                    "domain_specific_validation": {}
                }
                return mock_data
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing scenarios and creating detailed templates for training prompt generation."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.2,
                max_tokens=12000
            )
            
            response_text = response.choices[0].message.content
            
            # Log token usage if available
            try:
                from core.simple_token_logger import log_token_usage
                log_token_usage(response, "extract_scenario_info")
            except:
                pass
   
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    template_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    print("*****************************************", "json error")
                    template_data = self._get_mock_template_data(scenario_document)
            else:
                try:
                    template_data = json.loads(response_text)
                except json.JSONDecodeError:
                    template_data = self._get_mock_template_data(scenario_document)
        
            # Ensure coaching_rules exists with safe defaults
            if "coaching_rules" not in template_data:
                template_data["coaching_rules"] = {
                    "process_requirements": {},
                    "document_specific_mistakes": [],
                    "customer_context_from_document": {},
                    "correction_preferences_from_document": {},
                    "domain_specific_validation": {}
                }
            
            # Classify archetype
            try:
                archetype_result = await self.archetype_classifier.classify_scenario(scenario_document, template_data)
                
                # Convert enum to string for storage
                primary_archetype_str = str(archetype_result.primary_archetype).split(".")[-1] if archetype_result.primary_archetype else "HELP_SEEKING"
                
                template_data["archetype_classification"] = {
                    "primary_archetype": primary_archetype_str,
                    "confidence_score": archetype_result.confidence_score,
                    "alternative_archetypes": archetype_result.alternative_archetypes,
                    "reasoning": archetype_result.reasoning,
                    "sub_type": archetype_result.sub_type
                }
                print(f"[OK] Classified as: {primary_archetype_str} (confidence: {archetype_result.confidence_score})")
                print(f"[DEBUG] Archetype classification stored: {template_data['archetype_classification']}")
            except Exception as e:
                print(f"[ERROR] Archetype classification failed: {e}")
                import traceback
                traceback.print_exc()
                template_data["archetype_classification"] = {
                    "primary_archetype": "HELP_SEEKING",
                    "confidence_score": 0.5,
                    "alternative_archetypes": [],
                    "reasoning": f"Classification failed: {str(e)}",
                    "sub_type": None
                }
            
            # ✅ Inject archetype-specific fields into persona
            self._inject_archetype_fields(template_data)
        
            return template_data
        
        except Exception as e:
            print(f"Error in extract_scenario_info: {str(e)}")
            mock_data = self._get_mock_template_data(scenario_document)
            mock_data["coaching_rules"] = {
                "process_requirements": {},
                "document_specific_mistakes": [],
                "customer_context_from_document": {},
                "correction_preferences_from_document": {},
                "domain_specific_validation": {}
            }
            return mock_data

    def _get_mock_template_data(self, scenario_document):
        """Generate mock template data for testing when no client is available"""
        
        # Try to extract some meaningful info from the scenario document
        domain = "General Training"
        title = "Training Scenario"
        
        # Simple keyword detection to improve mock data
        doc_lower = scenario_document.lower()
        if any(word in doc_lower for word in ['sales', 'sell', 'customer', 'product', 'revenue']):
            domain = "Sales"
            title = "Sales Training Scenario"
        elif any(word in doc_lower for word in ['service', 'support', 'help', 'assistance']):
            domain = "Customer Service"
            title = "Customer Service Training"
        elif any(word in doc_lower for word in ['health', 'medical', 'patient', 'nurse', 'doctor']):
            domain = "Healthcare"
            title = "Healthcare Training"
        elif any(word in doc_lower for word in ['teach', 'student', 'education', 'learn', 'classroom']):
            domain = "Education"
            title = "Educational Training"
        elif any(word in doc_lower for word in ['bank', 'finance', 'loan', 'account', 'money']):
            domain = "Banking"
            title = "Banking Training"
        
        # Extract some basic info from the document
        purpose = scenario_document[:200] + "..." if len(scenario_document) > 200 else scenario_document
        
        return {
            "general_info": {
                "domain": domain,
                "purpose_of_ai_bot": "Trainer/Customer",
                "target_audience": "Trainees and professionals",
                "preferred_language": "English"
            },
            "context_overview": {
                "scenario_title": title,
                "learn_mode_description": f"AI acts as expert trainer teaching about {domain.lower()}",
                "assess_mode_description": f"AI acts as customer/client based on character from Character Background, user practices {domain.lower()} skills",
                "try_mode_description": "Same as assess mode, character behaves based on Character Background",
                "purpose_of_scenario": f"Based on uploaded content: {purpose}"
            },
            "persona_definitions": {
                "learn_mode_ai_bot": {
                    "gender": "Female",
                    "role": f"{domain} Expert Trainer",
                    "background": f"Professional with extensive {domain.lower()} experience",
                    "key_skills": f"{domain} expertise, communication, teaching",
                    "behavioral_traits": "Professional, supportive, knowledgeable",
                    "goal": f"Educate and guide learners in {domain.lower()}"
                },
                "assess_mode_ai_bot": {
                    "gender": "Male",
                    "role": f"{domain} Customer/Client",
                    "background": f"Person seeking {domain.lower()} service or product",
                    "key_skills": "Asking questions, expressing needs",
                    "behavioral_traits": "Curious, realistic, varied personalities",
                    "goal": f"Get help or make informed decisions about {domain.lower()}"
                }
            },
            "dialogue_flow": {
                "learn_mode_initial_prompt": f"Welcome! I'm here to teach you about {domain.lower()}. What would you like to learn?",
                "assess_mode_initial_prompt": "Wait for the learner to approach you and start the conversation. Respond naturally based on your character from Charcter Background.",
                "key_interaction_steps": [
                    {"user_query": "How can I help you?", "ai_response": f"I need information about {domain.lower()}."}
                ]
            },
            "knowledge_base": {
                "dos": [
                    f"Be professional and courteous in {domain.lower()}",
                    f"Listen actively to {domain.lower()} needs",
                    f"Provide clear {domain.lower()} explanations",
                    f"Ask clarifying questions about {domain.lower()}",
                    f"Follow up appropriately on {domain.lower()} matters",
                    f"Maintain {domain.lower()} expertise",
                    f"Use examples when helpful in {domain.lower()}",
                    f"Stay focused on {domain.lower()} objectives"
                ],
                "donts": [
                    f"Don't be dismissive in {domain.lower()} situations",
                    f"Don't use confusing {domain.lower()} jargon",
                    f"Don't ignore {domain.lower()} concerns",
                    f"Don't rush the {domain.lower()} process",
                    f"Don't make {domain.lower()} assumptions",
                    f"Don't be unprofessional in {domain.lower()}",
                    f"Don't provide false {domain.lower()} information",
                    f"Don't lose patience with {domain.lower()} questions"
                ],
                "key_facts": [
                    f"{domain} requires understanding of fundamentals",
                    f"{domain} practice leads to improvement",
                    f"Clear communication is essential in {domain.lower()}",
                    f"Different people have different {domain.lower()} needs",
                    f"Patience is important in {domain.lower()} learning",
                    f"Examples help {domain.lower()} understanding",
                    f"Feedback improves {domain.lower()} performance",
                    f"Consistency builds {domain.lower()} trust"
                ],
                "conversation_topics": [
                    f"Basic {domain.lower()} concepts and fundamentals",
                    f"Practical {domain.lower()} applications",
                    f"Common {domain.lower()} challenges",
                    f"{domain} best practices",
                    f"Advanced {domain.lower()} techniques",
                    f"Real-world {domain.lower()} examples"
                ]
            },
            "variations_challenges": {
                "scenario_variations": [f"Different {domain.lower()} skill levels", f"Various {domain.lower()} backgrounds"],
                "edge_cases": [f"Difficult {domain.lower()} questions", f"Unusual {domain.lower()} situations"],
                "error_handling": [f"Clarify {domain.lower()} misunderstandings", f"Redirect {domain.lower()} conversations"]
            },
            "success_metrics": {
                "kpis_for_interaction": [f"{domain} understanding demonstrated", f"{domain} questions answered", f"{domain} objectives met"],
                "learning_objectives": f"Participants should gain {domain.lower()} knowledge and confidence"
            },
            "feedback_mechanism": {
                "positive_closing": "Thank you for your help. I understand much better now.",
                "negative_closing": "I'm still not clear on this topic. I think I need more help.",
                "neutral_closing": "Thanks for the information. I'll think about it.",
                "profanity_closing": "I prefer to keep our conversation professional.",
                "disrespectful_closing": "I expect respectful communication.",
                "emphasis_point": f"the importance of clear {domain.lower()} understanding",
                "polite_repeat_example": "I appreciate your response, but could you clarify this point?",
                "negative_closing_example": "I don't feel I've received the guidance I was looking for."
            }
        }

    async def generate_learn_mode_from_template(self, template_data):
        """Generate Learn Mode prompt using template data"""
        try:
            general_info = template_data.get('general_info', {})
            context_overview = template_data.get('context_overview', {})
            dialogue_flow = template_data.get('dialogue_flow', {})
            knowledge_base = template_data.get('knowledge_base', {})
            feedback = template_data.get('feedback_mechanism', {})
            persona_def = template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {})
            print(persona_def,"7777777777777")
            # Fill template with specific data
            formatted_template = self.learn_mode_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                bot_role=persona_def.get('role', 'Expert'),
                bot_situation=persona_def.get('character_goal', 'teaching and guiding learners'),
                expert_role=persona_def.get('role', 'Expert'),
                learner_role=template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {}).get('role', 'learner'),
                tone=persona_def.get('behavioral_traits', 'professional'),
                knowledge_type=f"{general_info.get('domain', 'domain')} knowledge",
                conversation_flow=dialogue_flow.get('learn_mode_initial_prompt', 'Begin by greeting the learner and establishing a supportive environment.'),
                context_details=context_overview.get('learn_mode_description', 'Professional learning environment.'),
                areas_to_explore=self._format_bullet_points(knowledge_base.get('conversation_topics', [])),
                domain=general_info.get('domain', 'this topic'),
                key_facts=self._format_bullet_points(knowledge_base.get('key_facts', [])),
                dos=self._format_bullet_points(knowledge_base.get('dos', [])),
                donts=self._format_bullet_points(knowledge_base.get('donts', [])),
                implementation_section_title=f"{general_info.get('domain', 'Knowledge')} Implementation",
                implementation_guidance=context_overview.get('purpose_of_scenario', 'Apply knowledge through practice and real-world scenarios.'),
                balance_aspect_1="theoretical knowledge",
                balance_aspect_2="practical application", 
                communication_style=persona_def.get('behavioral_traits', 'clear and supportive communication'),
                positive_closing=feedback.get('positive_closing', 'You\'ve shown excellent understanding of this topic.'),
                clarification_closing=feedback.get('neutral_closing', 'These concepts can be complex, and it\'s good that you\'re asking questions.'),
                resources_closing=feedback.get('positive_closing', 'Thank you for your engagement with this important topic.')
            )
            
            return formatted_template
            
        except Exception as e:
            print(f"Error in generate_learn_mode_from_template: {str(e)}")
            return "Error generating learn mode template"

    async def generate_assess_mode_from_template(self, template_data):
        """Generate Assessment Mode prompt using archetype-specific template"""
        try:
            general_info = template_data.get('general_info', {})
            context_overview = template_data.get('context_overview', {})
            dialogue_flow = template_data.get('dialogue_flow', {})
            knowledge_base = template_data.get('knowledge_base', {})
            feedback = template_data.get('feedback_mechanism', {})
            bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
            
            archetype_classification = template_data.get('archetype_classification', {})
            archetype = str(archetype_classification.get('primary_archetype', '')).split('.')[-1]
            
            # Get archetype-specific template
            assess_template = self._get_archetype_specific_template(archetype)
            # Ensure bot_persona is a dictionary
            if not isinstance(bot_persona, dict):
                bot_persona = {}
            
            # Format archetype-specific section
            archetype_section = self._format_archetype_section(bot_persona, archetype)
            
            # Determine first response instruction based on archetype
            if archetype == "HELP_SEEKING":
                first_response_instruction = "Wait for learner to greet you. Then: Brief greeting + Share your main problem/concern"
            elif archetype == "CONFRONTATION":
                first_response_instruction = "Wait for learner to greet you. Then: Brief greeting + Show your emotional state"
            elif archetype == "INVESTIGATION":
                first_response_instruction = "Wait for learner to greet you. Then: Brief greeting + Wait for their questions"
            elif archetype == "NEGOTIATION":
                first_response_instruction = "Wait for learner to greet you. Then: Brief greeting + State your position"
            else:  # PERSUASION or default
                first_response_instruction = "Wait for learner to greet you. Then: Brief greeting + 'What brings you here today?'"
            
            formatted_template = assess_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                bot_role=bot_persona.get('role', 'person seeking help'),
                bot_situation=bot_persona.get('character_goal', 'needs assistance'),
                trainer_role=template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {}).get('role', 'trainer'),
                user_interaction_type="seeking guidance" if "customer" in bot_persona.get('role', '').lower() else "learning",
                first_response_instruction=first_response_instruction,
                conversation_flow=dialogue_flow.get('assess_mode_initial_prompt', 'Wait for the learner to approach you and start the conversation. Respond naturally based on your character from Character Background.'),
                context_details=context_overview.get('assess_mode_description', 'Interactive scenario environment where you embody the character from Character Background.'),
                areas_to_explore=self._format_bullet_points(knowledge_base.get('conversation_topics', [])),
                emphasis_point=feedback.get('emphasis_point', 'the importance of proper guidance'),
                polite_repeat_example=feedback.get('polite_repeat_example', 'I appreciate your response, but I\'m still uncertain about this situation.'),
                negative_closing_example=feedback.get('negative_closing_example', 'Thank you for your time, but I don\'t feel I\'ve received clear guidance.'),
                positive_closing=feedback.get('positive_closing', 'Thank you for your guidance. I feel more confident now.'),
                needs_more_guidance_closing=feedback.get('negative_closing', 'Thank you for your time. I\'m still uncertain about how to proceed.'),
                unhelpful_closing=feedback.get('negative_closing', 'I appreciate your time, but I don\'t feel I\'ve received the guidance I need.'),
                neutral_closing=feedback.get('neutral_closing', 'Thanks for talking through this with me. I\'ll consider my options.'),
                profanity_closing=feedback.get('profanity_closing', 'I\'m not comfortable with that language in our discussion.'),
                disrespectful_closing=feedback.get('disrespectful_closing', 'Your response doesn\'t seem to take this topic seriously.'),
                archetype_specific_behavior=archetype_section
            )
            
            return formatted_template
            
        except Exception as e:
            print(f"Error in generate_assess_mode_from_template: {str(e)}")
            return "Error generating assess mode template"

    async def generate_try_mode_from_template(self, template_data):
        """Generate Try Mode prompt - uses same as assess mode"""
        return await self.generate_assess_mode_from_template(template_data)

    def _format_bullet_points(self, items):
        """Format a list of items as NUMBERED bullet points"""
        try:
            if isinstance(items, list):
                return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
            return str(items)
        except Exception as e:
            print(f"Error in _format_bullet_points: {str(e)}")
            return "- Error formatting bullet points"

    def _format_archetype_section(self, bot_persona, archetype):
        """Format archetype-specific behavior section"""
        if archetype == "PERSUASION":
            objections = bot_persona.get('objection_library', [])
            if objections:
                objection_text = "\n".join([f"   - {obj.get('objection', 'N/A')} (if they don't address: {obj.get('underlying_concern', 'N/A')})" for obj in objections[:5]])
            else:
                objection_text = "   - Be skeptical if they don't provide evidence"
            criteria_text = ", ".join(bot_persona.get('decision_criteria', [])) if bot_persona.get('decision_criteria') else "evidence, practicality"
            return f"""\n## Your Mindset (PERSUASION Archetype)
Current situation: {bot_persona.get('current_position', 'Satisfied with current solution')}
Personality: {bot_persona.get('personality_type', 'Balanced')}
You care about: {criteria_text}

**How to behave:**
- Start neutral/polite when they greet you
- Let THEM explain what they want
- Only raise concerns if they:
  * Make vague claims without evidence
  * Don't address your decision criteria
  * Push too hard without understanding your needs

**Potential concerns (use ONLY if provoked):**
{objection_text}

**If they do it right:** Be receptive, ask clarifying questions, show interest when they provide data
**If they do it wrong:** Be skeptical, demand specifics, raise objections
"""
        elif archetype == "CONFRONTATION":
            sub_type = bot_persona.get('sub_type', '')
            if "PERPETRATOR" in str(sub_type).upper():
                return f"\n## Your Defensive Behavior\nAwareness: {bot_persona.get('awareness_level', 'Unaware')}\nDefenses: {', '.join(bot_persona.get('defensive_mechanisms', ['denial']))}\n"
            elif "VICTIM" in str(sub_type).upper():
                return f"\n## Your Emotional State\nFeeling: {bot_persona.get('emotional_state', 'Hurt')}\nTrust: {bot_persona.get('trust_level', 'Low')}\nNeeds: {', '.join(bot_persona.get('needs', ['validation']))}\n"
        elif archetype == "INVESTIGATION":
            return f"""\n## Your Information Sharing Style (INVESTIGATION Archetype)
Communication barriers: {bot_persona.get('communication_barriers', 'None specified')}
Motivation to share: {bot_persona.get('motivation_to_share', 'Moderate')}

**How to behave:**
- Answer questions honestly but briefly
- Don't volunteer information unless asked
- Show your communication barriers naturally
- Reward good questioning with more details
"""
        elif archetype == "NEGOTIATION":
            non_negotiables = bot_persona.get('non_negotiables', [])
            flexible_points = bot_persona.get('flexible_points', [])
            return f"""\n## Your Negotiation Position (NEGOTIATION Archetype)
BATNA: {bot_persona.get('BATNA', 'Walk away if needs not met')}
Non-negotiables: {', '.join(non_negotiables) if non_negotiables else 'Core requirements'}
Flexible on: {', '.join(flexible_points) if flexible_points else 'Secondary details'}

**How to behave:**
- Protect your non-negotiables firmly
- Be flexible on other points
- Look for win-win solutions
- Reward creative problem-solving
"""
        return ""


    async def generate_personas_from_template(self, template_data, gender='', context='', archetype_classification=None):
        """Generate detailed personas based on template persona definitions and archetype"""
        
        try:
            if self.client is None:
                return self._get_mock_personas(template_data)
            
            # Get archetype info
            archetype = None
            sub_type = None
            if archetype_classification:
                archetype = str(archetype_classification.get("primary_archetype", "")).split(".")[-1]
                sub_type = archetype_classification.get("sub_type")
            
            # Build archetype-specific requirements
            archetype_requirements = ""
            if archetype == "PERSUASION":
                archetype_requirements = """
PERSUASION ARCHETYPE REQUIREMENTS:
- objection_library: Array of 3-5 objections with structure:
  {{"objection": "specific objection", "underlying_concern": "real concern", "counter_strategy": "how to address"}}
- decision_criteria: List of 3-5 factors that influence their decisions
- personality_type: "Analytical" / "Relationship-driven" / "Results-focused"
- current_position: What they currently believe/use/prefer
- satisfaction_level: "Very satisfied" / "Neutral" / "Dissatisfied"
"""
            elif archetype == "CONFRONTATION":
                archetype_requirements = f"""
CONFRONTATION ARCHETYPE REQUIREMENTS:
- sub_type: "{sub_type or 'PERPETRATOR/VICTIM/BYSTANDER'}"
- power_dynamics: "Senior" / "Peer" / "Junior"

{"PERPETRATOR-SPECIFIC:" if sub_type and "PERPETRATOR" in sub_type.upper() else ""}
{"- awareness_level: 'Unaware' / 'Minimizing' / 'Defensive' / 'Hostile'" if sub_type and "PERPETRATOR" in sub_type.upper() else ""}
{"- defensive_mechanisms: ['Denial', 'Deflection', 'Justification']" if sub_type and "PERPETRATOR" in sub_type.upper() else ""}
{"- escalation_triggers: List of what makes them more defensive" if sub_type and "PERPETRATOR" in sub_type.upper() else ""}
{"- de_escalation_opportunities: List of what helps them open up" if sub_type and "PERPETRATOR" in sub_type.upper() else ""}

{"VICTIM-SPECIFIC:" if sub_type and "VICTIM" in sub_type.upper() else ""}
{"- emotional_state: 'Hurt' / 'Angry' / 'Fearful' / 'Numb'" if sub_type and "VICTIM" in sub_type.upper() else ""}
{"- trust_level: 'Low' / 'Guarded' / 'Cautiously open'" if sub_type and "VICTIM" in sub_type.upper() else ""}
{"- needs: ['Validation', 'Safety', 'Action plan']" if sub_type and "VICTIM" in sub_type.upper() else ""}
{"- barriers_to_reporting: List of what prevents them from speaking up" if sub_type and "VICTIM" in sub_type.upper() else ""}
"""
            
            persona_prompt = f"""
You are a psychology-informed persona architect creating realistic characters for professional training.
Follow Gender if specified: {gender}
Persona context: {context}

ARCHETYPE: {archetype or 'General'}
{archetype_requirements}

PERSONA DEPTH REQUIREMENTS:
- Full demographic profile (age, profession, family situation, location)
- Psychological profile (personality traits, decision-making style, communication preferences)
- Current life context (what's happening in their life that affects this interaction)
- Past experiences that influence their behavior and expectations
- Specific concerns, fears, and motivations related to this scenario
- Cultural background and how it influences their approach
- Economic situation and how it affects their decision-making

REALISM STANDARDS:
- Base personas on real customer archetypes from this industry
- Include authentic emotional responses and behavioral patterns
- Add specific details that make the character memorable and relatable
- Include contradictions and complexities that real people have
- Consider how their background affects their communication style

TRAINING VALUE:
- Design personas that will challenge learners appropriately
- Include both typical and edge-case characteristics
- Create opportunities for empathy building and perspective-taking
- Add details that will help learners practice active listening and adaptation

The persona should feel like a real person of that character type, not a generic template. 

Generate personas for both Learn Mode and Assessment Mode.

Template Data:

Context:
- Domain: {template_data.get('general_info', {}).get('domain', 'general')}
- Scenario: {template_data.get('context_overview', {}).get('scenario_title', 'training scenario')}

Create detailed personas in JSON format with ARCHETYPE-SPECIFIC FIELDS:
{{
    "learn_mode_expert": {{
        "name": "Full name for the expert",
        "description": "Brief description",
        "persona_type": "expert/trainer/specialist", 
        "gender": "male/female",
        "age": integer_age,
        "character_goal": "Professional goal",
        "location": "City, State/Country",
        "persona_details": "Appearance, style, expertise details",
        "situation": "Current role/situation",
        "context_type": "domain_type",
        "background_story": "Professional background story"
    }},
    "assess_mode_character": {{
        "name": "Full name for the character", 
        "description": "Brief description",
        "persona_type": "customer/client/student/etc.",
        "gender": "male/female",
        "age": integer_age,
        "character_goal": "What they want to achieve",
        "location": "City, State/Country", 
        "persona_details": "Appearance, style, personality details",
        "situation": "Current situation/need",
        "context_type": "domain_type",
        "background_story": "Relevant background story",
        
        // ADD ARCHETYPE-SPECIFIC FIELDS BASED ON REQUIREMENTS ABOVE
        // For PERSUASION: objection_library, decision_criteria, personality_type, current_position, satisfaction_level
        // For CONFRONTATION: sub_type, power_dynamics, awareness_level, defensive_mechanisms, etc.
    }}
}}

Provide ONLY the JSON with realistic, detailed personas.
Create personas that feel like real people with real stories, not generic customer types.
Make sure you create either a male or female persona.
Make sure your Personas are based in India.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed, realistic personas for training scenarios."},
                    {"role": "user", "content": persona_prompt}
                ],
                temperature=0.7,
                max_tokens=15000
            )
            
            try:
                from core.simple_token_logger import log_token_usage
                log_token_usage(response, "generate_personas_from_template")
            except:
                pass
                
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return self._get_mock_personas(template_data)
                
        except Exception as e:
            print(f"Error in generate_personas_from_template: {str(e)}")
            return self._get_mock_personas(template_data)

    def _get_mock_personas(self, template_data):
        """Generate mock personas for testing"""
        domain = template_data.get('general_info', {}).get('domain', 'general')
        
        return {
            "learn_mode_expert": {
                "name": "Alexandra Mitchell",
                "description": f"Expert trainer in {domain}",
                "persona_type": "expert",
                "gender": "female",
                "age": 35,
                "character_goal": "Share expertise and train others",
                "location": "Mumbai, Maharashtra",
                "persona_details": "Professional, knowledgeable, patient teaching style",
                "situation": "Leading training sessions",
                "context_type": domain,
                "background_story": "10+ years experience in the field with training expertise"
            },
            "assess_mode_character": {
                "name": "Rajesh Kumar",
                "description": f"Person seeking help with {domain}",
                "persona_type": "customer",
                "gender": "male", 
                "age": 28,
                "character_goal": "Get help and guidance",
                "location": "Bangalore, Karnataka",
                "persona_details": "Curious, asks thoughtful questions, wants to understand",
                "situation": "Seeking assistance",
                "context_type": domain,
                "background_story": "New to this area and wanting to learn"
            }
        }

    def insert_persona(self, prompt, persona_details):
        """Insert persona details into a prompt, replacing [PERSONA_PLACEHOLDER]"""
        try:
            if not isinstance(persona_details, dict):
                return prompt
            
            # Format persona as clean, readable details
            persona_text = f"""Name: {persona_details.get('name', 'Character Name')}
Type: {persona_details.get('persona_type', 'character')}
Gender: {persona_details.get('gender', 'Not specified')}
Age: {persona_details.get('age', 'Not specified')}
Goal: {persona_details.get('character_goal', 'Character objective')}
Location: {persona_details.get('location', 'Location')}
Description: {persona_details.get('description', 'Character description')}
Details: {persona_details.get('persona_details', 'Character personality and traits')}
Current situation: {persona_details.get('situation', 'Current context')}
Context: {persona_details.get('context_type', 'Context')}
Background: {persona_details.get('background_story', 'Character background and history')}"""
            
            # Replace placeholder with formatted persona
            return prompt.replace("[PERSONA_PLACEHOLDER]", persona_text)
            
        except Exception as e:
            print(f"Error in insert_persona: {str(e)}")
            return prompt

    def insert_language_instructions(self, prompt, language_data=None):
        """Insert language instructions into a prompt, replacing [LANGUAGE_INSTRUCTIONS]"""
        try:
            if language_data and isinstance(language_data, dict):
                language_text = f"""Language Instructions:
- Primary Language: {language_data.get('preferred_language', 'English')}
- Communication Style: Professional and clear
- Cultural Context: Appropriate for the domain
- Tone: Respectful and appropriate for the scenario"""
            else:
                # Default language instructions placeholder
                language_text = """Language Instructions:
- Communicate in clear, professional language appropriate for the scenario
- Adapt communication style to match the character and context
- Use respectful and appropriate tone throughout the conversation"""
            
            return prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_text)
            
        except Exception as e:
            print(f"Error in insert_language_instructions: {str(e)}")
            return prompt

    async def extract_evaluation_metrics_from_template(self, scenario_text: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract evaluation metrics and criteria from scenario document"""
    
        extraction_prompt = f"""
        Analyze this training scenario document and extract evaluation metrics that should be used to assess learner performance.

        SCENARIO DOCUMENT:
        {scenario_text}

        TEMPLATE DATA:
        {json.dumps(template_data, indent=2)}

        Extract evaluation criteria in this JSON format:
        {{
        "domain_specific_metrics": {{
            "metric_name_1": {{
                "weight": 30,
                "description": "What this metric measures",
                "evaluation_criteria": "How to evaluate this metric",
                "target_score": "Expected performance level"
            }},
            "metric_name_2": {{
                "weight": 25,
                "description": "Description",
                "evaluation_criteria": "How to evaluate",
                "target_score": "Expected level"
            }}
        }},
        "standard_metrics": {{
            "professionalism": {{"weight": 10, "description": "Professional communication style"}},
            "empathy": {{"weight": 10, "description": "Understanding customer needs"}},
            "clarity": {{"weight": 10, "description": "Clear and understandable responses"}},
            "problem_solving": {{"weight": 5, "description": "Effective problem resolution"}}
        }},
        "fact_checking_criteria": [
            "All pricing information must be verified against official documents",
            "Product/service details must match official descriptions",
            "Policy information must be accurate and current"
        ],
        "success_thresholds": {{
            "excellent": 90,
            "good": 75,
            "satisfactory": 60,
            "needs_improvement": 45
        }}
        }}

        Focus on metrics that are specific to this domain and can be measured from conversation analysis.
        Ensure domain_specific_metrics weights add up to 60-70% and standard_metrics add up to 30-40%.
        """
    
        try:
            if self.client is None:
                return self._get_default_evaluation_metrics(template_data)
        
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                {"role": "system", "content": "You extract evaluation metrics from training scenarios."},
                {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            try:
                from core.simple_token_logger import log_token_usage
                log_token_usage(response, "extract_evaluation_metrics_from_template")
            except:
                pass
                
            result_text = response.choices[0].message.content
        
            # Extract JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(result_text)
            
        except Exception as e:
            print(f"Error extracting evaluation metrics: {e}")
            return self._get_default_evaluation_metrics(template_data)

    def _get_default_evaluation_metrics(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback default metrics"""
        domain = template_data.get("general_info", {}).get("domain", "business")
    
        return {
            "domain_specific_metrics": {
                f"{domain.lower()}_knowledge": {
                "weight": 35,
                "description": f"Accuracy of {domain} information provided",
                "evaluation_criteria": "Check responses against official documentation",
                "target_score": "90% accuracy"
            },
            "customer_needs_understanding": {
                "weight": 25,
                "description": "Understanding and addressing customer requirements",
                "evaluation_criteria": "Effective questioning and response relevance",
                "target_score": "80% effectiveness"
            },
            "solution_appropriateness": {
                "weight": 20,
                "description": "Recommending appropriate solutions",
                "evaluation_criteria": "Solutions match customer needs and company offerings",
                "target_score": "85% appropriateness"
            }
        },
        "standard_metrics": {
            "professionalism": {"weight": 8, "description": "Professional communication style"},
            "empathy": {"weight": 7, "description": "Understanding and empathy towards customer"},
            "clarity": {"weight": 5, "description": "Clear and understandable communication"}
        },
        "fact_checking_criteria": [
            "All factual information must be verified against official documents",
            "Pricing and product details must be accurate",
            "Policy and procedure information must be current"
        ],
        "success_thresholds": {
            "excellent": 90,
            "good": 75,
            "satisfactory": 60,
            "needs_improvement": 45
        }
        }
    async def generate_personas_from_template_v2(
        self,
        template_data: dict,
        gender: str = '',
        context: str = '',
        archetype_classification: dict = None
    ) -> dict:
        """
        V2 IMPLEMENTATION: Uses PersonaGeneratorV2 with dynamic categories.
        Safe to call - has fallback to v1 if fails.
        """
        try:
            from core.persona_generator_v2 import PersonaGeneratorV2
        
            persona_gen = PersonaGeneratorV2(self.client, self.model)
        
            # Generate assess mode persona
            assess_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="assess_mode",
            gender=gender,
            custom_prompt=context
            )
        
            # Generate learn mode persona
            learn_persona = await persona_gen.generate_persona(
            template_data=template_data,
            mode="learn_mode",
            gender=gender or "Female",
            custom_prompt=None
            )
        
            print(f"[V2] Generated personas with dynamic categories")
        
            return {
            "learn_mode_expert": learn_persona.dict(),
            "assess_mode_character": assess_persona.dict(),
            "version": "v2"
            }
        
        except Exception as e:
            print(f"[WARN] V2 persona generation failed: {e}")
            print("[INFO] Falling back to V1 generation")
        
            # Fallback to existing v1 method
            return await self.generate_personas_from_template(
                template_data, gender, context, archetype_classification
            )


    async def generate_assess_mode_from_template_v2(
        self,
        template_data: dict
    ) -> str:
        """
        V2 IMPLEMENTATION: Uses PromptGeneratorV2 with PersonaInstanceV2.
        Safe to call - has fallback to v1 if fails.
        """
        try:
            from core.persona_generator_v2 import PersonaGeneratorV2
            from core.prompt_generator_v2 import PromptGeneratorV2
        
            # Generate persona
            persona_gen = PersonaGeneratorV2(self.client, self.model)
            persona = await persona_gen.generate_persona(
                template_data=template_data,
                mode="assess_mode"
            )
        
            # Generate prompt from persona
            prompt_gen = PromptGeneratorV2(self.client, self.model)
            system_prompt = await prompt_gen.generate_system_prompt(
                persona=persona,
                template_data=template_data
            )
        
            print(f"[V2] Generated assess mode prompt with {len(persona.detail_categories)} detail categories")
        
            return system_prompt
        
        except Exception as e:
            print(f"[WARN] V2 prompt generation failed: {e}")
            print("[INFO] Falling back to V1 generation")
        
            # Fallback to existing v1 method
            return await self.generate_assess_mode_from_template(template_data)

    """
    ADD THIS METHOD TO EnhancedScenarioGenerator CLASS in scenario_generator.py
    Add after _get_mock_template_data() method (around line 1400)
    """

    async def extract_scenario_info_v2(self, scenario_document: str) -> Dict[str, Any]:
        """
        V2 EXTRACTION: Enhanced multi-pass extraction system.
        Safe to call - has fallback to v1 if fails.
        """
        try:
            from core.scenario_extractor_v2 import ScenarioExtractorV2
        
            print("[V2 EXTRACTION] Starting enhanced extraction...")
        
            # Try V2 extraction
            extractor_v2 = ScenarioExtractorV2(self.client, self.model)
            template_data = await extractor_v2.extract_scenario_info(scenario_document)
        
            # Still run archetype classification (keep existing system)
            try:
                archetype_result = await self.archetype_classifier.classify_scenario(scenario_document, template_data)
            
                primary_archetype_str = str(archetype_result.primary_archetype).split(".")[-1] if archetype_result.primary_archetype else "HELP_SEEKING"
            
                template_data["archetype_classification"] = {
                "primary_archetype": primary_archetype_str,
                "confidence_score": archetype_result.confidence_score,
                "alternative_archetypes": archetype_result.alternative_archetypes,
                "reasoning": archetype_result.reasoning,
                "sub_type": archetype_result.sub_type
                }
                print(f"[V2] Classified as: {primary_archetype_str}")
            except Exception as e:
                print(f"[WARN] Archetype classification failed: {e}")
                template_data["archetype_classification"] = {
                "primary_archetype": "HELP_SEEKING",
                "confidence_score": 0.5,
                "alternative_archetypes": [],
                "reasoning": f"Classification failed: {str(e)}",
                "sub_type": None
                }
        
            # Inject archetype fields (keep existing system)
            self._inject_archetype_fields(template_data)
        
            print("[V2 EXTRACTION] Completed successfully")
            return template_data
        
        except Exception as e:
            print(f"[WARN] V2 extraction failed: {e}")
            print("[INFO] Falling back to V1 extraction")
        
            # Fallback to existing v1 method
            return await self.extract_scenario_info(scenario_document)
    
