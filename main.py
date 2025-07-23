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
from core.companies import router as companies_router
from core.knowledge_base_manager import router as knowledge_base_router  # ADD THIS
# from core.document_processor import DocumentProcessor  # ADD THIS
# from core.azure_search_manager import AzureVectorSearchManager  # ADD THIS


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
app.include_router(companies_router)
# Add this line with your other app.include_router() calls:
app.include_router(knowledge_base_router)  # ADD THIS

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
        assignment_date = user.get("created_at", datetime.now())
        
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
"""
SIMPLE FastAPI Startup Event
============================

Just creates:
1. Mother Company
2. Boss Admin for that company
3. Basic system data

Replace your @app.on_event("startup") with this:
"""

from fastapi import FastAPI
from datetime import datetime
from uuid import uuid4
from passlib.context import CryptContext
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_mother_company(db):
    """Create Mother Company if it doesn't exist"""
    
    # Check if Mother Company already exists
    mother_company = await db.companies.find_one({"company_type": "mother"})
    if mother_company:
        print("✅ Mother Company already exists")
        return mother_company["_id"]
    
    # Create Mother Company
    mother_company_id = str(uuid4())
    
    mother_company = {
        "_id": mother_company_id,
        "name": "NovacTech Solutions",
        "description": "Mother company for all training organizations",
        "industry": "Training & Technology",
        "location": "Global",
        "contact_email": "admin@novactech.com",
        "company_type": "mother",
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "total_users": 0
    }
    
    await db.companies.insert_one(mother_company)
    print(f"✅ Created Mother Company: {mother_company['name']}")
    
    return mother_company_id

