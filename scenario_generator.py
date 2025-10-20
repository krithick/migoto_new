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
router = APIRouter(prefix="/scenario", tags=["Scenario Generation"])
api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
        
      
azure_openai_client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

print(f"🔍 Azure OpenAI Client initialized: {azure_openai_client is not None}")
print(f"🔑 API Key present: {bool(api_key)}")
print(f"🌐 Endpoint: {endpoint}")

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

# async def extract_text_from_docx(file_content):
#     """Extract text from .docx file content"""
#     try:
#         with io.BytesIO(file_content) as f:
#             doc = docx.Document(f)
#             text = ""
#             for para in doc.paragraphs:
#                 text += para.text + "\n"
#         return text.strip()
#     except Exception as e:
#         print(f"Error extracting text from docx: {str(e)}")
#         return None

async def extract_text_from_docx(file_content):
    """Enhanced DOCX extraction with better error handling and table support"""
    try:
        with io.BytesIO(file_content) as f:
            doc = docx.Document(f)
            text_parts = []
            
            print(f"DOCX Document has {len(doc.paragraphs)} paragraphs and {len(doc.tables)} tables")
            
            # Extract paragraphs with section markers
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    text_parts.append(f"PARAGRAPH_{i}: {para.text.strip()}")
            
            # Extract tables with better structure preservation
            for table_idx, table in enumerate(doc.tables):
                text_parts.append(f"\nTABLE_{table_idx}_START:")
                for row_idx, row in enumerate(table.rows):
                    row_text = []
                    for cell_idx, cell in enumerate(row.cells):
                        if cell.text.strip():
                            row_text.append(f"CELL_{cell_idx}: {cell.text.strip()}")
                    if row_text:
                        text_parts.append(f"ROW_{row_idx}: {' | '.join(row_text)}")
                text_parts.append(f"TABLE_{table_idx}_END\n")
            
            full_text = "\n".join(text_parts)
            print(f"Extracted {len(full_text)} characters from DOCX")
            print(f"First 500 characters: {full_text[:500]}...")
            
            # Check for key template sections
            key_sections = ["SECTION 1", "SECTION 2", "SECTION 3", "AI Trainer Role", "Success Metrics"]
            found_sections = [section for section in key_sections if section.lower() in full_text.lower()]
            print(f"Found template sections: {found_sections}")
            
            return full_text if full_text.strip() else None
            
    except Exception as e:
        print(f"DOCX extraction error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

# async def extract_text_from_docx_structured(file_content):
#     """Enhanced DOCX extraction that preserves template structure and key-value pairs"""
#     try:
#         with io.BytesIO(file_content) as f:
#             doc = docx.Document(f)
#             structured_data = {
#                 "sections": {},
#                 "tables": [],
#                 "key_value_pairs": {},
#                 "conversation_examples": []
#             }
            
#             current_section = "header"
            
#             # Extract paragraphs with section awareness
#             for para in doc.paragraphs:
#                 text = para.text.strip()
#                 if not text:
#                     continue
                
#                 # Detect section headers
#                 if text.startswith("SECTION"):
#                     current_section = text
#                     structured_data["sections"][current_section] = []
#                 elif current_section:
#                     structured_data["sections"].setdefault(current_section, []).append(text)
            
#             # Extract tables with structure preservation
#             for table_idx, table in enumerate(doc.tables):
#                 table_data = {
#                     "table_index": table_idx,
#                     "rows": [],
#                     "key_value_pairs": {}
#                 }
                
#                 for row_idx, row in enumerate(table.rows):
#                     row_data = []
#                     for cell in row.cells:
#                         cell_text = cell.text.strip()
#                         row_data.append(cell_text)
                    
#                     if len(row_data) >= 2 and row_data[0] and row_data[1]:
#                         # Extract key-value pairs from tables
#                         key = row_data[0].replace("**", "").strip()
#                         value = row_data[1].replace("**", "").strip()
#                         if key and value and len(value) > 2:
#                             table_data["key_value_pairs"][key] = value
#                             structured_data["key_value_pairs"][key] = value
                    
#                     table_data["rows"].append(row_data)
                
#                 structured_data["tables"].append(table_data)
            
#             # Extract conversation examples
#             full_text = "\n".join([para.text for para in doc.paragraphs])
            
#             # Look for conversation patterns
#             conversation_patterns = [
#                 r"Conversation Topic:\s*([^\n]+)",
#                 r"AI Colleague:\s*[\"']([^\"']+)[\"']",
#                 r"Correct Learner Response:\s*[\"']([^\"']+)[\"']",
#                 r"Incorrect Learner Response:\s*[\"']([^\"']+)[\"']",
#                 r"AI Trainer:\s*[\"']([^\"']+)[\"']"
#             ]
            
#             for pattern in conversation_patterns:
#                 matches = re.findall(pattern, full_text, re.IGNORECASE | re.DOTALL)
#                 if matches:
#                     structured_data["conversation_examples"].extend(matches)
            
#             return structured_data
            
#     except Exception as e:
#         print(f"Enhanced DOCX extraction error: {str(e)}")
#         return None

async def extract_text_from_pdf(file_content):
    """Extract text from PDF file content using pypdf"""
    try:
        with io.BytesIO(file_content) as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

# Pydantic Models
class PersonaDetails(BaseModel):
    name: str
    description: str
    persona_type: str
    gender: str
    age: int
    character_goal: str
    location: str
    persona_details: str
    situation: str
    context_type: str
    background_story: str
    full_persona: Optional[Dict[str, Any]] = None

class TemplateAnalysisResponse(BaseModel):
    general_info: Dict[str, Any]
    context_overview: Dict[str, Any]
    persona_definitions: Dict[str, Any]
    dialogue_flow: Dict[str, Any]
    knowledge_base: Dict[str, Any]
    variations_challenges: Dict[str, Any]
    success_metrics: Dict[str, Any]
    feedback_mechanism: Dict[str, Any]

class ScenarioResponse(BaseModel):
    learn_mode: str
    assess_mode: str
    try_mode: str
    scenario_title: str
    extracted_info: Optional[Dict[str, Any]] = None
    generated_persona: Optional[Dict[str, Any]] = None
    knowledge_base_id: Optional[str] = None  # 🔑 ADD THIS

class ScenarioListResponse(BaseModel):
    scenarios: List[Dict[str, Any]]
    total_count: int

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
        """Final clean template - fully dynamic, works for any scenario"""
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

---

## 🗣️ First Response
Wait for the learner to greet you ("hi", "hello").  
Then:
1. Greet them briefly.  
2. Immediately share your main **concern/situation**.  

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
            "background_story": "Detailed background story - extract or enhance from document"
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
                template_data["archetype_classification"] = {
                    "primary_archetype": archetype_result.primary_archetype,
                    "confidence_score": archetype_result.confidence_score,
                    "alternative_archetypes": archetype_result.alternative_archetypes,
                    "reasoning": archetype_result.reasoning,
                    "sub_type": archetype_result.sub_type
                }
                print(f"✅ Classified as: {archetype_result.primary_archetype} (confidence: {archetype_result.confidence_score})")
            except Exception as e:
                print(f"⚠️ Archetype classification failed: {e}")
                template_data["archetype_classification"] = {
                    "primary_archetype": "HELP_SEEKING",  # Default fallback
                    "confidence_score": 0.5,
                    "alternative_archetypes": [],
                    "reasoning": "Classification failed, using default",
                    "sub_type": None
                }
        
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
        """Generate Assessment Mode prompt using template data"""
        try:
            general_info = template_data.get('general_info', {})
            context_overview = template_data.get('context_overview', {})
            dialogue_flow = template_data.get('dialogue_flow', {})
            knowledge_base = template_data.get('knowledge_base', {})
            feedback = template_data.get('feedback_mechanism', {})
            bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
            
            # Ensure bot_persona is a dictionary
            if not isinstance(bot_persona, dict):
                bot_persona = {}
            
            formatted_template = self.assess_mode_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                bot_role=bot_persona.get('role', 'person seeking help'),
                bot_situation=bot_persona.get('character_goal', 'needs assistance'),
                trainer_role=template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {}).get('role', 'trainer'),
                user_interaction_type="seeking guidance" if "customer" in bot_persona.get('role', '').lower() else "learning",
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
                disrespectful_closing=feedback.get('disrespectful_closing', 'Your response doesn\'t seem to take this topic seriously.')
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

# API Endpoints

@router.post("/test-archetype-classification")
async def test_archetype_classification(
    scenario_document: str = Body(..., embed=True),
    db: Any = Depends(get_db)
):
    """
    Test endpoint: Classify scenario archetype without full template generation
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Quick extraction for classification
        template_data = await generator.extract_scenario_info(scenario_document)
        
        archetype_info = template_data.get("archetype_classification", {})
        
        return {
            "scenario_preview": scenario_document[:200] + "...",
            "archetype_classification": archetype_info,
            "scenario_title": template_data.get("context_overview", {}).get("scenario_title", "Unknown"),
            "domain": template_data.get("general_info", {}).get("domain", "Unknown"),
            "message": "Archetype classification completed"
        }
    except Exception as e:
        print(f"Error in test_archetype_classification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-scenario", response_model=TemplateAnalysisResponse)
async def analyze_scenario_endpoint(scenario_document: str = Body(..., embed=True)):
    """
    Step 1: Analyze raw scenario description and create comprehensive template structure.
    """
    try:
        # Initialize generator (replace None with your actual client)
        generator = EnhancedScenarioGenerator(azure_openai_client)
        template_data = await generator.extract_scenario_info(scenario_document)
        evaluation_metrics = await generator.extract_evaluation_metrics_from_template(scenario_document, template_data)
        template_data["evaluation_metrics"] = evaluation_metrics        
        return TemplateAnalysisResponse(
            general_info=template_data.get("general_info", {}),
            context_overview=template_data.get("context_overview", {}),
            persona_definitions=template_data.get("persona_definitions", {}),
            dialogue_flow=template_data.get("dialogue_flow", {}),
            knowledge_base=template_data.get("knowledge_base", {}),
            variations_challenges=template_data.get("variations_challenges", {}),
            success_metrics=template_data.get("success_metrics", {}),
            feedback_mechanism=template_data.get("feedback_mechanism", {})
        )
    except Exception as e:
        print(f"Error in analyze_scenario_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit-template-section")
async def edit_template_section(
    section_name: str = Body(...),
    section_data: Dict[str, Any] = Body(...),
    current_template: Dict[str, Any] = Body(...)
):
    """
    Step 2: Edit specific sections of the template.
    """
    try:
        # Update the specific section in the template
        if section_name in current_template:
            current_template[section_name].update(section_data)
        else:
            current_template[section_name] = section_data
        
        return {
            "message": f"Section '{section_name}' updated successfully",
            "updated_template": current_template,
            "section_preview": current_template.get(section_name, {})
        }
    except Exception as e:
        print(f"Error in edit_template_section: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-remove-points")
async def add_remove_points(
    section: str = Body(...),
    subsection: str = Body(...),
    action: str = Body(...),
    point_data: Dict[str, Any] = Body(...),
    current_template: Dict[str, Any] = Body(...)
):
    """
    Step 2.1: Add, remove, or edit specific points in knowledge base or dialogue flow.
    """
    try:
        if section not in current_template:
            current_template[section] = {}
        
        if subsection not in current_template[section]:
            current_template[section][subsection] = []
        
        points_list = current_template[section][subsection]
        
        if action == "add":
            new_point = point_data.get("content", "")
            if new_point:
                points_list.append(new_point)
        
        elif action == "remove":
            index = point_data.get("index", -1)
            if 0 <= index < len(points_list):
                points_list.pop(index)
            else:
                raise HTTPException(status_code=400, detail="Invalid index")
        
        elif action == "edit":
            index = point_data.get("index", -1)
            new_content = point_data.get("content", "")
            if 0 <= index < len(points_list) and new_content:
                points_list[index] = new_content
            else:
                raise HTTPException(status_code=400, detail="Invalid index or content")
        
        current_template[section][subsection] = points_list
        
        return {
            "message": f"Successfully {action}ed point in {section}.{subsection}",
            "updated_points": points_list,
            "updated_template": current_template
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in add_remove_points: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-final-prompts", response_model=ScenarioResponse)
async def generate_final_prompts(template_data: Dict[str, Any] = Body(...)):
    """
    Step 3: Generate final customized prompts using the edited template data.
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Generate personas from template
        personas = await generator.generate_personas_from_template(template_data)
        
        # Generate all three prompts using template data
        learn_mode_prompt = await generator.generate_learn_mode_from_template(template_data)
        assess_mode_prompt = await generator.generate_assess_mode_from_template(template_data)
        try_mode_prompt = await generator.generate_try_mode_from_template(template_data)
        
        # Apply personas to prompts
        # learn_mode_prompt = generator.insert_persona(learn_mode_prompt, personas.get("learn_mode_expert", {}))
        # assess_mode_prompt = generator.insert_persona(assess_mode_prompt, personas.get("assess_mode_character", {}))
        # try_mode_prompt = generator.insert_persona(try_mode_prompt, personas.get("assess_mode_character", {}))
        
        # Apply language instructions
        # language_data = template_data.get("general_info", {})
        # learn_mode_prompt = generator.insert_language_instructions(learn_mode_prompt, language_data)
        # assess_mode_prompt = generator.insert_language_instructions(assess_mode_prompt, language_data)
        # try_mode_prompt = generator.insert_language_instructions(try_mode_prompt, language_data)
        template_id = template_data.get("template_id")  # Frontend should pass this
        knowledge_base_id = None
        if template_id:
            template_record = await db.templates.find_one({"id": template_id})
            if template_record:
                knowledge_base_id = template_record.get("knowledge_base_id")                
        return ScenarioResponse(
            learn_mode=learn_mode_prompt,
            try_mode=assess_mode_prompt,
            assess_mode=try_mode_prompt,
            scenario_title=template_data.get("context_overview", {}).get("scenario_title", "Training Scenario"),
            extracted_info=template_data,
            generated_persona=personas,
            knowledge_base_id=knowledge_base_id
        )
    except Exception as e:
        print(f"Error in generate_final_prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-generate-prompts", response_model=ScenarioResponse)
