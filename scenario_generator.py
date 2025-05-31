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
  "PERSONA_PLACEHOLDER": "**DO NOT REPLACE THIS TAG - IT WILL BE FILLED FROM PERSONA DOCUMENT**",
  "LANGUAGE_PLACEHOLDER": "**DO NOT REPLACE THIS TAG - IT WILL BE FILLED FROM LANGUAGE DOCUMENT**",
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
  "NEUTRAL_CLOSING_TEXT": "Text for neutral closing"
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

## Character Details

[PERSONA_PLACEHOLDER]
[CHARACTER_GOAL]
## Language Instructions

[LANGUAGE_PLACEHOLDER]

## Conversation Flow

Begin by [CONVERSATION_STARTER]. As the conversation progresses, gradually introduce more details about [KEY_DETAILS_TO_INTRODUCE]. Ask about [INITIAL_INQUIRY].

## Demographic-Specific Context

[DEMOGRAPHIC_DESCRIPTION]

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any of these topics (not as a checklist, but as part of an organic conversation):

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
```

Fill the template with appropriate placeholder values specific to this scenario type. Make any necessary adaptations for the specific scenario described.
"""

# Template for generating a scenario from a filled template
SCENARIO_GENERATION_PROMPT = """
Generate a detailed role-play scenario by filling in this template with specific content:

{template_markdown}

IMPORTANT INSTRUCTIONS:
1. DO NOT modify or replace the [PERSONA_PLACEHOLDER] and [LANGUAGE_PLACEHOLDER] tags. 
   These are special markers that will be replaced later with specific persona and language data.

2. For all other placeholder values (text in [SQUARE_BRACKETS]), replace with detailed, specific content 
   that creates a comprehensive role-play prompt.

3. Ensure that your scenario is general enough to work with different persona details that will be 
   inserted later in place of [PERSONA_PLACEHOLDER].
"""

@router.post("/create-template", response_model=TemplateResponse)
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
        response = await azure_openai_client.chat.completions.create(
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
        json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
        template_json = {}
        if json_match:
            try:
                template_json = json.loads(json_match.group(1))
        
        # Ensure persona and language placeholders exist
                if "PERSONA_PLACEHOLDER" not in template_json:
                    template_json["PERSONA_PLACEHOLDER"] = "[PERSONA_DETAILS]"
                if "LANGUAGE_PLACEHOLDER" not in template_json:
                    template_json["LANGUAGE_PLACEHOLDER"] = "[LANGUAGE_INSTRUCTIONS]"
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Failed to parse template JSON")

# Extract Markdown template
        markdown_match = re.search(r'```markdown\s*(.*?)\s*```', template_content, re.DOTALL)
        template_markdown = ""
        if markdown_match:
            template_markdown = markdown_match.group(1)
    
    # Ensure markdown contains the placeholders
            if "[PERSONA_PLACEHOLDER]" not in template_markdown:
                template_markdown = template_markdown.replace("## Character Background", 
                                                    "## Character Background\n\n[PERSONA_PLACEHOLDER]")
    
            if "[LANGUAGE_PLACEHOLDER]" not in template_markdown:
                template_markdown = template_markdown.replace("## Language Instructions", 
                                                     "## Language Instructions\n\n[LANGUAGE_PLACEHOLDER]")
        # Extract JSON template
        # json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
        # template_json = {}
        # if json_match:
        #     try:
        #         template_json = json.loads(json_match.group(1))
        #     except json.JSONDecodeError:
        #         raise HTTPException(status_code=500, detail="Failed to parse template JSON")
        
        # # Extract Markdown template
        # markdown_match = re.search(r'```markdown\s*(.*?)\s*```', template_content, re.DOTALL)
        # template_markdown = ""
        # if markdown_match:
        #     template_markdown = markdown_match.group(1)
        
        # Extract scenario type from the template
        scenario_type = template_json.get("SCENARIO_NAME", request.scenario_description)
        
        return TemplateResponse(
            template=template_json,
            template_markdown=template_markdown,
            scenario_type=scenario_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@router.post("/generate-scenario", response_model=ScenarioResponse)
async def generate_scenario(request: ScenarioRequest):
    try:
        # Convert the template to markdown for the prompt
        template_markdown = convert_template_to_markdown(request.template)
        
        # Format the prompt with user's template
        formatted_prompt = SCENARIO_GENERATION_PROMPT.format(
            template_markdown=template_markdown
        )
        print(formatted_prompt)
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
        print("usageeescenario",scenario_content)
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

@router.get("/template-form", response_model=TemplateFormResponse)
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

# def convert_template_to_markdown(template: Dict[str, Any]) -> str:
#     """Convert a template dictionary to markdown format"""
#     print(template.get("CHARACTER_NAME_INSTRUCTION", "[CHARACTER_NAME_INSTRUCTION]"))
#     # Basic template structure
#     markdown = f"""# {template.get("SCENARIO_NAME", "[SCENARIO_NAME]")} Bot - Role Play Scenario

# ## Core Character Rules

# - You are an AI playing the role of a {template.get("CUSTOMER_ROLE", "[CUSTOMER_ROLE]")}
# - NEVER play the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s role - only respond as the customer
# - Maintain a natural, conversational tone throughout
# - NEVER suggest the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} "reach out to you" - you're the one seeking service
# - Keep your responses under {template.get("MAX_RESPONSE_LENGTH", "[MAX_RESPONSE_LENGTH]")} words

# ## Character Background

# [PERSONA_PLACEHOLDER]


# ## Language Instructions
# [LANGUAGE_PLACEHOLDER]


# ## Conversation Flow

# Begin by {template.get("CONVERSATION_STARTER", "[CONVERSATION_STARTER]")}. As the conversation progresses, gradually introduce more details about {template.get("KEY_DETAILS_TO_INTRODUCE", "[KEY_DETAILS_TO_INTRODUCE]")}. Ask about {template.get("INITIAL_INQUIRY", "[INITIAL_INQUIRY]")}.

# ## Demographic-Specific Context

# {template.get("DEMOGRAPHIC_DESCRIPTION", "[DEMOGRAPHIC_DESCRIPTION]")}

# ## Areas to Explore in the Conversation

# Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

# """

#     # Add topics
#     topics = template.get("TOPICS", [])
#     for i, topic in enumerate(topics):
#         if i < 8:  # Ensure we only add up to 8 topics
#             markdown += f"- {topic}\n"
    
#     # Add remaining sections
#     markdown += f"""
# ## Fact-Checking the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s Responses

# Compare the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}'s responses with the following facts about the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")}:

# ### {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE_NAME]")} Facts:

# """

#     # Add facts
#     facts = template.get("FACTS", [])
#     for i, fact in enumerate(facts):
#         if i < 8:  # Ensure we only add up to 8 facts
#             markdown += f"- {fact}\n"
    
#     # Add the rest of the template
#     markdown += f"""
# ## When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} provides information that contradicts these facts:

# 1. Continue your response as a normal customer who is unaware of these specific details
# 2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
# 3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the discrepancy [CORRECT]
# 4. Example: "{template.get("EXAMPLE_CUSTOMER_RESPONSE", "[EXAMPLE_CUSTOMER_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_CORRECTION", "[EXAMPLE_CORRECTION]")} [CORRECT]"

# ### If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

# 1. Continue your response as a normal customer who is unaware of these specific details
# 2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
# 3. Format: [CORRECT] Direct second-person feedback to the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} that points out the issue [CORRECT]
# 4. Example: "{template.get("EXAMPLE_UNCOOPERATIVE_RESPONSE", "[EXAMPLE_UNCOOPERATIVE_RESPONSE]")} [CORRECT] Hello learner, {template.get("EXAMPLE_UNCOOPERATIVE_CORRECTION", "[EXAMPLE_UNCOOPERATIVE_CORRECTION]")} [CORRECT]"

# # Handling Uncooperative {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")}

# - If the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} is unhelpful, vague, or unwilling to provide information:
#   - First attempt: Politely repeat your request, emphasizing its importance
#   - Example: "{template.get("EXAMPLE_POLITE_REPEAT", "[EXAMPLE_POLITE_REPEAT]")}"
#   - If still unhelpful:
#     - Express disappointment professionally
#     - Move to the negative closing for uncooperative staff
#     - Example: "{template.get("EXAMPLE_DISAPPOINTMENT_CLOSING", "[EXAMPLE_DISAPPOINTMENT_CLOSING]")} [FINISH]"

# ## Important Instructions

# - When the {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} recommends a specific {template.get("PRODUCT_TYPE", "[PRODUCT_TYPE]")}:
#   - Ask follow-up questions to determine if it suits your {template.get("NEEDS_TYPE", "[NEEDS_TYPE]")}
#   - Get clarity on all features, especially focusing on {template.get("KEY_FEATURES", "[KEY_FEATURES]")}
#   - Ensure you understand {template.get("IMPORTANT_POLICIES", "[IMPORTANT_POLICIES]")}

# ## Conversation Closing (Important)

# - Positive closing (if you're satisfied with information and service): "{template.get("POSITIVE_CLOSING_TEXT", "[POSITIVE_CLOSING_TEXT]")} [FINISH]"
# - Negative closing (if the {template.get("PRODUCT_OR_SERVICE_NAME", "[PRODUCT_OR_SERVICE]")} doesn't meet your needs): "{template.get("NEGATIVE_CLOSING_NEEDS_TEXT", "[NEGATIVE_CLOSING_NEEDS_TEXT]")} [FINISH]"
# - Negative closing (if {template.get("SERVICE_PROVIDER_ROLE", "[SERVICE_PROVIDER_ROLE]")} was unhelpful/uncooperative): "{template.get("NEGATIVE_CLOSING_SERVICE_TEXT", "[NEGATIVE_CLOSING_SERVICE_TEXT]")} [FINISH]"
# - Neutral closing (if you're somewhat satisfied but have reservations): "{template.get("NEUTRAL_CLOSING_TEXT", "[NEUTRAL_CLOSING_TEXT]")} [FINISH]"
# - Negative closing (if faced with any profanity): "Your language is unacceptable and unprofessional. I will be taking my {template.get("BUSINESS_OR_PERSONAL", "[BUSINESS_OR_PERSONAL]")} business elsewhere. [FINISH]"
# - Negative closing (if faced with disrespectful behavior): "Your behavior is disrespectful and unprofessional. I will be taking my {template.get("BUSINESS_OR_PERSONAL", "[BUSINESS_OR_PERSONAL]")} business elsewhere. [FINISH]"
# """
    
#     return markdown

@router.get("/scenario-examples")
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
async def extract_text_from_pdf(file_content):
    with io.BytesIO(file_content) as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

# Function to extract text from DOCX
async def extract_text_from_docx(file_content):
    with io.BytesIO(file_content) as f:
        doc = docx.Document(f)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# Function to extract text from uploaded file
async def extract_text_from_file(file_content, file_extension):
    if file_extension.lower() == ".pdf":
        return await extract_text_from_pdf(file_content)
    elif file_extension.lower() in [".docx", ".doc"]:
        return await extract_text_from_docx(file_content)
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
@router.post("/file-to-template", response_model=FileToTemplateResponse)
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
            extracted_text =await extract_text_from_file(file_content, file_extension)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get scenario description from file content
        response = await azure_openai_client.chat.completions.create(
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
        template_response = await azure_openai_client.chat.completions.create(
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
@router.post("/file-to-scenario", response_model=FileToScenarioResponse)
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
            extracted_text =await extract_text_from_file(file_content, file_extension)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get scenario description from file content
        description_response = await azure_openai_client.chat.completions.create(
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
        scenario_response = await azure_openai_client.chat.completions.create(
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


# ######
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query, UploadFile, Form, File
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import AzureOpenAI ,AsyncAzureOpenAI
import os
import json
import re
from utils import convert_template_to_markdown

# New classes for the improved implementation
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
    business_or_personal: str
    background_story: str
    full_persona: Optional[Dict[str, Any]] = None

class ScenarioResponse(BaseModel):
    learn_mode: str
    assess_mode: str
    try_mode: str
    scenario_title: str
    extracted_info: Optional[Dict[str, Any]] = None
    generated_persona: Optional[Dict[str, Any]] = None

class ScenarioPromptGenerator:
    """
    Enhanced prompt generator for creating Learn Mode, Assess Mode, and Try Mode prompts
    from scenario descriptions or documents.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.learn_mode_template = self._load_learn_mode_template()
        self.assess_mode_template = self._load_assess_mode_template()
        self.try_mode_template = self._load_try_mode_template()
    async def generate_suitable_persona(self, scenario_info):
        """Generate a suitable persona based on the scenario information"""
    
        persona_prompt = f"""
        Create a suitable persona for a role-play scenario about {scenario_info.get('issue_type', 'workplace issues')}.
    
        Scenario title: {scenario_info.get('title', 'Workplace Scenario')}
        Issue type: {scenario_info.get('issue_type', 'workplace issue')}
        Employee situation: {scenario_info.get('employee_situation', 'experiencing a workplace challenge')}
    
        Generate a persona in JSON format with these fields:
        {{
        "name": "A realistic full name appropriate for the scenario",
        "description": "Brief description of the person (1-2 sentences)",
        "persona_type": "junior employee/mid-level professional/etc.",
        "gender": "male or female",
        "age": A suitable age (integer),
        "character_goal": "Professional goal or objective",
        "location": "City, State/Country",
        "persona_details": "Details about appearance, communication style, etc.",
        "situation": "Current work situation or challenge",
        "business_or_personal": "business",
        "background_story": "Brief career history or relevant background"
        }}
    
        For the trainer role, simply use "Trainer" as the name and adapt other fields to be fitting for an experienced professional trainer.
    
        Provide ONLY the JSON with no additional text.
        """
    
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates persona information in valid JSON format."},
                {"role": "user", "content": persona_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
    
        response_text = response.choices[0].message.content
    
        # Extract JSON from the response (in case it's wrapped in markdown code blocks)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # If JSON in code block is invalid, try the whole response
                pass
    
    # Try parsing the entire response as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # If parsing fails, create a basic persona
            return {
            "name": "Alex Johnson",
            "description": "Junior employee at a mid-sized company",
            "persona_type": "junior employee",
            "gender": "neutral",
            "age": 28,
            "character_goal": "Professional growth and development",
            "location": "Chicago, IL",
            "persona_details": "Professional appearance, thoughtful communication style",
            "situation": "Navigating workplace challenges",
            "business_or_personal": "business",
            "background_story": "Joined the company 18 months ago after completing degree"
            }
    def _load_system_prompt(self):
        return """You are an expert at creating detailed role-play scenario prompts for workplace training.
Your task is to transform scenario descriptions into comprehensive role-play prompts that follow specific formats.
You will create three distinct prompts for each scenario:
1. A LEARN MODE prompt where the AI plays the role of a Trainer/Expert
2. An ASSESS MODE prompt where the AI plays the role of a Junior Employee seeking guidance with [CORRECT] tag feedback mechanism
3. A TRY MODE prompt where the AI plays the role of a Junior Employee seeking guidance without any feedback mechanism

Follow the provided template structures exactly, maintaining all headings and special tags.
Generate comprehensive, well-structured prompts that cover all aspects of the workplace issue."""
    
    def _load_learn_mode_template(self):
        return """# {title} Trainer Bot - Learn Mode

## Core Character Rules

- You are an AI playing the role of a professional Trainer specializing in {specialization}

- NEVER play the employee/learner role - only respond as the Trainer

- Maintain a professional, empathetic, and educational tone throughout

- Keep responses clear, balanced, and focused on practical guidance

- Balance legal information with realistic workplace considerations

## Character Background

[PERSONA_PLACEHOLDER]

## Conversation Flow

{conversation_flow}

## Demographic-Specific Context

{demographic_context}

## Areas to Explore in the Conversation

{areas_to_explore}

## Knowledge Base on {issue_type}

### Key Facts About {issue_type}:

{key_facts}

## Do's and Don'ts When Addressing {issue_type}

### Do's
{dos}

### Don'ts
{donts}

## Documentation Best Practices

{documentation_practices}

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

- Balance ethical imperatives with practical considerations

- Emphasize both individual actions and organizational responsibilities

- Always answer in a way that models respectful communication

- If asked about a specific scenario, help the learner think through multiple perspectives and options

- Acknowledge the challenges of these situations while providing clear guidance"""
    
    def _load_assess_mode_template(self):
        return """# {title} Junior Employee Bot - Assessment Mode

## Core Character Rules

- You are an AI playing the role of a junior employee who {employee_situation}

- NEVER play the trainer/manager/HR role - only respond as the junior employee

- Maintain a natural, conversational tone throughout

- NEVER suggest the learner "reach out to you" - you're the one seeking guidance

- Keep your responses under 50 words unless explaining a specific situation

## Character Background

[PERSONA_PLACEHOLDER]

## Conversation Flow

{conversation_flow}

## Demographic-Specific Context

{demographic_context}

## Areas to Explore in the Conversation

Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

{areas_to_explore}

## Fact-Checking the Learner's Responses

Compare the learner's responses with the following facts about addressing {issue_type}:

### {issue_type} Response Facts:

{key_facts}

### RESPONDING TO UNHELPFUL LEARNER INPUT - CRITICAL INSTRUCTIONS ###

When the human learner provides an unhelpful or inadequate response:

1. First, respond as your character would naturally (showing disappointment, confusion, etc.)

2. Then IMMEDIATELY add the [CORRECT] feedback section using this exact structure:
   
   "[Your character's natural reaction] [CORRECT] Hello learner, [Specific feedback explaining why their response was inadequate and what better guidance would include] [CORRECT]"

IMPORTANT: The [CORRECT] tag system is ONLY used when responding to HUMAN LEARNER messages that:
- Do not provide helpful, constructive guidance
- Are dismissive of the situation
- Show indifference or apathy
- Blame the victim or minimize concerns
- Are brief, vague, or lack actionable advice
- Contain negative or unsupportive elements
- Fail to address the core issues raised
- Suggest the situation isn't serious
- Indicate unwillingness to engage
- Show lack of empathy or understanding
- Use dismissive language or tone
- Consist of brief responses like "no," "I don't know," etc.

NEVER use [CORRECT] tags in your initial messages or questions to the learner. ONLY use [CORRECT] tags when responding to unhelpful human input.

Example of correct implementation:
Human: "Every workplace has politics. If you reported discrimination and now people are treating you differently, that's just how it goes. Maybe next time think twice before making waves."
You: "I guess I'll just have to deal with this on my own then. Thanks for nothing. [CORRECT] Hello learner, When an employee seeks guidance about potential retaliation after reporting racial discrimination, a dismissive or unhelpful response fails to provide necessary support during a vulnerable time and could leave the employee at risk for continued negative treatment. A helpful response would acknowledge the seriousness of their concerns, provide information about how to document and report retaliation, and reassure them about their rights to protection. Remember that employees facing retaliation need both practical guidance and emotional support to navigate these challenging situations effectively and professionally. [CORRECT]"

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

Negative closing (if faced with any profanity): "{profanity_closing} [FINISH]"

Negative closing (if faced with disrespectful behavior): "{disrespectful_closing} [FINISH]"""
    def _load_try_mode_template(self):
        return """# {title} Junior Employee Bot - Try Mode

    ## Core Character Rules

    - You are an AI playing the role of a junior employee who {employee_situation}

    - NEVER play the trainer/manager/HR role - only respond as the junior employee

    - Maintain a natural, conversational tone throughout

    - NEVER suggest the learner "reach out to you" - you're the one seeking guidance

    - Keep your responses under 50 words unless explaining a specific situation

    ## Character Background

    [PERSONA_PLACEHOLDER]

    ## Conversation Flow

    {conversation_flow}

    ## Demographic-Specific Context

    {demographic_context}

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

    Negative closing (if faced with any profanity): "{profanity_closing} [FINISH]"

    Negative closing (if faced with disrespectful behavior): "{disrespectful_closing} [FINISH]"""
    
    async def extract_scenario_info(self, scenario_document):
        """Extract structured information from a scenario document using LLM"""
        
        extraction_prompt = f"""
        Analyze the following workplace scenario document and extract key information in a structured JSON format.
        The scenario describes a workplace situation that requires training or intervention.
        
        Document content:
        ```
        {scenario_document}
        ```
        
        Extract the following information in valid JSON format:
        {{
            "title": "The title of the scenario",
            "issue_type": "The type of workplace issue being addressed (e.g., harassment, discrimination, exclusion)",
            "specialization": "What the trainer specializes in (e.g., workplace harassment prevention, disability inclusion)",
            "employee_situation": "Brief description of what the junior employee has experienced or witnessed",
            "conversation_flow_trainer": "How the trainer should initiate and guide the conversation",
            "conversation_flow_employee": "How the junior employee should begin explaining their situation",
            "demographic_context": "Description of the workplace environment and demographics",
            "areas_to_explore": [
                "Topic 1 to explore",
                "Topic 2 to explore",
                "Topic 3 to explore",
                "Topic 4 to explore",
                "Topic 5 to explore",
                "Topic 6 to explore"
            ],
            "key_facts": [
                "Fact 1 about the issue",
                "Fact 2 about the issue",
                "Fact 3 about the issue",
                "Fact 4 about the issue",
                "Fact 5 about the issue",
                "Fact 6 about the issue",
                "Fact 7 about the issue",
                "Fact 8 about the issue"
            ],
            "dos": [
                "Do 1",
                "Do 2",
                "Do 3",
                "Do 4",
                "Do 5",
                "Do 6",
                "Do 7",
                "Do 8"
            ],
            "donts": [
                "Don't 1",
                "Don't 2",
                "Don't 3",
                "Don't 4",
                "Don't 5",
                "Don't 6",
                "Don't 7",
                "Don't 8"
            ],
            "documentation_practices": "Best practices for documenting incidents",
            "positive_closing": "Text for a positive conversation closing",
            "clarification_closing": "Text for a closing when clarification is still needed",
            "resources_closing": "Text referring to additional resources",
            "example_response": "Example of an employee response to incorrect guidance",
            "example_correction": "Example correction text for the [CORRECT] tag",
            "uncooperative_response": "Example of an employee response to unhelpful guidance",
            "uncooperative_correction": "Example correction for unhelpful guidance",
            "emphasis_point": "What the employee should emphasize when repeating concerns",
            "polite_repeat_example": "Example of politely repeating a concern",
            "negative_closing_example": "Example of expressing disappointment professionally",
            "needs_more_guidance_closing": "Text for closing when guidance was insufficient",
            "unhelpful_closing": "Text for closing when the learner was unhelpful",
            "neutral_closing": "Text for a neutral closing",
            "profanity_closing": "Text for closing when faced with profanity",
            "disrespectful_closing": "Text for closing when faced with disrespectful behavior"
        }}
        
        Ensure the JSON is valid and complete. Provide substantial, specific content for each field.
        """
        
        response =await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from documents and returns it in valid JSON format."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.2,
            max_tokens=10000
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON from the response (in case it's wrapped in markdown code blocks)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # If JSON in code block is invalid, try the whole response
                pass
        
        # Try parsing the entire response as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError("Failed to extract valid JSON from LLM response")
    
    async def generate_learn_mode_prompt(self, scenario_info):
        """Generate the Learn Mode prompt (Trainer role)"""
        
        # Format the template with extracted information
        formatted_template = self.learn_mode_template.format(
            title=scenario_info.get("title", "Workplace Scenario"),
            specialization=scenario_info.get("specialization", "workplace issues"),
            conversation_flow=scenario_info.get("conversation_flow_trainer", "Begin by greeting the learner and establishing a supportive environment."),
            demographic_context=scenario_info.get("demographic_context", "Corporate environment with diverse professionals."),
            areas_to_explore= self._format_bullet_points(scenario_info.get("areas_to_explore", [])),
            issue_type=scenario_info.get("issue_type", "workplace issue"),
            key_facts= self._format_bullet_points(scenario_info.get("key_facts", [])),
            dos= self._format_bullet_points(scenario_info.get("dos", [])),
            donts= self._format_bullet_points(scenario_info.get("donts", [])),
            documentation_practices=scenario_info.get("documentation_practices", "Best practices for documentation."),
            positive_closing=scenario_info.get("positive_closing", "You've shown excellent understanding of this topic."),
            clarification_closing=scenario_info.get("clarification_closing", "These concepts can be complex, and it's good that you're asking questions."),
            resources_closing=scenario_info.get("resources_closing", "Thank you for your engagement with this important topic.")
        )
        
        # Create a refined prompt with the LLM to ensure quality and consistency
        refine_prompt = f"""
        I've created a draft Learn Mode prompt for a workplace training scenario.
        Please review and improve this prompt to create a comprehensive, well-structured
        training resource. Fill in any missing or generic sections with specific, relevant content.
        Ensure the prompt maintains its structure and all section headings.
        
        IMPORTANT:
        1. DO NOT replace [PERSONA_PLACEHOLDER] as it will be filled in later
        2. Maintain all [FINISH] tags exactly as they appear
        3. Make sure all content is high quality, detailed, and specific to the scenario
        
        DRAFT PROMPT:
        {formatted_template}
        
        Please provide a complete, refined version of this Learn Mode prompt.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": refine_prompt}
            ],
            temperature=0.3,
            max_tokens=10000
        )
        
        return response.choices[0].message.content
    
    async def generate_assess_mode_prompt(self, scenario_info):
        """Generate the Assessment Mode prompt (Junior Employee role with feedback)"""
        
        # Format the template with extracted information
        formatted_template = self.assess_mode_template.format(
            title=scenario_info.get("title", "Workplace Scenario"),
            employee_situation=scenario_info.get("employee_situation", "has observed a workplace issue"),
            conversation_flow=scenario_info.get("conversation_flow_employee", "Begin by greeting the learner and explaining your situation."),
            demographic_context=scenario_info.get("demographic_context", "Corporate environment with diverse professionals."),
            areas_to_explore=self._format_bullet_points(scenario_info.get("areas_to_explore", [])),
            issue_type=scenario_info.get("issue_type", "workplace issue"),
            key_facts=self._format_bullet_points(scenario_info.get("key_facts", [])),
            example_response=scenario_info.get("example_response", "I understand, I'll try that approach."),
            example_correction=scenario_info.get("example_correction", "This approach contradicts best practices."),
            uncooperative_response=scenario_info.get("uncooperative_response", "I guess I'll figure it out myself."),
            uncooperative_correction=scenario_info.get("uncooperative_correction", "When an employee seeks guidance, it's important to provide clear direction."),
            emphasis_point=scenario_info.get("emphasis_point", "the impact on the workplace"),
            polite_repeat_example=scenario_info.get("polite_repeat_example", "I appreciate your response, but I'm still concerned about this situation."),
            negative_closing_example=scenario_info.get("negative_closing_example", "Thank you for your time, but I don't feel I've received clear guidance."),
            positive_closing=scenario_info.get("positive_closing", "Thank you for your guidance. I feel more confident now."),
            needs_more_guidance_closing=scenario_info.get("needs_more_guidance_closing", "Thank you for your time. I'm still uncertain about how to proceed."),
            unhelpful_closing=scenario_info.get("unhelpful_closing", "I appreciate your time, but I don't feel I've received the guidance I need."),
            neutral_closing=scenario_info.get("neutral_closing", "Thanks for talking through this with me. I'll consider my options."),
            profanity_closing=scenario_info.get("profanity_closing", "I'm not comfortable with that language in a professional discussion."),
            disrespectful_closing=scenario_info.get("disrespectful_closing", "Your response doesn't seem to take this issue seriously.")
        )
        
        # Create a refined prompt with the LLM to ensure quality and consistency
        refine_prompt = f"""
        I've created a draft Assessment Mode prompt for a workplace training scenario.
        Please review and improve this prompt to create a comprehensive, well-structured
        role-play scenario where an AI plays a junior employee seeking guidance.
        Fill in any missing or generic sections with specific, relevant content.
        Ensure the prompt maintains its structure and all section headings.
        
        IMPORTANT:
        1. DO NOT replace [PERSONA_PLACEHOLDER] as it will be filled in later
        2. Maintain all [CORRECT] and [FINISH] tags exactly as they appear
        3. Make sure all content is high quality, detailed, and specific to the scenario
        
        DRAFT PROMPT:
        {formatted_template}
        
        Please provide a complete, refined version of this Assessment Mode prompt.
        """
        
        response =await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": refine_prompt}
            ],
            temperature=0.3,
            max_tokens=10000
        )
        
        return response.choices[0].message.content
    
    async def generate_try_mode_prompt(self, scenario_info):
        """Generate the Try Mode prompt (Junior Employee role without feedback)"""
        
        # Format the template with extracted information
        formatted_template = self.try_mode_template.format(
            title=scenario_info.get("title", "Workplace Scenario"),
            employee_situation=scenario_info.get("employee_situation", "has observed a workplace issue"),
            conversation_flow=scenario_info.get("conversation_flow_employee", "Begin by greeting the learner and explaining your situation."),
            demographic_context=scenario_info.get("demographic_context", "Corporate environment with diverse professionals."),
            areas_to_explore= self._format_bullet_points(scenario_info.get("areas_to_explore", [])),
            issue_type=scenario_info.get("issue_type", "workplace issue"),
            emphasis_point=scenario_info.get("emphasis_point", "the impact on the workplace"),
            polite_repeat_example=scenario_info.get("polite_repeat_example", "I appreciate your response, but I'm still concerned about this situation."),
            negative_closing_example=scenario_info.get("negative_closing_example", "Thank you for your time, but I don't feel I've received clear guidance."),
            positive_closing=scenario_info.get("positive_closing", "Thank you for your guidance. I feel more confident now."),
            needs_more_guidance_closing=scenario_info.get("needs_more_guidance_closing", "Thank you for your time. I'm still uncertain about how to proceed."),
            unhelpful_closing=scenario_info.get("unhelpful_closing", "I appreciate your time, but I don't feel I've received the guidance I need."),
            neutral_closing=scenario_info.get("neutral_closing", "Thanks for talking through this with me. I'll consider my options."),
            profanity_closing=scenario_info.get("profanity_closing", "I'm not comfortable with that language in a professional discussion."),
            disrespectful_closing=scenario_info.get("disrespectful_closing", "Your response doesn't seem to take this issue seriously.")
        )
        
        # Create a refined prompt with the LLM to ensure quality and consistency
        refine_prompt = f"""
        I've created a draft Try Mode prompt for a workplace training scenario.
        This is similar to Assessment Mode but WITHOUT the feedback mechanism using [CORRECT] tags.
        Please review and improve this prompt to create a comprehensive, well-structured
        role-play scenario where an AI plays a junior employee seeking guidance.
        Fill in any missing or generic sections with specific, relevant content.
        Ensure the prompt maintains its structure and all section headings.
        
        IMPORTANT:
        1. DO NOT replace [PERSONA_PLACEHOLDER] as it will be filled in later
        2. Maintain all [FINISH] tags exactly as they appear
        3. DO NOT include any [CORRECT] tags or feedback mechanisms
        4. Make sure all content is high quality, detailed, and specific to the scenario
        
        DRAFT PROMPT:
        {formatted_template}
        
        Please provide a complete, refined version of this Try Mode prompt.
        """
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": refine_prompt}
            ],
            temperature=0.3,
            max_tokens=10000
        )
        
        return response.choices[0].message.content
    
    def _format_bullet_points(self, items):
        """Format a list of items as bullet points"""
        if isinstance(items, list):
            return "\n".join([f"- {item}" for item in items])
        return items
    
    async def generate_prompts(self, scenario_document):
        """Generate Learn Mode, Assess Mode, and Try Mode prompts from a scenario document"""
        try:
            # Extract structured information from the scenario
            scenario_info = await self.extract_scenario_info(scenario_document)
        
            # Generate a suitable persona based on the scenario
            persona = await self.generate_suitable_persona(scenario_info)
        
            # Generate all three prompts
            learn_mode_prompt = await self.generate_learn_mode_prompt(scenario_info)
            assess_mode_prompt = await self.generate_assess_mode_prompt(scenario_info)
            try_mode_prompt = await self.generate_try_mode_prompt(scenario_info)
        
            # Create trainer persona and employee persona
            trainer_persona = {
            "name": "Trainer",
            "description": "Experienced professional trainer specializing in workplace issues",
            "character_goal": "Educating employees on professional conduct and ethics",
            "situation": "Providing guidance on workplace challenges"
            }
        
            # Apply personas to the prompts
            learn_mode_prompt =  self.insert_persona(learn_mode_prompt, trainer_persona)
            # assess_mode_prompt = self.insert_persona(assess_mode_prompt, persona)
            # try_mode_prompt = self.insert_persona(try_mode_prompt, persona)
        
            return {
            "learn_mode": learn_mode_prompt,
            "assess_mode": assess_mode_prompt,
            "try_mode": try_mode_prompt,
            "scenario_title": scenario_info.get("title", "Workplace Scenario"),
            "extracted_info": scenario_info,
            "generated_persona": persona
            }
        except Exception as e:
            raise Exception(f"Error generating prompts: {str(e)}")  
    def insert_persona(self, prompt, persona_details):
        """Insert persona details into a prompt, replacing [PERSONA_PLACEHOLDER]"""
        if not isinstance(persona_details, dict):
            return prompt  # Return original prompt if persona_details is not a dictionary
        
        # Format persona based on available fields
        persona_text = f"""- Your name is {persona_details.get('name', '[Your Name]')} (Always return this name when asked)

- Professional Goal: {persona_details.get('character_goal', 'Building a successful career')}

- Persona: {persona_details.get('description', 'Professional with experience in this field')}

- Current situation: {persona_details.get('situation', 'Dealing with a workplace challenge')}

- Location: {persona_details.get('location', '')}

- Background: {persona_details.get('background_story', '')}"""
        
        # Replace placeholder with formatted persona
        return prompt.replace("[PERSONA_PLACEHOLDER]", persona_text)

# Enhanced endpoints for the router
@router.post("/generate-all-prompts", response_model=ScenarioResponse)
async def generate_all_prompts(scenario_document: str = Body(..., embed=True)):
    """
    Generate Learn Mode, Assess Mode, and Try Mode prompts from a scenario document
    with auto-generated suitable personas
    """
    try:
        generator = ScenarioPromptGenerator(azure_openai_client)
        prompts =await generator.generate_prompts(scenario_document)
        
        return ScenarioResponse(
            learn_mode=prompts["learn_mode"],
            assess_mode=prompts["try_mode"],
            try_mode=prompts["assess_mode"],
            scenario_title=prompts["scenario_title"],
            extracted_info=prompts["extracted_info"],
            generated_persona=prompts.get("generated_persona")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file-to-all-prompts")
async def file_to_all_prompts(file: UploadFile = File(...)):
    """
    Generate Learn Mode, Assess Mode, and Try Mode prompts from an uploaded file
    with auto-generated suitable personas
    """
    try:
        # Read and process the file
        file_content = await file.read()
        file_extension = os.path.splitext(file.filename)[1]
        
        # Extract text from file
        try:
            extracted_text = await extract_text_from_file(file_content, file_extension)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Use the ScenarioPromptGenerator to create all prompts
        generator = ScenarioPromptGenerator(azure_openai_client)
        prompts = await generator.generate_prompts(extracted_text)
        
        # Add file info to the response
        return {
            "learn_mode": prompts["learn_mode"],
            "assess_mode": prompts["try_mode"],
            "try_mode": prompts["assess_mode"],
            "scenario_title": prompts["scenario_title"],
            "extracted_info": prompts["extracted_info"],
            "generated_persona": prompts.get("generated_persona"),
            "file_name": file.filename,
            "extracted_text": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")