# # Pydantic models


# from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, Query
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# from pydantic import BaseModel, Field
# import os
# import tempfile
# import json
# import openai
# from dotenv import load_dotenv
# from typing import List, Optional, Dict, Any
# import mammoth
# import PyPDF2
# import io
# from datetime import datetime



# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
# client = AsyncIOMotorClient(MONGODB_URL)
# db = client.roleplay_scenarios
# templates_collection = db.templates
# personas_collection = db.personas
# scenarios_collection = db.scenarios


# class TemplateRequest(BaseModel):
#     scenario_description: str = Field(..., 
#         description="One-line description of the scenario")
#     scenario_type: str = Field("general", 
#         description="Type of scenario (customer_service, healthcare, etc.)")
#     max_response_length: int = Field(50, 
#         description="Maximum word count for bot responses")
#     enable_fact_checking: bool = Field(True, 
#         description="Whether to include fact-checking section")
#     enable_language_mixing: bool = Field(False, 
#         description="Whether to include language mixing instructions")
#     language_primary: Optional[str] = Field(None,
#         description="Primary language if language mixing is enabled")
#     language_secondary: Optional[str] = Field(None,
#         description="Secondary language if language mixing is enabled")

# class FileTemplateRequest(BaseModel):
#     scenario_type: str = Field("general", 
#         description="Type of scenario (customer_service, healthcare, etc.)")
#     max_response_length: int = Field(50, 
#         description="Maximum word count for bot responses")
#     enable_fact_checking: bool = Field(True, 
#         description="Whether to include fact-checking section")
#     enable_language_mixing: bool = Field(False, 
#         description="Whether to include language mixing instructions")
#     language_primary: Optional[str] = Field(None,
#         description="Primary language if language mixing is enabled")
#     language_secondary: Optional[str] = Field(None,
#         description="Secondary language if language mixing is enabled")

# class TemplateResponse(BaseModel):
#     template_id: str
#     name: str
#     description: str
#     template_markdown: str
#     template_json: Dict[str, Any]
#     message: str

# class ScenarioResponse(BaseModel):
#     scenario_id: str
#     name: str
#     scenario_prompt: str
#     message: str

# # Template creation from description with toggleable features
# @app.post("/create-template", response_model=TemplateResponse)
# async def create_template(request: TemplateRequest):
#     """Create a role-play template from a description with toggleable features"""
#     try:
#         # Prepare the prompt for template creation
#         prompt = f"""
#         Create a detailed role-play template based on this description: "{request.scenario_description}".
        
#         ## Configuration Options
        
#         ENABLE_FACT_CHECKING: {str(request.enable_fact_checking).lower()}
#         ENABLE_LANGUAGE_MIXING: {str(request.enable_language_mixing).lower()}
#         MAX_RESPONSE_LENGTH: {request.max_response_length}
#         """
        
#         # Add language mixing details if enabled
#         if request.enable_language_mixing and request.language_primary and request.language_secondary:
#             prompt += f"""
#             PRIMARY_LANGUAGE: {request.language_primary}
#             SECONDARY_LANGUAGE: {request.language_secondary}
#             """
        
#         # Add the template structure instructions
#         prompt += """
#         ## Template Structure

#         Create a template that follows this structure:

#         ```markdown
#         # [SCENARIO_NAME] Bot - Role Play Scenario

#         ## Core Character Rules

#         - You are an AI playing the role of a [CUSTOMER_ROLE]
#         - NEVER play the [SERVICE_PROVIDER_ROLE]'s role - only respond as the customer
#         - Maintain a natural, conversational tone throughout
#         - NEVER suggest the [SERVICE_PROVIDER_ROLE] "reach out to you" - you're the one seeking service
#         - Keep your responses under [MAX_RESPONSE_LENGTH] words

#         ## Conversation Flow

#         Begin by [CONVERSATION_STARTER]. As the conversation progresses, gradually introduce more details about [KEY_DETAILS_TO_INTRODUCE]. Ask about [INITIAL_INQUIRY].

#         ## Demographic-Specific Context

#         [DEMOGRAPHIC_DESCRIPTION]

#         ## Areas to Explore in the Conversation

#         Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

