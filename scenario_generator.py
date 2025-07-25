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

router = APIRouter(prefix="/scenario", tags=["Scenario Generation"])
api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
        
      
azure_openai_client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

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
router = APIRouter()

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
            
            # Extract paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text.strip())
            
            # Extract tables (important for your structured document)
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_parts.append(" | ".join(row_text))
            
            full_text = "\n".join(text_parts)
            print(f"Extracted {len(full_text)} characters from DOCX")
            return full_text if full_text.strip() else None
            
    except Exception as e:
        print(f"DOCX extraction error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return None
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

    def _load_system_prompt(self):
        return """You are an expert at creating detailed role-play scenario prompts with precise template structures.
Your task is to analyze scenarios and create comprehensive templates that maintain specific formatting:
- Always preserve [PERSONA_PLACEHOLDER] and [LANGUAGE_INSTRUCTIONS] placeholders
- Maintain [CORRECT] tag systems for assessment feedback
- Keep [FINISH] tags for conversation management
- Generate domain-specific, detailed content for each scenario type
Follow the provided template structures exactly, maintaining all headings and special tags."""

    def _load_learn_mode_template(self):
        return """# {title} - Learn Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {expert_role} specializing in {specialization}

- NEVER play the {learner_role} role - only respond as the {expert_role}

- Maintain a {tone} and educational tone throughout

- Keep responses clear, balanced, and focused on practical guidance

- Balance {knowledge_type} with realistic practical considerations

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
        return """# {title} - Assessment Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {bot_role} who {bot_situation}

- NEVER play the {trainer_role} role - only respond as the {bot_role}

- Maintain a natural, conversational tone throughout

- NEVER suggest the learner "reach out to you" - you're the one {user_interaction_type}

- Keep your responses under 50 words unless explaining a specific situation

## Character Background

[PERSONA_PLACEHOLDER]

## Conversation Flow

{conversation_flow}

## Context and Environment

{context_details}

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

{areas_to_explore}

## Fact-Checking the Learner's Responses

Compare the learner's responses with the following facts about {domain}:

### {domain} Response Facts:

{key_facts}

### RESPONDING TO UNHELPFUL LEARNER INPUT - CRITICAL INSTRUCTIONS ###

When the human learner provides an unhelpful or inadequate response:

1. First, respond as your character would naturally (showing {natural_reaction_type})

2. Then IMMEDIATELY add the [CORRECT] feedback section using this exact structure:
   
   "[Your character's natural reaction] [CORRECT] Hello learner, [Specific feedback explaining why their response was inadequate and what better guidance would include] [CORRECT]"

IMPORTANT: The [CORRECT] tag system is ONLY used when responding to HUMAN LEARNER messages that:
{incorrect_response_criteria}

NEVER use [CORRECT] tags in your initial messages or questions to the learner. ONLY use [CORRECT] tags when responding to unhelpful human input.

{correct_examples}

# Handling Uncooperative Learner Responses

- If the learner is unhelpful, vague, or unwilling to provide guidance:

- First attempt: Politely repeat your concern, emphasizing {emphasis_point}

- Example: "{polite_repeat_example}"

- If still unhelpful:

- Express disappointment professionally

- Move to the negative closing for uncooperative responses

- Example: "{negative_closing_example} [FINISH]"

## Important Instructions

- When the learner recommends a specific approach to addressing the {issue_type}:

  - Ask follow-up questions to understand how to implement their suggestion

  - Express realistic concerns about potential challenges or consequences

  - Ensure you understand both immediate actions and longer-term strategies

## Conversation Closing (Important)

- Positive closing (if you're satisfied with guidance and support): "{positive_closing} [FINISH]"

- Negative closing (if the guidance doesn't address your concerns): "{needs_more_guidance_closing} [FINISH]"

- Negative closing (if learner was unhelpful/uncooperative): "{unhelpful_closing} [FINISH]"

- Neutral closing (if somewhat satisfied but have reservations): "{neutral_closing} [FINISH]"

- Negative closing (if faced with any profanity): "{profanity_closing} [FINISH]"

- Negative closing (if faced with disrespectful behavior): "{disrespectful_closing} [FINISH]"""

    def _load_try_mode_template(self):
        return """# {title} - Try Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {bot_role} who {bot_situation}

- NEVER play the {trainer_role} role - only respond as the {bot_role}

- Maintain a natural, conversational tone throughout

- NEVER suggest the learner "reach out to you" - you're the one {user_interaction_type}

- Keep your responses under 50 words unless explaining a specific situation

## Character Background

[PERSONA_PLACEHOLDER]

## Conversation Flow

{conversation_flow}

## Context and Environment

{context_details}

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

{areas_to_explore}

# Handling Uncooperative Learner Responses

- If the learner is unhelpful, vague, or unwilling to provide guidance:

- First attempt: Politely repeat your concern, emphasizing {emphasis_point}

- Example: "{polite_repeat_example}"

- If still unhelpful:

- Express disappointment professionally

- Move to the negative closing for uncooperative responses

- Example: "{negative_closing_example} [FINISH]"

## Important Instructions

- When the learner recommends a specific approach to addressing the {issue_type}:

- Ask follow-up questions to understand how to implement their suggestion

- Express realistic concerns about potential challenges or consequences

- Ensure you understand both immediate actions and longer-term strategies

## Conversation Closing (Important)

- Positive closing (if you're satisfied with guidance and support): "{positive_closing} [FINISH]"

- Negative closing (if the guidance doesn't address your concerns): "{needs_more_guidance_closing} [FINISH]"

- Negative closing (if learner was unhelpful/uncooperative): "{unhelpful_closing} [FINISH]"

- Neutral closing (if somewhat satisfied but have reservations): "{neutral_closing} [FINISH]"

- Negative closing (if faced with any profanity): "{profanity_closing} [FINISH]"

- Negative closing (if faced with disrespectful behavior): "{disrespectful_closing} [FINISH]"""

    async def extract_scenario_info(self, scenario_document):
        """Extract structured information from any type of scenario document using LLM"""
        
        extraction_prompt = f"""
      You are an expert instructional designer and training scenario architect. Analyze this document to create a sophisticated, psychologically-informed training scenario.

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
        ```
        {scenario_document}
        ```
        
        Extract the following information in valid JSON format:
        {{
            "general_info": {{
                "domain": "The domain/field (e.g., sales, customer service, education, healthcare, etc.)",
                "purpose_of_ai_bot": "What the AI bot should do (trainer/customer/student/etc.)",
                "target_audience": "Who this is for (employees/public/etc.)",
                "preferred_language": "English"
            }},
            "context_overview": {{
                "scenario_title": "The title of the scenario",
                "learn_mode_description": "What happens in learn mode",
                "assess_mode_description": "What happens in assessment mode",
                "try_mode_description": "What happens in try mode",
                "purpose_of_scenario": "Learning objectives"
            }},
            "persona_definitions": {{
                "learn_mode_ai_bot": {{
                    "gender": "Male/Female",
                    "role": "Expert/Trainer/Specialist",
                    "background": "Professional background",
                    "key_skills": "Relevant skills",
                    "behavioral_traits": "Communication style",
                    "goal": "What they want to achieve"
                }},
                "assess_mode_ai_bot": {{
                    "gender": "Male/Female",
                    "role": "Customer/Client/Student/etc.",
                    "background": "Relevant background",
                    "key_skills": "Relevant skills",
                    "behavioral_traits": "Personality traits",
                    "goal": "What they want to achieve"
                }}
            }},
            "dialogue_flow": {{
                "learn_mode_initial_prompt": "How expert starts conversation",
                "assess_mode_initial_prompt": "How bot character starts conversation",
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
                    "Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5", "Topic 6"
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
                "positive_closing": "Positive ending message",
                "negative_closing": "Negative ending message",
                "neutral_closing": "Neutral ending message",
                "profanity_closing": "Response to profanity",
                "disrespectful_closing": "Response to disrespect",
                "emphasis_point": "What to emphasize when repeating",
                "polite_repeat_example": "Example of polite repetition",
                "negative_closing_example": "Example of disappointment"
            }},
             "coaching_rules": {{
            "process_requirements": {{
                "mentioned_methodology": "What specific process/methodology is mentioned in the document? (e.g., SPIN model, KYC process, etc.)",
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
    - Preserve the exact language and examples from the document when possible
        Provide comprehensive, scenario-specific content for each field.
        
Generate a comprehensive training scenario with the depth and sophistication of professional corporate training programs. Focus on creating realistic, challenging, and educationally valuable experiences.

Return in the specified JSON format with rich, detailed content in each section.
        """
        
        try:
            if self.client is None:
                # Return mock data for testing
                mock_data = self._get_mock_template_data(scenario_document)
            # ADD: Empty coaching rules for mock data
                mock_data["coaching_rules"] = {
                "process_requirements": {},
                "document_specific_mistakes": [],
                "customer_context_from_document": {},
                "correction_preferences_from_document": {},
                "domain_specific_validation": {}
                }
                return mock_data                # return self._get_mock_template_data(scenario_document)
            
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
            
        #     # Extract JSON from response
        #     json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        #     if json_match:
        #         try:
        #             return json.loads(json_match.group(1))
        #         except json.JSONDecodeError:
        #             pass
            
        #     try:
        #         return json.loads(response_text)
        #     except json.JSONDecodeError:
        #         return self._get_mock_template_data(scenario_document)
                
        # except Exception as e:
        #     print(f"Error in extract_scenario_info: {str(e)}")
        #     return self._get_mock_template_data(scenario_document)
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    template_data = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    template_data = self._get_mock_template_data(scenario_document)
            else:
                try:
                    template_data = json.loads(response_text)
                except json.JSONDecodeError:
                    template_data = self._get_mock_template_data(scenario_document)
        
            # ADD: Ensure coaching_rules exists with safe defaults
            if "coaching_rules" not in template_data:
                template_data["coaching_rules"] = {
                "process_requirements": {},
                "document_specific_mistakes": [],
                "customer_context_from_document": {},
                "correction_preferences_from_document": {},
                "domain_specific_validation": {}
                }
        
            return template_data
        
        except Exception as e:
            print(f"Error in extract_scenario_info: {str(e)}")
            mock_data = self._get_mock_template_data(scenario_document)
            # ADD: Empty coaching rules for error case
            mock_data["coaching_rules"] = {
            "process_requirements": {},
            "document_specific_mistakes": [],
            "customer_context_from_document": {},
            "correction_preferences_from_document": {},
            "domain_specific_validation": {}
            }
            return mock_data            
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
                "assess_mode_description": f"AI acts as customer/client, user practices {domain.lower()} skills",
                "try_mode_description": "Same as assess mode without feedback",
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
                "assess_mode_initial_prompt": f"Hello, I'm looking for help with {domain.lower()}. Can you assist me?",
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
                "positive_closing": f"Thank you for your help with {domain.lower()}. I understand much better now.",
                "negative_closing": f"I'm still not clear on this {domain.lower()} topic. I think I need more help.",
                "neutral_closing": f"Thanks for the {domain.lower()} information. I'll think about it.",
                "profanity_closing": "I prefer to keep our conversation professional.",
                "disrespectful_closing": "I expect respectful communication.",
                "emphasis_point": f"the importance of clear {domain.lower()} understanding",
                "polite_repeat_example": f"I appreciate your response, but could you clarify this {domain.lower()} point?",
                "negative_closing_example": f"I don't feel I've received the {domain.lower()} guidance I was looking for."
            }
        }

    async def generate_personas_from_template(self, template_data):
        """Generate detailed personas based on template persona definitions"""
        
        try:
            if self.client is None:
                # Return mock personas for testing
                return self._get_mock_personas(template_data)
            
            persona_prompt = f"""
           You are a psychology-informed persona architect creating realistic characters for professional training.

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
            Generate personas for both Learn Mode and Assessment Mode.
            
            Template Data:
            {json.dumps(template_data.get('persona_definitions', {}), indent=2)}
            
            Context:
            - Domain: {template_data.get('general_info', {}).get('domain', 'general')}
            - Scenario: {template_data.get('context_overview', {}).get('scenario_title', 'training scenario')}
            
            Create detailed personas in JSON format:
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
                    "background_story": "Relevant background story"
                }}
            }}
            
            Provide ONLY the JSON with realistic, detailed personas.
            Create personas that feel like real people with real stories, not generic customer types.
            Make sure you create either a male or female persona
            Make sure your Personas are of based in india
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
                "location": "New York, NY",
                "persona_details": "Professional, knowledgeable, patient teaching style",
                "situation": "Leading training sessions",
                "context_type": domain,
                "background_story": "10+ years experience in the field with training expertise"
            },
            "assess_mode_character": {
                "name": "Michael Johnson",
                "description": f"Person seeking help with {domain}",
                "persona_type": "customer",
                "gender": "male", 
                "age": 28,
                "character_goal": "Get help and guidance",
                "location": "Chicago, IL",
                "persona_details": "Curious, asks thoughtful questions, wants to understand",
                "situation": "Seeking assistance",
                "context_type": domain,
                "background_story": "New to this area and wanting to learn"
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
            
            # Fill template with specific data
            formatted_template = self.learn_mode_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                expert_role=persona_def.get('role', 'Expert'),
                specialization=general_info.get('domain', 'this field'),
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
            
            # Build incorrect response criteria
            incorrect_criteria = """- Do not provide helpful, constructive guidance
- Are dismissive of the situation
- Show indifference or apathy  
- Are brief, vague, or lack actionable advice
- Contain negative or unsupportive elements
- Fail to address the core issues raised
- Suggest the situation isn't important
- Indicate unwillingness to engage
- Show lack of knowledge or understanding
- Use dismissive language or tone
- Consist of brief responses like "no," "I don't know," etc."""

            # Build correct examples
            correct_examples = f"""Example of correct implementation:
Human: "I don't know much about {general_info.get('domain', 'this topic')}. Just figure it out yourself."
You: "I understand this might be challenging. [CORRECT] Hello learner, When someone seeks guidance about {general_info.get('domain', 'this topic')}, a dismissive response fails to provide necessary support. A helpful response would acknowledge their concerns, provide clear information, and offer actionable guidance. Remember that learners need both practical guidance and encouragement to build their confidence effectively. [CORRECT]" """

            formatted_template = self.assess_mode_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                bot_role=bot_persona.get('role', 'person seeking help'),
                bot_situation=bot_persona.get('goal', 'needs assistance'),
                trainer_role=template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {}).get('role', 'trainer'),
                user_interaction_type="seeking guidance" if "customer" in bot_persona.get('role', '').lower() else "learning",
                conversation_flow=dialogue_flow.get('assess_mode_initial_prompt', 'Begin by greeting the user and explaining your situation.'),
                context_details=context_overview.get('assess_mode_description', 'Interactive scenario environment.'),
                areas_to_explore=self._format_bullet_points(knowledge_base.get('conversation_topics', [])),
                domain=general_info.get('domain', 'this topic'),
                key_facts=self._format_bullet_points(knowledge_base.get('key_facts', [])),
                natural_reaction_type=bot_persona.get('behavioral_traits', 'confusion, disappointment, etc.'),
                incorrect_response_criteria=incorrect_criteria,
                correct_examples=correct_examples,
                emphasis_point=feedback.get('emphasis_point', 'the importance of proper guidance'),
                polite_repeat_example=feedback.get('polite_repeat_example', 'I appreciate your response, but I\'m still uncertain about this situation.'),
                negative_closing_example=feedback.get('negative_closing_example', 'Thank you for your time, but I don\'t feel I\'ve received clear guidance.'),
                issue_type=general_info.get('domain', 'topic'),
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
        """Generate Try Mode prompt using template data"""
        try:
            general_info = template_data.get('general_info', {})
            context_overview = template_data.get('context_overview', {})
            dialogue_flow = template_data.get('dialogue_flow', {})
            knowledge_base = template_data.get('knowledge_base', {})
            feedback = template_data.get('feedback_mechanism', {})
            bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
            
            formatted_template = self.try_mode_template.format(
                title=context_overview.get('scenario_title', 'Training Scenario'),
                bot_role=bot_persona.get('role', 'person seeking help'),
                bot_situation=bot_persona.get('goal', 'needs assistance'),
                trainer_role=template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {}).get('role', 'trainer'),
                user_interaction_type="seeking guidance" if "customer" in bot_persona.get('role', '').lower() else "learning",
                conversation_flow=dialogue_flow.get('assess_mode_initial_prompt', 'Begin by greeting the user and explaining your situation.'),
                context_details=context_overview.get('try_mode_description', 'Practice scenario environment.'),
                areas_to_explore=self._format_bullet_points(knowledge_base.get('conversation_topics', [])),
                emphasis_point=feedback.get('emphasis_point', 'the importance of proper guidance'),
                polite_repeat_example=feedback.get('polite_repeat_example', 'I appreciate your response, but I\'m still uncertain about this situation.'),
                negative_closing_example=feedback.get('negative_closing_example', 'Thank you for your time, but I don\'t feel I\'ve received clear guidance.'),
                issue_type=general_info.get('domain', 'topic'),
                positive_closing=feedback.get('positive_closing', 'Thank you for your guidance. I feel more confident now.'),
                needs_more_guidance_closing=feedback.get('negative_closing', 'Thank you for your time. I\'m still uncertain about how to proceed.'),
                unhelpful_closing=feedback.get('negative_closing', 'I appreciate your time, but I don\'t feel I\'ve received the guidance I need.'),
                neutral_closing=feedback.get('neutral_closing', 'Thanks for talking through this with me. I\'ll consider my options.'),
                profanity_closing=feedback.get('profanity_closing', 'I\'m not comfortable with that language in our discussion.'),
                disrespectful_closing=feedback.get('disrespectful_closing', 'Your response doesn\'t seem to take this topic seriously.')
            )
            
            return formatted_template
            
        except Exception as e:
            print(f"Error in generate_try_mode_from_template: {str(e)}")
            return "Error generating try mode template"

    def _format_bullet_points(self, items):
        """Format a list of items as bullet points"""
        try:
            if isinstance(items, list):
                return "\n".join([f"- {item}" for item in items])
            return str(items)
        except Exception as e:
            print(f"Error in _format_bullet_points: {str(e)}")
            return "- Error formatting bullet points"

    def insert_persona(self, prompt, persona_details):
        """Insert persona details into a prompt, replacing [PERSONA_PLACEHOLDER]"""
        try:
            if not isinstance(persona_details, dict):
                return prompt
            
            # Format persona based on available fields  
            persona_text = f"""- Your name is {persona_details.get('name', '[Your Name]')} (Always return this name when asked)

- Age: {persona_details.get('age', '[Age]')}

- Background: {persona_details.get('background_story', '[Background]')}

- Personality: {persona_details.get('persona_details', '[Personality traits]')}

- Current Goal: {persona_details.get('character_goal', '[Current objective]')}

- Location: {persona_details.get('location', '[Location]')}"""
            
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

# API Endpoints

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
        elif template_file.filename.lower().endswith('.pdf'):
            scenario_text = await extract_text_from_pdf(content)
        else:
            scenario_text = content.decode('utf-8')
            
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
        generated_personas = await generator.generate_personas_from_template(template_data)
        
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
        
        template_data = template.get("template_data")
        if not template_data:
            raise HTTPException(status_code=400, detail="No template data found")
        
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
        
        # Store generated prompts in scenario (you may need to adjust this based on your schema)
        if "learn_mode" in generated_prompts and scenario.get("learn_mode"):
            update_data["learn_mode.prompt"] = generated_prompts["learn_mode"]
        
        if "assess_mode" in generated_prompts and scenario.get("assess_mode"):
            update_data["assess_mode.prompt"] = generated_prompts["assess_mode"]
        
        if "try_mode" in generated_prompts and scenario.get("try_mode"):
            update_data["try_mode.prompt"] = generated_prompts["try_mode"]
        
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
    
    

    """
    Generate a single persona with random gender and regional diversity
    """
    
    # Random selections for diversity
    genders = ["male", "female"]
    random_gender = random.choice(genders)
    
    # Regional diversity (randomly selected internally)
    regions = [
        # {
        #     "name": "us",
        #     "locations": ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ"],
        #     "cultural_context": "American cultural background, direct communication style",
        #     "naming_style": "American names like Sarah, Michael, Jennifer, David"
        # },
        {
            "name": "india", 
            "locations": ["Mumbai, Maharashtra", "Delhi, NCR", "Bangalore, Karnataka", "Hyderabad, Telangana", "Chennai, Tamil Nadu"],
            "cultural_context": "Indian cultural background, respectful and relationship-focused communication",
            "naming_style": "Indian names like Priya, Rajesh, Anita, Vikram"
        }
        # ,
        # {
        #     "name": "uk",
        #     "locations": ["London, England", "Manchester, England", "Birmingham, England", "Glasgow, Scotland"],
        #     "cultural_context": "British cultural background, polite and formal communication style", 
        #     "naming_style": "British names like Emma, James, Charlotte, Oliver"
        # },
        # {
        #     "name": "australia",
        #     "locations": ["Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA"],
        #     "cultural_context": "Australian cultural background, friendly and direct communication style",
        #     "naming_style": "Australian names like Sophie, Luke, Grace, Ryan"
        # }
    ]
    
    random_region = random.choice(regions)
    random_location = random.choice(random_region["locations"])
    
    # Get scenario context
    domain = template_data.get("general_info", {}).get("domain", "general")
    scenario_title = template_data.get("context_overview", {}).get("scenario_title", "Training Scenario")
    
    # Enhanced prompt with diversity built-in
    prompt = f"""
    Create a highly realistic, single-person persona for {domain} training scenarios.
    
    STRICT REQUIREMENTS:
    - SINGLE PERSON ONLY (not a couple, not multiple people)
    - Gender: {random_gender} (must be consistent throughout)
    - Cultural Background: {random_region['cultural_context']}
    - Location: {random_location}
    - Naming Style: {random_region['naming_style']}
    
    PERSONA TYPE: {persona_type}
    SCENARIO CONTEXT: {scenario_title}
    DOMAIN: {domain}
    
    PERSONA PROFILE REQUIREMENTS:
    1. Create ONE individual person (not a family, not a couple)
    2. Ensure ALL pronouns and references match {random_gender} gender
    3. Use culturally appropriate names from the specified region
    4. Include region-specific cultural nuances and communication styles
    5. Make the persona realistic and authentic
    6. Include specific demographic details appropriate for the cultural background
    
    RESPONSE FORMAT (JSON only):
    {{
        "name": "Single culturally appropriate {random_gender} name",
        "gender": "{random_gender}",
        "age": [specific age number between 22-55],
        "character_goal": "Specific goal relevant to {domain}",
        "location": "{random_location}",
        "persona_details": "Detailed description of this ONE {random_gender} person - personality, background, preferences, communication style",
        "situation": "Current specific situation this person is facing in {domain} context",
        "background_story": "Rich backstory explaining this person's background and experiences"
    }}
    
    CRITICAL: 
    - Use {random_gender} pronouns consistently (he/him for male, she/her for female)
    - NO mixing of genders or multiple people
    - Make it culturally authentic for the specified background
    - Focus on ONE individual {random_gender} person only
    
    Generate the persona now.
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert persona designer who creates authentic, culturally diverse, single-person character profiles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher temperature for more diversity
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        persona_data = json.loads(response.choices[0].message.content)
        
        # Validate and ensure consistency
        persona_data["gender"] = random_gender  # Force consistency
        
        return persona_data
        
    except Exception as e:
        print(f"Error generating persona: {str(e)}")
        # Fallback persona with random diversity
        fallback_names = {
            "male": ["James", "Michael", "David", "Rajesh", "Oliver", "Ryan"],
            "female": ["Sarah", "Jennifer", "Priya", "Emma", "Sophie", "Grace"]
        }
        
        return {
            "name": random.choice(fallback_names[random_gender]),
            "gender": random_gender,
            "age": random.randint(25, 45),
            "character_goal": f"Engage in {domain} scenario",
            "location": random_location,
            "persona_details": f"A {random_gender} professional with relevant {domain} experience",
            "situation": f"Participating in {domain} training scenario", 
            "background_story": f"Professional background in {domain} from {random_region['name']}"
        }