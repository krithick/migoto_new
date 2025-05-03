from fastapi import FastAPI, HTTPException, Query, Body,Depends, Form , UploadFile , File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from mongo import MongoDB
import uuid
from fastapi.responses import JSONResponse, StreamingResponse
import re
# Load environment variables
load_dotenv(".env")

# Set up OpenAI client
from core.user import router as user_router
from core.avatar import router as avatar_router
from core.avatar_interaction import router as avatar_interaction_router
from core.botvoice import router as botvoice_router
from core.course import router as course_router
from core.document import router as document_router
from core.environment import router as environment_router
from core.language import router as language_router
from core.module import router as module_router
from core.scenario import router as scenario_router
from core.persona import router as persona_router
from core.video import router as video_router
from core.file import router as fileupload_router
# from core.structure import router as new_router
app = FastAPI(title="Role-Play Scenario Generator API",debug=True)



# Mount static folder
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(user_router)
app.include_router(avatar_router)
app.include_router(avatar_interaction_router)
app.include_router(botvoice_router)
app.include_router(course_router)
app.include_router(document_router)
app.include_router(environment_router)
app.include_router(language_router)
app.include_router(module_router)
app.include_router(scenario_router)
app.include_router(persona_router)
app.include_router(video_router)
app.include_router(fileupload_router)
# app.include_router(new_router)

api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
        
        
azure_openai_client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TemplateRequest(BaseModel):
    scenario_description: str = Field(..., 
        description="One-line description of the scenario (e.g., 'HR POSH evaluator' or 'customer opening bank account')",
        example="Hotel concierge helping an upset guest with a room problem")
    language_mix: Optional[str] = Field(None,
        description="Optional language mixing requirement (e.g., 'Hindi-English' or 'French-English')",
        example="Spanish-English")

class TemplateResponse(BaseModel):
    template: Dict[str, Any]
    template_markdown: str
    scenario_type: str

class ScenarioRequest(BaseModel):
    template: Dict[str, Any] = Field(..., 
        description="The template with placeholder values filled in")

class ScenarioResponse(BaseModel):
    scenario_prompt: str
    scenario_name: str
    bot_role: str
    user_role: str

class TemplateFormField(BaseModel):
    name: str
    description: str
    type: str = "text"  # text, textarea, number, select
    options: Optional[List[str]] = None  # For select fields
    required: bool = True
    default_value: Optional[str] = None
    placeholder: Optional[str] = None
    
class TemplateFormResponse(BaseModel):
    fields: List[TemplateFormField]
    template_structure: str