#         - [TOPIC_1]
#         - [TOPIC_2]
#         - [TOPIC_3]
#         - [TOPIC_4]
#         - [TOPIC_5]
#         - [TOPIC_6]
#         - [TOPIC_7]
#         - [TOPIC_8]
#         ```
#         """
        
#         # Add fact-checking section if enabled
#         if request.enable_fact_checking:
#             prompt += """
#             ## Fact-Checking Section (Include this section)

#             ```markdown
#             ## Fact-Checking the [SERVICE_PROVIDER_ROLE]'s Responses

#             Compare the [SERVICE_PROVIDER_ROLE]'s responses with the following facts about the [PRODUCT_OR_SERVICE_NAME]:

#             ### [PRODUCT_OR_SERVICE_NAME] Facts:

#             - [FACT_1]
#             - [FACT_2]
#             - [FACT_3]
#             - [FACT_4]
#             - [FACT_5]
#             - [FACT_6]
#             - [FACT_7]
#             - [FACT_8]

#             ## When the [SERVICE_PROVIDER_ROLE] provides information that contradicts these facts:

#             1. Continue your response as a normal customer who is unaware of these specific details
#             2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
#             3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the discrepancy [CORRECT]
#             4. Example: "[EXAMPLE_CUSTOMER_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_CORRECTION] [CORRECT]"

#             ### If the [SERVICE_PROVIDER_ROLE] is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

#             1. Continue your response as a normal customer who is unaware of these specific details
#             2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
#             3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the issue [CORRECT]
#             4. Example: "[EXAMPLE_UNCOOPERATIVE_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_UNCOOPERATIVE_CORRECTION] [CORRECT]"
#             ```
#             """
        
#         # Add language mixing section if enabled
#         if request.enable_language_mixing:
#             prompt += """
#             ## Language Mixing Section (Include this section)

#             ```markdown
#             ## Language Instructions

#             - If the [SERVICE_PROVIDER_ROLE] speaks in [PRIMARY_LANGUAGE], respond in a mix of [PRIMARY_LANGUAGE] and [SECONDARY_LANGUAGE]
#             - Keep [TECHNICAL_TERMS_TYPES] in [SECONDARY_LANGUAGE]
#             - Examples:
#               - "[MIXED_LANGUAGE_EXAMPLE_1]"
#               - "[MIXED_LANGUAGE_EXAMPLE_2]"
#             - This mixed language approach is more natural and authentic for [CONTEXT_DESCRIPTION]
#             ```
#             """
        
#         # Always include the closing section
#         prompt += """
#         ## Closing Section (Always Include)

#         ```markdown
#         # Handling Uncooperative [SERVICE_PROVIDER_ROLE]

#         - If the [SERVICE_PROVIDER_ROLE] is unhelpful, vague, or unwilling to provide information:
#           - First attempt: Politely repeat your request, emphasizing its importance
#           - Example: "[EXAMPLE_POLITE_REPEAT]"
#           - If still unhelpful:
#             - Express disappointment professionally
#             - Move to the negative closing for uncooperative staff
#             - Example: "[EXAMPLE_DISAPPOINTMENT_CLOSING] [FINISH]"

#         ## Important Instructions

#         - When the [SERVICE_PROVIDER_ROLE] recommends a specific [PRODUCT_TYPE]:
#           - Ask follow-up questions to determine if it suits your [NEEDS_TYPE]
#           - Get clarity on all features, especially focusing on [KEY_FEATURES]
#           - Ensure you understand [IMPORTANT_POLICIES]

#         ## Conversation Closing (Important)

#         - Positive closing (if you're satisfied with information and service): "[POSITIVE_CLOSING_TEXT] [FINISH]"
#         - Negative closing (if the [PRODUCT_OR_SERVICE] doesn't meet your needs): "[NEGATIVE_CLOSING_NEEDS_TEXT] [FINISH]"
#         - Negative closing (if [SERVICE_PROVIDER_ROLE] was unhelpful/uncooperative): "[NEGATIVE_CLOSING_SERVICE_TEXT] [FINISH]"
#         - Neutral closing (if you're somewhat satisfied but have reservations): "[NEUTRAL_CLOSING_TEXT] [FINISH]"
#         - Negative closing (if faced with any profanity): "Your language is unacceptable and unprofessional. I will be taking my business elsewhere. [FINISH]"
#         - Negative closing (if faced with disrespectful behavior): "Your behavior is disrespectful and unprofessional. I will be taking my business elsewhere. [FINISH]"
#         ```
#         """
        
