"""
Migration script to create and set up collections for module and scenario assignments

This script:
1. Creates the user_module_assignments and user_scenario_assignments collections
2. Sets up indexes for efficient querying
3. Creates any initial data needed
"""

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4
from datetime import datetime

# Load environment variables
load_dotenv(".env")

# MongoDB connection settings
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

async def create_collections(db):
    """Create the collections if they don't exist"""
    collections = await db.list_collection_names()
    
    if "user_module_assignments" not in collections:
        print("Creating user_module_assignments collection...")
        await db.create_collection("user_module_assignments")
    
    if "user_scenario_assignments" not in collections:
        print("Creating user_scenario_assignments collection...")
        await db.create_collection("user_scenario_assignments")
        
    print("Collections created successfully")

async def create_module_assignment_indexes(db):
    """Create indexes for the module assignments collection"""
    print("Creating indexes for user_module_assignments...")
    
    # Create compound unique index on user_id and module_id
    await db.user_module_assignments.create_index(
        [("user_id", 1), ("module_id", 1)], 
        unique=True
    )
    
    # Create index for filtering by course
    await db.user_module_assignments.create_index(
        [("user_id", 1), ("course_id", 1)]
    )
    
    # Create index for finding completed/incomplete modules
    await db.user_module_assignments.create_index(
        [("user_id", 1), ("completed", 1)]
    )
    
    print("Module assignment indexes created successfully")

async def create_scenario_assignment_indexes(db):
    """Create indexes for the scenario assignments collection"""
    print("Creating indexes for user_scenario_assignments...")
    
    # Create compound unique index on user_id and scenario_id
    await db.user_scenario_assignments.create_index(
        [("user_id", 1), ("scenario_id", 1)], 
        unique=True
    )
    
    # Create index for filtering by module
    await db.user_scenario_assignments.create_index(
        [("user_id", 1), ("module_id", 1)]
    )
    
    # Create index for filtering by course
    await db.user_scenario_assignments.create_index(
        [("user_id", 1), ("course_id", 1)]
    )
    
    # Create index for finding completed/incomplete scenarios
    await db.user_scenario_assignments.create_index(
        [("user_id", 1), ("completed", 1)]
    )
    
    # Create index for filtering by assigned modes
    await db.user_scenario_assignments.create_index(
        [("user_id", 1), ("assigned_modes", 1)]
    )
    
    print("Scenario assignment indexes created successfully")

async def initialize_collections(db):
    """Initialize collections and create necessary indexes"""
    # Create collections if they don't exist
    await create_collections(db)
    
    # Create indexes
    await create_module_assignment_indexes(db)
    await create_scenario_assignment_indexes(db)

async def migrate_existing_assignments(db):
    """
    For users with assigned courses, convert them to use the new module/scenario structure.
    This is an optional step if you want to preserve existing course assignments.
    """
    print("Checking for existing course assignments to migrate...")
    
    # Get users with course assignments
    cursor = db.users.find({"assigned_courses": {"$exists": True, "$ne": []}})
    count = 0
    
    async for user in cursor:
        user_id = user["_id"]
        assigned_courses = user.get("assigned_courses", [])
        
        for course_id in assigned_courses:
            # Get course to find its modules
            course = await db.courses.find_one({"_id": course_id})
            if not course:
                continue
                
            # Assign all modules in course
            modules = course.get("modules", [])
            for module_id in modules:
                # Check if module assignment already exists
                existing = await db.user_module_assignments.find_one({
                    "user_id": user_id,
                    "module_id": module_id
                })
                
                if not existing:
                    # Create module assignment
                    module_assignment = {
                        "_id": str(uuid4()),
                        "user_id": user_id,
                        "course_id": course_id,
                        "module_id": module_id,
                        "assigned_date": datetime.now(),
                        "completed": False,
                        "completed_date": None
                    }
                    
                    await db.user_module_assignments.insert_one(module_assignment)
                    count += 1
                    
                    # Get module to find its scenarios
                    module = await db.modules.find_one({"_id": module_id})
                    if not module:
                        continue
                        
                    # Assign all scenarios in module
                    scenarios = module.get("scenarios", [])
                    for scenario_id in scenarios:
                        # Create scenario assignment
                        scenario_assignment = {
                            "_id": str(uuid4()),
                            "user_id": user_id,
                            "course_id": course_id,
                            "module_id": module_id,
                            "scenario_id": scenario_id,
                            "assigned_date": datetime.now(),
                            "assigned_modes": ["learn_mode", "try_mode", "assess_mode"],
                            "completed": False,
                            "completed_date": None,
                            "mode_progress": {
                                "learn_mode": {"completed": False, "completed_date": None},
                                "try_mode": {"completed": False, "completed_date": None},
                                "assess_mode": {"completed": False, "completed_date": None}
                            }
                        }
                        
                        try:
                            await db.user_scenario_assignments.insert_one(scenario_assignment)
                            count += 1
                        except Exception as e:
                            # Skip duplicates
                            pass
    
    print(f"Migrated {count} assignments from existing course assignments")

async def main():
    """Main migration function"""
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL, uuidRepresentation='standard')
    db = client[DATABASE_NAME]
    
    print(f"Connected to database: {DATABASE_NAME}")
    
    try:
        # Initialize collections
        await initialize_collections(db)
        
        # Optionally migrate existing assignments
        migrate_existing = input("Do you want to migrate existing course assignments? (y/n): ")
        if migrate_existing.lower() == 'y':
            await migrate_existing_assignments(db)
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        client.close()
        print("MongoDB connection closed")

# Run the migration
if __name__ == "__main__":
    asyncio.run(main())