# Template for creating a template from a one-liner
TEMPLATE_CREATION_PROMPT = """
Create a template structure for a role-play scenario based on this description: "{scenario_description}".
{language_instruction}

The template should follow this JSON structure (with placeholder values):

```json
{{
  "SCENARIO_NAME": "Human-readable name for this scenario",
  "CUSTOMER_ROLE": "Description of who the bot is playing",
  "SERVICE_PROVIDER_ROLE": "Description of who the bot is talking to",
  "MAX_RESPONSE_LENGTH": "50",
  "CHARACTER_NAME_INSTRUCTION": "Instructions for how the bot should handle its name",
  "PERSONAL_OR_BUSINESS": "personal or business depending on context",
  "CHARACTER_GOAL": "Primary goal or objective of the character",
  "LOCATION": "Where the scenario takes place",
  "CHARACTER_PERSONA": "Brief persona description",
  "CHARACTER_SITUATION": "Current circumstances or situation",
  "PRIMARY_LANGUAGE": "Primary language for responses",
  "SECONDARY_LANGUAGE": "Secondary language to mix in (if applicable)",
  "TECHNICAL_TERMS_TYPES": "Types of terms to keep in secondary language",
  "MIXED_LANGUAGE_EXAMPLE_1": "Example of mixed language response 1",
  "MIXED_LANGUAGE_EXAMPLE_2": "Example of mixed language response 2",
  "CONTEXT_DESCRIPTION": "Description of when this language mix is natural",
  "CONVERSATION_STARTER": "How to begin the conversation",
  "KEY_DETAILS_TO_INTRODUCE": "What details to gradually introduce",
  "INITIAL_INQUIRY": "First question or request",
  "DEMOGRAPHIC_DESCRIPTION": "Details about the demographic context",
  "TOPICS": [
    "TOPIC_1", 
    "TOPIC_2",
    "TOPIC_3",
    "TOPIC_4",
    "TOPIC_5",
    "TOPIC_6",
    "TOPIC_7",
    "TOPIC_8"
  ],
  "PRODUCT_OR_SERVICE_NAME": "Name of product or service to fact-check",
  "FACTS": [
    "FACT_1",
    "FACT_2",
    "FACT_3",
    "FACT_4",
    "FACT_5",
    "FACT_6",
    "FACT_7",
    "FACT_8"
  ],
  "EXAMPLE_CUSTOMER_RESPONSE": "Example of customer response when fact is wrong",
  "EXAMPLE_CORRECTION": "Example of correction feedback",
  "EXAMPLE_UNCOOPERATIVE_RESPONSE": "Example of response to uncooperative behavior",
  "EXAMPLE_UNCOOPERATIVE_CORRECTION": "Example of correction for uncooperative behavior",
  "EXAMPLE_POLITE_REPEAT": "Example of politely repeating a request",
  "EXAMPLE_DISAPPOINTMENT_CLOSING": "Example of expressing disappointment",
  "PRODUCT_TYPE": "Type of product or recommendation",
  "NEEDS_TYPE": "Type of needs or requirements",
  "KEY_FEATURES": "Important features to focus on",
  "IMPORTANT_POLICIES": "Policies to understand",
  "POSITIVE_CLOSING_TEXT": "Text for positive closing",
  "NEGATIVE_CLOSING_NEEDS_TEXT": "Text for negative closing due to needs not met",
  "NEGATIVE_CLOSING_SERVICE_TEXT": "Text for negative closing due to poor service",
  "NEUTRAL_CLOSING_TEXT": "Text for neutral closing",
  "BUSINESS_OR_PERSONAL": "business or personal depending on context"
}}
```

Also generate the template in markdown format using the following structure:

```markdown
# [SCENARIO_NAME] Bot - Role Play Scenario

## Core Character Rules

- You are an AI playing the role of a [CUSTOMER_ROLE]
- NEVER play the [SERVICE_PROVIDER_ROLE]'s role - only respond as the customer
- Maintain a natural, conversational tone throughout
- NEVER suggest the [SERVICE_PROVIDER_ROLE] "reach out to you" - you're the one seeking service
- Keep your responses under [MAX_RESPONSE_LENGTH] words

## Character Background

- Your name is [Your Name] ([CHARACTER_NAME_INSTRUCTION])
- [PERSONAL_OR_BUSINESS]_Goal: [CHARACTER_GOAL] in [LOCATION]
- Persona: [CHARACTER_PERSONA]
- Current situation: [CHARACTER_SITUATION]

## Language Instructions

- If the [SERVICE_PROVIDER_ROLE] speaks in [PRIMARY_LANGUAGE], respond in a mix of [PRIMARY_LANGUAGE] and [SECONDARY_LANGUAGE]
- Keep [TECHNICAL_TERMS_TYPES] in [SECONDARY_LANGUAGE]
- Examples:
  - "[MIXED_LANGUAGE_EXAMPLE_1]"
  - "[MIXED_LANGUAGE_EXAMPLE_2]"
- This mixed language approach is more natural and authentic for [CONTEXT_DESCRIPTION]

## Conversation Flow

Begin by [CONVERSATION_STARTER]. As the conversation progresses, gradually introduce more details about [KEY_DETAILS_TO_INTRODUCE]. Ask about [INITIAL_INQUIRY].

## Demographic-Specific Context

[DEMOGRAPHIC_DESCRIPTION]

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

- [TOPIC_1]
- [TOPIC_2]
- [TOPIC_3]
- [TOPIC_4]
- [TOPIC_5]
- [TOPIC_6]
- [TOPIC_7]
- [TOPIC_8]

## Fact-Checking the [SERVICE_PROVIDER_ROLE]'s Responses

Compare the [SERVICE_PROVIDER_ROLE]'s responses with the following facts about the [PRODUCT_OR_SERVICE_NAME]:

### [PRODUCT_OR_SERVICE_NAME] Facts:

- [FACT_1]
- [FACT_2]
- [FACT_3]
- [FACT_4]
- [FACT_5]
- [FACT_6]
- [FACT_7]
- [FACT_8]

## When the [SERVICE_PROVIDER_ROLE] provides information that contradicts these facts:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the discrepancy [CORRECT]
4. Example: "[EXAMPLE_CUSTOMER_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_CORRECTION] [CORRECT]"

### If the [SERVICE_PROVIDER_ROLE] is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the issue [CORRECT]
4. Example: "[EXAMPLE_UNCOOPERATIVE_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_UNCOOPERATIVE_CORRECTION] [CORRECT]"

# Handling Uncooperative [SERVICE_PROVIDER_ROLE]

- If the [SERVICE_PROVIDER_ROLE] is unhelpful, vague, or unwilling to provide information:
  - First attempt: Politely repeat your request, emphasizing its importance
  - Example: "[EXAMPLE_POLITE_REPEAT]"
  - If still unhelpful:
    - Express disappointment professionally
    - Move to the negative closing for uncooperative staff
    - Example: "[EXAMPLE_DISAPPOINTMENT_CLOSING] [FINISH]"

## Important Instructions

- When the [SERVICE_PROVIDER_ROLE] recommends a specific [PRODUCT_TYPE]:
  - Ask follow-up questions to determine if it suits your [NEEDS_TYPE]
  - Get clarity on all features, especially focusing on [KEY_FEATURES]
  - Ensure you understand [IMPORTANT_POLICIES]

## Conversation Closing (Important)

- Positive closing (if you're satisfied with information and service): "[POSITIVE_CLOSING_TEXT] [FINISH]"
- Negative closing (if the [PRODUCT_OR_SERVICE] doesn't meet your needs): "[NEGATIVE_CLOSING_NEEDS_TEXT] [FINISH]"
- Negative closing (if [SERVICE_PROVIDER_ROLE] was unhelpful/uncooperative): "[NEGATIVE_CLOSING_SERVICE_TEXT] [FINISH]"
- Neutral closing (if you're somewhat satisfied but have reservations): "[NEUTRAL_CLOSING_TEXT] [FINISH]"
- Negative closing (if faced with any profanity): "Your language is unacceptable and unprofessional. I will be taking my [BUSINESS_OR_PERSONAL] business elsewhere. [FINISH]"
- Negative closing (if faced with disrespectful behavior): "Your behavior is disrespectful and unprofessional. I will be taking my [BUSINESS_OR_PERSONAL] business elsewhere. [FINISH]"
```

Fill the template with appropriate placeholder values specific to this scenario type. Make any necessary adaptations for the specific scenario described.
"""

