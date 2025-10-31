"""Quick script to get avatar info from avatar_interaction"""
import asyncio
from database import get_db
from dotenv import load_dotenv

load_dotenv()

async def get_avatar_info():
    db = await get_db()
    
    avatar_interaction_id = "b2212aac-16d3-478c-bd68-f720afd0b5e1"
    
    # Get avatar interaction
    ai = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    
    if ai:
        print(f"Avatar Interaction ID: {avatar_interaction_id}")
        print(f"Mode: {ai.get('mode')}")
        print(f"Avatars: {ai.get('avatars')}")
        print(f"Bot Role: {ai.get('bot_role')}")
        
        # Get first avatar
        avatars = ai.get('avatars', [])
        if avatars:
            avatar_id = avatars[0]
            avatar = await db.avatars.find_one({"_id": avatar_id})
            if avatar:
                print(f"\nAvatar ID: {avatar_id}")
                print(f"Persona IDs: {avatar.get('persona_id')}")
    else:
        print("Avatar interaction not found")

if __name__ == "__main__":
    asyncio.run(get_avatar_info())