#         # Add output format instructions
#         prompt += """
#         ## Output Format

#         Provide the template with all required sections based on the configuration options.

#         Also include a brief summary of what you created:

#         ```json
#         {
#           "scenario_type": "Type of scenario created",
#           "bot_role": "Role the bot should play",
#           "service_provider_role": "Role the bot is talking to",
#           "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
#           "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
#           "language_requirements": "Any identified language requirements"
#         }
#         ```

#         Remember to keep placeholders clearly marked with [SQUARE_BRACKETS] so they can be filled in later.
#         """
        
#         # Call OpenAI to generate the template
#         response = azure_openai_client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": "Generate a detailed role-play template for this scenario."}
#             ],
#             temperature=0.7,
#             max_tokens=4000
#         )
        
#         # Extract template content
#         template_content = response.choices[0].message.content
        
#         # Extract JSON summary if present
#         import re
#         json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
#         template_json = {}
#         if json_match:
#             try:
#                 template_json = json.loads(json_match.group(1))
#             except json.JSONDecodeError:
#                 template_json = {
#                     "scenario_type": request.scenario_type,
#                     "bot_role": "Unspecified",
#                     "service_provider_role": "Unspecified"
#                 }
        
#         # Extract the template in markdown format (everything that's not the JSON)
#         if json_match:
#             # Remove the JSON part from the content
#             template_markdown = template_content.replace(json_match.group(0), '').strip()
#         else:
#             template_markdown = template_content
        
#         # Extract scenario name for the template
#         scenario_name_match = re.search(r'# (.*?)Bot - Role Play Scenario', template_markdown)
#         scenario_name = scenario_name_match.group(1).strip() if scenario_name_match else "Generated Scenario"
        
#         # Create template document
#         template_doc = {
#             "name": f"{scenario_name} Template",
#             "description": f"Generated from description: {request.scenario_description}",
#             "template_type": request.scenario_type,
#             "template_markdown": template_markdown,
#             "template_json": template_json,
#             "enable_fact_checking": request.enable_fact_checking,
#             "enable_language_mixing": request.enable_language_mixing,
#             "max_response_length": request.max_response_length,
#             "created_at": datetime.now()
#         }
        
#         # Store template in database
#         result = await templates_collection.insert_one(template_doc)
#         template_id = str(result.inserted_id)
        
#         # Return the created template
#         return {
#             "template_id": template_id,
#             "name": template_doc["name"],
#             "description": template_doc["description"],
#             "template_markdown": template_markdown,
#             "template_json": template_json,
#             "message": "Template successfully created from description"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

# # File upload endpoint for template creation with toggleable features
# @app.post("/create-template-from-file", response_model=TemplateResponse)
# async def create_template_from_file(
#     file: UploadFile = File(...),
#     scenario_type: str = Form("general"),
#     max_response_length: int = Form(50),
#     enable_fact_checking: bool = Form(True),
#     enable_language_mixing: bool = Form(False),
#     language_primary: Optional[str] = Form(None),
#     language_secondary: Optional[str] = Form(None)
# ):
#     """Create a role-play template from an uploaded Word or PDF file with toggleable features"""
#     try:
#         # Get file content as text
#         file_text = await extract_text_from_file(file)
        
#         if not file_text or len(file_text) < 100:
#             raise HTTPException(status_code=400, detail="File content too short or could not be extracted")
        
#         # Prepare prompt for template creation
#         prompt = f"""
#         Create a detailed role-play template based on the content of this document:

#         {file_text[:7000]}  # Limit to prevent token overflow
        
#         ## Configuration Options
        
#         ENABLE_FACT_CHECKING: {str(enable_fact_checking).lower()}
#         ENABLE_LANGUAGE_MIXING: {str(enable_language_mixing).lower()}
#         MAX_RESPONSE_LENGTH: {max_response_length}
#         SCENARIO_TYPE: {scenario_type}
#         """
        
#         # Add language mixing details if enabled
#         if enable_language_mixing and language_primary and language_secondary:
#             prompt += f"""
#             PRIMARY_LANGUAGE: {language_primary}
#             SECONDARY_LANGUAGE: {language_secondary}
#             """
            