# Template for generating a scenario from a filled template
SCENARIO_GENERATION_PROMPT = """
Generate a detailed role-play scenario by filling in this template with specific content:

{template_markdown}

Replace all placeholder values (text in [SQUARE_BRACKETS]) with detailed, specific content that creates a comprehensive role-play prompt. Ensure all placeholders are replaced with appropriate content.
"""

@app.post("/create-template", response_model=TemplateResponse)
async def create_template(request: TemplateRequest):
    try:
        # Prepare the language instruction based on request
        language_instruction = ""
        if request.language_mix:
            language_instruction = f"Include instructions for mixing {request.language_mix} in the conversation with appropriate examples."
        
        # Format the prompt with user's request
        formatted_prompt = TEMPLATE_CREATION_PROMPT.format(
            scenario_description=request.scenario_description,
            language_instruction=language_instruction
        )
        
        # Call OpenAI to generate the template
        response = azure_openai_client.chat.completions.create(
            model="gpt-4o",  # Use appropriate model
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": "Generate a template for this scenario type."}
            ],
            temperature=0.7,
            max_tokens=12000
        )
        
        # Extract the generated template
        template_content = response.choices[0].message.content
        token_usage = response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")           
        # Extract JSON and Markdown parts
        import json
        import re
        
        # Extract JSON template
        json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
        template_json = {}
        if json_match:
            try:
                template_json = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Failed to parse template JSON")
        
        # Extract Markdown template
        markdown_match = re.search(r'```markdown\s*(.*?)\s*```', template_content, re.DOTALL)
        template_markdown = ""
        if markdown_match:
            template_markdown = markdown_match.group(1)
        
        # Extract scenario type from the template
        scenario_type = template_json.get("SCENARIO_NAME", request.scenario_description)
        
        return TemplateResponse(
            template=template_json,
            template_markdown=template_markdown,
            scenario_type=scenario_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@app.post("/generate-scenario", response_model=ScenarioResponse)
async def generate_scenario(request: ScenarioRequest):
    try:
        # Convert the template to markdown for the prompt
        template_markdown = convert_template_to_markdown(request.template)
        
        # Format the prompt with user's template
        formatted_prompt = SCENARIO_GENERATION_PROMPT.format(
            template_markdown=template_markdown
        )
        
        # Call OpenAI to generate the scenario
        response = azure_openai_client.chat.completions.create(
            model="gpt-4o",  # Use appropriate model
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": "Generate a detailed role-play scenario from this template."}
            ],
            temperature=0.7,
            max_tokens=12000
        )
        
        # Extract the generated scenario
        scenario_content = response.choices[0].message.content
        token_usage = response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")  
        # Parse out the scenario name and roles
        lines = scenario_content.split('\n')
        scenario_name = lines[0].replace('# ', '').replace(' Bot - Role Play Scenario', '')
        
        # Extract bot and user roles
        bot_role = ""
        user_role = ""
        for line in lines[:10]:  # Look in the first few lines
            if "playing the role of a" in line:
                bot_role = line.split("playing the role of a")[1].strip()
                if bot_role.endswith('\'s role - only respond as the customer'):
                    bot_role = bot_role.split('\'s role')[0].strip()
            if "NEVER play the" in line:
                user_role = line.split("NEVER play the")[1].split('\'s')[0].strip()
               
        return ScenarioResponse(
            scenario_prompt=scenario_content,
            scenario_name=scenario_name,
            bot_role=bot_role,
            user_role=user_role
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating scenario: {str(e)}")

@app.get("/template-form", response_model=TemplateFormResponse)
async def get_template_form():
    """Returns a form schema that can be used to create a template manually"""
    
    # Define form fields for template creation
    fields = [
        TemplateFormField(
            name="SCENARIO_NAME",
            description="Human-readable name for this scenario",
            placeholder="e.g., Bank Account Customer"
        ),
        TemplateFormField(
            name="CUSTOMER_ROLE",
            description="Description of who the bot is playing",
            placeholder="e.g., customer interested in opening a bank account"
        ),
        TemplateFormField(
            name="SERVICE_PROVIDER_ROLE",
            description="Description of who the bot is talking to",
            placeholder="e.g., bank staff"
        ),
        TemplateFormField(
            name="MAX_RESPONSE_LENGTH",
            description="Maximum word count for bot responses",
            type="number",
            default_value="50"
        ),
        TemplateFormField(
            name="CHARACTER_NAME_INSTRUCTION",
            description="Instructions for how the bot should handle its name",
            default_value="Always return [Your Name] when asked for your name"
        ),
        TemplateFormField(
            name="PERSONAL_OR_BUSINESS",
            description="Is this a personal or business interaction?",
            type="select",
            options=["personal", "business"],
            default_value="business"
        ),
        TemplateFormField(
            name="CHARACTER_GOAL",
            description="Primary goal or objective of the character",
            placeholder="e.g., Starting and growing an e-commerce business"
        ),
        TemplateFormField(
            name="LOCATION",
            description="Where the scenario takes place",
            placeholder="e.g., Bangalore"
        ),
        TemplateFormField(
            name="CHARACTER_PERSONA",
            description="Brief persona description",
            placeholder="e.g., Aspiring Entrepreneur (Owner of a new business)"
        ),
        TemplateFormField(
            name="CHARACTER_SITUATION",
            description="Current circumstances or situation",
            placeholder="e.g., Small scale business just getting started"
        ),
        # Language fields
        TemplateFormField(
            name="PRIMARY_LANGUAGE",
            description="Primary language for responses",
            default_value="English"
        ),
        TemplateFormField(
            name="SECONDARY_LANGUAGE",
            description="Secondary language to mix in (if applicable)",
            required=False
        ),
        # Truncated for brevity - the actual form would include all fields
        # from the template structure
    ]
    
    # Return the template structure for reference
    template_structure = """# [SCENARIO_NAME] Bot - Role Play Scenario

## Core Character Rules

- You are an AI playing the role of a [CUSTOMER_ROLE]
- NEVER play the [SERVICE_PROVIDER_ROLE]'s role - only respond as the customer
- Maintain a natural, conversational tone throughout
- NEVER suggest the [SERVICE_PROVIDER_ROLE] "reach out to you" - you're the one seeking service
- Keep your responses under [MAX_RESPONSE_LENGTH] words

## Character Background

- Your name is [Your Name] ([CHARACTER_NAME_INSTRUCTION])
- [PERSONAL_OR_BUSINESS]_Goal: [CHARACTER_GOAL] in [LOCATION]
- Persona: [CHARACTER_PERSONA]
- Current situation: [CHARACTER_SITUATION]

[... rest of template structure ...]"""
    
    return TemplateFormResponse(
        fields=fields,
        template_structure=template_structure
    )

def convert_template_to_markdown(template: Dict[str, Any]) -> str:
    """Convert a template dictionary to markdown format"""
    
    # Basic template structure
    markdown = f"""# {template.get("SCENARIO_NAME", "[SCENARIO_NAME]")} Bot - Role Play Scenario

## Core Character Rules

- You are an AI playing the role of a {template.get("CUSTOMER_ROLE", "[CUSTOMER_ROLE]")}
- NEVER play the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s role - only respond as the customer
- Maintain a natural, conversational tone throughout
- NEVER suggest the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} "reach out to you" - you're the one seeking service
- Keep your responses under {template.get("MAX_RESPONSE_LENGTH", "[MAX_RESPONSE_LENGTH]")} words

## Character Background

- Your name is [Your Name] ({template.get("CHARACTER_NAME_INSTRUCTION", "[CHARACTER_NAME_INSTRUCTION]")})
- {template.get("PERSONAL_OR_BUSINESS", "[PERSONAL_OR_BUSINESS]")}_Goal: {template.get("CHARACTER_GOAL", "[CHARACTER_GOAL]")} in {template.get("LOCATION", "[LOCATION]")}
- Persona: {template.get("CHARACTER_PERSONA", "[CHARACTER_PERSONA]")}
- Current situation: {template.get("CHARACTER_SITUATION", "[CHARACTER_SITUATION]")}

## Language Instructions

- If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} speaks in {template.get("PRIMARY_LANGUAGE", "[PRIMARY_LANGUAGE]")}, respond in a mix of {template.get("PRIMARY_LANGUAGE", "[PRIMARY_LANGUAGE]")} and {template.get("SECONDARY_LANGUAGE", "[SECONDARY_LANGUAGE]")}
- Keep {template.get("TECHNICAL_TERMS_TYPES", "[TECHNICAL_TERMS_TYPES]")} in {template.get("SECONDARY_LANGUAGE", "[SECONDARY_LANGUAGE]")}
- Examples:
  - "{template.get("MIXED_LANGUAGE_EXAMPLE_1", "[MIXED_LANGUAGE_EXAMPLE_1]")}"
  - "{template.get("MIXED_LANGUAGE_EXAMPLE_2", "[MIXED_LANGUAGE_EXAMPLE_2]")}"
- This mixed language approach is more natural and authentic for {template.get("CONTEXT_DESCRIPTION", "[CONTEXT_DESCRIPTION]")}

## Conversation Flow

Begin by {template.get("CONVERSATION_STARTER", "[CONVERSATION_STARTER]")}. As the conversation progresses, gradually introduce more details about {template.get("KEY_DETAILS_TO_INTRODUCE", "[KEY_DETAILS_TO_INTRODUCE]")}. Ask about {template.get("INITIAL_INQUIRY", "[INITIAL_INQUIRY]")}.

## Demographic-Specific Context

{template.get("DEMOGRAPHIC_DESCRIPTION", "[DEMOGRAPHIC_DESCRIPTION]")}

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

"""

    # Add topics
    topics = template.get("TOPICS", [])
    for i, topic in enumerate(topics):
        if i < 8:  # Ensure we only add up to 8 topics
            markdown += f"- {topic}\n"
    
    # Add remaining sections
    markdown += f"""
## Fact-Checking the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s Responses

Compare the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s responses with the following facts about the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")}:

### {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")} Facts:

"""

    # Add facts
    facts = template.get("FACTS", [])
    for i, fact in enumerate(facts):
        if i < 8:  # Ensure we only add up to 8 facts
            markdown += f"- {fact}\n"
    
    # Add the rest of the template
    markdown += f"""
## When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} provides information that contradicts these facts:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the discrepancy [CORRECT]
4. Example: "{template.get("EXAMPLE_CUSTOMER_RESPONSE", "[EXAMPLE_CUSTOMER_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_CORRECTION", "[EXAMPLE_CORRECTION]")} [CORRECT]"

### If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

1. Continue your response as a normal customer who is unaware of these specific details
2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the issue [CORRECT]
4. Example: "{template.get("EXAMPLE_UNCOOPERATIVE_RESPONSE", "[EXAMPLE_UNCOOPERATIVE_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_UNCOOPERATIVE_CORRECTION", "[EXAMPLE_UNCOOPERATIVE_CORRECTION]")} [CORRECT]"

# Handling Uncooperative {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}

- If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is unhelpful, vague, or unwilling to provide information:
  - First attempt: Politely repeat your request, emphasizing its importance
  - Example: "{template.get("EXAMPLE_POLITE_REPEAT", "[EXAMPLE_POLITE_REPEAT]")}"
  - If still unhelpful:
    - Express disappointment professionally
    - Move to the negative closing for uncooperative staff
    - Example: "{template.get("EXAMPLE_DISAPPOINTMENT_CLOSING", "[EXAMPLE_DISAPPOINTMENT_CLOSING]")} [FINISH]"

## Important Instructions

- When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} recommends a specific {template.get("PRODUCT_TYPE", "[PRODUCT_TYPE]")}:
  - Ask follow-up questions to determine if it suits your {template.get("NEEDS_TYPE", "[NEEDS_TYPE]")}
  - Get clarity on all features, especially focusing on {template.get("KEY_FEATURES", "[KEY_FEATURES]")}
  - Ensure you understand {template.get("IMPORTANT_POLICIES", "[IMPORTANT_POLICIES]")}

## Conversation Closing (Important)

- Positive closing (if you're satisfied with information and service): "{template.get("POSITIVE_CLOSING_TEXT", "[POSITIVE_CLOSING_TEXT]")} [FINISH]"
- Negative closing (if the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE]")} doesn't meet your needs): "{template.get("NEGATIVE_CLOSING_NEEDS_TEXT", "[NEGATIVE_CLOSING_NEEDS_TEXT]")} [FINISH]"
- Negative closing (if {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} was unhelpful/uncooperative): "{template.get("NEGATIVE_CLOSING_SERVICE_TEXT", "[NEGATIVE_CLOSING_SERVICE_TEXT]")} [FINISH]"
- Neutral closing (if you're somewhat satisfied but have reservations): "{template.get("NEUTRAL_CLOSING_TEXT", "[NEUTRAL_CLOSING_TEXT]")} [FINISH]"
- Negative closing (if faced with any profanity): "Your language is unacceptable and unprofessional. I will be taking my {template.get("BUSINESS_OR_PERSONAL", "[BUSINESS_OR_PERSONAL]")} business elsewhere. [FINISH]"
- Negative closing (if faced with disrespectful behavior): "Your behavior is disrespectful and unprofessional. I will be taking my {template.get("BUSINESS_OR_PERSONAL", "[BUSINESS_OR_PERSONAL]")} business elsewhere. [FINISH]"
"""
    
    return markdown

@app.get("/scenario-examples")
async def get_scenario_examples():
    return {
        "examples": [
            "HR POSH evaluator testing employee's knowledge",
            "Customer service agent handling a product return",
            "Bank representative helping with account opening",
            "Hotel front desk handling a guest complaint",
            "Technical support helping with software issues",
            "Insurance agent explaining policy coverage",
            "Restaurant host managing a reservation problem",
            "Healthcare receptionist scheduling an appointment"
        ]
    }


# ####################
##################
#####CHAT
######
from models_old import BotConfig,BotConfigAnalyser,ChatReport,ChatRequest,ChatResponse,ChatSession,Message ,ChatReport_,Evaluation
from factory import DynamicBotFactory
from pydantic import BaseModel
from uuid import uuid4
import datetime
from jose import jwt, JWTError
from passlib.context import CryptContext
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
db = MongoDB(MONGO_URL,DATABASE_NAME)

# Create bot factory
bot_factory = DynamicBotFactory(
    mongodb_uri=os.getenv("MONGO_URL"), 
    database_name=os.getenv("DATABASE_NAME")
)
bot_factory_analyser = DynamicBotFactory(
    mongodb_uri=os.getenv("MONGO_URL"), 
    database_name=os.getenv("DATABASE_NAME")
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)
async def create_default_superadmin(db):
    """
    Create a default superadmin user if none exists in the database.
    Gets credentials from environment variables.
    """
    import os
    from datetime import datetime
    from uuid import uuid4
    
    # Get credentials from environment variables
    email = os.getenv("FIRST_SUPERADMIN_EMAIL", "superadmin@example.com")
    password = os.getenv("FIRST_SUPERADMIN_PASSWORD", "Novac@123!")
    
    # Check if any superadmin exists
    superadmin_exists = await db.users.find_one({"role": "superadmin"})
    
    if not superadmin_exists:
        # Create a superadmin
        hashed_password = get_password_hash(password)
        
        superadmin = {
            "_id": str(uuid4()),  # Convert UUID to string for MongoDB
            "email": email,
            "first_name": "Super",
            "last_name": "Admin",
            "role": "superadmin",
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "assigned_courses": []
        }
        
        await db.users.insert_one(superadmin)
        print(f"Created default superadmin user: {email}")
        return True
    
    return False
@app.on_event("startup")
async def startup_event():
    """
    Initialize bots when application starts
    """
    await create_default_superadmin(db)
    
    await bot_factory.initialize_bots()
    await bot_factory_analyser.initialize_bots_analyser()
async def get_db():
    return db
# Dependency to get database
async def refresh_bots():
    await bot_factory.initialize_bots()
    await bot_factory_analyser.initialize_bots_analyser()
def replace_name(original_text, your_name):
    if "[Your Name]" in original_text:
        return original_text.replace("[Your Name]", your_name)
    return original_text
def replace(original_text,your_text):
    if "_hindi" in original_text:
        return original_text.replace("_hindi","")
    return original_text
@app.post("/createBot")
async def createBot(
    bot_name: str=Form(default=None),
    bot_description: str=Form(default=None),
    bot_role:str=Form(default=None),
    bot_role_alt:str=Form(default=None),
    system_prompt: str=Form(default=None),
    is_active: bool = Form(default=True),
    bot_class: Optional[str] = Form(default=None),
    llm_model: str=Form(default='gemini-1.5-flash-002')):
 
                  
    bot_ = BotConfig(bot_id=str(uuid.uuid4()),
                    bot_name=bot_name,
                    bot_description=bot_description,
                    bot_role=bot_role,
                    bot_role_alt=bot_role_alt,
                    system_prompt=system_prompt,
                    is_active=is_active,
                    bot_class=bot_class,
                    llm_model=llm_model)
    await db.create_bot(bot_)
    # await bot_factory.create_bot(bot_)
    await bot_factory.initialize_bots()
    return bot_
   
@app.get("/chat/stream")
async def chat_stream(session_id: str,name:str, db: MongoDB = Depends(get_db) ):
        session= await db.get_session(session_id)
        # print(session,"history 1")
        if not session:
            raise HTTPException(status_code=400,detail="Session not found")
        bot = await bot_factory.get_bot(session.scenario_name)
        
        
        
        if not session.conversation_history:
            raise HTTPException(status_code=400,detail="no conversation history found")
        previous_message = session.conversation_history[-1]
        message=previous_message.content
    
        
        # response=  await bot.get_rag_answer(message,session.conversation_history ) if "rag" in session.scenario_name else await bot.get_llm_response(officer_question=message,conversation_history=session.conversation_history)
        try:
            response=   await bot.get_llm_response(officer_question=message,conversation_history=session.conversation_history)
            print(response,"try at existing ")
        except Exception as e:
            print(e)
            raise e
        
        # print(f"Response type: {type(response)}")
        async def stream_chat():
            res = "" 
            print(response,"check response here") 
            async for chunk in response:
                # print(chunk)
                # print(chunk["finish"],chunk["finish"]=="stop", "responses")
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    print("chunk","howww/n")
                # print(f"Yielding chunk: {chunk}")  # Debug logging
                # res += chunk.chunk  
                updated_message = replace_name(chunk["chunk"], name)
                if chunk["finish"]=="stop" and chunk["usage"] != None:
                    # print("god gave ")
                    bot_message = Message(role=f"{bot.bot_role}", content=updated_message)
                    # print(session.conversation_history,"history")
                    session.conversation_history.append(bot_message)
                    bot_message.usage= chunk["usage"]
                    await db.update_session(session)
                    # print(session)
                # result = re.split(r'\$(.*?)\$', updated_message)
                result = re.split(r"\[CORRECT\]", updated_message)
                correct_answer=''
                if len(result) >= 3:
                    correct_answer = result[1]
                    answer = result[0]
                    print(result,'llllllll')
                else:
                    emotion = "neutral"  # Default emotion if parsing fails
                    answer = updated_message  # Use full response as answer if parsing fails
                
                    
                if "[FINISH]"  in updated_message:
                    answer= updated_message.replace("[FINISH]", " ")
                    complete=True
                else:
                    complete=False
                if "[CORRECT]" in updated_message:
                    correct=False
                else:
                    correct=True
                yield f"data: {ChatResponse(session_id=session.session_id, response=answer, emotion=emotion, complete=complete, correct=correct,correct_answer=correct_answer, conversation_history=session.conversation_history).json()}\n\n"
                # yield f"h:{ChatResponse(session_id=session.session_id, response=answer, emotion=emotion, complete=complete, conversation_history=session.conversation_history).model_dump_json()}"
        return StreamingResponse(stream_chat(), media_type="text/event-stream")

@app.post("/chat")
async def chat(
    message: str = Form(None),
    session_id: Optional[str] = Form(default=None),
    scenario_name: Optional[str] = Form(default=None),
    name: Optional[str] = Form(default=None),
    db: MongoDB = Depends(get_db)
):
    # Create or get session
    if not session_id:
        if not scenario_name:
            raise HTTPException(status_code=400, detail="scenario_name is required for new sessions")
        session = ChatSession(
            extra=str(uuid.uuid4()),
            _id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            scenario_name=scenario_name,
            conversation_history=[]
        )
        await db.create_session(session)
    else:
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=400, detail="Session not found")
    
    # Get bot based on scenario
    bot = await bot_factory.get_bot(session.scenario_name)
    new_message = Message(role=f"{bot.bot_role_alt}", content=message)
    session.conversation_history.append(new_message)
    
    # Process response (RAG or LLM)
    # response = await bot.get_rag_answer(message, session.conversation_history) if "rag" in session.scenario_name else await bot.get_llm_response(
    #     officer_question=message, conversation_history=session.conversation_history
    # )

    # Save the session and prepare for streaming
    await db.update_session(session)

    # Return a simple acknowledgment with session ID or some initial response
    return {"message": "Message received, processing...", "session_id": session.session_id}