async def create_boss_admin_for_mother_company(db):
    """Create Boss Admin assigned to Mother Company"""
    
    # Check if Boss Admin already exists
    boss_admin = await db.users.find_one({"role": "boss_admin"})
    if boss_admin:
        print("✅ Boss Admin already exists")
        return boss_admin["_id"]
    
    # Get Mother Company ID
    mother_company = await db.companies.find_one({"company_type": "mother"})
    if not mother_company:
        raise Exception("Mother Company not found!")
    
    mother_company_id = mother_company["_id"]
    
    # Get credentials from environment
    boss_email = os.getenv("BOSS_ADMIN_EMAIL", "boss@novactech.com")
    boss_password = os.getenv("BOSS_ADMIN_PASSWORD", "BossAdmin@123!")
    
    # Create Boss Admin
    boss_admin_id = str(uuid4())
    
    boss_admin = {
        "_id": boss_admin_id,
        "email": boss_email,
        "username": "Boss Admin",
        "first_name": "Boss",
        "last_name": "Admin",
        "role": "boss_admin",
        "hashed_password": pwd_context.hash(boss_password),
        "company_id": mother_company_id,  # 🔑 Assigned to Mother Company
        "is_active": True,
        "can_create_companies": True,
        "can_view_all_analytics": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    await db.users.insert_one(boss_admin)
    
    # Update Mother Company user count
    await db.companies.update_one(
        {"_id": mother_company_id},
        {"$inc": {"total_users": 1}}
    )
    
    print(f"✅ Created Boss Admin: {boss_email}")
    print(f"   Password: {boss_password}")
    print(f"   Company: {mother_company['name']}")
    
    return boss_admin_id

async def create_basic_system_data(db):
    """Create basic system data (avatars, languages, etc.)"""
    
    # Create default avatar
    avatar_count = await db.avatars.count_documents({})
    if avatar_count == 0:
        default_avatar = {
            "_id": str(uuid4()),
            "name": "Default Avatar",
            "description": "Default avatar for training",
            "avatar_image": None,
            "persona_id": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "fbx": None,
            "animation": None,
            "glb": [],
            "selected": []
        }
        await db.avatars.insert_one(default_avatar)
        print("✅ Created default avatar")
    
    # Create default language
    language_count = await db.languages.count_documents({})
    if language_count == 0:
        default_language = {
            "_id": str(uuid4()),
            "name": "English",
            "code": "en",
            "prompt": "Communicate in clear, professional English.",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        await db.languages.insert_one(default_language)
        print("✅ Created default language")
    
    # Create default bot voice
    voice_count = await db.bot_voices.count_documents({})
    if voice_count == 0:
        default_voice = {
            "_id": str(uuid4()),
            "name": "Default Voice",
            "description": "Default voice for avatars",
            "voice_settings": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        await db.bot_voices.insert_one(default_voice)
        print("✅ Created default bot voice")
    
    # Create default environment
    env_count = await db.environments.count_documents({})
    if env_count == 0:
        default_env = {
            "_id": str(uuid4()),
            "name": "Default Environment",
            "description": "Default environment for training",
            "environment_settings": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        await db.environments.insert_one(default_env)
        print("✅ Created default environment")
    
    # Create default persona
    persona_count = await db.personas.count_documents({})
    if persona_count == 0:
        default_persona = {
            "_id": str(uuid4()),
            "name": "Default Customer",
            "description": "Default customer persona",
            "persona_type": "customer",
            "gender": "neutral",
            "age": 30,
            "character_goal": "Get help with their needs",
            "location": "General",
            "persona_details": "Friendly, asks questions",
            "situation": "Seeking assistance",
            "business_or_personal": "general",
            "background_story": "A typical customer",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        await db.personas.insert_one(default_persona)
        print("✅ Created default persona")
    
    print("✅ Basic system data ready")

# ENVIRONMENT VARIABLES TO SET
"""
Set these in your .env file:

BOSS_ADMIN_EMAIL=boss@novactech.com
BOSS_ADMIN_PASSWORD=BossAdmin@123!
"""

# QUICK TEST FUNCTION
async def test_startup():
    """Test what gets created"""
    from database import get_db
    db = await get_db()
    
    print("🔍 Testing startup results...")
    
    # Check Mother Company
    mother_company = await db.companies.find_one({"company_type": "mother"})
    if mother_company:
        print(f"✅ Mother Company: {mother_company['name']}")
    else:
        print("❌ Mother Company not found")
    
    # Check Boss Admin
    boss_admin = await db.users.find_one({"role": "boss_admin"})
    if boss_admin:
        print(f"✅ Boss Admin: {boss_admin['email']}")
        print(f"   Company: {boss_admin['company_id']}")
    else:
        print("❌ Boss Admin not found")
    
    # Check basic data
    avatar_count = await db.avatars.count_documents({})
    language_count = await db.languages.count_documents({})
    persona_count = await db.personas.count_documents({})
    
    print(f"✅ Basic data: {avatar_count} avatars, {language_count} languages, {persona_count} personas")
@app.on_event("startup")
async def startup_event():
    """Simple startup - just Mother Company + Boss Admin + Basic Data"""
    
    print("🚀 Starting FastAPI Application...")
    
    try:
        from database import get_db
        db = await get_db()
        
        # Step 1: Create Mother Company
        await create_mother_company(db)
        
        # Step 2: Create Boss Admin for Mother Company
        await create_boss_admin_for_mother_company(db)
        
        # Step 3: Create basic system data
        # await create_basic_system_data(db)
        
        print("✅ FastAPI startup completed successfully!")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("⚠️  App will continue but may have issues")
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

from models.company_models import CompanyDB, CompanyType, CompanyStatus
from models.user_models import BossAdminDB, UserRole, AccountType
from uuid import UUID
from datetime import datetime, timedelta
# Add this to your main.py file

async def migrate_user_hierarchy_and_companies(db):
    """
    Comprehensive migration script to:
    1. Create mother company and boss admin
    2. Create companies for existing superadmins
    3. Migrate existing users to new hierarchy structure
    4. Update all documents with new fields
    """
    print("Starting user hierarchy and company migration...")
    
    try:
        # Step 1: Create the mother company
        mother_company_id = await create_mother_company(db)
        print(f"✅ Created mother company: {mother_company_id}")
        
        # Step 2: Create the boss admin
        boss_admin_id = await create_boss_admin(db, mother_company_id)
        print(f"✅ Created boss admin: {boss_admin_id}")
        
        # Step 3: Handle existing superadmins
        migrated_superadmins = await migrate_existing_superadmins(db, boss_admin_id)
        print(f"✅ Migrated {len(migrated_superadmins)} superadmins with their companies")
        
        # Step 4: Migrate remaining users
        migrated_users = await migrate_remaining_users(db, migrated_superadmins)
        print(f"✅ Migrated {migrated_users} remaining users")
        
        # Step 5: Update company statistics
        await update_company_statistics(db)
        print("✅ Updated company statistics")
        
        print("🎉 Migration completed successfully!")
        
        # Print summary
        await print_migration_summary(db)
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

async def create_mother_company(db):
    """Create the mother company for the boss admin"""
    from models.company_models import CompanyDB, CompanyType, CompanyStatus
    
    # Check if mother company already exists
    existing_mother = await db.companies.find_one({"company_type": "mother"})
    if existing_mother:
        print("Mother company already exists, skipping creation")
        return existing_mother["_id"]
    
    mother_company = CompanyDB(
        name="NovacTech Solutions (Mother Company)",
        description="Mother company managing all client organizations",
        industry="Technology Solutions",
        location="Global",
        contact_email="admin@novactech.com",
        company_type=CompanyType.MOTHER,
        status=CompanyStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    company_dict = mother_company.dict(by_alias=True)
    company_dict["_id"] = str(company_dict["_id"])
    
    result = await db.companies.insert_one(company_dict)
    return str(result.inserted_id)

async def create_boss_admin(db, mother_company_id):
    """Create the boss admin user"""
    import os
    from models.user_models import BossAdminDB, UserRole, AccountType
    
    # Check if boss admin already exists
    existing_boss = await db.users.find_one({"role": "boss_admin"})
    if existing_boss:
        print("Boss admin already exists, skipping creation")
        return existing_boss["_id"]
    
    # Get boss admin credentials from environment
    boss_email = os.getenv("BOSS_ADMIN_EMAIL", "boss@novactech.com")
    boss_password = os.getenv("BOSS_ADMIN_PASSWORD", "BossAdmin@123!")
    
    # Check if email is already taken
    existing_user = await db.users.find_one({"email": boss_email})
    if existing_user:
        # Update existing user to boss admin
        hashed_password = get_password_hash(boss_password)
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": {
                "role": UserRole.BOSS_ADMIN,
                "company_id": mother_company_id,
                "account_type": AccountType.REGULAR,
                "can_create_companies": True,
                "can_view_all_analytics": True,
                "managed_companies": [],
                "managed_users": [],
                "hashed_password": hashed_password,
                "updated_at": datetime.now()
            }}
        )
        return existing_user["_id"]
    
    boss_admin = BossAdminDB(
        email=boss_email,
        emp_id="BOSS001",
        username="Boss Admin",
        role=UserRole.BOSS_ADMIN,
        hashed_password=get_password_hash(boss_password),
        company_id=UUID(mother_company_id),
        account_type=AccountType.REGULAR,
        is_active=True,
        can_create_companies=True,
        can_view_all_analytics=True,
        managed_companies=[],
        managed_users=[],
        assigned_courses=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    boss_dict = boss_admin.dict(by_alias=True)
    boss_dict["_id"] = str(boss_dict["_id"])
    boss_dict["company_id"] = str(boss_dict["company_id"])
    
    result = await db.users.insert_one(boss_dict)
    
    # Update mother company with boss admin info
    await db.companies.update_one(
        {"_id": mother_company_id},
        {"$set": {
            "created_by": str(result.inserted_id),
            "total_users": 1,
            "total_superadmins": 0,
            "total_admins": 0
        }}
    )
    
    print(f"Boss admin created with email: {boss_email}")
    return str(result.inserted_id)

async def migrate_existing_superadmins(db, boss_admin_id):
    """Find existing superadmins and create companies for them"""
    from models.company_models import CompanyDB, CompanyType, CompanyStatus
    from models.user_models import UserRole, AccountType
    
    migrated_superadmins = []
    
    # Find all existing superadmins
    superadmins_cursor = db.users.find({"role": "superadmin"})
    superadmin_count = 0
    
    async for superadmin_doc in superadmins_cursor:
        superadmin_count += 1
        superadmin_id = superadmin_doc["_id"]
        superadmin_email = superadmin_doc.get("email", f"superadmin{superadmin_count}@company.com")
        superadmin_name = superadmin_doc.get("username", f"SuperAdmin {superadmin_count}")
        
        # Create a company for this superadmin
        company_name = f"Company {superadmin_count} ({superadmin_name})"
        
        company = CompanyDB(
            name=company_name,
            description=f"Company managed by {superadmin_name}",
            industry="Business",
            location="Office Location",
            contact_email=superadmin_email,
            company_type=CompanyType.CLIENT,
            status=CompanyStatus.ACTIVE,
            created_by=UUID(boss_admin_id),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        company_dict = company.dict(by_alias=True)
        company_dict["_id"] = str(company_dict["_id"])
        
        company_result = await db.companies.insert_one(company_dict)
        company_id = str(company_result.inserted_id)
        
        # Update superadmin with company_id and new fields
        update_data = {
            "company_id": company_id,
            "account_type": AccountType.REGULAR,
            "demo_expires_at": None,
            "can_access_analytics": True,
            "updated_at": datetime.now()
        }
        
        # Add missing fields if they don't exist
        if "managed_users" not in superadmin_doc:
            update_data["managed_users"] = []
        if "assigned_courses" not in superadmin_doc:
            update_data["assigned_courses"] = []
        if "assignee_emp_id" not in superadmin_doc:
            update_data["assignee_emp_id"] = None
        
        await db.users.update_one(
            {"_id": superadmin_id},
            {"$set": update_data}
        )
        
        migrated_superadmins.append({
            "user_id": superadmin_id,
            "company_id": company_id,
            "email": superadmin_email
        })
        
        print(f"  - Created company '{company_name}' for superadmin {superadmin_email}")
    
    # Update boss admin's managed_companies
    if migrated_superadmins:
        managed_companies = [sa["company_id"] for sa in migrated_superadmins]
        await db.users.update_one(
            {"_id": boss_admin_id},
            {"$set": {"managed_companies": managed_companies}}
        )
    
    return migrated_superadmins

async def migrate_remaining_users(db, migrated_superadmins):
    """Migrate all remaining users (admins and regular users)"""
    from models.user_models import AccountType
    
    migrated_count = 0
    
    # Create a mapping of existing admins to their potential superadmins
    # This is a best-effort assignment based on existing managed_users relationships
    
    # Find all users that aren't superadmins or boss_admin
    remaining_users_cursor = db.users.find({
        "role": {"$nin": ["superadmin", "boss_admin"]},
        "company_id": {"$exists": False}
    })
    
    # Default company assignment strategy
    default_company_id = None
    if migrated_superadmins:
        default_company_id = migrated_superadmins[0]["company_id"]  # Assign to first company
    
    async for user_doc in remaining_users_cursor:
        user_id = user_doc["_id"]
        
        # Try to find which superadmin this user belongs to
        assigned_company_id = default_company_id
        assigned_by_superadmin = None
        
        # Check if any superadmin has this user in managed_users
        for superadmin_info in migrated_superadmins:
            superadmin = await db.users.find_one({"_id": superadmin_info["user_id"]})
            if superadmin and "managed_users" in superadmin:
                if user_id in superadmin.get("managed_users", []):
                    assigned_company_id = superadmin_info["company_id"]
                    assigned_by_superadmin = superadmin_info["user_id"]
                    break
        
        # If still no company assigned, assign to first available company
        if not assigned_company_id and migrated_superadmins:
            assigned_company_id = migrated_superadmins[0]["company_id"]
        
        # Update user with new fields
        update_data = {
            "company_id": assigned_company_id,
            "account_type": AccountType.REGULAR,
            "demo_expires_at": None,
            "can_access_analytics": False,
            "updated_at": datetime.now()
        }
        
        # Add missing fields if they don't exist
        if "assigned_courses" not in user_doc:
            update_data["assigned_courses"] = []
        if "assignee_emp_id" not in user_doc:
            update_data["assignee_emp_id"] = None
        if user_doc.get("role") == "admin" and "managed_users" not in user_doc:
            update_data["managed_users"] = []
        
        await db.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        migrated_count += 1
        
        if migrated_count % 10 == 0:
            print(f"  - Migrated {migrated_count} users...")
    
    return migrated_count

async def update_company_statistics(db):
    """Update statistics for all companies"""
    companies_cursor = db.companies.find()
    
    async for company_doc in companies_cursor:
        company_id = company_doc["_id"]
        
        # Count users in this company
        total_users = await db.users.count_documents({"company_id": company_id})
        total_admins = await db.users.count_documents({
            "company_id": company_id,
            "role": "admin"
        })
        total_superadmins = await db.users.count_documents({
            "company_id": company_id,
            "role": "superadmin"
        })
        
        # Update company statistics
        await db.companies.update_one(
            {"_id": company_id},
            {"$set": {
                "total_users": total_users,
                "total_admins": total_admins,
                "total_superadmins": total_superadmins,
                "total_courses": 0,  # TODO: Update when courses have company_id
                "total_modules": 0,   # TODO: Update when modules have company_id
                "total_scenarios": 0, # TODO: Update when scenarios have company_id
                "updated_at": datetime.now()
            }}
        )

async def print_migration_summary(db):
    """Print a summary of the migration"""
    print("\n" + "="*50)
    print("MIGRATION SUMMARY")
    print("="*50)
    
    # Count companies
    total_companies = await db.companies.count_documents({})
    mother_companies = await db.companies.count_documents({"company_type": "mother"})
    client_companies = await db.companies.count_documents({"company_type": "client"})
    
    print(f"Companies: {total_companies} total ({mother_companies} mother, {client_companies} client)")
    
    # Count users by role
    boss_admins = await db.users.count_documents({"role": "boss_admin"})
    superadmins = await db.users.count_documents({"role": "superadmin"})
    admins = await db.users.count_documents({"role": "admin"})
    users = await db.users.count_documents({"role": "user"})
    
    print(f"Users: {boss_admins} boss admins, {superadmins} superadmins, {admins} admins, {users} regular users")
    
    # Count demo users
    demo_users = await db.users.count_documents({"account_type": "demo"})
    print(f"Demo users: {demo_users}")
    
    # Show companies and their user counts
    print("\nCompany Details:")
    companies_cursor = db.companies.find()
    async for company in companies_cursor:
        print(f"  - {company['name']}: {company.get('total_users', 0)} users")
    
    print("="*50)

# Add this to your existing startup event in main.py
async def startup_event_updated():
    """Updated startup event with migration"""
    try:
        # Run existing migrations first
        await create_default_superadmin(db)
        await migrate_course_assignments(db)
        await migrate_avatar_models(db)
        
        # Run new hierarchy migration
        await migrate_user_hierarchy_and_companies(db)
        
        # Initialize bots
        await bot_factory.initialize_bots()
        await bot_factory_analyser.initialize_bots_analyser()
        
        print("✅ All startup tasks completed successfully!")
        
    except Exception as e:
        print(f"❌ Startup failed: {str(e)}")
        # Don't raise here so the app can still start
        print("⚠️  App starting with potential migration issues")


@app.post("/run-fact-check-benchmark")
async def run_benchmark_endpoint(
    knowledge_base_id: str = Body(...),
    avatar_interaction_id: str = Body(...),
    persona_id: Optional[str] = Body(None),
    avatar_id: Optional[str] = Body(None),
    language_id: Optional[str] = Body(None),
    num_test_cases: int = Body(50),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Run fact-checking benchmark via API"""
    
    try:
        from benchmark_generator import run_fact_checking_benchmark
        from dynamic_chat import get_chat_factory
        from uuid import UUID
        
        # Convert string IDs to UUIDs where needed
        avatar_interaction_uuid = UUID(avatar_interaction_id)
        persona_uuid = UUID(persona_id) if persona_id else None
        avatar_uuid = UUID(avatar_id) if avatar_id else None
        language_uuid = UUID(language_id) if language_id else None
        
        # Get chat handler with all IDs
        chat_factory = await get_chat_factory()
        chat_handler = await chat_factory.get_chat_handler(
            avatar_interaction_id=avatar_interaction_uuid,
            mode="try_mode",
            persona_id=persona_uuid,
            language_id=language_uuid
        )
        
        # Initialize fact-checking
        await chat_handler.initialize_fact_checking("benchmark_session")
        
        # Validate that fact-checking is enabled
        if not chat_handler.fact_checking_enabled:
            return {
                "success": False,
                "error": "Fact-checking not enabled for this knowledge base"
            }
        
        # Run benchmark
        print(f"🚀 Starting benchmark for knowledge_base: {knowledge_base_id}")
        report = await run_fact_checking_benchmark(
            knowledge_base_id=knowledge_base_id,
            chat_handler=chat_handler,
            num_test_cases=num_test_cases
        )
        
        return {
            "success": True,
            "benchmark_config": {
                "knowledge_base_id": knowledge_base_id,
                "avatar_interaction_id": avatar_interaction_id,
                "persona_id": persona_id,
                "avatar_id": avatar_id,
                "language_id": language_id,
                "num_test_cases": num_test_cases
            },
            "report": report
        }
        
    except Exception as e:
        print(f"❌ Benchmark error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
# FILE: Add this debug endpoint to main.py
@app.get("/debug/check-chunks/{knowledge_base_id}")
async def debug_check_chunks(knowledge_base_id: str, db: Any = Depends(get_db)):
    """Debug: Check what's in your chunks"""
    
    # Check MongoDB chunks
    chunks = await db.document_chunks.find(
        {"knowledge_base_id": knowledge_base_id}
    ).limit(5).to_list(length=5)
    
    # Check Azure Search directly
    from core.azure_search_manager import AzureVectorSearchManager
    vector_search = AzureVectorSearchManager()
    search_client = vector_search.get_search_client(knowledge_base_id)
    
    try:
        # Get some documents from Azure Search
        results = await search_client.search(
            search_text="*",
            select=["id", "knowledge_base_id", "content"],
            top=5
        )
        
        azure_docs = []
        async for result in results:
            azure_docs.append({
                "id": result["id"],
                "knowledge_base_id": result.get("knowledge_base_id"),
                "content": result["content"][:100]
            })
    finally:
        await search_client.close()
    
    return {
        "knowledge_base_id": knowledge_base_id,
        "mongodb_chunks": len(chunks),
        "mongodb_sample": chunks[0] if chunks else None,
        "azure_docs": len(azure_docs),
        "azure_sample": azure_docs[0] if azure_docs else None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)