async def quick_generate_prompts(scenario_document: str = Body(..., embed=True)):
    """
    Quick Generation: All steps in one API call.
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Step 1: Analyze scenario to template
        template_data = await generator.extract_scenario_info(scenario_document)
        
        # Step 3: Generate final prompts
        personas = await generator.generate_personas_from_template(template_data)
        
        learn_mode_prompt = await generator.generate_learn_mode_from_template(template_data)
        assess_mode_prompt = await generator.generate_assess_mode_from_template(template_data)
        try_mode_prompt = await generator.generate_try_mode_from_template(template_data)
        
        # Apply personas and language instructions
        learn_mode_prompt = generator.insert_persona(learn_mode_prompt, personas.get("learn_mode_expert", {}))
        assess_mode_prompt = generator.insert_persona(assess_mode_prompt, personas.get("assess_mode_character", {}))
        try_mode_prompt = generator.insert_persona(try_mode_prompt, personas.get("assess_mode_character", {}))
        
        language_data = template_data.get("general_info", {})
        learn_mode_prompt = generator.insert_language_instructions(learn_mode_prompt, language_data)
        assess_mode_prompt = generator.insert_language_instructions(assess_mode_prompt, language_data)
        try_mode_prompt = generator.insert_language_instructions(try_mode_prompt, language_data)
        
        return ScenarioResponse(
            learn_mode=learn_mode_prompt,
            assess_mode=assess_mode_prompt,
            try_mode=try_mode_prompt,
            scenario_title=template_data.get("context_overview", {}).get("scenario_title", "Training Scenario"),
            extracted_info=template_data,
            generated_persona=personas
        )
    except Exception as e:
        print(f"Error in quick_generate_prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-prompts", response_model=ScenarioResponse)
async def regenerate_prompts(template_data: Dict[str, Any] = Body(...)):
    """
    Regenerate prompts from existing template data after user edits.
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Use existing personas or generate new ones if needed
        personas = template_data.get("generated_personas")
        if not personas:
            personas = await generator.generate_personas_from_template(template_data)
        
        # Generate all three prompts using updated template data
        learn_mode_prompt = await generator.generate_learn_mode_from_template(template_data)
        assess_mode_prompt = await generator.generate_assess_mode_from_template(template_data)
        try_mode_prompt = await generator.generate_try_mode_from_template(template_data)
        
        # Apply personas and language instructions
        learn_mode_prompt = generator.insert_persona(learn_mode_prompt, personas.get("learn_mode_expert", {}))
        assess_mode_prompt = generator.insert_persona(assess_mode_prompt, personas.get("assess_mode_character", {}))
        try_mode_prompt = generator.insert_persona(try_mode_prompt, personas.get("assess_mode_character", {}))
        
        language_data = template_data.get("general_info", {})
        learn_mode_prompt = generator.insert_language_instructions(learn_mode_prompt, language_data)
        assess_mode_prompt = generator.insert_language_instructions(assess_mode_prompt, language_data)
        try_mode_prompt = generator.insert_language_instructions(try_mode_prompt, language_data)
        
        return ScenarioResponse(
            learn_mode=learn_mode_prompt,
            assess_mode=assess_mode_prompt,
            try_mode=try_mode_prompt,
            scenario_title=template_data.get("context_overview", {}).get("scenario_title", "Training Scenario"),
            extracted_info=template_data,
            generated_persona=personas
        )
    except Exception as e:
        print(f"Error in regenerate_prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-template-to-db")