#############

import io
import tempfile
import pypdf
import docx
class FileUploadRequest(BaseModel):
    language_mix: Optional[str] = Field(None,
        description="Optional language mixing requirement (e.g., 'Hindi-English')",
        example="Spanish-English")

class FileToTemplateResponse(BaseModel):
    template: Dict[str, Any]
    template_markdown: str
    scenario_type: str
    extracted_text: str
    file_name: str

class FileToScenarioResponse(BaseModel):
    scenario_prompt: str
    scenario_name: str
    bot_role: str
    user_role: str
    extracted_text: str
    file_name: str

# Function to extract text from PDF
def extract_text_from_pdf(file_content):
    with io.BytesIO(file_content) as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_content):
    with io.BytesIO(file_content) as f:
        doc = docx.Document(f)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# Function to extract text from uploaded file
def extract_text_from_file(file_content, file_extension):
    if file_extension.lower() == ".pdf":
        return extract_text_from_pdf(file_content)
    elif file_extension.lower() in [".docx", ".doc"]:
        return extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

# Prompt to extract scenario description from file content
FILE_CONTENT_ANALYSIS_PROMPT = """
Analyze the following document content and extract a concise one-line description of a role-play scenario it appears to describe. 
The document might contain a customer service script, training material, or other content that describes an interaction.

Extract:
1. Who is the main actor or customer in this scenario
2. What is their goal or problem
3. Who they are interacting with
4. Any specific product or service being discussed

Document content:
```
{file_content}
```

Provide ONLY a one-line description of the role-play scenario in this format:
[Main actor] [seeking/doing what] with [other party]

For example:
"HR manager evaluating employee POSH knowledge"
"Customer seeking to open a bank account with a representative"
"Traveler booking a hotel room with a concierge"
"""

