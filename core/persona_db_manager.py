"""
Persona Database Manager
Handles saving/loading V2 personas with dynamic categories
"""

from typing import Any, List, Optional
from uuid import UUID
from models.persona_models import PersonaInstanceV2, PersonaV2DB, PersonaV2Response


class PersonaDBManager:
    """Manages V2 persona database operations"""
    
    @staticmethod
    async def save_persona(
        db: Any,
        persona: PersonaInstanceV2,
        created_by: UUID
    ) -> str:
        """
        Save V2 persona to database.
        Dynamic categories are saved as-is in detail_categories field.
        """
        
        # Convert to DB model
        db_model = persona.to_db_model(created_by)
        
        # Save to MongoDB (convert UUID to string)
        persona_dict = db_model.dict(by_alias=True)
        # Convert any UUID objects to strings
        for key, value in persona_dict.items():
            if hasattr(value, '__class__') and value.__class__.__name__ == 'UUID':
                persona_dict[key] = str(value)
        
        result = await db.personas_v2.insert_one(persona_dict)
        
        print(f"[DB] Saved persona: {persona.name} with {len(persona.detail_categories)} categories")
        
        return str(result.inserted_id)
    
    @staticmethod
    async def get_persona(db: Any, persona_id: str) -> Optional[PersonaInstanceV2]:
        """Load persona from database"""
        
        doc = await db.personas_v2.find_one({"_id": persona_id})
        
        if not doc:
            return None
        
        # Convert back to PersonaInstanceV2
        return PersonaInstanceV2(
            id=doc["_id"],
            template_id=doc["template_id"],
            persona_type=doc["persona_type"],
            mode=doc["mode"],
            scenario_type=doc.get("scenario_type"),
            name=doc["name"],
            age=doc["age"],
            gender=doc["gender"],
            role=doc["role"],
            description=doc["description"],
            location=doc["location"],
            archetype=doc.get("archetype"),
            archetype_confidence=doc.get("archetype_confidence"),
            archetype_specific_data=doc.get("archetype_specific_data", {}),
            detail_categories=doc.get("detail_categories", {}),
            conversation_rules=doc.get("conversation_rules", {}),
            system_prompt=doc.get("system_prompt"),
            prompt_mode=doc.get("prompt_mode"),
            detail_categories_included=doc.get("detail_categories_included", []),
            generation_metadata=doc.get("generation_metadata", {})
        )
    
    @staticmethod
    async def list_personas(
        db: Any,
        template_id: Optional[str] = None,
        mode: Optional[str] = None,
        archetype: Optional[str] = None,
        limit: int = 50
    ) -> List[PersonaV2Response]:
        """List personas with optional filters"""
        
        query = {}
        if template_id:
            query["template_id"] = template_id
        if mode:
            query["mode"] = mode
        if archetype:
            query["archetype"] = archetype
        
        cursor = db.personas_v2.find(query).limit(limit)
        personas = []
        
        async for doc in cursor:
            personas.append(PersonaV2Response(
                id=doc["_id"],
                template_id=doc["template_id"],
                persona_type=doc["persona_type"],
                mode=doc["mode"],
                name=doc["name"],
                age=doc["age"],
                gender=doc["gender"],
                role=doc["role"],
                description=doc["description"],
                location=doc["location"],
                archetype=doc["archetype"],
                detail_categories=doc.get("detail_categories", {}),
                detail_categories_included=doc.get("detail_categories_included", []),
                conversation_rules=doc.get("conversation_rules", {}),
                system_prompt=doc.get("system_prompt"),
                created_at=doc["created_at"]
            ))
        
        return personas
    
    @staticmethod
    async def update_persona(
        db: Any,
        persona_id: str,
        updates: dict
    ) -> bool:
        """Update persona fields"""
        
        from datetime import datetime
        updates["updated_at"] = datetime.now()
        
        result = await db.personas_v2.update_one(
            {"_id": persona_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def delete_persona(db: Any, persona_id: str) -> bool:
        """Delete persona"""
        
        result = await db.personas_v2.delete_one({"_id": persona_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def get_personas_by_template(
        db: Any,
        template_id: str
    ) -> List[PersonaInstanceV2]:
        """Get all personas for a template"""
        
        cursor = db.personas_v2.find({"template_id": template_id})
        personas = []
        
        async for doc in cursor:
            personas.append(PersonaInstanceV2(
                id=doc["_id"],
                template_id=doc["template_id"],
                persona_type=doc["persona_type"],
                mode=doc["mode"],
                scenario_type=doc.get("scenario_type"),
                name=doc["name"],
                age=doc["age"],
                gender=doc["gender"],
                role=doc["role"],
                description=doc["description"],
                location=doc["location"],
                archetype=doc.get("archetype"),
                archetype_confidence=doc.get("archetype_confidence"),
                archetype_specific_data=doc.get("archetype_specific_data", {}),
                detail_categories=doc.get("detail_categories", {}),
                conversation_rules=doc.get("conversation_rules", {}),
                system_prompt=doc.get("system_prompt"),
                prompt_mode=doc.get("prompt_mode"),
                detail_categories_included=doc.get("detail_categories_included", []),
                generation_metadata=doc.get("generation_metadata", {})
            ))
        
        return personas
    
    @staticmethod
    async def search_personas_by_category(
        db: Any,
        category_name: str,
        limit: int = 20
    ) -> List[PersonaV2Response]:
        """Find personas that have a specific detail category"""
        
        query = {f"detail_categories.{category_name}": {"$exists": True}}
        
        cursor = db.personas_v2.find(query).limit(limit)
        personas = []
        
        async for doc in cursor:
            personas.append(PersonaV2Response(
                id=doc["_id"],
                template_id=doc["template_id"],
                persona_type=doc["persona_type"],
                mode=doc["mode"],
                name=doc["name"],
                age=doc["age"],
                gender=doc["gender"],
                role=doc["role"],
                description=doc["description"],
                location=doc["location"],
                archetype=doc["archetype"],
                detail_categories=doc.get("detail_categories", {}),
                detail_categories_included=doc.get("detail_categories_included", []),
                conversation_rules=doc.get("conversation_rules", {}),
                system_prompt=doc.get("system_prompt"),
                created_at=doc["created_at"]
            ))
        
        return personas
