# from fastapi import FastAPI, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# import logging
# import os
# import sys

# # Add project root to path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # Import settings
# from src.core.config import settings

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Import database functions
# from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Global database client
# db_client = None
# db = None

# # Import your existing routers
# from core.user import router as user_router
# from core.avatar import router as avatar_router
# from core.avatar_interaction import router as avatar_interaction_router
# from core.botvoice import router as botvoice_router
# from core.course import router as course_router
# from core.document import router as document_router
# from core.environment import router as environment_router
# from core.language import router as language_router
# from core.module import router as module_router
# from core.scenario import router as scenario_router
# from core.persona import router as persona_router
# from core.video import router as video_router
# from core.chat import router as chat_router
# from scenario_generator import router as scenario_router_
# from core.scenario_assignment_router import router as scenario_assignment_router
# from core.module_assignment_router import router as module_assignment_router
# from core.speech import router as speech_router
# from core.file_upload import router as upload_router
# from core.course_assignment_router import router as course_assignment_router
# from core.analysis_report import router as analysis_report_router
# from core.dashboard import router as dashboard_router

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan manager"""
#     global db_client, db
    
#     try:
#         # Connect to MongoDB
#         mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
#         database_name = os.getenv("DATABASE_NAME", "learning_platform")
        
#         db_client = AsyncIOMotorClient(mongo_url)
#         db = db_client[database_name]
        
#         # Test connection
#         await db_client.admin.command('ping')
#         logger.info(f"Connected to MongoDB: {database_name}")
        
#         # Initialize bot factories if they exist
#         try:
#             from factory import DynamicBotFactory
#             bot_factory = DynamicBotFactory(
#                 mongodb_uri=mongo_url,
#                 database_name=database_name
#             )
#             await bot_factory.initialize_bots()
#             await bot_factory.initialize_bots_analyser()
#             logger.info("Bot factories initialized")
#         except ImportError:
#             logger.warning("Bot factory not found, skipping initialization")
#         except Exception as e:
#             logger.error(f"Bot factory initialization error: {e}")
        
#         # Create default superadmin if needed
#         await ensure_superadmin_exists()
        
#         yield
        
#     except Exception as e:
#         logger.error(f"Startup error: {e}")
#         raise
#     finally:
#         # Cleanup
#         if db_client is not None:  # Fixed: Check against None
#             db_client.close()
#             logger.info("Disconnected from MongoDB")

# # Create FastAPI app
# app = FastAPI(
#     title="Learning Platform API",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount static files if uploads directory exists
# if os.path.exists("uploads"):
#     from fastapi.staticfiles import StaticFiles
#     app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# # Include all routers
# app.include_router(user_router)
# # app.include_router(avatar_router)
# # app.include_router(avatar_interaction_router)
# # app.include_router(botvoice_router)
# # app.include_router(course_router)
# # app.include_router(document_router)
# # app.include_router(environment_router)
# # app.include_router(language_router)
# # app.include_router(module_router)
# # app.include_router(scenario_router)
# # app.include_router(persona_router)
# # app.include_router(video_router)
# # app.include_router(chat_router)
# # app.include_router(scenario_router_)
# # app.include_router(scenario_assignment_router)
# # app.include_router(module_assignment_router)
# # app.include_router(speech_router)
# # app.include_router(upload_router)
# # app.include_router(course_assignment_router)
# # app.include_router(analysis_report_router)
# # app.include_router(dashboard_router)

# # Helper functions
# async def ensure_superadmin_exists():
#     """Create default superadmin if none exists"""
#     global db
    
#     # Fixed: Check against None instead of using boolean
#     if db is None:
#         logger.warning("Database not initialized, skipping superadmin check")
#         return
    
#     try:
#         from passlib.context import CryptContext
#         pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
#         # Check if superadmin exists
#         superadmin = await db.users.find_one({"role": "superadmin"})
        
#         if superadmin is None:  # Fixed: Check against None
#             email = os.getenv("FIRST_SUPERADMIN_EMAIL", "superadmin@example.com")
#             password = os.getenv("FIRST_SUPERADMIN_PASSWORD", "Novac@123!")
            
#             from uuid import uuid4
#             from datetime import datetime
            
#             superadmin_doc = {
#                 "_id": str(uuid4()),
#                 "email": email,
#                 "emp_id": "SUPER001",
#                 "username": "superadmin",
#                 "hashed_password": pwd_context.hash(password),
#                 "role": "superadmin",
#                 "is_active": True,
#                 "created_at": datetime.now(),
#                 "updated_at": datetime.now(),
#                 "assigned_courses": []
#             }
            
#             await db.users.insert_one(superadmin_doc)
#             logger.info(f"Created default superadmin: {email}")
#         else:
#             logger.info("Superadmin already exists")
            
#     except Exception as e:
#         logger.error(f"Error in ensure_superadmin_exists: {e}")
#         # Don't raise, just log - allow app to start

# # Root endpoint
# @app.get("/")
# async def root():
#     return {
#         "message": "Learning Platform API",
#         "version": "1.0.0",
#         "docs": "/docs"
#     }

# # Health check
# @app.get("/health")
# async def health_check():
#     global db_client
    
#     try:
#         # Fixed: Check against None
#         if db_client is not None:
#             await db_client.admin.command('ping')
#             db_status = "connected"
#         else:
#             db_status = "disconnected"
#     except Exception as e:
#         db_status = f"error: {str(e)}"
    
#     return {
#         "status": "healthy",
#         "database": db_status
#     }

# # Database dependency for routes
# async def get_db():
#     global db
#     if db is None:  # Fixed: Check against None
#         raise RuntimeError("Database not initialized")
#     return db

# # OpenAI client getter (from your original code)
# def get_azure_openai_client():
#     """Get Azure OpenAI client"""
#     from openai import AzureOpenAI
    
#     api_key = os.getenv("api_key")
#     endpoint = os.getenv("endpoint")
#     api_version = os.getenv("api_version")
    
#     if not all([api_key, endpoint, api_version]):
#         logger.warning("Azure OpenAI credentials not fully configured")
#         return None
    
#     return AzureOpenAI(
#         api_key=api_key,
#         api_version=api_version,
#         azure_endpoint=endpoint
#     )

# # MongoDB client getter (for compatibility with existing code)
# async def get_mongo_db():
#     """Get MongoDB database instance"""
#     return await get_db()

# if __name__ == "__main__":
#     import uvicorn
    
#     # Get port from environment or default
#     port = int(os.getenv("PORT", 8000))
    
#     # Run the application
#     uvicorn.run(
#         "new_main:app",  # or "main:app" depending on your filename
#         host="0.0.0.0",
#         port=port,
#         reload=True
#     )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core imports
from src.core.config import settings
from src.core.container import Container
from src.core.events import EventBus
from src.infrastructure.database import connect_to_mongo, close_mongo_connection

# API imports - ONLY NEW ARCHITECTURE
from src.api.v1.endpoints import auth, users

# Event imports
from src.application.user.events import (
    UserCreatedEvent,
    UserUpdatedEvent,
    UserDeletedEvent,
    CourseAssignedToUserEvent
)
from src.application.user.event_handlers import UserEventHandlers

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create DI container
container = Container()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    try:
        # Load configuration
        container.config.from_dict({
            "mongodb_uri": settings.mongodb_uri,
            "database_name": settings.database_name,
            "secret_key": settings.secret_key,
            "algorithm": settings.algorithm,
            "token_expire_minutes": settings.token_expire_minutes
        })
        
        # Connect to MongoDB
        await connect_to_mongo(settings.mongodb_uri, settings.database_name)
        logger.info("Connected to MongoDB")
        
        # Initialize event handlers
        await setup_event_handlers(container)
        logger.info("Event handlers initialized")
        
        # Create indexes
        await create_indexes(container)
        logger.info("Database indexes created")
        
        # Create default superadmin if needed
        await ensure_superadmin_exists(container)
        
        logger.info("Application started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        # Shutdown
        await close_mongo_connection()
        logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Learning Platform API - New Architecture",
    version="2.0.0",
    description="Migrated User Module with Clean Architecture",
    lifespan=lifespan
)

# Wire dependency injection
container.wire(modules=[
    "src.api.v1.endpoints.auth",
    "src.api.v1.endpoints.users",
    "src.api.v1.dependencies.auth"
])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ONLY NEW routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])

# Helper functions
async def setup_event_handlers(container: Container):
    """Setup event handlers and subscriptions"""
    event_bus = container.event_bus()
    
    # Create event handlers
    user_event_handlers = UserEventHandlers()
    
    # Subscribe to events
    event_bus.subscribe(UserCreatedEvent, user_event_handlers.handle_user_created)
    event_bus.subscribe(UserUpdatedEvent, user_event_handlers.handle_user_updated)
    event_bus.subscribe(UserDeletedEvent, user_event_handlers.handle_user_deleted)
    event_bus.subscribe(CourseAssignedToUserEvent, user_event_handlers.handle_course_assigned)

async def create_indexes(container: Container):
    """Create database indexes"""
    user_repository = container.user_repository()
    
    # User indexes
    await user_repository.create_index("email", unique=True)
    await user_repository.create_index("emp_id", unique=True)
    await user_repository.create_index("role")

async def ensure_superadmin_exists(container: Container):
    """Create default superadmin if none exists"""
    from src.domain.user.entities import UserRole
    
    user_service = container.user_service()
    user_repository = container.user_repository()
    
    # Check if any superadmin exists
    superadmins = await user_repository.find_by_role(UserRole.SUPERADMIN, limit=1)
    
    if not superadmins:
        # Create default superadmin
        email = os.getenv("FIRST_SUPERADMIN_EMAIL", "superadmin@example.com")
        password = os.getenv("FIRST_SUPERADMIN_PASSWORD", "Novac@123!")
        
        await user_service.create_user(
            email=email,
            password=password,
            emp_id="SUPER001",
            username="superadmin",
            role=UserRole.SUPERADMIN
        )
        logger.info(f"Created default superadmin: {email}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Learning Platform API - New Architecture",
        "version": "2.0.0",
        "endpoints": {
            "auth": {
                "login": "POST /api/v1/auth/login",
                "token": "POST /api/v1/auth/token",
                "change_password": "POST /api/v1/auth/password/change"
            },
            "users": {
                "create": "POST /api/v1/users",
                "list": "GET /api/v1/users",
                "me": "GET /api/v1/users/me",
                "get": "GET /api/v1/users/{user_id}",
                "update": "PUT /api/v1/users/{user_id}",
                "delete": "DELETE /api/v1/users/{user_id}"
            }
        }
    }

# Health check
@app.get("/health")
async def health_check():
    from src.infrastructure.database import db
    
    try:
        if db.client is not None:
            await db.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "architecture": "clean",
        "modules": ["user"]
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
