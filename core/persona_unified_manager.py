"""
Unified Persona Manager
Handles both V1 and V2 personas using the SAME old methods
"""

from typing import Any, Optional, Union
from uuid import UUID
from models.persona_models import PersonaDB, PersonaResponse, PersonaInstanceV2


class UnifiedPersonaManager:
    """
    Manages personas with backward compatibility.
    Old methods work with both V1 and V2 data.
    """
    
    @staticmethod
    async def save_persona(
        db: Any,
        persona: Union[dict, PersonaInstanceV2],
        created_by: UUID
    ) -> str:
        """
        Save persona (V1 or V2) to database.
        Works with old PersonaDB model but stores V2 data if present.
        
        Args:
            persona: Either old dict format or PersonaInstanceV2
        """
        
        # If it's V2 PersonaInstanceV2, convert to old PersonaDB
        if isinstance(persona, PersonaInstanceV2):
            db_model = persona.to_legacy_db_model(created_by)
        else:
            # Old dict format - convert to PersonaDB
            db_model = PersonaDB(
                name=persona.get("name"),
                description=persona.get("description"),
                persona_type=persona.get("persona_type"),
                gender=persona.get("gender"),
                age=persona.get("age"),
                character_goal=persona.get("character_goal"),
                location=persona.get("location"),
                persona_details=persona.get("persona_details"),
                situation=persona.get("situation"),
                business_or_personal=persona.get("business_or_personal"),
                full_persona=persona,
                created_by=created_by,
                # V2 fields (will be None for old data)
                detail_categories=persona.get("detail_categories"),
                detail_categories_included=persona.get("detail_categories_included"),
                conversation_rules=persona.get("conversation_rules"),
                archetype=persona.get("archetype"),
                archetype_confidence=persona.get("archetype_confidence"),
                system_prompt=persona.get("system_prompt")
            )
        
        # Save to old collection
        result = await db.personas.insert_one(db_model.dict(by_alias=True))
        
        persona_name = db_model.name
        has_v2_data = db_model.detail_categories is not None
        print(f"[DB] Saved persona: {persona_name} (V2 data: {has_v2_data})")
        
        return str(result.inserted_id)
    
    @staticmethod
    async def get_persona(db: Any, persona_id: str) -> Optional[PersonaResponse]:
        """
        Load persona from database.
        Returns PersonaResponse with V2 fields if present.
        """
        
        doc = await db.personas.find_one({"_id": UUID(persona_id)})
        
        if not doc:
            return None
        
        # Build response with both V1 and V2 fields
        return PersonaResponse(
            id=doc["_id"],
            name=doc["name"],
            description=doc["description"],
            persona_type=doc["persona_type"],
            gender=doc["gender"],
            age=doc["age"],
            character_goal=doc["character_goal"],
            location=doc["location"],
            persona_details=doc["persona_details"],
            situation=doc["situation"],
            business_or_personal=doc["business_or_personal"],
            created_by=doc["created_by"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            # V2 fields (will be None if not present)
            detail_categories=doc.get("detail_categories"),
            detail_categories_included=doc.get("detail_categories_included"),
            conversation_rules=doc.get("conversation_rules"),
            archetype=doc.get("archetype"),
            system_prompt=doc.get("system_prompt")
        )
    
    @staticmethod
    async def list_personas(
        db: Any,
        created_by: Optional[UUID] = None,
        limit: int = 50
    ) -> list[PersonaResponse]:
        """
        List personas (both V1 and V2).
        Frontend gets same response format, with V2 fields if present.
        """
        
        query = {}
        if created_by:
            query["created_by"] = created_by
        
        cursor = db.personas.find(query).limit(limit)
        personas = []
        
        async for doc in cursor:
            personas.append(PersonaResponse(
                id=doc["_id"],
                name=doc["name"],
                description=doc["description"],
                persona_type=doc["persona_type"],
                gender=doc["gender"],
                age=doc["age"],
                character_goal=doc["character_goal"],
                location=doc["location"],
                persona_details=doc["persona_details"],
                situation=doc["situation"],
                business_or_personal=doc["business_or_personal"],
                created_by=doc["created_by"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                # V2 fields
                detail_categories=doc.get("detail_categories"),
                detail_categories_included=doc.get("detail_categories_included"),
                conversation_rules=doc.get("conversation_rules"),
                archetype=doc.get("archetype"),
                system_prompt=doc.get("system_prompt")
            ))
        
        return personas
    
    @staticmethod
    def is_v2_persona(persona: PersonaResponse) -> bool:
        """Check if persona has V2 data"""
        return persona.detail_categories is not None
    
    @staticmethod
    async def update_persona(
        db: Any,
        persona_id: str,
        updates: dict
    ) -> bool:
        """Update persona (works for both V1 and V2)"""
        
        from datetime import datetime
        updates["updated_at"] = datetime.now()
        
        result = await db.personas.update_one(
            {"_id": UUID(persona_id)},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def delete_persona(db: Any, persona_id: str) -> bool:
        """Delete persona"""
        
        result = await db.personas.delete_one({"_id": UUID(persona_id)})
        return result.deleted_count > 0
