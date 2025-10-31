"""
Quick test - just check if language instructions are being retrieved
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def quick_test():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client.migoto_new
    
    # List all languages
    languages = await db.languages.find({}).to_list(length=10)
    print("Available languages:")
    for lang in languages:
        print(f"- ID: {lang['_id']}, Name: {lang.get('name', 'No name')}")
        print(f"  Prompt: {lang.get('prompt', 'No prompt')[:100]}...")
        print()

if __name__ == "__main__":
    asyncio.run(quick_test())