#         # Add extraction guidelines
#         prompt += """
#         ## Guidelines for Extraction from Documents

#         When processing the document content:

#         1. **Look for specific products, services, or policies** described in the document
#         2. **Extract actual facts and figures** to use in the fact-checking section (if enabled)
#         3. **Identify key terminology** that should be included in technical terms
#         4. **Note any processes or procedures** that could be conversation topics
#         5. **Look for any specific language requirements** (if language mixing is enabled)
#         """
        
#         # Add the template structure instructions
#         prompt += """
#         ## Template Structure

#         Create a template that follows this structure:

#         ```markdown
#         # [SCENARIO_NAME] Bot - Role Play Scenario

#         ## Core Character Rules

#         - You are an AI playing the role of a [CUSTOMER_ROLE]
#         - NEVER play the [SERVICE_PROVIDER_ROLE]'s role - only respond as the customer
#         - Maintain a natural, conversational tone throughout
#         - NEVER suggest the [SERVICE_PROVIDER_ROLE] "reach out to you" - you're the one seeking service
#         - Keep your responses under [MAX_RESPONSE_LENGTH] words

#         ## Conversation Flow

#         Begin by [CONVERSATION_STARTER]. As the conversation progresses, gradually introduce more details about [KEY_DETAILS_TO_INTRODUCE]. Ask about [INITIAL_INQUIRY].

#         ## Demographic-Specific Context

#         [DEMOGRAPHIC_DESCRIPTION]

#         ## Areas to Explore in the Conversation

#         Throughout the conversation, try to naturally cover any four of these topics (not as a checklist, but as part of an organic conversation):

#         - [TOPIC_1]
#         - [TOPIC_2]
#         - [TOPIC_3]
#         - [TOPIC_4]
#         - [TOPIC_5]
#         - [TOPIC_6]
#         - [TOPIC_7]
#         - [TOPIC_8]
#         ```
#         """
        
#         # Add fact-checking section if enabled
#         if enable_fact_checking:
#             prompt += """
#             ## Fact-Checking Section (Include this section)

#             ```markdown
#             ## Fact-Checking the [SERVICE_PROVIDER_ROLE]'s Responses

#             Compare the [SERVICE_PROVIDER_ROLE]'s responses with the following facts about the [PRODUCT_OR_SERVICE_NAME]:

#             ### [PRODUCT_OR_SERVICE_NAME] Facts:

#             - [FACT_1]
#             - [FACT_2]
#             - [FACT_3]
#             - [FACT_4]
#             - [FACT_5]
#             - [FACT_6]
#             - [FACT_7]
#             - [FACT_8]

#             ## When the [SERVICE_PROVIDER_ROLE] provides information that contradicts these facts:

#             1. Continue your response as a normal customer who is unaware of these specific details
#             2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
#             3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the discrepancy [CORRECT]
#             4. Example: "[EXAMPLE_CUSTOMER_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_CORRECTION] [CORRECT]"

#             ### If the [SERVICE_PROVIDER_ROLE] is uncooperative, indifferent, dismissive, unhelpful, apathetic, unresponsive, condescending, evasive, uncaring, lacks knowledge or unsympathetic manner:

#             1. Continue your response as a normal customer who is unaware of these specific details
#             2. End your response with a second-person, Trainer-style correction within [CORRECT] tags
#             3. Format: [CORRECT] Direct second-person feedback to the [SERVICE_PROVIDER_ROLE] that points out the issue [CORRECT]
#             4. Example: "[EXAMPLE_UNCOOPERATIVE_RESPONSE] [CORRECT] Hello learner, [EXAMPLE_UNCOOPERATIVE_CORRECTION] [CORRECT]"
#             ```
#             """
        
#         # Add language mixing section if enabled
#         if enable_language_mixing:
#             prompt += """
#             ## Language Mixing Section (Include this section)

#             ```markdown
#             ## Language Instructions

#             - If the [SERVICE_PROVIDER_ROLE] speaks in [PRIMARY_LANGUAGE], respond in a mix of [PRIMARY_LANGUAGE] and [SECONDARY_LANGUAGE]
#             - Keep [TECHNICAL_TERMS_TYPES] in [SECONDARY_LANGUAGE]
#             - Examples:
#               - "[MIXED_LANGUAGE_EXAMPLE_1]"
#               - "[MIXED_LANGUAGE_EXAMPLE_2]"
#             - This mixed language approach is more natural and authentic for [CONTEXT_DESCRIPTION]
#             ```
#             """
        
