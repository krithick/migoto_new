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
from database import db,get_db
from models.user_models import UserDB
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
from core.chat import router as chat_router
from scenario_generator import router as scenario_router_
from core.scenario_assignment_router import router as scenario_assignment_router
from core.module_assignment_router import router as module_assignment_router
from core.speech import router as speech_router
from core.file_upload import router as upload_router
from core.course_assignment_router import router as course_assignment_router
from core.analysis_report import router as analysis_report_router
from core.dashboard import router as dashboard_router

# from core.structure import router as new_router
app = FastAPI(title="Role-Play Scenario Generator API",debug=True)
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
app.include_router(chat_router)
app.include_router(scenario_router_)
app.include_router(scenario_assignment_router)
app.include_router(module_assignment_router)
app.include_router(speech_router)
app.include_router(upload_router)
app.include_router(course_assignment_router)
app.include_router(analysis_report_router)
app.include_router(dashboard_router)

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

# 23333333333
# @app.get("/avatar-interactions-with-scenarios")
# async def list_avatar_interactions_with_scenarios(
#     db: Any = Depends(get_db),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all avatar interactions with their associated scenarios
#     """
#     # Get all avatar interactions
#     interactions = []
#     cursor = db.avatar_interactions.find()
#     async for doc in cursor:
#         # Convert _id to string for JSON serialization
#         doc["id"] = doc.pop("_id")
#         interactions.append(doc)
    
#     # Get associated scenarios for each interaction
#     for interaction in interactions:
#         # Get learn mode scenarios
#         learn_scenarios = await db.scenarios.find(
#             {"learn_mode.avatar_interaction": interaction["id"]}
#         ).to_list(length=None)
        
#         # Get try mode scenarios
#         try_scenarios = await db.scenarios.find(
#             {"try_mode.avatar_interaction": interaction["id"]}
#         ).to_list(length=None)
        
#         # Get assess mode scenarios
#         assess_scenarios = await db.scenarios.find(
#             {"assess_mode.avatar_interaction": interaction["id"]}
#         ).to_list(length=None)
        
#         # Add scenarios to interaction
#         interaction["scenarios"] = {
#             "learn_mode": [{"id": s.pop("_id"), **s} for s in learn_scenarios],
#             "try_mode": [{"id": s.pop("_id"), **s} for s in try_scenarios],
#             "assess_mode": [{"id": s.pop("_id"), **s} for s in assess_scenarios]
#         }
    
#     return interactions


# # 4. Add an endpoint to get available personas
# @app.get("/available-personas")
# async def list_available_personas(
#     db: Any = Depends(get_db),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all available personas
#     """
#     personas = []
#     cursor = db.personas.find()
#     async for doc in cursor:
#         # Convert _id to string for JSON serialization
#         doc["id"] = doc.pop("_id")
#         personas.append(doc)
    
#     return personas


# # 5. Add an endpoint to get available languages
# @app.get("/available-languages")
# async def list_available_languages(
#     db: Any = Depends(get_db),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a list of all available languages
#     """
#     languages = []
#     cursor = db.languages.find()
#     async for doc in cursor:
#         # Convert _id to string for JSON serialization
#         doc["id"] = doc.pop("_id")
#         languages.append(doc)
    
#     return languages


# # 6. Add template-adaptation utilities
# @app.post("/adapt-scenario-template")
# async def adapt_scenario_template(
#     scenario_id: UUID = Form(...),
#     persona_id: Optional[UUID] = Form(None),
#     language_id: Optional[UUID] = Form(None),
#     db: Any = Depends(get_db)
# ):
#     """
#     Adapt a scenario template for use with a specific persona and language
    
#     Returns the modified scenario prompt with persona and language details injected
#     """
#     # Get scenario
#     scenario = await db.scenarios.find_one({"_id": str(scenario_id)})
#     if not scenario:
#         raise HTTPException(status_code=404, detail="Scenario not found")
    
#     # Get the scenario prompt
#     scenario_prompt = scenario.get("scenario_prompt", "")
#     if not scenario_prompt:
#         raise HTTPException(status_code=400, detail="Scenario has no prompt")
    
#     # Inject persona details if provided
#     if persona_id:
#         # Get persona
#         persona = await db.personas.find_one({"_id": str(persona_id)})
#         if not persona:
#             raise HTTPException(status_code=404, detail="Persona not found")
        