async def save_template_to_db(
    template_data: Dict[str, Any] = Body(...),
    template_name: str = Body(...),
    template_id: Optional[str] = Body(default=None)
):
    """Save template data to database"""
    try:
        template_record = {
            "id": template_id or str(uuid.uuid4()),
            "name": template_name,
            "template_data": template_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to your database
        db.templates.insert_one(template_record)  # or update if template_id exists
        
        return {
            "message": "Template saved to database successfully",
            "template_id": template_record["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def convert_objectid(document):
    """Convert ObjectId to str in a MongoDB document"""
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document
@router.get("/load-template-from-db/{template_id}")
async def load_template_from_db(template_id: str):
    """Load template data from database"""
    try:
        template = await db.templates.find_one({"id": template_id})
        print(template,"template")
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return convert_objectid(template)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-templates-from-db")
async def list_templates_from_db():
    try:
        cursor = db.templates.find({}, {"_id": 0})
        templates = await cursor.to_list(length=100)
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put("/update-template-in-db/{template_id}")
async def update_template_in_db(
    template_id: str,
    template_data: Dict[str, Any] = Body(...),
    template_name: str = Body(...)
):
    """Update existing template in database"""
    try:
        # Check if template exists
        existing_template = db.templates.find_one({"id": template_id})
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update template
        updated_template = {
            "name": template_name,
            "template_data": template_data,
            "updated_at": datetime.now().isoformat()
        }
        
        db.templates.update_one(
            {"id": template_id}, 
            {"$set": updated_template}
        )
        
        return {
            "message": "Template updated successfully",
            "template_id": template_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-template-from-db/{template_id}")
async def delete_template_from_db(template_id: str):
    """Delete template from database"""
    try:
        # Check if template exists
        existing_template = db.templates.find_one({"id": template_id})
        if not existing_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Delete template
        result = db.templates.delete_one({"id": template_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "message": "Template deleted successfully",
            "deleted_template": {
                "id": template_id,
                "name": existing_template.get("name")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Additional utility endpoints

@router.post("/generate-personas-from-template")
async def generate_personas_from_template_endpoint(template_data: Dict[str, Any] = Body(...)):
    """
    Generate detailed personas based on template persona definitions.
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        personas = await generator.generate_personas_from_template(template_data)
        
        return {
            "learn_mode_expert": personas.get("learn_mode_expert", {}),
            "assess_mode_character": personas.get("assess_mode_character", {}),
            "scenario_info": {
                "title": template_data.get("context_overview", {}).get("scenario_title", "Training Scenario"),
                "domain": template_data.get("general_info", {}).get("domain", "general"),
                "purpose": template_data.get("context_overview", {}).get("purpose_of_scenario", "learning scenario")
            }
        }
    except Exception as e:
        print(f"Error in generate_personas_from_template_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file-to-template")
async def file_to_template(file: UploadFile = File(...)):
    try:
        print(f"Processing file: {file.filename}")
        print(f"Content type: {file.content_type}")
        
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        # Process based on file type
        scenario_text = ""
        extraction_method = "unknown"
        
        if file.filename.lower().endswith('.txt'):
            scenario_text = content.decode('utf-8')
            extraction_method = "text"
            
        elif file.filename.lower().endswith(('.doc', '.docx')):
            scenario_text = await extract_text_from_docx(content)
            extraction_method = "docx"
            
            if scenario_text is None:
                # Try alternative extraction
                print("Primary DOCX extraction failed, trying alternative...")
                try:
                    scenario_text = content.decode('utf-8', errors='ignore')
                    extraction_method = "fallback_text"
                except:
                    raise HTTPException(400, "Could not extract text from DOCX file")
        
        # Validate extraction
        if not scenario_text or len(scenario_text.strip()) < 50:
            raise HTTPException(400, f"Insufficient content extracted. Got {len(scenario_text)} characters")
        
        print(f"Successfully extracted {len(scenario_text)} characters using {extraction_method}")
        print(f"Content preview: {scenario_text[:300]}...")
        
        # Process with LLM
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Check if client is properly initialized
        if generator.client is None:
            print("WARNING: LLM client not initialized, using enhanced mock data")
            template_data = generator._get_enhanced_mock_template_data(scenario_text)
        else:
            template_data = await generator.extract_scenario_info(scenario_text)
        
        return template_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File processing error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        raise HTTPException(500, f"File processing failed: {str(e)}")
@router.get("/template-schema")
async def get_template_schema():
    """
    Get the complete template schema for UI builders.
    """
    try:
        return {
            "general_info": {
                "domain": "string - Healthcare/Banking/Sales/Education/etc.",
                "purpose_of_ai_bot": "string - Trainer/Customer/Student/etc.", 
                "target_audience": "string - Employees/General Public/etc.",
                "preferred_language": "string - English/Spanish/etc."
            },
            "context_overview": {
                "scenario_title": "string - Descriptive title",
                "learn_mode_description": "string - What happens in learn mode",
                "assess_mode_description": "string - What happens in assessment mode",
                "try_mode_description": "string - What happens in try mode", 
                "purpose_of_scenario": "string - Learning objectives"
            },
            "knowledge_base": {
                "dos": "array - List of best practices",
                "donts": "array - List of things to avoid",
                "key_facts": "array - Important facts about the domain",
                "conversation_topics": "array - Topics to explore in conversation"
            },
            "feedback_mechanism": {
                "positive_closing": "string - Positive ending message",
                "negative_closing": "string - Negative ending message",
                "neutral_closing": "string - Neutral ending message"
            }
        }
    except Exception as e:
        print(f"Error in get_template_schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ADD these imports at the top of your existing file
from core.document_processor import DocumentProcessor
from core.azure_search_manager import AzureVectorSearchManager
from core.user import get_current_user
from models.user_models import UserDB
from database import get_db

# newwww
@router.post("/analyze-template-with-docs")
async def analyze_template_with_docs(
    template_file: UploadFile = File(...),
    supporting_docs: List[UploadFile] = File(...),
    template_name: str = Form(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Step 1: Analyze template + process docs, return editable template"""
    try:
        # 1. Process template file
        content = await template_file.read()
        
        if template_file.filename.lower().endswith(('.doc', '.docx')):
            scenario_text = await extract_text_from_docx(content)
            
            # Fallback extraction if primary method fails
            if not scenario_text or len(scenario_text.strip()) < 100:
                print("Primary DOCX extraction failed, trying alternative methods...")
                try:
                    # Try simple text extraction
                    scenario_text = content.decode('utf-8', errors='ignore')
                    print(f"Fallback text extraction got {len(scenario_text)} characters")
                except Exception as e2:
                    print(f"Fallback extraction also failed: {e2}")
                    raise HTTPException(400, "Could not extract text from Word document")
                    
        elif template_file.filename.lower().endswith('.pdf'):
            scenario_text = await extract_text_from_pdf(content)
        else:
            scenario_text = content.decode('utf-8')
            
        # Validate extraction before processing
        if not scenario_text or len(scenario_text.strip()) < 50:
            raise HTTPException(400, f"Insufficient content extracted from document. Got {len(scenario_text) if scenario_text else 0} characters")
            
        print(f"Successfully extracted {len(scenario_text)} characters for processing")
        print(f"Content preview: {scenario_text[:300]}...")
            
        # 2. Analyze template to get editable structure
        generator = EnhancedScenarioGenerator(azure_openai_client)
        template_data = await generator.extract_scenario_info(scenario_text)
        evaluation_metrics = await generator.extract_evaluation_metrics_from_template(scenario_text, template_data)
        template_data["evaluation_metrics"] = evaluation_metrics
        # 3. Process supporting documents → Create knowledge base
        knowledge_base_id = f"kb_{str(uuid4())}"
        supporting_docs_metadata = []
        
        if supporting_docs and len(supporting_docs) > 0:
            supporting_docs_metadata = await process_and_index_documents(
                supporting_docs, knowledge_base_id, db
            )
        
        # 4. Store template for editing (NO prompts yet)
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "template_data": template_data,  # EDITABLE
            # "evaluation_metrics": evaluation_metrics,
            "knowledge_base_id": knowledge_base_id if supporting_docs_metadata else None,
            "supporting_documents": len(supporting_docs_metadata),
            "status": "ready_for_editing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        await db.templates.insert_one(template_record)
        
        # 5. Create knowledge base record
        if supporting_docs_metadata:
            knowledge_base_record = {
                "_id": knowledge_base_id,
                "template_id": template_record["id"],
                "scenario_title": template_data.get("context_overview", {}).get("scenario_title", template_name),
                "supporting_documents": supporting_docs_metadata,
                "total_documents": len(supporting_docs_metadata),
                "total_chunks": sum(doc.get("chunk_count", 0) for doc in supporting_docs_metadata),
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "fact_checking_enabled": True
            }
            await db.knowledge_bases.insert_one(knowledge_base_record)
        
        return {
            "template_id": template_record["id"],
            "template_data": template_data,  # For frontend editing
            # "evaluation_metrics": evaluation_metrics,
            "knowledge_base_id": knowledge_base_id if supporting_docs_metadata else None,
            "supporting_documents_count": len(supporting_docs_metadata),
            "message": "Template analyzed and ready for editing",
            "next_step": "Edit template sections, then generate prompts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# newww
# ADD this helper function
async def process_and_index_documents(supporting_docs: List[UploadFile], knowledge_base_id: str, db: Any) -> List[dict]:
    """Process documents and index in Azure Search"""
    vector_search = AzureVectorSearchManager()
    
    # Create index if it doesn't exist
    try:
        from core.azure_search_setup import AzureSearchIndexManager
        index_manager = AzureSearchIndexManager()
        
        # Check if index exists, create if not
        if not await index_manager.index_exists():
            print("Creating Azure Search index...")
            await index_manager.create_knowledge_base_index()
            print("✅ Index created successfully")
    except Exception as e:
        print(f"⚠️  Index creation warning: {e}")
        
    documents_metadata = []
    
    from openai import AsyncAzureOpenAI
    import os
    
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("api_key"),
        azure_endpoint=os.getenv("endpoint"),
        api_version=os.getenv("api_version")
    )
    
    document_processor = DocumentProcessor(openai_client, db)
    vector_search = AzureVectorSearchManager()
    
    for doc_file in supporting_docs:
        try:
            content = await doc_file.read()
            doc_id = str(uuid4())
            
            # Process document (extract text, create chunks, embeddings)
            chunks = await document_processor.process_document(doc_id, content, doc_file.filename)
            
            # Set knowledge base for chunks
            for chunk in chunks:
                chunk.knowledge_base_id = knowledge_base_id
            
            # Index in Azure Search
            await vector_search.index_document_chunks(chunks, knowledge_base_id)
            
            # Store metadata
            # doc_metadata = {
            #     "_id": doc_id,
            #     "knowledge_base_id": knowledge_base_id,
            #     "filename": doc_file.filename,
            #     "file_size": len(content),
            #     "chunk_count": len(chunks),
            #     "processed_at": datetime.now().isoformat()
            # }
            doc_metadata = {
                "_id": doc_id,
                "knowledge_base_id": knowledge_base_id,
                "filename": doc_file.filename,
                "original_filename": doc_file.filename,
                "file_size": len(content),
                "content_type": doc_file.content_type,
                "processing_status": "completed",
                "chunk_count": len(chunks),
                "processed_at": datetime.now().isoformat(),
                "indexed_in_vector_search": True
            }            
            await db.supporting_documents.insert_one(doc_metadata)
            documents_metadata.append(doc_metadata)
            
        except Exception as e:
            print(f"Error processing {doc_file.filename}: {e}")
    
    return documents_metadata

@router.put("/template/{template_id}/evaluation-metrics")
async def update_evaluation_metrics(
    template_id: str,
    evaluation_metrics: Dict[str, Any] = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Edit evaluation metrics for a template"""
    try:
        # Check if template exists
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update evaluation metrics
        await db.templates.update_one(
            {"id": template_id},
            {"$set": {
                "evaluation_metrics": evaluation_metrics,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        return {
            "message": "Evaluation metrics updated successfully",
            "template_id": template_id,
            "updated_metrics": evaluation_metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template/{template_id}/evaluation-metrics")
async def get_evaluation_metrics(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get evaluation metrics for a template"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "template_id": template_id,
            "evaluation_metrics": template.get("evaluation_metrics", {}),
            "template_name": template.get("name", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/generate-personas")
async def generate_personas(
    template_id: str = Body(...),
    persona_type: str = Body(..., description="learn_mode_expert or assess_mode_character"),
    gender: str = Body(default="",description="Specify Gender if needed"),
    prompt: str = Body(default="",description="Specify context if needed"),
    count: int = Body(default=1, description="Number of personas to generate"),
    db: Any = Depends(get_db)
):
    """
    Simple API: Generate personas from template ID
    """
    try:
        # Get template data from database
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        
        # Generate personas using existing logic
        generator = EnhancedScenarioGenerator(azure_openai_client)
        generated_personas = await generator.generate_personas_from_template(template_data,gender,prompt)
        
        # Return requested persona type
        if persona_type in generated_personas:
            persona = generated_personas[persona_type]
            # If count > 1, generate variations (for future use)
            personas = [persona] * count  # For now, return same persona
            
            return {
                "template_id": template_id,
                "persona_type": persona_type,
                "count": count,
                "personas": personas
            }
        else:
            raise HTTPException(status_code=400, detail=f"Persona type '{persona_type}' not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-template-with-optional-docs")
async def analyze_template_with_optional_docs(
    template_file: UploadFile = File(...),
    supporting_docs: List[UploadFile] = File(default=[]),  # NOW OPTIONAL
    template_name: str = Form(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Updated version: Template file required, supporting docs optional
    """
    try:
        # 1. Process template file (same as before)
        content = await template_file.read()
        
        if template_file.filename.lower().endswith(('.doc', '.docx')):
            scenario_text = await extract_text_from_docx(content)
        elif template_file.filename.lower().endswith('.pdf'):
            scenario_text = await extract_text_from_pdf(content)
        else:
            scenario_text = content.decode('utf-8')
            
        # 2. Analyze template
        generator = EnhancedScenarioGenerator(azure_openai_client)
        template_data = await generator.extract_scenario_info(scenario_text)
        evaluation_metrics = await generator.extract_evaluation_metrics_from_template(scenario_text, template_data)
        template_data["evaluation_metrics"] = evaluation_metrics
        
        # 3. Process supporting documents ONLY if provided
        knowledge_base_id = None
        supporting_docs_metadata = []
        
        if supporting_docs and len(supporting_docs) > 0:
            knowledge_base_id = f"kb_{str(uuid4())}"
            supporting_docs_metadata = await process_and_index_documents(
                supporting_docs, knowledge_base_id, db
            )
        
        # 4. Save template (same structure for both flows)
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "template_data": template_data,
            "knowledge_base_id": knowledge_base_id if supporting_docs_metadata else None,
            "supporting_documents": len(supporting_docs_metadata),
            "status": "ready_for_editing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": str(current_user.id),
            "source": "file_upload"
        }
        
        await db.templates.insert_one(template_record)
        
        # 5. Create knowledge base if docs provided
        if supporting_docs_metadata:
            knowledge_base_record = {
                "_id": knowledge_base_id,
                "template_id": template_record["id"],
                "scenario_title": template_data.get("context_overview", {}).get("scenario_title", template_name),
                "supporting_documents": supporting_docs_metadata,
                "total_documents": len(supporting_docs_metadata),
                "total_chunks": sum(doc.get("chunk_count", 0) for doc in supporting_docs_metadata),
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "fact_checking_enabled": True
            }
            await db.knowledge_bases.insert_one(knowledge_base_record)
        
        return {
            "template_id": template_record["id"],
            "template_data": template_data,
            "knowledge_base_id": knowledge_base_id,
            "supporting_documents_count": len(supporting_docs_metadata),
            "has_supporting_docs": len(supporting_docs_metadata) > 0,
            "fact_checking_enabled": len(supporting_docs_metadata) > 0,
            "message": "Template analyzed and ready for editing",
            "next_step": "Edit template sections, then generate prompts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
@router.post("/analyze-scenario-enhanced")
async def analyze_scenario_enhanced(
    scenario_document: str = Form(...),
    template_name: str = Form(...),
    supporting_docs: List[UploadFile] = File(default=[]),  # OPTIONAL now
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Enhanced analyze-scenario: Creates template + optionally processes documents
    - scenario_document: Text description of the scenario
    - template_name: Name for the template
    - supporting_docs: OPTIONAL supporting documents
    """
    try:
        # 1. Analyze scenario text to get editable template structure
        generator = EnhancedScenarioGenerator(azure_openai_client)
        template_data = await generator.extract_scenario_info(scenario_document)
        
        # Add evaluation metrics
        evaluation_metrics = await generator.extract_evaluation_metrics_from_template(scenario_document, template_data)
        template_data["evaluation_metrics"] = evaluation_metrics
        
        # 2. Process supporting documents if provided (OPTIONAL)
        knowledge_base_id = None
        supporting_docs_metadata = []
        
        if supporting_docs and len(supporting_docs) > 0:
            knowledge_base_id = f"kb_{str(uuid4())}"
            supporting_docs_metadata = await process_and_index_documents(
                supporting_docs, knowledge_base_id, db
            )
        
        # 3. Create template record (same structure as analyze-template-with-docs)
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "template_data": template_data,  # EDITABLE template data
            "knowledge_base_id": knowledge_base_id if supporting_docs_metadata else None,
            "supporting_documents": len(supporting_docs_metadata),
            "status": "ready_for_editing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "created_by": str(current_user.id),
            "source": "text_analysis"  # vs "file_upload" for template files
        }
        
        await db.templates.insert_one(template_record)
        
        # 4. Create knowledge base record if documents were provided
        if supporting_docs_metadata:
            knowledge_base_record = {
                "_id": knowledge_base_id,
                "template_id": template_record["id"],
                "scenario_title": template_data.get("context_overview", {}).get("scenario_title", template_name),
                "supporting_documents": supporting_docs_metadata,
                "total_documents": len(supporting_docs_metadata),
                "total_chunks": sum(doc.get("chunk_count", 0) for doc in supporting_docs_metadata),
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "fact_checking_enabled": True
            }
            await db.knowledge_bases.insert_one(knowledge_base_record)
        
        return {
            "template_id": template_record["id"],
            "template_data": template_data,  # For frontend editing
            "knowledge_base_id": knowledge_base_id,
            "supporting_documents_count": len(supporting_docs_metadata),
            "has_supporting_docs": len(supporting_docs_metadata) > 0,
            "fact_checking_enabled": len(supporting_docs_metadata) > 0,
            "message": "Scenario analyzed and template created successfully",
            "next_step": "Edit template sections, then generate prompts"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/scenarios/{scenario_id}/template-data")
async def get_scenario_template_data(
    scenario_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get template data for a scenario"""
    try:
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get template from template_id
        template_id = scenario.get("template_id")
        if not template_id:
            raise HTTPException(status_code=404, detail="No template linked to this scenario")
        
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        knowledge_base_id = template.get("knowledge_base_id")
        
        return {
            "scenario_id": scenario_id,
            "template_id": template_id,
            "scenario_title": scenario.get("title", ""),
            "template_data": template_data,
            "knowledge_base_id": knowledge_base_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/scenarios-editor/{scenario_id}/template-data")
async def update_scenario_template_data(
    scenario_id: str,
    request: Dict[str, Any] = Body(...),  # Accept raw dict instead of Pydantic model
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Update template data for a scenario (updates the linked template)"""
    try:
        print('test')
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Check permissions (similar to your existing scenario update logic)
        if current_user.role == UserRole.ADMIN:
            if scenario.get("created_by") != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized")
        elif current_user.role not in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get template_id
        template_id = scenario.get("template_id")
        if not template_id:
            raise HTTPException(status_code=404, detail="No template linked to this scenario")
        
        # Extract template_data from request (in case it's nested)
        template_data = request
        if "template_data" in request:
            template_data = request["template_data"]
        
        # Update the template document (not the scenario)
        await db.templates.update_one(
            {"id": template_id},
            {"$set": {
                "template_data": template_data,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        return {
            "message": "Template data updated successfully",
            "scenario_id": scenario_id,
            "template_id": template_id,
            "updated_template": template_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/{scenario_id}/regenerate")
async def regenerate_scenario_from_template(
    scenario_id: str,
    regenerate_options: Dict[str, Any] = Body(default={
        "modes_to_regenerate": ["learn_mode", "assess_mode", "try_mode"],
        "regenerate_personas": True
    }),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Regenerate scenario prompts from linked template data"""
    try:
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Check permissions
        if current_user.role == UserRole.ADMIN:
            if scenario.get("created_by") != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized")
        elif current_user.role not in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get template data from linked template
        template_id = scenario.get("template_id")
        if not template_id:
            raise HTTPException(status_code=400, detail="No template linked to this scenario")
        
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Linked template not found")
        
        # DEBUG: Log template fetch
        print(f"🔍 Regenerate: Fetched template {template_id}")
        print(f"📅 Template last updated: {template.get('updated_at')}")
        
        template_data = template.get("template_data")
        if not template_data:
            raise HTTPException(status_code=400, detail="No template data found")
        
        # DEBUG: Log template data preview
        print(f"📝 Template data keys: {list(template_data.keys())}")
        print(f"📋 Scenario title from template: {template_data.get('context_overview', {}).get('scenario_title', 'N/A')}")
        
        # Initialize generator
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Regenerate personas if requested
        personas = None
        if regenerate_options.get("regenerate_personas", True):
            personas = await generator.generate_personas_from_template(template_data)
        else:
            # Try to get existing personas (this might not exist in current schema)
            personas = scenario.get("generated_persona", {})
        
        # Generate prompts for requested modes
        modes_to_regenerate = regenerate_options.get("modes_to_regenerate", ["learn_mode", "assess_mode", "try_mode"])
        generated_prompts = {}
        
        if "learn_mode" in modes_to_regenerate:
            learn_prompt = await generator.generate_learn_mode_from_template(template_data)
            # learn_prompt = generator.insert_persona(learn_prompt, personas.get("learn_mode_expert", {}))
            # learn_prompt = generator.insert_language_instructions(learn_prompt, template_data.get("general_info", {}))
            generated_prompts["learn_mode"] = learn_prompt
        
        if "assess_mode" in modes_to_regenerate:
            assess_prompt = await generator.generate_assess_mode_from_template(template_data)
            # assess_prompt = generator.insert_persona(assess_prompt, personas.get("assess_mode_character", {}))
            # assess_prompt = generator.insert_language_instructions(assess_prompt, template_data.get("general_info", {}))
            generated_prompts["assess_mode"] = assess_prompt
        
        if "try_mode" in modes_to_regenerate:
            try_prompt = await generator.generate_try_mode_from_template(template_data)
            # try_prompt = generator.insert_persona(try_prompt, personas.get("assess_mode_character", {}))
            # try_prompt = generator.insert_language_instructions(try_prompt, template_data.get("general_info", {}))
            generated_prompts["try_mode"] = try_prompt
        

        
        update_data = {
            "updated_at": datetime.now()
        }
        
        # Store generated prompts in scenario AND update avatar_interaction documents
        print(f"🔍 DEBUG: Scenario modes to regenerate: {modes_to_regenerate}")
        print(f"🔍 DEBUG: Scenario learn_mode exists: {scenario.get('learn_mode') is not None}")
        print(f"🔍 DEBUG: Scenario assess_mode exists: {scenario.get('assess_mode') is not None}")
        print(f"🔍 DEBUG: Scenario try_mode exists: {scenario.get('try_mode') is not None}")
        
        if "learn_mode" in generated_prompts and scenario.get("learn_mode"):
            update_data["learn_mode.prompt"] = generated_prompts["learn_mode"]
            avatar_interaction_id = scenario.get("learn_mode", {}).get("avatar_interaction")
            print(f"🔍 DEBUG: Learn mode avatar_interaction: {avatar_interaction_id}")
            if not avatar_interaction_id:
                raise HTTPException(status_code=400, detail=f"Learn mode avatar_interaction is missing. Scenario learn_mode data: {scenario.get('learn_mode')}")
            try:
                result = await db.avatar_interactions.update_one(
                    {"_id": str(avatar_interaction_id)},
                    {"$set": {"system_prompt": generated_prompts["learn_mode"], "updated_at": datetime.now()}}
                )
                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail=f"Learn mode avatar_interaction {avatar_interaction_id} not found")
                print(f"✅ Learn mode avatar_interaction updated: matched={result.matched_count}, modified={result.modified_count}")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update learn mode avatar_interaction: {str(e)}")
        
        if "assess_mode" in generated_prompts and scenario.get("assess_mode"):
            update_data["assess_mode.prompt"] = generated_prompts["assess_mode"]
            avatar_interaction_id = scenario.get("assess_mode", {}).get("avatar_interaction")
            print(f"🔍 DEBUG: Assess mode avatar_interaction: {avatar_interaction_id}")
            if not avatar_interaction_id:
                raise HTTPException(status_code=400, detail=f"Assess mode avatar_interaction is missing. Scenario assess_mode data: {scenario.get('assess_mode')}")
            try:
                result = await db.avatar_interactions.update_one(
                    {"_id": str(avatar_interaction_id)},
                    {"$set": {"system_prompt": generated_prompts["assess_mode"], "updated_at": datetime.now()}}
                )
                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail=f"Assess mode avatar_interaction {avatar_interaction_id} not found")
                print(f"✅ Assess mode avatar_interaction updated: matched={result.matched_count}, modified={result.modified_count}")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update assess mode avatar_interaction: {str(e)}")
        
        if "try_mode" in generated_prompts and scenario.get("try_mode"):
            update_data["try_mode.prompt"] = generated_prompts["try_mode"]
            avatar_interaction_id = scenario.get("try_mode", {}).get("avatar_interaction")
            print(f"🔍 DEBUG: Try mode avatar_interaction: {avatar_interaction_id}")
            if not avatar_interaction_id:
                raise HTTPException(status_code=400, detail=f"Try mode avatar_interaction is missing. Scenario try_mode data: {scenario.get('try_mode')}")
            try:
                result = await db.avatar_interactions.update_one(
                    {"_id": str(avatar_interaction_id)},
                    {"$set": {"system_prompt": generated_prompts["try_mode"], "updated_at": datetime.now()}}
                )
                if result.matched_count == 0:
                    raise HTTPException(status_code=404, detail=f"Try mode avatar_interaction {avatar_interaction_id} not found")
                print(f"✅ Try mode avatar_interaction updated: matched={result.matched_count}, modified={result.modified_count}")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update try mode avatar_interaction: {str(e)}")
        
        await db.scenarios.update_one(
            {"_id": scenario_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Scenario regenerated successfully",
            "scenario_id": scenario_id,
            "template_id": template_id,
            "regenerated_modes": modes_to_regenerate,
            "generated_prompts": generated_prompts,
            "generated_personas": personas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/scenarios/{scenario_id}/knowledge-base")
async def manage_scenario_knowledge_base(
    scenario_id: str,
    kb_action: Dict[str, Any] = Body(...),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Link, unlink, or create knowledge base for scenario"""
    try:
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Check permissions
        if current_user.role == UserRole.ADMIN:
            if scenario.get("created_by") != str(current_user.id):
                raise HTTPException(status_code=403, detail="Not authorized")
        elif current_user.role not in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        action = kb_action.get("action")  # "link", "unlink", "create"
        knowledge_base_id = kb_action.get("knowledge_base_id")
        
        if action == "link":
            # Link existing knowledge base
            if not knowledge_base_id:
                raise HTTPException(status_code=400, detail="knowledge_base_id required for link action")
            
            # Verify KB exists
            kb = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
            if not kb:
                raise HTTPException(status_code=404, detail="Knowledge base not found")
            
            await db.scenarios.update_one(
                {"_id": scenario_id},
                {"$set": {
                    "knowledge_base_id": knowledge_base_id,
                    "fact_checking_enabled": True,
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            return {
                "message": "Knowledge base linked successfully",
                "scenario_id": scenario_id,
                "knowledge_base_id": knowledge_base_id,
                "action": "linked"
            }
        
        elif action == "unlink":
            # Unlink knowledge base (but don't delete it)
            await db.scenarios.update_one(
                {"_id": scenario_id},
                {"$unset": {
                    "knowledge_base_id": "",
                    "fact_checking_enabled": ""
                },
                "$set": {
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            return {
                "message": "Knowledge base unlinked successfully",
                "scenario_id": scenario_id,
                "action": "unlinked"
            }
        
        elif action == "create":
            # Create new knowledge base for this scenario
            new_kb_id = f"kb_{scenario_id}_{str(uuid4())[:8]}"
            
            # Create empty knowledge base record
            kb_record = {
                "_id": new_kb_id,
                "scenario_id": scenario_id,
                "scenario_title": scenario.get("title", "Unknown Scenario"),
                "supporting_documents": [],
                "total_documents": 0,
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "fact_checking_enabled": False  # Will be enabled when docs are added
            }
            
            await db.knowledge_bases.insert_one(kb_record)
            
            # Link to scenario
            await db.scenarios.update_one(
                {"_id": scenario_id},
                {"$set": {
                    "knowledge_base_id": new_kb_id,
                    "fact_checking_enabled": False,  # Will be enabled when docs are added
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            return {
                "message": "Knowledge base created and linked successfully",
                "scenario_id": scenario_id,
                "knowledge_base_id": new_kb_id,
                "action": "created"
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'link', 'unlink', or 'create'")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios/{scenario_id}/editing-interface")
async def get_scenario_editing_interface(
    scenario_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get complete editing interface data for a scenario"""
    try:
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get template data from template_id
        template_id = scenario.get("template_id")
        template_data = {}
        
        if template_id:
            template = await db.templates.find_one({"id": template_id})
            if template:
                template_data = template.get("template_data", {})
        
        # Get knowledge base ID from template (not scenario)
        knowledge_base_id = None
        if template_id:
            template = await db.templates.find_one({"id": template_id})
            if template:
                knowledge_base_id = template.get("knowledge_base_id")
        
        # Get knowledge base info and documents
        kb_info = None
        kb_documents = []
        kb_stats = None
        
        if knowledge_base_id:
            # Get KB info
            kb_info = await db.knowledge_bases.find_one({"_id": knowledge_base_id})
            
            # Get KB documents
            docs_cursor = db.supporting_documents.find({"knowledge_base_id": knowledge_base_id})
            kb_documents = await docs_cursor.to_list(length=100)
            
            # Get KB stats
            total_chunks = sum(doc.get("chunk_count", 0) for doc in kb_documents)
            indexed_count = sum(1 for doc in kb_documents if doc.get("processing_status") == "completed")
            
            kb_stats = {
                "total_documents": len(kb_documents),
                "total_chunks": total_chunks,
                "indexed_documents": indexed_count,
                "search_ready": indexed_count > 0 and total_chunks > 0
            }
        
        return {
            "scenario_id": scenario_id,
            "scenario": {
                "title": scenario.get("title", ""),
                "description": scenario.get("description", ""),
                "template_id": template_id,
                "created_at": scenario.get("created_at"),
                "updated_at": scenario.get("updated_at")
            },
            "template_data": template_data,
            "knowledge_base": {
                "id": knowledge_base_id,
                "info": kb_info,
                "documents": kb_documents,
                "stats": kb_stats,
                "fact_checking_enabled": kb_info.get("fact_checking_enabled", False) if kb_info else False
            },
            "editing_capabilities": {
                "can_edit_template": True,
                "can_manage_knowledge_base": True,
                "can_regenerate": True,
                "available_modes": ["learn_mode", "assess_mode", "try_mode"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

# Add these imports to your scenario_generator.py
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn
from io import BytesIO
import tempfile
import os

# Add this new endpoint to your router
@router.post("/fill-word-template")
async def fill_word_template(
    scenario_prompt: str = Body(..., description="Natural language description of the training scenario"),
    template_name: str = Body(..., description="Name for the scenario"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Generate a filled Word document template based on a natural language prompt
    Returns a downloadable .docx file with all tables and sections populated
    """
    try:
        # Initialize generator and get template data
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Enhanced prompt for Word template filling
        word_template_prompt = f"""
        You are an expert instructional designer filling out a comprehensive training scenario template.
        
        SCENARIO REQUEST: {scenario_prompt}
        
        Fill out ALL sections with REALISTIC, CHALLENGING content that reflects actual workplace resistance and complex situations. Create authentic dialogue that mirrors real employee concerns and sophisticated scenarios that test learners properly.
        
        REALISM REQUIREMENTS:
        - Design authentic personas with genuine workplace concerns and realistic resistance patterns
        - Create multi-turn conversation examples with natural back-and-forth dialogue including both correct AND incorrect learner responses
        - Generate sophisticated mistake patterns reflecting actual workplace bias and misunderstanding
        - Make all content professionally challenging yet appropriate for corporate training
        
        CHARACTER DESIGN REQUIREMENTS:
        - AI character roles should match the scenario context (e.g., Skeptical Colleague, Concerned Team Member, Frustrated Customer, Hesitant Student, Worried Parent, etc.)
        - Create authentic backgrounds representing real workplace demographics and situations
        - Include realistic concerns that reflect actual resistance patterns people have
        - Design varied difficulty levels within each scenario
        CONVERSATION REQUIREMENTS:
        - Create multi-turn conversations with authentic back-and-forth dialogue
        - Include both correct AND incorrect learner responses with realistic AI character reactions
        - Show how the AI character responds differently to good vs bad responses
        - Include coaching feedback for incorrect responses using [CORRECT] format
        - Make conversations feel natural and workplace-appropriate
        Provide realistic, professional content suitable for corporate training.
        SUCCESS METRICS REQUIREMENTS:
        - Create specific, measurable targets (e.g., "At least 90% accuracy in distinguishing concepts")
        - Include detailed measurement methods (e.g., "Compare responses to rubric with defined criteria")
        - Make metrics domain-specific and actionable
        - Include both knowledge-based and application-based metrics
        COMMON MISTAKES REQUIREMENTS:
        - Create nuanced mistakes that reflect real workplace bias and misunderstanding
        - Include subtle errors, not just obvious ones
        - Explain why each mistake is problematic in detail
        - Provide comprehensive correct information
        - Make mistakes specific to the domain and scenario    
        
        Generate comprehensive, realistic content that challenges learners authentically.
 
        Return ONLY valid JSON with this exact structure:
        {{
            "project_basics": {{
                "company_name": "Example Corp (or appropriate name based on context)",
                "scenario_title": "Specific scenario title",
                "training_domain": "Primary domain from: Healthcare, Education, Banking, Retail, Insurance, Customer Service, Sales, HR",
                "preferred_language": "Primary: English"
            }},
            "training_goals": {{
                "learner_skills": [
                    "Specific skill 1 learners should master",
                    "Specific skill 2 learners should master", 
                    "Specific skill 3 learners should master",
                    "Specific skill 4 learners should master",
                    "Specific skill 5 learners should master"
                ],
                "job_roles": "Specific job roles this applies to",
                "experience_level": "New (0-1 year) / Experienced (1-5 years) / Expert (5+ years) / Mixed",
                "current_challenges": "Specific challenges learners face in this domain"
            }},
             "scenario_design": {{
                "learn_mode": {{
                    "ai_trainer_role": "Specific expert trainer role with experience level (e.g., Senior HR Trainer with 10+ years experience)",
                    "training_topics": "Detailed, comprehensive list of specific topics to cover in depth",
                    "teaching_style": "Supportive / Challenging / Step-by-step / Interactive (choose most appropriate)"
                }},
              "assess_try_mode": {{
                    "ai_character_role": "Specific character role matching scenario (e.g., Skeptical Colleague, Concerned Team Member, Frustrated Customer, etc.)",
                    "character_background": "Detailed, authentic background of the character including demographics, experience, and current situation",
                    "typical_concerns": "Realistic, specific concerns and questions this character would authentically raise",
                    "difficulty_level": "Easy / Moderate / Challenging / Mixed"
                }},
                "conversation_examples": [
                    {{
                        "character_says": "Realistic, challenging statement the character would make that tests learner skills",
                        "learner_should_respond": "Detailed ideal response with specific keywords and approaches learner should include",
                        "wrong_response": "Realistic example of inadequate or problematic learner response",
                        "correct_response": "Comprehensive correct response with explanation of why this approach works",
                        "character_positive_reaction": "How character responds when learner gives good answer",
                        "character_negative_reaction": "How character responds when learner gives poor answer",
                        "coaching_feedback": "Specific coaching feedback for incorrect responses"
                    }},
                    {{
                        "character_says": "Another realistic, challenging character statement",
                        "learner_should_respond": "Another ideal response with specific guidance",
                        "wrong_response": "Another realistic poor response example", 
                        "correct_response": "Another comprehensive correct response",
                        "character_positive_reaction": "Positive character reaction",
                        "character_negative_reaction": "Negative character reaction",
                        "coaching_feedback": "Coaching feedback for this scenario"
                    }}
                ]
            }},
            "knowledge_base": {{
                "accuracy_requirements": [
                    {{
                        "information_type": "Policies/Procedures",
                        "required": "Yes/No",
                        "details": "Specific details about what policy/procedure accuracy is needed"
                    }},
                    {{
                        "information_type": "Legal/Compliance", 
                        "required": "Yes/No",
                        "details": "Specific legal/compliance accuracy requirements"
                    }},
                    {{
                        "information_type": "Contact Information",
                        "required": "Yes/No",
                        "details": "Contact information accuracy needs"
                    }},
                    {{
                        "information_type": "Products/Services",
                        "required": "Yes/No",
                        "details": "Product/service accuracy requirements if applicable"
                    }}
                ],
                "common_situations": [
                    {{
                        "situation": "Realistic, challenging situation or question that commonly arises in this domain",
                        "correct_response": "Detailed correct response approach with specific guidance and keywords",
                        "source_document": "Type of document this information should come from"
                    }},
                    {{
                        "situation": "Another realistic challenging situation",
                        "correct_response": "Another detailed correct response",
                        "source_document": "Another source document type"
                    }},
                    {{
                        "situation": "Third realistic situation",
                        "correct_response": "Third detailed response", 
                        "source_document": "Third source type"
                    }},
                    {{
                        "situation": "Fourth realistic situation",
                        "correct_response": "Fourth detailed response",
                        "source_document": "Fourth source type"
                    }},
                    {{
                        "situation": "Fifth realistic situation",
                        "correct_response": "Fifth detailed response",
                        "source_document": "Fifth source type"
                    }}
                ]
            }},
            "assessment_feedback": {{
                "correction_tone": "Gentle coaching / Direct correction / Educational explanation",
                "correction_timing": "Immediately / End of conversation / Summary report",
                "correction_method": "Explain what's wrong / Show correct answer / Ask them to try again",
                "success_metrics": [
                    {{
                        "metric": "Specific, measurable metric with clear definition",
                        "target": "Specific target with percentage or criteria (e.g., At least 90% accuracy in distinguishing concepts)",
                        "measurement": "Detailed explanation of how to measure this metric with specific assessment methods"
                    }},
                    {{
                        "metric": "Another specific, measurable metric",
                        "target": "Another specific target with clear criteria",
                        "measurement": "Another detailed measurement method"
                    }},
                    {{
                        "metric": "Third specific metric",
                        "target": "Third specific target",
                        "measurement": "Third measurement method"
                    }},
                    {{
                        "metric": "Fourth specific metric",
                        "target": "Fourth specific target", 
                        "measurement": "Fourth measurement method"
                    }},
                    {{
                        "metric": "Fifth specific metric",
                        "target": "Fifth specific target",
                        "measurement": "Fifth measurement method"
                    }}
                ]
            }},
            "common_mistakes": [
                {{
                    "mistake": "Sophisticated mistake that reflects real workplace bias or misunderstanding",
                    "why_wrong": "Detailed explanation of why this mistake is problematic and what harm it causes",
                    "correct_information": "Comprehensive correct approach with specific guidance and reasoning"
                }},
                {{
                    "mistake": "Another sophisticated mistake pattern",
                    "why_wrong": "Another detailed explanation of problems this causes",
                    "correct_information": "Another comprehensive correct approach"
                }},
                {{
                    "mistake": "Third sophisticated mistake",
                    "why_wrong": "Third detailed explanation of why it's wrong", 
                    "correct_information": "Third comprehensive correct approach"
                }},
                {{
                    "mistake": "Fourth sophisticated mistake",
                    "why_wrong": "Fourth explanation of problems",
                    "correct_information": "Fourth correct approach"
                }},
                {{
                    "mistake": "Fifth sophisticated mistake",
                    "why_wrong": "Fifth explanation",
                    "correct_information": "Fifth correct approach"
                }}
            ]
        }}
        
        Make all content specific, challenging, and professionally sophisticated. Create authentic workplace scenarios that truly test learner skills.
        """
        
        # Get filled template data from LLM
        if azure_openai_client:
            response = await azure_openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at filling training scenario templates with realistic, professional content."},
                    {"role": "user", "content": word_template_prompt}
                ],
                temperature=0.3,
                max_tokens=16000
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                template_data = json.loads(json_match.group(1))
            else:
                template_data = json.loads(response_text)
        else:
            # Fallback mock data
            template_data = get_mock_word_template_data(scenario_prompt)
        
        # Generate the Word document
        doc = create_filled_word_template(template_data, template_name)
        
        # Save to temporary file and read content safely
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        temp_file.close()  # Close the file handle immediately
        
        try:
            doc.save(temp_file.name)
            
            # Read the file content
            with open(temp_file.name, 'rb') as f:
                file_content = f.read()
        finally:
            # Clean up - use try/except to handle any deletion issues
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass  # File might already be deleted or in use
        
        # Save record to database
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "scenario_title": template_data.get("project_basics", {}).get("scenario_title", template_name),
            "domain": template_data.get("project_basics", {}).get("training_domain", "General"),
            "template_data": template_data,
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id),
            "source": "word_template_fill",
            "original_prompt": scenario_prompt,
            "file_type": "docx"
        }
        
        await db.templates.insert_one(template_record)
        
        # Return file for download
        from fastapi.responses import Response
        
        return Response(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{template_name.replace(' ', '_')}_Training_Template.docx\"",
                "Content-Length": str(len(file_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Word template: {str(e)}")


def create_filled_word_template(template_data: Dict[str, Any], template_name: str) -> Document:
    """
    Create a filled Word document matching the structure of your template
    """
    doc = Document()
    
    # Title
    title = doc.add_heading('AI Training Scenario Template', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run('📋 Complete this form to create your AI training scenario with accurate, document-backed responses').bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # SECTION 1: PROJECT BASICS
    doc.add_heading('SECTION 1: PROJECT BASICS ⭐ REQUIRED', 1)
    
    # Create table for project basics
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Fill project basics table
    basics = template_data.get("project_basics", {})
    table.cell(0, 0).text = "Company Name"
    table.cell(0, 1).text = basics.get("company_name", "Your Company Name")
    
    table.cell(1, 0).text = "Scenario Title"
    table.cell(1, 1).text = basics.get("scenario_title", template_name)
    
    table.cell(2, 0).text = "Training Domain"
    table.cell(2, 1).text = f"☑ {basics.get('training_domain', 'General Training')}"
    
    table.cell(3, 0).text = "Preferred Language"
    table.cell(3, 1).text = basics.get("preferred_language", "English")
    
    # SECTION 2: TRAINING GOALS
    doc.add_heading('SECTION 2: TRAINING GOALS ⭐ REQUIRED', 1)
    
    doc.add_heading('2.1 What Should Learners Be Able to Do?', 2)
    doc.add_paragraph('📝 List 3-5 specific skills or knowledge areas:')
    
    goals = template_data.get("training_goals", {})
    skills = goals.get("learner_skills", [])
    
    for i, skill in enumerate(skills[:5], 1):
        doc.add_paragraph(f"{i}. {skill}")
    
    doc.add_heading('2.2 Who Are Your Learners?', 2)
    
    # Learners table
    learner_table = doc.add_table(rows=3, cols=2)
    learner_table.style = 'Table Grid'
    
    learner_table.cell(0, 0).text = "Job Roles"
    learner_table.cell(0, 1).text = goals.get("job_roles", "All relevant roles")
    
    learner_table.cell(1, 0).text = "Experience Level"
    learner_table.cell(1, 1).text = f"☑ {goals.get('experience_level', 'Mixed')}"
    
    learner_table.cell(2, 0).text = "Current Challenges"
    learner_table.cell(2, 1).text = goals.get("current_challenges", "Domain-specific challenges")
    
    # SECTION 3: SCENARIO DESIGN
    doc.add_heading('SECTION 3: SCENARIO DESIGN ⭐ REQUIRED', 1)
    
    doc.add_heading('3.1 Learn Mode: AI as Trainer', 2)
    
    design = template_data.get("scenario_design", {})
    learn_mode = design.get("learn_mode", {})
    
    learn_table = doc.add_table(rows=3, cols=2)
    learn_table.style = 'Table Grid'
    
    learn_table.cell(0, 0).text = "AI Trainer Role"
    learn_table.cell(0, 1).text = learn_mode.get("ai_trainer_role", "Expert Trainer")
    
    learn_table.cell(1, 0).text = "Training Topics"
    learn_table.cell(1, 1).text = learn_mode.get("training_topics", "Core topics for the domain")
    
    learn_table.cell(2, 0).text = "Teaching Style"
    learn_table.cell(2, 1).text = f"☑ {learn_mode.get('teaching_style', 'Supportive')}"
    
    doc.add_heading('3.2 Assess/Try Mode: AI as Customer/Client', 2)
    
    assess_mode = design.get("assess_try_mode", {})
    
    assess_table = doc.add_table(rows=4, cols=2)
    assess_table.style = 'Table Grid'
    
    assess_table.cell(0, 0).text = "AI Customer Role"
    assess_table.cell(0, 1).text = assess_mode.get("ai_customer_role", "Customer/Client")
    
    assess_table.cell(1, 0).text = "Customer Background"
    assess_table.cell(1, 1).text = assess_mode.get("customer_background", "Relevant background")
    
    assess_table.cell(2, 0).text = "Typical Concerns/Questions"
    assess_table.cell(2, 1).text = assess_mode.get("typical_concerns", "Domain-specific concerns")
    
    assess_table.cell(3, 0).text = "Difficulty Level"
    assess_table.cell(3, 1).text = f"☑ {assess_mode.get('difficulty_level', 'Mixed')}"
    
    # 3.3 Real Conversation Examples
    doc.add_heading('3.3 Real Conversation Examples', 2)
    doc.add_paragraph('📝 Provide examples of how conversations should go:')
    
    conversations = design.get("conversation_examples", [])
    for i, conv in enumerate(conversations[:2], 1):
        doc.add_paragraph(f'Example Conversation {i}:', style='Heading 3')
        doc.add_paragraph(f"• Customer says: \"{conv.get('customer_says', 'Customer statement')}\"")
        doc.add_paragraph(f"• Learner should respond: \"{conv.get('learner_should_respond', 'Ideal response')}\"")
        doc.add_paragraph(f"• If learner says wrong thing: \"{conv.get('wrong_response', 'Wrong response example')}\"")
        doc.add_paragraph(f"• Correct response should be: \"{conv.get('correct_response', 'Correct detailed response')}\"")
        doc.add_paragraph()
    
    # SECTION 4: KNOWLEDGE BASE
    doc.add_heading('SECTION 4: KNOWLEDGE BASE ⭐ REQUIRED', 1)
    
    doc.add_heading('4.1 What Information Must Be 100% Accurate?', 2)
    doc.add_paragraph('📝 Check all that apply and provide details:')
    
    knowledge = template_data.get("knowledge_base", {})
    accuracy_reqs = knowledge.get("accuracy_requirements", [])
    
    # Accuracy requirements table
    accuracy_table = doc.add_table(rows=len(accuracy_reqs) + 1, cols=3)
    accuracy_table.style = 'Table Grid'
    
    # Header row
    accuracy_table.cell(0, 0).text = "Information Type"
    accuracy_table.cell(0, 1).text = "Required"
    accuracy_table.cell(0, 2).text = "Details"
    
    for i, req in enumerate(accuracy_reqs, 1):
        accuracy_table.cell(i, 0).text = req.get("information_type", "")
        required_text = "☑ Yes" if req.get("required", "").lower() == "yes" else "☐ No"
        accuracy_table.cell(i, 1).text = required_text
        accuracy_table.cell(i, 2).text = req.get("details", "")
    
    doc.add_heading('4.2 Common Situations & Responses', 2)
    doc.add_paragraph('📝 Fill out for your specific domain:')
    
    # Common situations table
    situations = knowledge.get("common_situations", [])
    situations_table = doc.add_table(rows=len(situations) + 1, cols=3)
    situations_table.style = 'Table Grid'
    
    # Header row
    situations_table.cell(0, 0).text = "Common Situation/Question"
    situations_table.cell(0, 1).text = "Correct Response/Information"
    situations_table.cell(0, 2).text = "Source Document"
    
    for i, situation in enumerate(situations, 1):
        situations_table.cell(i, 0).text = situation.get("situation", "")
        situations_table.cell(i, 1).text = situation.get("correct_response", "")
        situations_table.cell(i, 2).text = situation.get("source_document", "")
    
    # SECTION 5: ASSESSMENT & FEEDBACK
    doc.add_heading('SECTION 5: ASSESSMENT & FEEDBACK ⭐ REQUIRED', 1)
    
    doc.add_heading('5.1 How Should AI Correct Mistakes?', 2)
    
    feedback = template_data.get("assessment_feedback", {})
    
    correction_table = doc.add_table(rows=3, cols=2)
    correction_table.style = 'Table Grid'
    
    correction_table.cell(0, 0).text = "Tone"
    tone = feedback.get("correction_tone", "Gentle coaching")
    correction_table.cell(0, 1).text = f"☑ {tone}"
    
    correction_table.cell(1, 0).text = "Timing"
    timing = feedback.get("correction_timing", "Immediately")
    correction_table.cell(1, 1).text = f"☑ {timing}"
    
    correction_table.cell(2, 0).text = "Method"
    method = feedback.get("correction_method", "Explain what's wrong")
    correction_table.cell(2, 1).text = f"☑ {method}"
    
    doc.add_heading('5.2 Success Metrics', 2)
    doc.add_paragraph('📝 How will you measure if training is working?')
    
    # Success metrics table
    metrics = feedback.get("success_metrics", [])
    metrics_table = doc.add_table(rows=len(metrics) + 1, cols=3)
    metrics_table.style = 'Table Grid'
    
    metrics_table.cell(0, 0).text = "Metric"
    metrics_table.cell(0, 1).text = "Target"
    metrics_table.cell(0, 2).text = "How to Measure"
    
    for i, metric in enumerate(metrics, 1):
        metrics_table.cell(i, 0).text = metric.get("metric", "")
        metrics_table.cell(i, 1).text = metric.get("target", "")
        metrics_table.cell(i, 2).text = metric.get("measurement", "")
    
    # SECTION 6: SUPPORTING DOCUMENTS
    doc.add_heading('SECTION 6: SUPPORTING DOCUMENTS ⭐ REQUIRED', 1)
    
    doc.add_heading('6.1 Document Checklist', 2)
    doc.add_paragraph('📎 Attach ALL documents that contain information the AI should know:')
    
    # Standard document checklist
    doc_categories = [
        ("Core Information Documents", [
            "Product/Service Catalog - What you offer, features, benefits",
            "Pricing Information - Current rates, costs, fee structures", 
            "Policies & Procedures - Rules, guidelines, standard processes",
            "FAQ Document - Common questions and approved answers"
        ]),
        ("Training & Reference Materials", [
            "Training Manuals - Current training content",
            "Best Practice Guides - How things should be done",
            "Templates & Scripts - Standard responses, forms, processes",
            "Case Studies - Real examples and scenarios"
        ]),
        ("Compliance & Standards", [
            "Regulatory Guidelines - Legal requirements, compliance rules",
            "Quality Standards - Service levels, performance criteria",
            "Safety Procedures - Emergency protocols, safety guidelines",
            "Competitive Information - How you compare to others"
        ])
    ]
    
    for category, items in doc_categories:
        doc.add_paragraph(category, style='Heading 3')
        for item in items:
            doc.add_paragraph(f"• ☐ {item}")
    
    # SECTION 7: CONVERSATION EXAMPLES  
    doc.add_heading('SECTION 7: CONVERSATION EXAMPLES ⭐ REQUIRED', 1)
    
    doc.add_heading('7.1 Learn Mode Example', 2)
    doc.add_paragraph('📝 Show how AI trainer should teach:')
    
    # Add learn mode example from template data
    if design.get("conversation_examples"):
        example = design["conversation_examples"][0]
        doc.add_paragraph(f'Topic: {basics.get("training_domain", "Training Topic")}')
        doc.add_paragraph(f'AI Trainer: "{learn_mode.get("ai_trainer_role", "Expert")}, I\'m here to help you learn..."')
        doc.add_paragraph(f'Learner Question: "How should I handle this situation?"')
        doc.add_paragraph(f'AI Response: "{example.get("learner_should_respond", "Detailed educational response")}"')
    
    doc.add_heading('7.2 Assess Mode Example', 2)
    doc.add_paragraph('📝 Show how AI customer should behave:')
    
    if design.get("conversation_examples"):
        example = design["conversation_examples"][0]
        doc.add_paragraph(f'Scenario: {assess_mode.get("customer_background", "Customer scenario")}')
        doc.add_paragraph(f'AI Customer: "{example.get("customer_says", "Customer statement")}"')
        doc.add_paragraph(f'Learner Response: "{example.get("learner_should_respond", "Learner response")}"')
        doc.add_paragraph(f'If Correct: "Thank you, that helps clarify things."')
        doc.add_paragraph(f'If Incorrect: "{example.get("wrong_response", "Im still confused about this.")}')
    
    doc.add_heading('7.3 Common Mistakes to Catch', 2)
    doc.add_paragraph('📝 What errors should trigger [CORRECT] feedback?')
    
    # Common mistakes table
    mistakes = template_data.get("common_mistakes", [])
    if mistakes:
        mistakes_table = doc.add_table(rows=len(mistakes) + 1, cols=3)
        mistakes_table.style = 'Table Grid'
        
        mistakes_table.cell(0, 0).text = "Common Mistake"
        mistakes_table.cell(0, 1).text = "Why It's Wrong"
        mistakes_table.cell(0, 2).text = "Correct Information"
        
        for i, mistake in enumerate(mistakes, 1):
            mistakes_table.cell(i, 0).text = mistake.get("mistake", "")
            mistakes_table.cell(i, 1).text = mistake.get("why_wrong", "")
            mistakes_table.cell(i, 2).text = mistake.get("correct_information", "")
    
    # Add footer note
    doc.add_paragraph()
    footer_note = doc.add_paragraph()
    footer_note.add_run("✅ This template has been automatically filled based on your scenario description. ").bold = True
    footer_note.add_run("Review and customize as needed for your specific training requirements.")
    
    # Format the document
    for paragraph in doc.paragraphs:
        if paragraph.style.name.startswith('Heading'):
            for run in paragraph.runs:
                run.font.name = 'Calibri'
        else:
            for run in paragraph.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(11)
    
    return doc


def get_mock_word_template_data(scenario_prompt: str) -> Dict[str, Any]:
    """Generate mock data for Word template when LLM is not available"""
    
    # Analyze prompt for domain
    prompt_lower = scenario_prompt.lower()
    
    if 'dei' in prompt_lower or 'diversity' in prompt_lower:
        domain = "HR"
        title = "DEI Workplace Training"
        trainer_role = "Senior HR Trainer in DEI"
        customer_role = "Colleague with DEI concerns"
    elif 'sales' in prompt_lower:
        domain = "Sales" 
        title = "Sales Skills Training"
        trainer_role = "Senior Sales Coach"
        customer_role = "Potential customer"
    else:
        domain = "Customer Service"
        title = "Customer Service Training"
        trainer_role = "Customer Service Expert"
        customer_role = "Customer with issue"
    
    return {
        "project_basics": {
            "company_name": "Your Organization",
            "scenario_title": title,
            "training_domain": domain,
            "preferred_language": "Primary: English"
        },
        "training_goals": {
            "learner_skills": [
                f"Understand core {domain.lower()} principles and best practices",
                f"Demonstrate effective communication in {domain.lower()} situations", 
                f"Apply appropriate responses to challenging {domain.lower()} scenarios",
                f"Show cultural sensitivity and professional behavior",
                f"Build confidence in handling real-world {domain.lower()} interactions"
            ],
            "job_roles": f"All employees involved in {domain.lower()} activities",
            "experience_level": "Mixed (New to Expert)",
            "current_challenges": f"Lack of confidence in {domain.lower()} situations, inconsistent responses, need for better cultural awareness"
        },
        "scenario_design": {
            "learn_mode": {
                "ai_trainer_role": trainer_role,
                "training_topics": f"Core {domain.lower()} concepts, best practices, communication techniques, cultural considerations, real-world applications",
                "teaching_style": "Supportive, Interactive, Step-by-step"
            },
            "assess_try_mode": {
                "ai_customer_role": customer_role,
                "customer_background": f"Professional seeking {domain.lower()} assistance with specific needs and concerns",
                "typical_concerns": f"Domain-specific questions, requests for clarification, need for guidance on {domain.lower()} matters",
                "difficulty_level": "Mixed"
            },
            "conversation_examples": [
                {
                    "customer_says": f"I have a {domain.lower()} situation that I'm not sure how to handle properly.",
                    "learner_should_respond": f"I'd be happy to help you with your {domain.lower()} concern. Can you tell me more about the specific situation?",
                    "wrong_response": "That's not really my area. You should probably ask someone else.",
                    "correct_response": f"I understand you're facing a {domain.lower()} challenge. Let me help you work through this step by step. First, can you give me more details about what's happening?"
                },
                {
                    "customer_says": f"I'm not sure if I'm approaching this {domain.lower()} situation correctly.",
                    "learner_should_respond": f"Let's review your approach together. What steps have you taken so far regarding this {domain.lower()} matter?",
                    "wrong_response": "Just do what feels right.",
                    "correct_response": f"It's smart to double-check your approach. Let me help you evaluate your current strategy and suggest any adjustments that might improve your {domain.lower()} outcomes."
                }
            ]
        },
        "knowledge_base": {
            "accuracy_requirements": [
                {
                    "information_type": "Policies/Procedures",
                    "required": "Yes",
                    "details": f"All {domain.lower()} policies and procedures must be current and accurate"
                },
                {
                    "information_type": "Products/Services",
                    "required": "Yes", 
                    "details": f"Product/service information must match current {domain.lower()} offerings"
                },
                {
                    "information_type": "Legal/Compliance",
                    "required": "Yes",
                    "details": f"Legal and compliance information must be up-to-date and jurisdiction-appropriate"
                },
                {
                    "information_type": "Contact Information",
                    "required": "Yes",
                    "details": "Contact details must be current and verified"
                }
            ],
            "common_situations": [
                {
                    "situation": f"Customer asks about {domain.lower()} process or procedure",
                    "correct_response": f"Provide clear, step-by-step explanation of the {domain.lower()} process with relevant examples",
                    "source_document": f"{domain} procedure manual or policy document"
                },
                {
                    "situation": f"Customer expresses frustration or confusion about {domain.lower()} matter",
                    "correct_response": f"Acknowledge their feelings, clarify the {domain.lower()} situation, and provide helpful guidance",
                    "source_document": f"{domain} best practices guide or training manual"
                },
                {
                    "situation": f"Customer needs specific {domain.lower()} information or assistance",
                    "correct_response": f"Provide accurate, detailed information and offer appropriate {domain.lower()} solutions",
                    "source_document": f"{domain} reference guide or official documentation"
                }
            ]
        },
        "assessment_feedback": {
            "correction_tone": "Gentle coaching",
            "correction_timing": "Immediately", 
            "correction_method": "Explain what's wrong and show correct answer",
            "success_metrics": [
                {
                    "metric": f"{domain} Knowledge Accuracy",
                    "target": "At least 85% accuracy in domain-specific responses",
                    "measurement": f"Compare responses against {domain.lower()} best practices rubric"
                },
                {
                    "metric": "Professional Communication",
                    "target": "Consistent professional tone and appropriate language",
                    "measurement": "Evaluate communication style and cultural sensitivity"
                },
                {
                    "metric": "Problem-Solving Effectiveness", 
                    "target": "80% of responses provide actionable solutions",
                    "measurement": "Assess whether responses include clear next steps and practical guidance"
                }
            ]
        },
        "common_mistakes": [
            {
                "mistake": f"Providing generic responses instead of {domain.lower()}-specific guidance",
                "why_wrong": "Generic responses don't address the specific context and needs of the situation",
                "correct_information": f"Provide targeted, domain-specific advice with relevant examples and clear implementation guidance"
            },
            {
                "mistake": "Dismissing or minimizing customer concerns",
                "why_wrong": "This approach undermines trust and fails to address underlying issues that may be important",
                "correct_information": "Acknowledge concerns seriously, validate feelings, and provide thoughtful, comprehensive guidance"
            },
            {
                "mistake": f"Using inappropriate terminology or culturally insensitive language in {domain.lower()} contexts",
                "why_wrong": "Inappropriate language can offend, exclude, or create barriers to effective communication",
                "correct_information": "Use inclusive, respectful language that is culturally appropriate and professionally suitable"
            }
        ]
    }


# Alternative endpoint that returns the Word file as base64 for frontend handling
@router.post("/fill-word-template-base64")
async def fill_word_template_base64(
    scenario_prompt: str = Body(..., description="Natural language description of the training scenario"),
    template_name: str = Body(..., description="Name for the scenario"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Generate filled Word template and return as base64 for frontend download handling
    """
    try:
        # Get template data (same logic as above)
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        word_template_prompt = f"""
        Create a comprehensive training scenario template based on this request: {scenario_prompt}
        
        Fill out all sections with specific, professional content suitable for corporate training.
        Ensure all information is realistic and appropriate for Indian workplace context.
        
        Return the filled template data in JSON format with the exact structure needed for Word document generation.
        
        [Same detailed prompt structure as above...]
        """
        
        if azure_openai_client:
            response = await azure_openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at filling training scenario templates."},
                    {"role": "user", "content": word_template_prompt}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            response_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                template_data = json.loads(json_match.group(1))
            else:
                template_data = json.loads(response_text)
        else:
            template_data = get_mock_word_template_data(scenario_prompt)
        
        # Generate Word document
        doc = create_filled_word_template(template_data, template_name)
        
        # Convert to base64
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        import base64
        file_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Save record to database
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "scenario_title": template_data.get("project_basics", {}).get("scenario_title", template_name),
            "domain": template_data.get("project_basics", {}).get("training_domain", "General"),
            "template_data": template_data,
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id),
            "source": "word_template_fill",
            "original_prompt": scenario_prompt,
            "file_type": "docx"
        }
        
        await db.templates.insert_one(template_record)
        
        return {
            "template_id": template_record["id"],
            "file_base64": file_base64,
            "filename": f"{template_name.replace(' ', '_')}_Training_Template.docx",
            "file_size": len(buffer.getvalue()),
            "template_data": template_data,
            "scenario_title": template_data.get("project_basics", {}).get("scenario_title"),
            "domain": template_data.get("project_basics", {}).get("training_domain"),
            "message": "Word template generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Word template: {str(e)}")


# Endpoint to regenerate Word file from existing template data
@router.post("/regenerate-word-template/{template_id}")
async def regenerate_word_template(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Regenerate Word document from existing template data in database
    """
    try:
        # Get template from database
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_data = template.get("template_data", {})
        template_name = template.get("name", "Training Template")
        
        # Convert your internal template format to Word template format
        word_template_data = convert_internal_to_word_format(template_data)
        
        # Generate Word document
        doc = create_filled_word_template(word_template_data, template_name)
        
        # Save to temporary file and return safely
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        temp_file.close()  # Close file handle immediately
        
        try:
            doc.save(temp_file.name)
            
            with open(temp_file.name, 'rb') as f:
                file_content = f.read()
        finally:
            # Safe cleanup
            try:
                os.unlink(temp_file.name)
            except OSError:
                pass
        
        from fastapi.responses import Response
        
        return Response(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{template_name.replace(' ', '_')}_Template.docx\"",
                "Content-Length": str(len(file_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating Word template: {str(e)}")


def convert_internal_to_word_format(internal_template_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert your internal template format to the Word template format
    """
    
    general_info = internal_template_data.get("general_info", {})
    context_overview = internal_template_data.get("context_overview", {})
    persona_definitions = internal_template_data.get("persona_definitions", {})
    knowledge_base = internal_template_data.get("knowledge_base", {})
    feedback_mechanism = internal_template_data.get("feedback_mechanism", {})
    
    return {
        "project_basics": {
            "company_name": "Your Organization",
            "scenario_title": context_overview.get("scenario_title", "Training Scenario"),
            "training_domain": general_info.get("domain", "General"),
            "preferred_language": "Primary: English"
        },
        "training_goals": {
            "learner_skills": knowledge_base.get("conversation_topics", [
                "Develop professional communication skills",
                "Learn to handle challenging situations",
                "Build cultural awareness and sensitivity",
                "Practice active listening techniques",
                "Apply domain-specific best practices"
            ]),
            "job_roles": general_info.get("target_audience", "All relevant employees"),
            "experience_level": "Mixed (all experience levels)",
            "current_challenges": context_overview.get("purpose_of_scenario", "Need for improved skills and confidence")
        },
        "scenario_design": {
            "learn_mode": {
                "ai_trainer_role": persona_definitions.get("learn_mode_ai_bot", {}).get("role", "Expert Trainer"),
                "training_topics": ", ".join(knowledge_base.get("conversation_topics", [])),
                "teaching_style": persona_definitions.get("learn_mode_ai_bot", {}).get("behavioral_traits", "Supportive, Interactive")
            },
            "assess_try_mode": {
                "ai_customer_role": persona_definitions.get("assess_mode_ai_bot", {}).get("role", "Customer/Client"),
                "customer_background": persona_definitions.get("assess_mode_ai_bot", {}).get("background", "Professional seeking assistance"),
                "typical_concerns": persona_definitions.get("assess_mode_ai_bot", {}).get("goal", "Domain-specific concerns and questions"),
                "difficulty_level": "Mixed"
            },
            "conversation_examples": [
                {
                    "customer_says": "I need help understanding how to approach this situation properly.",
                    "learner_should_respond": "I'd be happy to help you work through this. Can you tell me more about your specific concerns?",
                    "wrong_response": "Just figure it out yourself.",
                    "correct_response": "Let me help you understand the best approach. First, let's identify the key factors in your situation..."
                }
            ]
        },
        "knowledge_base": {
            "accuracy_requirements": [
                {
                    "information_type": "Policies/Procedures",
                    "required": "Yes",
                    "details": "All policies and procedures must be current and accurate"
                },
                {
                    "information_type": "Products/Services",
                    "required": "Yes",
                    "details": "Product and service information must be up-to-date"
                },
                {
                    "information_type": "Legal/Compliance", 
                    "required": "Yes",
                    "details": "Legal and compliance information must be jurisdiction-appropriate"
                }
            ],
            "common_situations": [
                {
                    "situation": situation,
                    "correct_response": f"Provide appropriate guidance for: {situation}",
                    "source_document": "Policy manual or best practices guide"
                } for situation in knowledge_base.get("conversation_topics", ["General inquiries"])[:3]
            ]
        },
        "assessment_feedback": {
            "correction_tone": "Gentle coaching",
            "correction_timing": "Immediately",
            "correction_method": "Explain what's wrong and show correct answer",
            "success_metrics": [
                {
                    "metric": f"{general_info.get('domain', 'Domain')} Knowledge Application",
                    "target": "85% accuracy in responses",
                    "measurement": "Compare responses to established best practices"
                },
                {
                    "metric": "Professional Communication",
                    "target": "Consistent professional tone",
                    "measurement": "Evaluate communication style and appropriateness"
                },
                {
                    "metric": "Cultural Sensitivity",
                    "target": "100% culturally appropriate responses",
                    "measurement": "Review responses for cultural awareness and inclusion"
                }
            ]
        },
        "common_mistakes": [
            {
                "mistake": mistake.replace("Don't ", "").replace("don't ", ""),
                "why_wrong": f"This approach undermines the effectiveness of {general_info.get('domain', 'the domain')} interactions",
                "correct_information": f"Instead, provide thoughtful, specific guidance appropriate for {general_info.get('domain', 'the situation')}"
            } for mistake in knowledge_base.get("donts", ["Generic response", "Dismissive attitude", "Cultural insensitivity"])[:3]
        ]
    }


# Enhanced endpoint with more customization options
@router.post("/fill-word-template-advanced")
async def fill_word_template_advanced(
    scenario_prompt: str = Body(...),
    template_name: str = Body(...),
    customization_options: Dict[str, Any] = Body(default={}, description="Additional customization options"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Advanced Word template filling with customization options
    
    customization_options can include:
    - company_name: Override company name
    - specific_domain: Force specific domain
    - language_preferences: Additional language options
    - complexity_level: Easy/Moderate/Advanced
    - cultural_context: Specific cultural considerations
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Enhanced prompt with customization
        customizations = customization_options
        company_name = customizations.get("company_name", "Your Organization")
        specific_domain = customizations.get("specific_domain", "")
        complexity_level = customizations.get("complexity_level", "Mixed")
        cultural_context = customizations.get("cultural_context", "Indian corporate workplace")
        
        enhanced_prompt = f"""
        Create a comprehensive training scenario template for: {scenario_prompt}
        
        CUSTOMIZATION REQUIREMENTS:
        - Company Name: {company_name}
        - Complexity Level: {complexity_level}
        - Cultural Context: {cultural_context}
        {f"- Specific Domain: {specific_domain}" if specific_domain else ""}
        
        Fill out ALL sections with realistic, professional content.
        Make the content specific to the scenario and appropriate for the cultural context.
        Ensure all conversation examples and personas are authentic and engaging.
        
        [Include the same detailed JSON structure as previous prompts...]
        """
        
        if azure_openai_client:
            response = await azure_openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at creating customized training scenario templates."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.3,
                max_tokens=8000
            )
            
            response_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                template_data = json.loads(json_match.group(1))
            else:
                template_data = json.loads(response_text)
        else:
            template_data = get_mock_word_template_data(scenario_prompt)
            # Apply customizations to mock data
            template_data["project_basics"]["company_name"] = company_name
        
        # Apply any additional customizations
        if company_name != "Your Organization":
            template_data["project_basics"]["company_name"] = company_name
        
        # Generate Word document
        doc = create_filled_word_template(template_data, template_name)
        
        # Convert to base64
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        import base64
        file_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Save record
        template_record = {
            "id": str(uuid4()),
            "name": template_name,
            "scenario_title": template_data.get("project_basics", {}).get("scenario_title", template_name),
            "domain": template_data.get("project_basics", {}).get("training_domain", "General"),
            "template_data": template_data,
            "customization_options": customization_options,
            "created_at": datetime.now().isoformat(),
            "created_by": str(current_user.id),
            "source": "word_template_advanced",
            "original_prompt": scenario_prompt,
            "file_type": "docx"
        }
        
        await db.templates.insert_one(template_record)
        
        return {
            "template_id": template_record["id"],
            "file_base64": file_base64,
            "filename": f"{template_name.replace(' ', '_')}_Training_Template.docx",
            "file_size": len(buffer.getvalue()),
            "template_data": template_data,
            "customization_applied": customization_options,
            "scenario_title": template_data.get("project_basics", {}).get("scenario_title"),
            "domain": template_data.get("project_basics", {}).get("training_domain"),
            "message": "Customized Word template generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating customized Word template: {str(e)}")


# Endpoint to list previously generated Word templates
@router.get("/list-word-templates")
async def list_word_templates(
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    List all Word templates generated by the current user
    """
    try:
        cursor = db.templates.find(
            {"created_by": str(current_user.id), "file_type": "docx"},
            {"_id": 0}
        ).sort("created_at", -1)
        
        templates = await cursor.to_list(length=100)
        
        return {
            "templates": templates,
            "total_count": len(templates),
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing templates: {str(e)}")


# Endpoint to download previously generated Word template
@router.get("/download-word-template/{template_id}")
async def download_word_template(
    template_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Download a previously generated Word template
    """
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check ownership or admin access
        if (template.get("created_by") != str(current_user.id) and 
            current_user.role not in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Regenerate Word document from stored data
        template_data = template.get("template_data", {})
        template_name = template.get("name", "Training Template")
        
        doc = create_filled_word_template(template_data, template_name)
        
        # Return as file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        doc.save(temp_file.name)
        
        with open(temp_file.name, 'rb') as f:
            file_content = f.read()
        
        os.unlink(temp_file.name)
        
        from fastapi.responses import Response
        
        return Response(
            content=file_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{template_name.replace(' ', '_')}_Template.docx\"",
                "Content-Length": str(len(file_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading template: {str(e)}")


# Utility endpoint to preview what would be filled in the Word template
@router.post("/preview-word-template-content")
async def preview_word_template_content(
    scenario_prompt: str = Body(...),
    template_name: str = Body(...)
):
    """
    Preview the content that would be filled in the Word template without generating the actual file
    """
    try:
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Same prompt as fill-word-template but just return the data
        word_template_prompt = f"""
        Analyze this scenario request and provide the content that would fill a training template:
        
        SCENARIO: {scenario_prompt}
        
        Provide specific, realistic content for each section that would appear in the filled template.
        Make it professional and appropriate for corporate training use.
        
        Return JSON with filled content for preview.
        [Same structure as above...]
        """
        
        if azure_openai_client:
            response = await azure_openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are creating preview content for training templates."},
                    {"role": "user", "content": word_template_prompt}
                ],
                temperature=0.3,
                max_tokens=6000
            )
            
            response_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                template_data = json.loads(json_match.group(1))
            else:
                template_data = json.loads(response_text)
        else:
            template_data = get_mock_word_template_data(scenario_prompt)
        
        return {
            "preview_content": template_data,
            "scenario_prompt": scenario_prompt,
            "template_name": template_name,
            "estimated_sections": len(template_data),
            "preview_summary": {
                "domain": template_data.get("project_basics", {}).get("training_domain"),
                "scenario_title": template_data.get("project_basics", {}).get("scenario_title"),
                "trainer_role": template_data.get("scenario_design", {}).get("learn_mode", {}).get("ai_trainer_role"),
                "customer_role": template_data.get("scenario_design", {}).get("assess_try_mode", {}).get("ai_customer_role"),
                "skills_count": len(template_data.get("training_goals", {}).get("learner_skills", [])),
                "situations_count": len(template_data.get("knowledge_base", {}).get("common_situations", []))
            },
            "message": "Preview generated successfully. Use /fill-word-template to generate the actual Word document."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


# Add requirements.txt note for the Word document generation
"""
ADDITIONAL REQUIREMENTS FOR WORD GENERATION:
Add to your requirements.txt:

python-docx==0.8.11

For enhanced Word formatting, also consider:
python-docx2==0.1.0
docx2txt==0.8

Installation:
pip install python-docx==0.8.11
"""
# Add these imports at the top
from core.template_validator import TemplateValidator, PromptsValidator

# Add these validation endpoints

@router.post("/validate-template")
async def validate_template_endpoint(
    template_data: Dict[str, Any] = Body(...),
    db: Any = Depends(get_db)
):
    """
    Validate template data quality before prompt generation
    Returns validation score, issues, and completeness metrics
    """
    try:
        validation_result = TemplateValidator.validate_template(template_data)
        
        return {
            "valid": validation_result.valid,
            "score": validation_result.score,
            "issues": [
                {
                    "field": issue.field,
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in validation_result.issues
            ],
            "completeness": validation_result.completeness,
            "quality_metrics": validation_result.quality_metrics,
            "recommendation": "Ready for prompt generation" if validation_result.valid else "Fix errors before generating prompts"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-prompts")
async def validate_prompts_endpoint(
    prompts_data: Dict[str, Any] = Body(...),
    db: Any = Depends(get_db)
):
    """
    Validate generated prompts quality before scenario creation
    Returns validation score, issues, and quality metrics
    """
    try:
        validation_result = PromptsValidator.validate_prompts(prompts_data)
        
        return {
            "valid": validation_result.valid,
            "score": validation_result.score,
            "issues": [
                {
                    "field": issue.field,
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in validation_result.issues
            ],
            "completeness": validation_result.completeness,
            "quality_metrics": validation_result.quality_metrics,
            "recommendation": "Ready for scenario creation" if validation_result.valid else "Review issues before creating scenario"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-prompts-from-template")
async def generate_prompts_from_template_with_validation(
    template_id: str = Body(...),
    modes: List[str] = Body(default=["learn", "try", "assess"]),
    validate_before_generation: bool = Body(default=True),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """
    Generate prompts from template with optional validation
    """
    try:
        print(f"🔍 DEBUG: Starting generate_prompts_from_template with template_id: {template_id}")
        
        # Get template
        template = await db.templates.find_one({"id": template_id})
        if not template:
            print(f"❌ DEBUG: Template not found for id: {template_id}")
            raise HTTPException(status_code=404, detail="Template not found")
        
        print(f"✅ DEBUG: Template found, keys: {list(template.keys())}")
        
        # Get template_data and handle both string and dict formats
        template_data_raw = template.get("template_data", {})
        print(f"🔍 DEBUG: template_data_raw type: {type(template_data_raw)}")
        print(f"🔍 DEBUG: template_data_raw preview: {str(template_data_raw)[:200]}...")
        
        # Handle case where template_data is stored as JSON string
        if isinstance(template_data_raw, str):
            print(f"🔄 DEBUG: Converting string to dict")
            try:
                import json
                template_data = json.loads(template_data_raw)
                print(f"✅ DEBUG: Successfully parsed JSON, type: {type(template_data)}")
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: JSON decode error: {e}")
                raise HTTPException(status_code=400, detail="Invalid template data format - not valid JSON")
        elif isinstance(template_data_raw, dict):
            print(f"✅ DEBUG: template_data_raw is already a dict")
            template_data = template_data_raw
        else:
            print(f"❌ DEBUG: Unexpected template_data type: {type(template_data_raw)}")
            raise HTTPException(status_code=400, detail=f"Template data must be a dictionary or JSON string, got {type(template_data_raw)}")
        
        # Final validation that we have a dictionary
        if not isinstance(template_data, dict):
            print(f"❌ DEBUG: Final template_data is not a dict: {type(template_data)}")
            raise HTTPException(status_code=400, detail="Template data must be a dictionary after parsing")
        
        print(f"✅ DEBUG: Final template_data is dict with keys: {list(template_data.keys())}")
        
        # Validate template if requested
        validation_result = None
        if validate_before_generation:
            print(f"🔍 DEBUG: Starting template validation")
            try:
                validation_result = TemplateValidator.validate_template(template_data)
                print(f"✅ DEBUG: Template validation completed, valid: {validation_result.valid}")
            except Exception as e:
                print(f"❌ DEBUG: Template validation error: {e}")
                print(f"❌ DEBUG: Error type: {type(e)}")
                import traceback
                print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Template validation failed: {str(e)}")
            
            if not validation_result.valid:
                print(f"⚠️ DEBUG: Template validation failed")
                return {
                    "error": "Template validation failed",
                    "validation": {
                        "valid": False,
                        "score": validation_result.score,
                        "issues": [
                            {
                                "field": issue.field,
                                "severity": issue.severity,
                                "message": issue.message,
                                "suggestion": issue.suggestion
                            }
                            for issue in validation_result.issues
                        ]
                    },
                    "message": "Fix template errors before generating prompts"
                }
        
        # Generate prompts
        print(f"🔍 DEBUG: Creating EnhancedScenarioGenerator")
        generator = EnhancedScenarioGenerator(azure_openai_client)
        
        # Get archetype classification - safely handle if template_data.get fails
        archetype_classification = None
        try:
            print(f"🔍 DEBUG: Accessing archetype_classification")
            if isinstance(template_data, dict):
                archetype_classification = template_data.get("archetype_classification")
                print(f"✅ DEBUG: archetype_classification: {archetype_classification}")
            else:
                print(f"❌ DEBUG: template_data is not a dict when accessing archetype_classification: {type(template_data)}")
                archetype_classification = None
        except (AttributeError, TypeError) as e:
            print(f"❌ DEBUG: Error accessing archetype_classification: {e}")
            archetype_classification = None
        
        # Generate personas
        print(f"🔍 DEBUG: Generating personas")
        try:
            personas = await generator.generate_personas_from_template(
                template_data,
                archetype_classification=archetype_classification
            )
            print(f"✅ DEBUG: Personas generated successfully")
        except Exception as e:
            print(f"❌ DEBUG: Error generating personas: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Persona generation failed: {str(e)}")
        
        # Generate prompts
        print(f"🔍 DEBUG: Generating prompts for modes: {modes}")
        prompts = {}
        try:
            if "learn" in modes:
                print(f"🔍 DEBUG: Generating learn mode prompt")
                prompts["learn_mode_prompt"] = await generator.generate_learn_mode_from_template(template_data)
                print(f"✅ DEBUG: Learn mode prompt generated")
            if "try" in modes:
                print(f"🔍 DEBUG: Generating try mode prompt")
                prompts["try_mode_prompt"] = await generator.generate_try_mode_from_template(template_data)
                print(f"✅ DEBUG: Try mode prompt generated")
            if "assess" in modes:
                print(f"🔍 DEBUG: Generating assess mode prompt")
                prompts["assess_mode_prompt"] = await generator.generate_assess_mode_from_template(template_data)
                print(f"✅ DEBUG: Assess mode prompt generated")
        except Exception as e:
            print(f"❌ DEBUG: Error generating prompts: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Prompt generation failed: {str(e)}")
        
        prompts["personas"] = personas
        
        # Validate generated prompts
        print(f"🔍 DEBUG: Validating generated prompts")
        try:
            prompts_validation = PromptsValidator.validate_prompts(prompts)
            print(f"✅ DEBUG: Prompts validation completed")
        except Exception as e:
            print(f"❌ DEBUG: Error validating prompts: {e}")
            print(f"❌ DEBUG: Error type: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Prompts validation failed: {str(e)}")
        
        print(f"✅ DEBUG: All operations completed successfully")
        return {
            "template_id": template_id,
            "prompts": prompts,
            "template_validation": {
                "score": validation_result.score if validation_result else None,
                "completeness": validation_result.completeness if validation_result else None
            } if validation_result else None,
            "prompts_validation": {
                "valid": prompts_validation.valid,
                "score": prompts_validation.score,
                "issues": [
                    {
                        "field": issue.field,
                        "severity": issue.severity,
                        "message": issue.message
                    }
                    for issue in prompts_validation.issues
                ],
                "quality_metrics": prompts_validation.quality_metrics
            },
            "message": "Prompts generated and validated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from core.prompt_quality_validator import PromptQualityValidator, InteractivePromptTester

@router.post("/test-prompt-quality")
async def test_prompt_quality(
    system_prompt: str = Body(...),
    persona: Dict[str, Any] = Body(...),
    template_data: Dict[str, Any] = Body(...),
    mode: str = Body(default="assess"),
    db: Any = Depends(get_db)
):
    """
    Test prompt quality by running actual test conversations
    Returns conversation examples and quality analysis
    """
    try:
        validator = PromptQualityValidator(azure_openai_client)
        
        result = await validator.validate_prompt_with_conversations(
            system_prompt=system_prompt,
            persona=persona,
            template_data=template_data,
            mode=mode
        )
        
        return {
            "overall_score": result["overall_score"],
            "test_summary": {
                "passed_tests": result.get("passed_tests", 0),
                "total_tests": result.get("total_tests", 0),
                "pass_rate": result.get("passed_tests", 0) / result.get("total_tests", 1) * 100
            },
            "conversation_examples": result["conversation_examples"],
            "strengths": result["strengths"],
            "weaknesses": result["weaknesses"],
            "recommendations": result["recommendations"],
            "message": "Prompt tested with actual conversations"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-interactive-test")
async def start_interactive_test(
    system_prompt: str = Body(...),
    persona: Dict[str, Any] = Body(...),
    initial_message: Optional[str] = Body(default=None),
    db: Any = Depends(get_db)
):
    """
    Start an interactive test conversation with a persona
    Returns conversation_id for continuing the test
    """
    try:
        tester = InteractivePromptTester(azure_openai_client)
        
        result = await tester.start_test_conversation(
            system_prompt=system_prompt,
            persona=persona,
            initial_message=initial_message
        )
        
        # Store tester in session (in production, use Redis or similar)
        # For now, return conversation_id for client to track
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue-interactive-test")
async def continue_interactive_test(
    system_prompt: str = Body(...),
    user_message: str = Body(...),
    conversation_history: List[Dict[str, str]] = Body(default=[]),
    db: Any = Depends(get_db)
):
    """
    Continue an interactive test conversation
    """
    try:
        tester = InteractivePromptTester(azure_openai_client)
        tester.conversation_history = conversation_history
        
        result = await tester.continue_test_conversation(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-test-conversation")
async def evaluate_test_conversation(
    conversation_history: List[Dict[str, str]] = Body(...),
    template_data: Dict[str, Any] = Body(...),
    persona: Dict[str, Any] = Body(...),
    db: Any = Depends(get_db)
):
    """
    Evaluate a completed test conversation
    """
    try:
        tester = InteractivePromptTester(azure_openai_client)
        tester.conversation_history = conversation_history
        
        evaluation = await tester.evaluate_conversation(
            template_data=template_data,
            persona=persona
        )
        
        return {
            "evaluation": evaluation,
            "conversation_length": len(conversation_history) // 2,
            "message": "Conversation evaluated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-interactive-test")
async def start_interactive_test(
    system_prompt: str = Body(...),
    persona: Dict[str, Any] = Body(...),
    initial_message: Optional[str] = Body(default=None),
    db: Any = Depends(get_db)
):
    """Start interactive testing session"""
    try:
        tester = InteractivePromptTester(azure_openai_client)
        
        result = await tester.start_test_conversation(
            system_prompt=system_prompt,
            persona=persona,
            initial_message=initial_message or "Hi, I need some help"
        )
        
        return {
            "test_id": result["test_id"],
            "persona": persona.get("name", "AI Character"),
            "conversation_history": result["conversation_history"],
            "message": "Interactive test started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue-interactive-test")
async def continue_interactive_test(
    system_prompt: str = Body(...),
    user_message: str = Body(...),
    conversation_history: List[Dict[str, str]] = Body(...),
    db: Any = Depends(get_db)
):
    """Continue interactive testing conversation"""
    try:
        tester = InteractivePromptTester(azure_openai_client)
        
        result = await tester.continue_test_conversation(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=conversation_history
        )
        
        return {
            "conversation_history": result["conversation_history"],
            "ai_response": result["ai_response"],
            "message": "Conversation continued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-test-conversation")
async def evaluate_test_conversation(
    conversation_history: List[Dict[str, str]] = Body(...),
    persona: Dict[str, Any] = Body(...),
    template_data: Dict[str, Any] = Body(...),
    db: Any = Depends(get_db)
):
    """Evaluate interactive test conversation"""
    try:
        tester = InteractivePromptTester(azure_openai_client)
        
        result = await tester.evaluate_conversation(
            conversation_history=conversation_history,
            persona=persona,
            template_data=template_data
        )
        
        return {
            "evaluation_score": result["score"],
            "strengths": result["strengths"],
            "weaknesses": result["weaknesses"],
            "recommendations": result["recommendations"],
            "conversation_quality": result["quality_assessment"],
            "message": "Conversation evaluated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template_data: Dict[str, Any] = Body(...),
    db: Any = Depends(get_db)
):
    """Update template - matches frontend expectation"""
    try:
        result = await db.templates.update_one(
            {"id": template_id},
            {"$set": {
                "template_data": template_data,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "message": "Template updated successfully",
            "template_id": template_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))