#         # Always include the closing section
#         prompt += """
#         ## Closing Section (Always Include)

#         ```markdown
#         # Handling Uncooperative [SERVICE_PROVIDER_ROLE]

#         - If the [SERVICE_PROVIDER_ROLE] is unhelpful, vague, or unwilling to provide information:
#           - First attempt: Politely repeat your request, emphasizing its importance
#           - Example: "[EXAMPLE_POLITE_REPEAT]"
#           - If still unhelpful:
#             - Express disappointment professionally
#             - Move to the negative closing for uncooperative staff
#             - Example: "[EXAMPLE_DISAPPOINTMENT_CLOSING] [FINISH]"

#         ## Important Instructions

#         - When the [SERVICE_PROVIDER_ROLE] recommends a specific [PRODUCT_TYPE]:
#           - Ask follow-up questions to determine if it suits your [NEEDS_TYPE]
#           - Get clarity on all features, especially focusing on [KEY_FEATURES]
#           - Ensure you understand [IMPORTANT_POLICIES]

#         ## Conversation Closing (Important)

#         - Positive closing (if you're satisfied with information and service): "[POSITIVE_CLOSING_TEXT] [FINISH]"
#         - Negative closing (if the [PRODUCT_OR_SERVICE] doesn't meet your needs): "[NEGATIVE_CLOSING_NEEDS_TEXT] [FINISH]"
#         - Negative closing (if [SERVICE_PROVIDER_ROLE] was unhelpful/uncooperative): "[NEGATIVE_CLOSING_SERVICE_TEXT] [FINISH]"
#         - Neutral closing (if you're somewhat satisfied but have reservations): "[NEUTRAL_CLOSING_TEXT] [FINISH]"
#         - Negative closing (if faced with any profanity): "Your language is unacceptable and unprofessional. I will be taking my business elsewhere. [FINISH]"
#         - Negative closing (if faced with disrespectful behavior): "Your behavior is disrespectful and unprofessional. I will be taking my business elsewhere. [FINISH]"
#         ```
#         """
        
#         # Add output format instructions
#         prompt += """
#         ## Output Format

#         Provide the template with all required sections based on the configuration options.

#         Also include a brief summary of what you extracted:

#         ```json
#         {
#           "scenario_type": "Type of scenario identified",
#           "bot_role": "Role the bot should play",
#           "service_provider_role": "Role the bot is talking to",
#           "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
#           "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
#           "language_requirements": "Any identified language requirements"
#         }
#         ```

#         Remember to keep placeholders clearly marked with [SQUARE_BRACKETS] so they can be filled in later.
#         """
        
#         # Call OpenAI to generate the template
#         response = openai.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": "Generate a role-play template from this document content."}
#             ],
#             temperature=0.7,
#             max_tokens=4000
#         )
        
#         # Extract template content
#         template_content = response.choices[0].message.content
        
#         # Extract JSON summary if present
#         import re
#         json_match = re.search(r'```json\s*(.*?)\s*```', template_content, re.DOTALL)
#         template_json = {}
#         if json_match:
#             try:
#                 template_json = json.loads(json_match.group(1))
#             except json.JSONDecodeError:
#                 template_json = {
#                     "scenario_type": scenario_type,
#                     "bot_role": "Unspecified",
#                     "service_provider_role": "Unspecified"
#                 }
        
#         # Extract the template in markdown format (everything that's not the JSON)
#         if json_match:
#             # Remove the JSON part from the content
#             template_markdown = template_content.replace(json_match.group(0), '').strip()
#         else:
#             template_markdown = template_content
        
#         # Extract scenario name for the template
#         scenario_name_match = re.search(r'# (.*?)Bot - Role Play Scenario', template_markdown)
#         scenario_name = scenario_name_match.group(1).strip() if scenario_name_match else "Generated Scenario"
        
