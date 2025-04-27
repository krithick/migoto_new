from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime


from models.course_models import   CourseCreate, CourseResponse, CourseWithModulesResponse, CourseDB,CourseBase
from models.modules_models import ModuleResponse
from models.user_models import UserDB ,UserRole

from core.user import get_current_user, get_admin_user, get_superadmin_user

# Create router
router = APIRouter(prefix="/courses", tags=["Courses"])

# Any dependency (assumed to be defined elsewhere)
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()

# Course Any Operations
async def get_courses(
    db: Any, 
    skip: int = 0, 
    limit: int = 100,
    current_user: Optional[UserDB] = None
) -> List[CourseDB]:
    """
    Get a list of courses based on user role:
    - Regular users: only assigned courses
    - Admins/Superadmins: all courses
    """
    if not current_user:
        return []
    
    courses = []
    
    # For regular users, only return assigned courses
    if current_user.role == UserRole.USER:
        # Get user's assigned courses
        user_data = current_user.dict()
        assigned_course_ids = user_data.get("assigned_courses", [])
        
        # Convert UUIDs to strings for MongoDB
        assigned_course_ids_str = [str(course_id) for course_id in assigned_course_ids]
        
        if assigned_course_ids_str:
            cursor = db.courses.find({"_id": {"$in": assigned_course_ids_str}}).skip(skip).limit(limit)
            async for document in cursor:
                courses.append(CourseDB(**document))
    else:
        # For admins and superadmins, return all courses
        cursor = db.courses.find().skip(skip).limit(limit)
        async for document in cursor:
            courses.append(CourseDB(**document))
    
    return courses

async def get_course(db: Any, course_id: UUID, current_user: Optional[UserDB] = None) -> Optional[CourseDB]:
    """
    Get a course by ID with permission checks:
    - Regular users: can only access assigned courses
    - Admins/Superadmins: can access all courses
    """
    # Always use string representation for MongoDB query
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        return None
    
    # If user is regular user, check if course is assigned to them
    if current_user and current_user.role == UserRole.USER:
        user_data = current_user.dict()
        assigned_courses = user_data.get("assigned_courses", [])
        
        # Convert assigned courses to strings for comparison
        assigned_courses_str = [str(course_id) for course_id in assigned_courses]
        
        if str(course_id) not in assigned_courses_str:
            return None
    
    return CourseDB(**course)

