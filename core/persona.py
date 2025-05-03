
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime


from models.persona_models import  PersonaBase, PersonaCreate, PersonaResponse, PersonaDB, PersonaGenerateRequest
from models.user_models import UserDB,UserRole

from core.user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/personas", tags=["Personas"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Persona Any Operations
async def get_personas(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[PersonaDB]:
    """
    Get a list of all personas with permission checks.
    - Regular users can view all personas (read-only)
    - Admins/Superadmins: all personas
    """
    if not current_user:
        return []
    
    personas = []
    cursor = db.personas.find().skip(skip).limit(limit)
    async for document in cursor:
        personas.append(PersonaDB(**document))
    
    return personas

async def get_persona(
    db: Any, 
    persona_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[PersonaDB]:
    """
    Get a persona by ID (all users can view personas)
    """
    if not current_user:
        return None
        
    # Use string representation for MongoDB query
    persona = await db.personas.find_one({"_id": str(persona_id)})
    if persona:
        return PersonaDB(**persona)
    return None

async def get_personas_by_type(
    db: Any, 
    persona_type: str,
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[PersonaDB]:
    """
    Get personas filtered by type
    """
    if not current_user:
        return []
    
    personas = []
    cursor = db.personas.find({"persona_type": persona_type}).skip(skip).limit(limit)
    async for document in cursor:
        personas.append(PersonaDB(**document))
    
    return personas

async def create_persona(
    db: Any, 
    persona: PersonaCreate, 
    created_by: UUID
) -> PersonaDB:
    """
    Create a new persona (admin/superadmin only)
    """
    # Create the full persona representation
    # This would typically combine all fields into a structured document
    full_persona = {
        "name": persona.name,
        "description": persona.description,
        "type": persona.persona_type,
        "goal": persona.character_goal,
        "location": persona.location,
        "details": persona.persona_details,
        "situation": persona.situation,
        "context": persona.business_or_personal,
        "background": persona.background_story
    }
    
    # Create PersonaDB model
    persona_db = PersonaDB(
        **persona.dict(),
        full_persona=full_persona,  # Set the full persona
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    persona_dict = persona_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in persona_dict:
        persona_dict["_id"] = str(persona_dict["_id"])
    
    # Store created_by as string
    if "created_by" in persona_dict:
        persona_dict["created_by"] = str(persona_dict["created_by"])
    
    result = await db.personas.insert_one(persona_dict)
    created_persona = await db.personas.find_one({"_id": str(result.inserted_id)})
    
    return PersonaDB(**created_persona)

async def generate_persona(
    db: Any, 
    request: PersonaGenerateRequest, 
    created_by: UUID
) -> PersonaDB:
    """
    Generate a persona based on a description (admin/superadmin only)
    
    In a real application, this might involve AI services or templates.
    For this example, we'll create a simple persona from the request.
    """
    # Generate persona name
    persona_name = f"Generated {request.persona_type.capitalize()}"
    
    # Create a generated persona
    persona = PersonaCreate(
        name=persona_name,
        description=request.persona_description,
        persona_type=request.persona_type,
        character_goal="Generated goal based on description",
        location=request.location or "Unknown",
        persona_details="Generated details based on the provided description",
        situation="Standard situation for this persona type",
        business_or_personal=request.business_or_personal,
        background_story="Generated background story"
    )
    
    # Use the standard creation method
    return await create_persona(db, persona, created_by)

async def update_persona(
    db: Any, 
    persona_id: UUID, 
    persona_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[PersonaDB]:
    """
    Update a persona with permission checks
    """
    # Get the persona to update - use string representation
    persona = await db.personas.find_one({"_id": str(persona_id)})
    if not persona:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update personas they created
        if persona.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update personas they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update personas
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update personas"
        )
    
    # Add updated timestamp
    persona_updates["updated_at"] = datetime.now()
    
    # If changing core fields that affect the full_persona, update it too
    if any(key in persona_updates for key in ["name", "description", "persona_type", "character_goal", 
                                             "location", "persona_details", "situation", 
                                             "business_or_personal", "background_story"]):
        # Get current persona to merge with updates
        current_persona = PersonaDB(**persona)
        
        # Apply updates to create updated persona
        updated_fields = current_persona.dict()
        updated_fields.update(persona_updates)
        
        # Create the updated full_persona
        full_persona = {
            "name": updated_fields.get("name"),
            "description": updated_fields.get("description"),
            "type": updated_fields.get("persona_type"),
            "goal": updated_fields.get("character_goal"),
            "location": updated_fields.get("location"),
            "details": updated_fields.get("persona_details"),
            "situation": updated_fields.get("situation"),
            "context": updated_fields.get("business_or_personal"),
            "background": updated_fields.get("background_story")
        }
        
        # Add full_persona to updates
        persona_updates["full_persona"] = full_persona
    
    # Update in database - use string representation
    await db.personas.update_one(
        {"_id": str(persona_id)},
        {"$set": persona_updates}
    )
    
    updated_persona = await db.personas.find_one({"_id": str(persona_id)})
    if updated_persona:
        return PersonaDB(**updated_persona)
    return None

async def delete_persona(db: Any, persona_id: UUID, deleted_by: UUID) -> bool:
    """
    Delete a persona with permission checks
    """
    # Get the persona to delete - use string representation
    persona = await db.personas.find_one({"_id": str(persona_id)})
    if not persona:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete personas they created
        if persona.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete personas they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete personas
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete personas"
        )
    
    # Check if this persona is being used in any avatar interactions - use string representation
    avatar_interactions_using_persona = await db.avatar_interactions.find(
        {"personas": str(persona_id)}
    ).to_list(length=1)
    
    if avatar_interactions_using_persona:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete persona as it is being used in one or more avatar interactions"
        )
    
    # Delete the persona - use string representation
    result = await db.personas.delete_one({"_id": str(persona_id)})
    
    return result.deleted_count > 0

# Persona API Endpoints
@router.get("/", response_model=List[PersonaResponse])
async def get_personas_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of all personas (all users can view)
    """
    return await get_personas(db, skip, limit, current_user)

@router.get("/type/{persona_type}", response_model=List[PersonaResponse])
async def get_personas_by_type_endpoint(
    persona_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get personas filtered by type
    """
    return await get_personas_by_type(db, persona_type, skip, limit, current_user)

@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona_endpoint(
    persona_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific persona by ID
    """
    persona = await get_persona(db, persona_id, current_user)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return persona

@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona_endpoint(
    persona: PersonaCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create personas
):
    """
    Create a new persona (admin/superadmin only)
    """
    return await create_persona(db, persona, admin_user.id)

@router.post("/generate", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def generate_persona_endpoint(
    request: PersonaGenerateRequest,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can generate personas
):
    """
    Generate a persona based on a description (admin/superadmin only)
    """
    return await generate_persona(db, request, admin_user.id)

@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona_endpoint(
    persona_id: UUID,
    persona_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update personas
):
    """
    Update a persona by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_persona = await update_persona(db, persona_id, persona_updates, admin_user.id)
    if not updated_persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return updated_persona

@router.delete("/{persona_id}", response_model=Dict[str, bool])
async def delete_persona_endpoint(
    persona_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete personas
):
    """
    Delete a persona by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_persona(db, persona_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
    return {"success": True}