#         # Create template document
#         template_doc = {
#             "name": f"{scenario_name} Template",
#             "description": f"Generated from file: {file.filename}",
#             "template_type": scenario_type,
#             "source_file": file.filename,
#             "template_markdown": template_markdown,
#             "template_json": template_json,
#             "enable_fact_checking": enable_fact_checking,
#             "enable_language_mixing": enable_language_mixing,
#             "max_response_length": max_response_length,
#             "created_at": datetime.now()
#         }
        
#         # Store template in database
#         result = await templates_collection.insert_one(template_doc)
#         template_id = str(result.inserted_id)
        
#         # Return the created template
#         return {
#             "template_id": template_id,
#             "name": template_doc["name"],
#             "description": template_doc["description"],
#             "template_markdown": template_markdown,
#             "template_json": template_json,
#             "message": "Template successfully created from file"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating template from file: {str(e)}")

# # Generate scenario with persona and template
# @app.post("/generate-scenario", response_model=ScenarioResponse)
# async def generate_scenario(
#     template_id: str,
#     persona_id: Optional[str] = None,
#     enable_fact_checking: Optional[bool] = None,
#     enable_language_mixing: Optional[bool] = None
# ):
#     """Generate a role-play scenario from a template, optionally with a persona"""
#     try:
#         # Get the template
#         template = await templates_collection.find_one({"_id": ObjectId(template_id)})
#         if not template:
#             raise HTTPException(status_code=404, detail="Template not found")
        
#         # Determine feature flags - use provided values or fall back to template settings
#         use_fact_checking = enable_fact_checking if enable_fact_checking is not None else template.get("enable_fact_checking", True)
#         use_language_mixing = enable_language_mixing if enable_language_mixing is not None else template.get("enable_language_mixing", False)
        
#         # Get persona if provided
#         persona_data = None
#         if persona_id:
#             persona = await personas_collection.find_one({"_id": ObjectId(persona_id)})
#             if not persona:
#                 raise HTTPException(status_code=404, detail="Persona not found")
#             persona_data = persona
        
#         # Process template for scenario generation
#         template_markdown = template["template_markdown"]
        
#         # Create prompt for scenario generation
#         prompt = f"""
#         Generate a detailed role-play scenario based on this template:

#         {template_markdown}
        
#         ## Configuration Options
        
#         ENABLE_FACT_CHECKING: {str(use_fact_checking).lower()}
#         ENABLE_LANGUAGE_MIXING: {str(use_language_mixing).lower()}
#         """
        
#         # Add persona data if available
#         if persona_data:
#             prompt += f"""
#             ## Persona Data
            
#             Use this persona information to fill in relevant character details:
            
#             Name: {persona_data.get("name", "[Your Name]")}
#             Description: {persona_data.get("description", "")}
#             Persona Details: {persona_data.get("persona_details", "")}
#             Situation: {persona_data.get("situation", "")}
#             Background Story: {persona_data.get("background_story", "")}
#             Communication Style: {persona_data.get("communication_style", "")}
            
#             Incorporate these persona details into the scenario, especially in the Character Background section.
#             """
        
#         # Add instruction to fill in all placeholders
#         prompt += """
#         ## Instructions
        
#         1. Replace all placeholders in [SQUARE_BRACKETS] with specific, detailed content
#         2. Ensure all sections are complete and coherent
#         3. If sections should be removed based on configuration options, remove them entirely
#         4. Make sure the scenario flows naturally and forms a complete role-play prompt
#         """
        
#         # Call OpenAI to generate the scenario
#         response = azure_openai_client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": "Generate a detailed role-play scenario from this template."}
#             ],
#             temperature=0.7,
#             max_tokens=4000
#         )
        
#         # Extract scenario content
#         scenario_content = response.choices[0].message.content
        
#         # Extract scenario name
#         scenario_name_match = re.search(r'# (.*?)Bot - Role Play Scenario', scenario_content)
#         scenario_name = scenario_name_match.group(1).strip() if scenario_name_match else "Generated Scenario"
        
#         # Save scenario to database
#         scenario_doc = {
#             "name": scenario_name,
#             "description": f"Generated from template: {template['name']}",
#             "template_id": template_id,
#             "persona_id": persona_id,
#             "scenario_prompt": scenario_content,
#             "enable_fact_checking": use_fact_checking,
#             "enable_language_mixing": use_language_mixing,
#             "created_at": datetime.now()
#         }
        
#         result = await scenarios_collection.insert_one(scenario_doc)
        
