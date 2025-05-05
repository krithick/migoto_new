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
from openai import AzureOpenAI
import os
from utils import convert_template_to_markdown
load_dotenv(".env")

router = APIRouter(prefix="/scenario", tags=["Scenario Generation"])
api_key = os.getenv("api_key")
endpoint = os.getenv("endpoint")
api_version =  os.getenv("api_version")
        
        
azure_openai_client = AzureOpenAI(
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