#         # Format persona details
#         persona_markdown = f"""
# - Name: {persona.get('name', '[Your Name]')}
# - Type: {persona.get('persona_type', '')}
# - Gender: {persona.get('gender', '')}
# - Goal: {persona.get('character_goal', '')}
# - Location: {persona.get('location', '')}
# - Description: {persona.get('description', '')}
# - Details: {persona.get('persona_details', '')}
# - Current situation: {persona.get('situation', '')}
# - Context: {persona.get('business_or_personal', '')}
# """
        
#         # Add background story if available
#         if 'background_story' in persona and persona['background_story']:
#             persona_markdown += f"- Background: {persona['background_story']}\n"
        
#         # Replace persona placeholder
#         scenario_prompt = scenario_prompt.replace("[PERSONA_PLACEHOLDER]", persona_markdown)
    
#     # Inject language details if provided
#     if language_id:
#         # Get language
#         language = await db.languages.find_one({"_id": str(language_id)})
#         if not language:
#             raise HTTPException(status_code=404, detail="Language not found")
        
#         # Format language details
#         language_markdown = f"""
# - Primary language: {language.get('name', 'English')}
# - Language code: {language.get('code', 'en')}
# """
        
#         # Replace language placeholder
#         scenario_prompt = scenario_prompt.replace("[LANGUAGE_PLACEHOLDER]", language_markdown)
    
#     return {
#         "scenario_id": str(scenario_id),
#         "persona_id": str(persona_id) if persona_id else None,
#         "language_id": str(language_id) if language_id else None,
#         "adapted_prompt": scenario_prompt
#     }

# ####################
##################
#####CHAT
######
from models_old import BotConfig,BotConfigAnalyser
from factory import DynamicBotFactory
from pydantic import BaseModel
from uuid import uuid4
import datetime
from jose import jwt, JWTError
from passlib.context import CryptContext
from core.avatar_interaction import get_avatar_interaction
from core.user import get_current_user
from models.evaluation_models import Evaluation
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
db = MongoDB(MONGO_URL,DATABASE_NAME)
import json
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


async def migrate_course_assignments(db: Any):
    """
    One-time migration script to populate assignment dates for existing assignments
    """
    print("Starting migration of course assignments...")
    
    # Get all users
    users_cursor = db.users.find({"assigned_courses": {"$exists": True, "$ne": []}})
    user_count = 0
    assignment_count = 0
    
    async for user in users_cursor:
        user_id = user["_id"]
        assigned_courses = user.get("assigned_courses", [])
        
        if not assigned_courses:
            continue
            
        user_count += 1
        
        # Use user creation date as the assignment date (best guess)
        assignment_date = user.get("created_at", datetime.datetime.now())
        
        # Create assignment records
        for course_id in assigned_courses:
            # Check if assignment already exists
            existing = await db.user_course_assignments.find_one({
                "user_id": user_id,
                "course_id": course_id
            })
            
            if not existing:
                assignment = {
                    "_id": str(uuid4()),
                    "user_id": user_id,
                    "course_id": course_id,
                    "assigned_date": assignment_date,
                    "completed": False,
                    "completed_date": None  
                }
                
                await db.user_course_assignments.insert_one(assignment)
                assignment_count += 1
    
    print(f"Migration complete. Processed {user_count} users and created {assignment_count} assignment records.")

async def migrate_avatar_models(db: Any):
    """
    Update existing avatar documents to include new fields:
    - fbx
    - animation
    - glb
    - selected
    """
    db = db
    
    # Count avatars before migration
    count_before = await db.avatars.count_documents({})
    
    # Update all avatars that don't have the new fields
    update_result = await db.avatars.update_many(
        {"fbx": {"$exists": False}},
        {"$set": {"fbx": None}}
    )
    
    update_result = await db.avatars.update_many(
        {"animation": {"$exists": False}},
        {"$set": {"animation": None}}
    )
    
    update_result = await db.avatars.update_many(
        {"glb": {"$exists": False}},
        {"$set": {"glb": []}}
    )
    
    update_result = await db.avatars.update_many(
        {"selected": {"$exists": False}},
        {"$set": {"selected": []}}
    )
    
    # Count updated avatars
    count_updated = 0
    cursor = db.avatars.find({
        "$and": [
            {"fbx": {"$exists": True}},
            {"animation": {"$exists": True}},
            {"glb": {"$exists": True}},
            {"selected": {"$exists": True}}
        ]
    })
    
    async for _ in cursor:
        count_updated += 1
    
    print(f"Avatar migration completed. Found {count_before} avatars, updated to new schema: {count_updated}")
    return count_updated