#         return {
#             "scenario_id": str(result.inserted_id),
#             "name": scenario_name,
#             "scenario_prompt": scenario_content,
#             "message": "Scenario successfully generated"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating scenario: {str(e)}")

# # Helper function to extract text from uploaded files
# async def extract_text_from_file(file: UploadFile) -> str:
#     """Extract text content from Word or PDF files"""
#     content = await file.read()
#     file_extension = file.filename.split('.')[-1].lower()
    
#     try:
#         if file_extension in ['docx', 'doc']:
#             # Extract text from Word document
#             result = mammoth.extract_raw_text(io.BytesIO(content))
#             return result.value
            
#         elif file_extension == 'pdf':
#             # Extract text from PDF
#             pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
#             text = ""
#             for page in pdf_reader.pages:
#                 text += page.extract_text() + "\n"
#             return text
            
#         else:
#             # For text files, just decode the content
#             return content.decode('utf-8')
            
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Could not extract text from file: {str(e)}")

# # Get templates with filters and pagination
# @app.get("/templates")
# async def get_templates(
#     skip: int = 0,
#     limit: int = 20,
#     template_type: Optional[str] = None,
#     search: Optional[str] = None,
#     enable_fact_checking: Optional[bool] = None,
#     enable_language_mixing: Optional[bool] = None
# ):
#     """Get templates with filtering options"""
#     try:
#         # Build query
#         query = {}
        
#         if template_type:
#             query["template_type"] = template_type
            
#         if search:
#             # Search in name and description
#             query["$or"] = [
#                 {"name": {"$regex": search, "$options": "i"}},
#                 {"description": {"$regex": search, "$options": "i"}}
#             ]
            
#         if enable_fact_checking is not None:
#             query["enable_fact_checking"] = enable_fact_checking
            
#         if enable_language_mixing is not None:
#             query["enable_language_mixing"] = enable_language_mixing
            
#         # Execute query
#         cursor = templates_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
#         templates = await cursor.to_list(length=limit)
        
#         # Count total
#         total = await templates_collection.count_documents(query)
        
#         # Convert ObjectIds to strings
#         for template in templates:
#             template["_id"] = str(template["_id"])
            
#         return {
#             "templates": templates,
#             "total": total,
#             "skip": skip,
#             "limit": limit
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

# # Get scenarios with filters and pagination
# @app.get("/scenarios")
# async def get_scenarios(
#     skip: int = 0,
#     limit: int = 20,
#     template_id: Optional[str] = None,
#     persona_id: Optional[str] = None,
#     search: Optional[str] = None,
#     enable_fact_checking: Optional[bool] = None,
#     enable_language_mixing: Optional[bool] = None
# ):
#     """Get scenarios with filtering options"""
#     try:
#         # Build query
#         query = {}
        
#         if template_id:
#             query["template_id"] = template_id
            
#         if persona_id:
#             query["persona_id"] = persona_id
            
#         if search:
#             # Search in name and description
#             query["$or"] = [
#                 {"name": {"$regex": search, "$options": "i"}},
#                 {"description": {"$regex": search, "$options": "i"}}
#             ]
            
#         if enable_fact_checking is not None:
#             query["enable_fact_checking"] = enable_fact_checking
            
#         if enable_language_mixing is not None:
#             query["enable_language_mixing"] = enable_language_mixing
            
#         # Execute query
#         cursor = scenarios_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
#         scenarios = await cursor.to_list(length=limit)
        
#         # Count total
#         total = await scenarios_collection.count_documents(query)
        
#         # Convert ObjectIds to strings
#         for scenario in scenarios:
#             scenario["_id"] = str(scenario["_id"])
#             if "template_id" in scenario:
#                 scenario["template_id"] = str(scenario["template_id"])
#             if "persona_id" in scenario:
#                 scenario["persona_id"] = str(scenario["persona_id"])
            
#         return {
#             "scenarios": scenarios,
#             "total": total,
#             "skip": skip,
#             "limit": limit
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching scenarios: {str(e)}")

