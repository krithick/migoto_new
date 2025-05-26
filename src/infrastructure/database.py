from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo(uri: str, database_name: str):
    """Create database connection"""
    db.client = AsyncIOMotorClient(uri)
    db.database = db.client[database_name]
    
    # Verify connection
    await db.client.admin.command('ping')
    print(f"Connected to MongoDB: {database_name}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if not db.database:
        raise RuntimeError("Database not initialized")
    return db.database