# Example usage
# import asyncio
# asyncio.run(migrate_course_assignments(db))
@app.on_event("startup")
async def startup_event():
    """
    Initialize bots when application starts
    """
    # await create_default_superadmin(db)
    # await migrate_course_assignments(db)
    # await migrate_avatar_models(db)
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

#
@app.post("/createBotAnalyser")
async def createBotAnalyser(
    bot_name: str=Form(default=None),
    bot_description: str=Form(default=None),
    bot_schema:str=Form(default=None),
    system_prompt: str=Form(default=None),
    is_active: bool = Form(default=True),
    llm_model: str=Form(default='gemini-1.5-flash-002'),
    instructions:str=Form(default=''),
    responseFormat:str=Form(default=None),
    guidelines:str=Form(default='')):
    test="json.loads(bot_schema)"
    ints="json.loads(responseFormat)"
    bot_ = BotConfigAnalyser(bot_id=str(uuid.uuid4()),
                    bot_name=bot_name,
                    bot_description=bot_description,
                    bot_schema=test,
                    system_prompt=system_prompt,
                    is_active=is_active,
                    llm_model=llm_model,
                    instructions=instructions,
                    responseFormat=ints,
                    guidelines=guidelines)
    await db.create_bot_analyser(bot_)
    await bot_factory_analyser.initialize_bots_analyser()
    return bot_
 
@app.put("/updateBotAnalyser/{bot_id}")
async def updateBotAnalyser(
    bot_id: str,
    bot_name: str = Form(default=None),
    bot_description: str = Form(default=None),
    bot_schema: str = Form(default=None),
    system_prompt: str = Form(default=None),
    is_active: bool = Form(default=True),
    llm_model: str = Form(default='gemini-1.5-flash-002'),
    instructions: str = Form(default=''),
    responseFormat: str = Form(default=None),
    guidelines: str = Form(default='')
):
    # Parse JSON strings to Python dictionaries
    schema = json.loads(bot_schema) if bot_schema else None
    response_format = json.loads(responseFormat) if responseFormat else None
    
    # Create updated bot object
    updated_bot = BotConfigAnalyser(
        bot_id=bot_id,
        bot_name=bot_name,
        bot_description=bot_description,
        bot_schema=schema,
        system_prompt=system_prompt,
        is_active=is_active,
        llm_model=llm_model,
        instructions=instructions,
        responseFormat=response_format,
        guidelines=guidelines
    )
    
    # Update in database
    result = await db.update_bot_analyser(bot_id, updated_bot)
    
    # Reinitialize bots after update
    await bot_factory_analyser.initialize_bots_analyser()
    
    if result:
        return updated_bot
    else:
        raise HTTPException(status_code=404, detail=f"Bot with ID {bot_id} not found")

@app.get("/getBotAnalysers")
async def getBotAnalysers():
    bots = await db.get_all_bot_analysers()
    return bots
@app.get("/sessionAnalyser/{id}")
    
async def get_session_analysis(
    id: str,
    db: MongoDB = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    session2 = await db.get_session_raw(id)
    analysis= await db.get_session_analysis(id)
    if not session2:
        raise HTTPException(status_code=404, detail="Session not found")
    if not analysis:
    # Access the conversation_history
        conversation_history = session2['conversation_history']

        conversation = {"conversation_history":conversation_history}

        scenario_name= "To Analyze chats"
        analyzer= await bot_factory_analyser.get_bot_analyser(scenario_name)
        interaction_details=  await get_avatar_interaction(db,session2['avatar_interaction'],current_user)
        results =await analyzer.analyze_conversation(conversation,interaction_details,session2["scenario_name"])
        results['session_id']=str(session2["_id"])
        results['user_id']=str(session2["user_id"])
        results['conversation_id']=str(uuid.uuid4())
        results['timestamp']=datetime.datetime.now()
        # category_scores=results['category_scores']
        # # results['overall_score']=category_scores['language_and_communication']+category_scores['product_knowledge']+category_scores['empathy_and_trust']+category_scores['process_clarity']+category_scores['product_suitability']
        report = Evaluation(**results)
        session_dict = report.dict(by_alias=True)
        if "_id" in session_dict:
            session_dict["_id"] = str(session_dict["_id"])    
    # Save to database
        await db.analysis.insert_one(session_dict)
        return results
        # return results
    return analysis

# 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)