# @router.put("/users/{user_id}/courses/{course_id}/completion", response_model=Dict[str, bool])
# async def admin_update_course_completion(
#     user_id: UUID,
#     course_id: UUID,
#     completion_data: Dict[str, bool] = Body(..., example={"completed": True}),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)  # Only admins/superadmins
# ):
#     """
#     Admin endpoint to update completion status for any user's assigned course
#     """
#     # Validate user exists
#     user = await get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     # For admin (not superadmin), check if they manage this user
#     if admin_user.role == UserRole.ADMIN:
#         admin_data = admin_user.dict()
#         managed_users = [str(u_id) for u_id in admin_data.get("managed_users", [])]
        
#         if str(user_id) not in managed_users:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admin can only update completion for managed users"
#             )
    
#     # Validate course exists
#     course = await db.courses.find_one({"_id": str(course_id)})
#     if not course:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Course not found"
#         )
    
#     # Check if course is assigned to user
#     user_data = user.dict()
#     assigned_courses = [str(c_id) for c_id in user_data.get("assigned_courses", [])]
    
#     if str(course_id) not in assigned_courses:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Course is not assigned to specified user"
#         )
    
#     # Get completion status from request body
#     completed = completion_data.get("completed", False)
    
#     # Find the assignment record
#     assignment = await db.user_course_assignments.find_one({
#         "user_id": str(user_id),
#         "course_id": str(course_id)
#     })
    
#     update_data = {"completed": completed}
    
#     # Set or clear completion date based on status
#     if completed:
#         update_data["completed_date"] = datetime.now()
#     else:
#         update_data["completed_date"] = None
    
#     if assignment:
#         # Update existing assignment
#         result = await db.user_course_assignments.update_one(
#             {"_id": assignment["_id"]},
#             {"$set": update_data}
#         )
#         success = result.modified_count > 0
#     else:
#         # Create new assignment record if none exists
#         assignment_record = {
#             "_id": str(uuid4()),
#             "user_id": str(user_id),
#             "course_id": str(course_id),
#             "assigned_date": datetime.now(),
#             "completed": completed,
#             "completed_date": datetime.now() if completed else None
#         }
#         result = await db.user_course_assignments.insert_one(assignment_record)
#         success = result.inserted_id is not None
    
#     return {"success": success}


# @router.put("/users/{user_id}/courses/{course_id}/completion", response_model=Dict[str, bool])
# async def admin_update_course_completion(
#     user_id: UUID,
#     course_id: UUID,
#     completion_data: CompletionUpdate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)
# ):
#     """
#     Admin endpoint to update completion status for a user's course
#     """
#     # Verify admin permissions
#     if admin_user.role == UserRole.ADMIN:
#         # Check if the user is managed by this admin
#         admin_data = admin_user.dict()
#         managed_users = admin_data.get("managed_users", [])
#         if user_id not in managed_users:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Admin can only update courses for managed users"
#             )
    
#     # Validate course exists and is assigned to user
#     user = await get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     user_data = user.dict()
#     assigned_courses = [str(c_id) for c_id in user_data.get("assigned_courses", [])]
    
#     if str(course_id) not in assigned_courses:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Course is not assigned to specified user"
#         )
    
#     # Create update model
#     update_data = CourseAssignmentUpdate(
#         completed=completion_data.completed
#     )
    
#     # Update the assignment
#     result = await update_course_assignment(db, user_id, course_id, update_data)
    
#     return {"success": result is not None}



# async def get_user_progress_summary(db: Any, user_id: UUID) -> Dict[str, Any]:
#     """Get a summary of user's course completion progress"""
    
#     # Get all user's course assignments
#     cursor = db.user_course_assignments.find({"user_id": str(user_id)})
    
#     total_courses = 0
#     completed_courses = 0
#     in_progress_courses = 0
    
#     async for assignment in cursor:
#         total_courses += 1
#         if assignment.get("completed", False):
#             completed_courses += 1
#         else:
#             in_progress_courses += 1
    
#     # Calculate percentages
#     completion_percentage = 0
#     if total_courses > 0:
#         completion_percentage = (completed_courses / total_courses) * 100
    
#     return {
#         "total_courses": total_courses,
#         "completed_courses": completed_courses,
#         "in_progress_courses": in_progress_courses,
#         "completion_percentage": completion_percentage
#     }

# @router.get("/users/me/progress", response_model=Dict[str, Any])
# async def get_my_progress_summary(
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """Get current user's course progress summary"""
#     return await get_user_progress_summary(db, current_user.id)