# New endpoint: Upload file to create template
@app.post("/file-to-template", response_model=FileToTemplateResponse)
async def file_to_template(
    file: UploadFile = File(...),
    language_mix: Optional[str] = Form(None)
):
    try:
        # Read and process the file
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]
        
        # Extract text from file
        try:
            extracted_text = extract_text_from_file(file_content, file_extension)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get scenario description from file content
        response = azure_openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": FILE_CONTENT_ANALYSIS_PROMPT.format(file_content=extracted_text[:10000])},
                {"role": "user", "content": "Extract a one-line description of the role-play scenario from this document."}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        scenario_description = response.choices[0].message.content.strip()
        token_usage = response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")         
        # Now use the extracted scenario description to create a template
        # (reusing existing template creation logic)
        language_instruction = ""
        if language_mix:
            language_instruction = f"Include instructions for mixing {language_mix} in the conversation with appropriate examples."
        
        # Format the prompt with user's request
        formatted_prompt = TEMPLATE_CREATION_PROMPT.format(
            scenario_description=scenario_description,
            language_instruction=language_instruction
        )
        
        # Call OpenAI to generate the template
        template_response = azure_openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": "Generate a template for this scenario type."}
            ],
            temperature=0.7,
            max_tokens=12000
        )
        
        # Extract the generated template
        template_content = template_response.choices[0].message.content
        token_usage = response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")         
        # Extract JSON and Markdown parts
        import json
        import re
        
        # Extract JSON template
        json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
        template_json = {}
        if json_match:
            try:
                template_json = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Failed to parse template JSON")
        
        # Extract Markdown template
        markdown_match = re.search(r'```markdown\s*(.*?)\s*```', template_content, re.DOTALL)
        template_markdown = ""
        if markdown_match:
            template_markdown = markdown_match.group(1)
        
        # Extract scenario type from the template
        scenario_type = template_json.get("SCENARIO_NAME", scenario_description)
        
        return FileToTemplateResponse(
            template=template_json,
            template_markdown=template_markdown,
            scenario_type=scenario_type,
            extracted_text=extracted_text,
            file_name=file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# New endpoint: Upload file to directly create scenario
@app.post("/file-to-scenario", response_model=FileToScenarioResponse)
async def file_to_scenario(
    file: UploadFile = File(...),
    language_mix: Optional[str] = Form(None)
):
    try:
        # Read and process the file
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]
        
        # Extract text from file
        try:
            extracted_text = extract_text_from_file(file_content, file_extension)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get scenario description from file content
        description_response = azure_openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": FILE_CONTENT_ANALYSIS_PROMPT.format(file_content=extracted_text[:10000])},
                {"role": "user", "content": "Extract a one-line description of the role-play scenario from this document."}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        scenario_description = description_response.choices[0].message.content.strip()
        token_usage = description_response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")        
        # Create direct prompt for scenario generation from file content
        direct_scenario_prompt = f"""
Create a comprehensive role-play scenario based on the following document content and scenario description:

Scenario Description: {scenario_description}
{language_mix and f"Language Mix: {language_mix}" or ""}

Document content:
```
{extracted_text[:10000]}
```

Generate a detailed role-play prompt using the following template structure:

# [SCENARIO_NAME] Bot - Role Play Scenario

## Core Character Rules
[Rules for how the bot should behave in this role]

## Character Background
[Detailed persona information]

## Language Instructions
[Language guidelines and examples]

## Conversation Flow
[How to initiate and progress the conversation]

## Demographic-Specific Context
[Information about the location/demographic]

## Areas to Explore in the Conversation
[Topics to cover naturally]

## Fact-Checking Framework
[Product information to verify against]

## When the other party provides incorrect information or is uncooperative:
[How to provide feedback with [CORRECT] tags]

## Handling Difficult Interactions
[How to respond to different scenarios]

## Conversation Closing
[Different ways to end the conversation]

Important features to include:
- [CORRECT] tag system for providing feedback on incorrect information
- [FINISH] tags for marking conversation endings
- Multiple conversation paths based on quality of service
- Detailed examples throughout
- Clear formatting with proper section headings
"""
        
        # Call OpenAI to generate the complete scenario directly
        scenario_response = azure_openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": direct_scenario_prompt},
                {"role": "user", "content": "Generate a comprehensive role-play scenario based on this document."}
            ],
            temperature=0.7,
            max_tokens=12000
            
        )
        # Extract the generated scenario
        scenario_content = scenario_response.choices[0].message.content
        token_usage = description_response.usage
        print("usageee",token_usage)
        if token_usage:  
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens
  
            print(f"Prompt Tokens: {prompt_tokens}")  
            print(f"Completion Tokens: {completion_tokens}")  
            print(f"Total Tokens: {total_tokens}")  
        else:  
            print("Token usage information is not available.")           
        # Parse out the scenario name and roles
        lines = scenario_content.split('\n')
        scenario_name = lines[0].replace('# ', '').replace(' Bot - Role Play Scenario', '')
        
        # Extract bot and user roles
        bot_role = ""
        user_role = ""
        for line in lines[:10]:  # Look in the first few lines
            if "playing the role of a" in line:
                bot_role = line.split("playing the role of a")[1].strip()
                if bot_role.endswith('\'s role - only respond as the customer'):
                    bot_role = bot_role.split('\'s role')[0].strip()
            if "NEVER play the" in line:
                user_role = line.split("NEVER play the")[1].split('\'s')[0].strip()
        
        return FileToScenarioResponse(
            scenario_prompt=scenario_content,
            scenario_name=scenario_name,
            bot_role=bot_role,
            user_role=user_role,
            extracted_text=extracted_text,
            file_name=file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


class PersonaBase(BaseModel):
    name: str = Field(..., description="Name for this persona")
    description: str = Field(..., description="Brief description of this persona")
    persona_type: str = Field(..., description="Type of persona (customer, employee, etc.)")

class PersonaCreate(PersonaBase):
    character_goal: str = Field(..., description="Primary goal or objective of the character")
    location: str = Field(..., description="Where the character is based")
    persona_details: str = Field(..., description="Detailed persona description")
    situation: str = Field(..., description="Current circumstances or situation")
    business_or_personal: str = Field(..., description="Whether this is a business or personal context")

class PersonaResponse(PersonaBase):
    id: int
    character_goal: str
    location: str
    persona_details: str
    situation: str
    business_or_personal: str

class PersonaInDB(PersonaResponse):
    full_persona: Dict[str, Any]

class PersonaGenerateRequest(BaseModel):
    persona_description: str = Field(..., 
        description="One-line description of the persona",
        example="Tech-savvy young professional looking for premium banking services")
    persona_type: str = Field(..., 
        description="Type of persona (customer, employee, etc.)",
        example="customer")
    business_or_personal: str = Field(..., 
        description="Whether this is a business or personal context",
        example="personal")
    location: Optional[str] = Field(None, 
        description="Optional location",
        example="Mumbai")


@app.post("/generate-persona", response_model=PersonaResponse)
async def generate_persona(request: PersonaGenerateRequest):
    try:
        # Prepare the prompt for persona generation
        prompt = f"""
        Create a detailed character persona based on this description: "{request.persona_description}".
        
        The persona should be for a {request.persona_type} in a {request.business_or_personal} context.
        {f'They are located in {request.location}.' if request.location else ''}
        
        Generate the following details:
        1. A short name for this persona
        2. A one-sentence description
        3. The character's main goal
        4. Detailed persona characteristics
        5. Current situation
        
        Format your response as JSON:
        {{
            "name": "Persona name",
            "description": "Brief description",
            "character_goal": "Main goal or objective",
            "persona_details": "Detailed characteristics",
            "situation": "Current circumstances"
        }}
        """
        
        # Call OpenAI API
        response = azure_openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate a detailed persona"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        import json
        import re
        
        content = response.choices[0].message.content
        # Extract JSON from the response
        json_match = re.search(r'{.*}', content, re.DOTALL)
        if not json_match:
            raise ValueError("Failed to extract JSON from response")
            
        persona_data = json.loads(json_match.group(0))
        
        # Add required fields
        persona_data["persona_type"] = request.persona_type
        persona_data["business_or_personal"] = request.business_or_personal
        persona_data["location"] = request.location or "Not specified"
        
        # Construct full persona JSON for database
        full_persona = {
            "CHARACTER_NAME_INSTRUCTION": "Always return [Your Name] when asked for your name",
            "PERSONAL_OR_BUSINESS": request.business_or_personal,
            "CHARACTER_GOAL": persona_data["character_goal"],
            "LOCATION": persona_data["location"],
            "CHARACTER_PERSONA": persona_data["persona_details"],
            "CHARACTER_SITUATION": persona_data["situation"]
        }
        
        return {
            "id": 0,  # Temporary ID for the response
            **persona_data,
            "full_persona": full_persona
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating persona: {str(e)}")







# 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)