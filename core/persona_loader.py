"""
Utility to load persona data from JSON files (like persona_from_extraction.json)
into the database with full dynamic field support.
"""

from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException
from models.persona_models import PersonaInstanceV2, PersonaLocation


async def load_persona_from_json(
    db: Any,
    persona_data: Dict[str, Any],
    created_by: UUID
) -> Dict[str, Any]:
    """
    Load a persona from JSON data (like extraction output) into database.
    Preserves all fields including dynamic ones.
    
    Args:
        db: Database connection
        persona_data: Raw persona dict from JSON
        created_by: User ID creating this persona
        
    Returns:
        Stored persona dict with all fields
    """
    try:
        # Validate required base fields
        required_fields = ["name", "age", "gender", "role", "description", "persona_type", "mode"]
        missing = [f for f in required_fields if f not in persona_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        # Prepare persona dict for storage
        storage_dict = persona_data.copy()
        
        # Add metadata
        storage_dict["created_by"] = str(created_by)
        storage_dict["created_at"] = datetime.now()
        storage_dict["updated_at"] = datetime.now()
        storage_dict["version"] = "v2"
        
        # Handle ID field
        if "id" in storage_dict:
            storage_dict["_id"] = storage_dict.pop("id")
        elif "_id" not in storage_dict:
            from uuid import uuid4
            storage_dict["_id"] = str(uuid4())
        
        # Ensure all fields are preserved
        # No validation - just store everything
        
        # Insert into personas_v2 collection
        result = await db.personas_v2.insert_one(storage_dict)
        
        # Retrieve stored persona
        stored = await db.personas_v2.find_one({"_id": storage_dict["_id"]})
        
        print(f"[SUCCESS] Loaded persona: {stored['name']} with {len(stored.get('detail_categories', {}))} detail categories")
        
        return stored
        
    except Exception as e:
        print(f"[ERROR] Failed to load persona from JSON: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load persona: {str(e)}")


async def validate_persona_structure(persona_data: Dict[str, Any]) -> bool:
    """
    Validate that persona data has minimum required structure.
    Does NOT validate dynamic fields - those are allowed to vary.
    
    Returns:
        True if valid, raises ValueError if not
    """
    required_base = ["name", "age", "gender", "role", "description", "persona_type", "mode"]
    
    for field in required_base:
        if field not in persona_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate types for base fields
    if not isinstance(persona_data["name"], str):
        raise ValueError("name must be string")
    if not isinstance(persona_data["age"], int):
        raise ValueError("age must be integer")
    if not isinstance(persona_data["gender"], str):
        raise ValueError("gender must be string")
    
    return True


async def update_persona_v2(
    db: Any,
    persona_id: str,
    updates: Dict[str, Any],
    updated_by: UUID
) -> Optional[Dict[str, Any]]:
    """
    Update a v2 persona with dynamic field support.
    Preserves all existing fields and adds/updates specified ones.
    """
    try:
        # Check if persona exists
        existing = await db.personas_v2.find_one({"_id": persona_id})
        if not existing:
            return None
        
        # Add update metadata
        updates["updated_at"] = datetime.now()
        updates["updated_by"] = str(updated_by)
        
        # Update in database
        await db.personas_v2.update_one(
            {"_id": persona_id},
            {"$set": updates}
        )
        
        # Return updated persona
        updated = await db.personas_v2.find_one({"_id": persona_id})
        return updated
        
    except Exception as e:
        print(f"[ERROR] Failed to update persona v2: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")
