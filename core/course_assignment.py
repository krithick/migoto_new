from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, status
from models.user_models import UserDB, UserRole
from models.course_assignment_models import CourseAssignmentCreate, CourseAssignmentDB, CourseAssignmentUpdate

# Create an assignment
async def create_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> CourseAssignmentDB:
    """Assign a course to a user and record the assignment"""
    
    # Check if assignment already exists
    existing = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if existing:
        return CourseAssignmentDB(**existing)
    
    # Create assignment record
    assignment = CourseAssignmentCreate(
        user_id=user_id,
        course_id=course_id,
        assigned_date=datetime.now(),
        completed=False,
        completed_date=None
    )
    
    # Convert to DB model
    assignment_db = CourseAssignmentDB(**assignment.dict())
    assignment_dict = assignment_db.dict(by_alias=True)
    
    # Convert UUIDs to strings for MongoDB
    if "_id" in assignment_dict:
        assignment_dict["_id"] = str(assignment_dict["_id"])
    assignment_dict["user_id"] = str(assignment_dict["user_id"])
    assignment_dict["course_id"] = str(assignment_dict["course_id"])
    
    # Insert into database
    result = await db.user_course_assignments.insert_one(assignment_dict)
    created_assignment = await db.user_course_assignments.find_one({"_id": str(result.inserted_id)})
    
    return CourseAssignmentDB(**created_assignment)

# Get all course assignments for a user
async def get_user_course_assignments(
    db: Any,
    user_id: UUID
) -> List[CourseAssignmentDB]:
    """Get all course assignments for a user"""
    
    assignments = []
    cursor = db.user_course_assignments.find({"user_id": str(user_id)})
    async for document in cursor:
        assignments.append(CourseAssignmentDB(**document))
    
    return assignments

# Get a specific course assignment
async def get_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> Optional[CourseAssignmentDB]:
    """Get a specific course assignment"""
    
    assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if assignment:
        return CourseAssignmentDB(**assignment)
    
    return None

# Update a course assignment
async def update_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID,
    update_data: CourseAssignmentUpdate
) -> Optional[CourseAssignmentDB]:
    """Update a course assignment"""
    
    # Find the assignment
    assignment = await db.user_course_assignments.find_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    if not assignment:
        return None
    
    # Prepare update data
    update_dict = {}
    for key, value in update_data.dict(exclude_unset=True).items():
        if value is not None:
            update_dict[key] = value
    
    # Special case for completion status
    if "completed" in update_dict:
        if update_dict["completed"]:
            # When marking as completed, set the completion date
            update_dict["completed_date"] = datetime.now()
        else:
            # When marking as incomplete, clear the completion date
            update_dict["completed_date"] = None
    
    # Update in database
    if update_dict:
        await db.user_course_assignments.update_one(
            {"_id": assignment["_id"]},
            {"$set": update_dict}
        )
        
        updated_assignment = await db.user_course_assignments.find_one({"_id": assignment["_id"]})
        if updated_assignment:
            return CourseAssignmentDB(**updated_assignment)
    
    return CourseAssignmentDB(**assignment)

# Delete a course assignment
async def delete_course_assignment(
    db: Any,
    user_id: UUID,
    course_id: UUID
) -> bool:
    """Delete a course assignment"""
    
    result = await db.user_course_assignments.delete_one({
        "user_id": str(user_id),
        "course_id": str(course_id)
    })
    
    return result.deleted_count > 0

# Get courses with assignment data
async def get_user_courses_with_assignments(
    db: Any,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """Get all courses assigned to a user with assignment data"""
    
    user = await db.users.find_one({"_id": str(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    assigned_course_ids = [str(course_id) for course_id in user.get("assigned_courses", [])]
    
    # Get all assignments for this user
    assignments = {}
    cursor = db.user_course_assignments.find({"user_id": str(user_id)})
    async for assignment in cursor:
        assignments[assignment["course_id"]] = {
            "assigned_date": assignment["assigned_date"],
            "completed": assignment.get("completed", False),
            "completed_date": assignment.get("completed_date")
        }
    
    # Get course data
    courses = []
    if assigned_course_ids:
        cursor = db.courses.find({"_id": {"$in": assigned_course_ids}})
        async for course in cursor:
            # CRITICAL FIX: Convert _id to id
            course["id"] = course.pop("_id")
            
            # Add assignment data
            course_id = course["id"]  # Now using "id" instead of "_id"
            if course_id in assignments:
                data = assignments[course_id]
                course["assigned_date"] = data["assigned_date"]
                course["completed"] = data["completed"]
                course["completed_date"] = data["completed_date"]
            else:
                # Default values
                course["assigned_date"] = user.get("created_at", datetime.now())
                course["completed"] = False
                course["completed_date"] = None
            
            courses.append(course)
    
    return courses