async def get_course_with_modules(
    db: Any, 
    course_id: UUID, 
    current_user: Optional[UserDB] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a course with all modules expanded and check permissions
    """
    # First check if user can access this course
    course = await get_course(db, course_id, current_user)
    if not course:
        return None
    
    # Get course with expanded modules
    course_dict = course.dict()
    
    # Get modules for this course
    module_ids = course_dict.get("modules", [])
    
    # Convert module_ids to strings for MongoDB
    module_ids_str = [str(module_id) for module_id in module_ids]
    
    modules = []
    
    for module_id in module_ids_str:
        module = await db.modules.find_one({"_id": module_id})
        if module:
            module["id"] = module.pop("_id")
            modules.append(module)
            # modules.append((module))
    
    # Replace module IDs with module data
    course_dict["modules"] = modules
    print(course_dict,"heeeeeeeeeeee")
    return CourseWithModulesResponse(**course_dict)

async def create_course(db: Any, course: CourseCreate, created_by: UUID) -> CourseDB:
    """Create a new course"""
    # Create CourseDB model
    course_dict = course.dict()
    
    course_db = CourseDB(
        **course_dict,
        created_by=created_by,  # Set the creator
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    course_dict = course_db.dict(by_alias=True)
    
    # Always use string for _id in MongoDB
    if "_id" in course_dict:
        course_dict["_id"] = str(course_dict["_id"])
    
    # Convert all UUIDs to strings for MongoDB
    if "modules" in course_dict and course_dict["modules"]:
        course_dict["modules"] = [str(module_id) for module_id in course_dict["modules"]]
    
    # Store created_by as string
    if "created_by" in course_dict:
        course_dict["created_by"] = str(course_dict["created_by"])
    
    result = await db.courses.insert_one(course_dict)
    created_course = await db.courses.find_one({"_id": str(result.inserted_id)})
    
    return CourseDB(**created_course)

async def update_course(
    db: Any, 
    course_id: UUID, 
    course_updates: Dict[str, Any], 
    updated_by: UUID
) -> Optional[CourseDB]:
    """Update a course with permission checks"""
    # Get the course to update - use string representation
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only update courses they created
        if course.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update courses they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot update courses
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update courses"
        )
    
    # Add updated timestamp
    course_updates["updated_at"] = datetime.now()
    
    # Convert module UUIDs to strings if present
    if "modules" in course_updates and course_updates["modules"]:
        course_updates["modules"] = [str(module_id) for module_id in course_updates["modules"]]
    
    # Update in database - use string representation
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$set": course_updates}
    )
    
    updated_course = await db.courses.find_one({"_id": str(course_id)})
    if updated_course:
        return CourseDB(**updated_course)
    return None

async def delete_course(db: Any, course_id: UUID, deleted_by: UUID) -> bool:
    """Delete a course with permission checks"""
    # Get the course to delete - use string representation
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        return False
    
    # Get the user making the deletion - use string representation
    deleter = await db.users.find_one({"_id": str(deleted_by)})
    if not deleter:
        return False
    
    # Convert deleter to UserDB for role checking
    deleter = UserDB(**deleter)
    
    # Check permissions - compare string representations
    if deleter.role == UserRole.ADMIN:
        # Admin can only delete courses they created
        if course.get("created_by") != str(deleted_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete courses they created"
            )
    elif deleter.role != UserRole.SUPERADMIN:
        # Regular users cannot delete courses
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete courses"
        )
    
    # Delete the course - use string representation
    result = await db.courses.delete_one({"_id": str(course_id)})
    
    # If course was deleted, remove references to it from users' assigned_courses
    if result.deleted_count > 0:
        await db.users.update_many(
            {"assigned_courses": str(course_id)},
            {"$pull": {"assigned_courses": str(course_id)}}
        )
    
    return result.deleted_count > 0

async def publish_course(db: Any, course_id: UUID, publish_status: bool, updated_by: UUID) -> Optional[CourseDB]:
    """Publish or unpublish a course with permission checks"""
    # Get the course - use string representation
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        return None
    
    # Get the user making the update - use string representation
    updater = await db.users.find_one({"_id": str(updated_by)})
    if not updater:
        return None
    
    # Convert updater to UserDB for role checking
    updater = UserDB(**updater)
    
    # Check permissions - compare string representations
    if updater.role == UserRole.ADMIN:
        # Admin can only publish/unpublish courses they created
        if course.get("created_by") != str(updated_by):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only publish/unpublish courses they created"
            )
    elif updater.role != UserRole.SUPERADMIN:
        # Regular users cannot publish/unpublish courses
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish/unpublish courses"
        )
    
    # Update the course - use string representation
    await db.courses.update_one(
        {"_id": str(course_id)},
        {"$set": {"is_published": publish_status, "updated_at": datetime.now()}}
    )
    
    updated_course = await db.courses.find_one({"_id": str(course_id)})
    if updated_course:
        return CourseDB(**updated_course)
    return None

# Course API Endpoints
@router.get("/", response_model=List[CourseResponse])
async def get_courses_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a list of courses (filtered by user role)
    - Regular users: only assigned courses
    - Admins/Superadmins: all courses
    """
    return await get_courses(db, skip, limit, current_user)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific course by ID (with permission checks)
    """
    course = await get_course(db, course_id, current_user)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or access denied")
    return course

@router.get("/{course_id}/full", response_model=CourseWithModulesResponse)
async def get_course_with_modules_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a course with all its modules expanded
    """
    course = await get_course_with_modules(db, course_id, current_user)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or access denied")
    return course

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    course: CourseCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can create courses
):
    """
    Create a new course (admin/superadmin only)
    """
    return await create_course(db, course, admin_user.id)

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course_endpoint(
    course_id: UUID,
    course_updates: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can update courses
):
    """
    Update a course by ID (admin/superadmin only, with ownership checks for admins)
    """
    updated_course = await update_course(db, course_id, course_updates, admin_user.id)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", response_model=Dict[str, bool])
async def delete_course_endpoint(
    course_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can delete courses
):
    """
    Delete a course by ID (admin/superadmin only, with ownership checks for admins)
    """
    deleted = await delete_course(db, course_id, admin_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return {"success": True}

@router.put("/{course_id}/publish", response_model=CourseResponse)
async def publish_course_endpoint(
    course_id: UUID,
    publish_data: Dict[str, bool] = Body(..., example={"publish": True}),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins and superadmins can publish courses
):
    """
    Publish or unpublish a course (admin/superadmin only, with ownership checks for admins)
    """
    publish_status = publish_data.get("publish", True)
    updated_course = await publish_course(db, course_id, publish_status, admin_user.id)
    if not updated_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return updated_course