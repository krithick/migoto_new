from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict, Any ,Union
from uuid import UUID
from datetime import datetime, timedelta
import os
from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt, JWTError
from passlib.context import CryptContext
from uuid import uuid4
from models.user_models import (
    UserResponse, UserCreate, UserUpdate, UserWithCoursesResponse, UserDB,
    AdminUserResponse, AdminUserCreate, AdminUserDB,
    Token, UserRole, LoginRequest, UserAssignmentUpdate, CourseAssignmentUpdate,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm,
    TokenData
)
from models.course_assignment_models import CompletionUpdate
from core.course_assignment import (
    update_course_assignment, 
    get_user_courses_with_assignments,
    CourseAssignmentUpdate
)
from models.course_models import CourseWithAssignmentResponse
from core.course_assignment import create_course_assignment, delete_course_assignment

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 1 week

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Create router
router = APIRouter(prefix="/auth", tags=["Auth"])
async def get_database():
    from database import get_db  # Import your existing function
    return await get_db()
# Any dependency (assumed to be defined elsewhere)
# async def get_database():
#     db = Any(
#         mongo_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
#         db_name=os.getenv("MONGODB_DB_NAME", "learning_platform")
#     )
#     try:
#         yield db
#     finally:
#         await db.close()
# async def get_database():
#     from database import get_db as main_get_database
#     return await anext(main_get_database())

# User Authentication Helpers
def verify_password(plain_password, hashed_password):
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> tuple:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, int(expire.timestamp())

# Dependency to get the current user
async def get_current_user(db: Any = Depends(get_database), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user

# Dependency to get admin user
async def get_admin_user(current_user: AdminUserDB = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Admin role required."
        )
    return current_user

# Dependency to get superadmin user
async def get_superadmin_user(current_user: UserDB = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Superadmin role required."
        )
    return current_user

# User Any Operations
async def get_users(db: Any, skip: int = 0, limit: int = 100) -> List[UserDB]:
    """Get a list of all users"""
    users = []
    cursor = db.users.find().skip(skip).limit(limit)
    async for document in cursor:
        users.append(UserDB(**document))
    return users

# 

async def get_user_by_id(db: Any, user_id: UUID) -> Optional[Union[UserDB, AdminUserDB]]:
    """Get a user by ID"""
    # Always use string representation of UUID for MongoDB queries
    user = await db.users.find_one({"_id": str(user_id)})
    
    if user:
        # Check the role and return the appropriate model
        if user.get("role") in [UserRole.ADMIN, UserRole.SUPERADMIN] and "managed_users" in user:
            return AdminUserDB(**user)
        else:
            return UserDB(**user)
    return None
# 
async def get_user_by_email(db: Any, email: str) -> Optional[UserDB]:
    """Get a user by email"""
    user = await db.users.find_one({"email": email})
    if user:
        return UserDB(**user)
    return None

async def authenticate_user(db: Any, email: str, password: str) -> Optional[UserDB]:
    """Authenticate a user and return user if successful"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(db: Any, users: List[UserCreate], created_by: Optional[UUID] = None) -> UserDB:
    """Create a new user"""
    created_users = []

    for user in users:
        existing_user = await get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_dict = user.dict()
        hashed_password = get_password_hash(user_dict.pop("password"))

        assignee_emp_id = None

        if created_by:
            admin = await get_user_by_id(db, created_by)
            if admin and admin.role == UserRole.ADMIN:
                assignee_emp_id = admin.emp_id

        user_db = UserDB(
            **user_dict,
            hashed_password=hashed_password,
            assignee_emp_id=assignee_emp_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        
        # Insert into database
        user_dict = user_db.dict(by_alias=True)
        
        # Always store _id as string in MongoDB
        if "_id" in user_dict:
            user_dict["_id"] = str(user_dict["_id"])


        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": str(result.inserted_id)})

        if created_by and admin and admin.role == UserRole.ADMIN:
            # Add the new user to admin's managed_users list
            await db.users.update_one(
                {"_id": str(admin.id)},
                {"$addToSet": {"managed_users": str(user_db.id)}}
            )
        created_users.append(UserDB(**created_user))

    return created_users


# Fix for create_admin_user 
async def create_admin_user(db: Any, admin: AdminUserCreate, created_by: UUID) -> AdminUserDB:
    """Create a new admin user (by superadmin)"""
    # Check if creator is superadmin
    creator = await get_user_by_id(db, created_by)
    if not creator or creator.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmins can create admin users"
        )
    
    # Check if user with this email already exists
    existing_user = await get_user_by_email(db, admin.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create AdminUserDB model
    admin_dict = admin.dict()
    hashed_password = get_password_hash(admin_dict.pop("password"))
    
    admin_db = AdminUserDB(
        **admin_dict,
        hashed_password=hashed_password,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into database
    admin_dict = admin_db.dict(by_alias=True)
    
    # Always store _id as string in MongoDB
    if "_id" in admin_dict:
        admin_dict["_id"] = str(admin_dict["_id"])
    
    # Convert managed_users UUIDs to strings
    if "managed_users" in admin_dict and admin_dict["managed_users"]:
        admin_dict["managed_users"] = [str(user_id) for user_id in admin_dict["managed_users"]]
    
    result = await db.users.insert_one(admin_dict)
    created_admin = await db.users.find_one({"_id": str(result.inserted_id)})
    
    return AdminUserDB(**created_admin)




# Fix for update_user
async def update_user(db: Any, user_id: UUID, update_data: UserUpdate, updated_by: UUID) -> Optional[UserDB]:
    """Update a user"""
    # Get the user to update
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Get the user making the update
    updater = await get_user_by_id(db, updated_by)
    if not updater:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized update attempt"
        )
    
    # Check authorization
    if updater.role == UserRole.USER and updater.id != user.id:
        # Regular users can only update themselves
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only update their own information"
        )
    elif updater.role == UserRole.ADMIN:
        # Admins can update users they manage and themselves
        admin = await db.users.find_one({
            "_id": str(updated_by), 
            "managed_users": str(user_id)
        })
        if not admin and updater.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can only update managed users or themselves"
            )
        
        # Admins can't change roles to superadmin
        if update_data.role == UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot promote users to superadmin"
            )
    
    # Prepare update data
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now()
    
    # Update in database
    await db.users.update_one(
        {"_id": str(user_id)},
        {"$set": update_dict}
    )
    
    updated_user = await db.users.find_one({"_id": str(user_id)})
    if updated_user:
        return UserDB(**updated_user)
    return None



# Fix for delete_user
async def delete_user(db: Any, user_id: UUID, deleted_by: UUID) -> bool:
    """Delete a user"""
    # Get the user to delete
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    # Get the user making the deletion
    deleter = await get_user_by_id(db, deleted_by)
    if not deleter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized deletion attempt"
        )
    
    # Check authorization
    if deleter.role == UserRole.USER and deleter.id != user.id:
        # Regular users can only delete themselves
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only delete themselves"
        )
    elif deleter.role == UserRole.ADMIN:
        # Admins can delete users they manage but not other admins or superadmins
        if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot delete other admins or superadmins"
            )
        
        admin = await db.users.find_one({
            "_id": str(deleted_by), 
            "managed_users": str(user_id)
        })
        if not admin and deleter.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can only delete managed users or themselves"
            )
    
    # Delete from database
    result = await db.users.delete_one({"_id": str(user_id)})
    
    # Remove user from any admin's managed_users
    if result.deleted_count > 0:
        await db.users.update_many(
            {"managed_users": str(user_id)},
            {"$pull": {"managed_users": str(user_id)}}
        )
    
    return result.deleted_count > 0
async def assign_users_to_admin(db: Any, admin_id: UUID, user_ids: List[UUID], operation: str) -> bool:
    """Assign or remove users from an admin's management"""
    # Check if admin exists and is actually an admin
    admin = await get_user_by_id(db, admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified admin does not exist or is not an admin"
        )
    
    # Validate that all user_ids exist and are not admins or superadmins
    for user_id in user_ids:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {user_id} does not exist"
            )
        if user.role != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot assign admin or superadmin as managed user"
            )
    
    # Perform the operation
    if operation == "add":
        # Add users to admin's managed_users
        await db.users.update_one(
            {"_id": admin_id},
            {"$addToSet": {"managed_users": {"$each": user_ids}}}
        )
    elif operation == "remove":
        # Remove users from admin's managed_users
        await db.users.update_one(
            {"_id": admin_id},
            {"$pull": {"managed_users": {"$in": user_ids}}}
        )
    
    return True




async def assign_courses_to_user(db: Any, user_id: UUID, course_ids: List[UUID], operation: str) -> bool:
    """Assign or remove courses from a user"""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified user does not exist"
        )
    
    # Convert UUIDs to strings for MongoDB
    course_ids_str = [str(course_id) for course_id in course_ids]
    
    # Validate that all course_ids exist
    for course_id in course_ids_str:
        course = await db.courses.find_one({"_id": course_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with ID {course_id} does not exist"
            )
    
    # Perform the operation
    if operation == "add":
        # Add courses to user's assigned_courses (existing functionality)
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$addToSet": {"assigned_courses": {"$each": course_ids_str}}}
        )
        
        # Record assignment dates in junction collection
        assignment_time = datetime.now()
        for course_id in course_ids_str:
            # Check if assignment already exists
            existing = await db.user_course_assignments.find_one({
                "user_id": str(user_id),
                "course_id": course_id
            })
            
            if not existing:
                # Create new assignment record
                assignment = {
                    "_id": str(uuid4()),
                    "user_id": str(user_id),
                    "course_id": course_id,
                    "assigned_date": assignment_time,
                    "completed": False,
                    "completed_date": None
                }
                await db.user_course_assignments.insert_one(assignment)
                
    elif operation == "remove":
        # Remove courses from user's assigned_courses (existing functionality)
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$pull": {"assigned_courses": {"$in": course_ids_str}}}
        )
        
        # Remove assignment records
        await db.user_course_assignments.delete_many({
            "user_id": str(user_id),
            "course_id": {"$in": course_ids_str}
        })
    
    return True

async def assign_courses_to_user(db: Any, user_id: UUID, course_ids: List[UUID], operation: str) -> bool:
    """Assign or remove courses from a user"""
    # Check if user exists
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified user does not exist"
        )
    
    # Convert UUIDs to strings for MongoDB
    course_ids_str = [str(course_id) for course_id in course_ids]
    
    # Validate that all course_ids exist
    for course_id in course_ids_str:
        course = await db.courses.find_one({"_id": course_id})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with ID {course_id} does not exist"
            )
    
    # Perform the operation
    if operation == "add":
        # Add courses to user's assigned_courses (existing functionality)
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$addToSet": {"assigned_courses": {"$each": course_ids_str}}}
        )
        
        # Create course assignments for each course
        for course_id in course_ids:
            await create_course_assignment(db, user_id, course_id)
            
    elif operation == "remove":
        # Remove courses from user's assigned_courses (existing functionality)
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$pull": {"assigned_courses": {"$in": course_ids_str}}}
        )
        
        # Delete course assignments
        for course_id in course_ids:
            await delete_course_assignment(db, user_id, course_id)
    
    return True
# adsdsa
# 

# Fix for get_users_by_admin
async def get_users_by_admin(db: Any, admin_id: UUID) -> List[UserDB]:
    """Get all users managed by a specific admin"""
    admin = await get_user_by_id(db, admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified admin does not exist or is not an admin"
        )
    
    admin_data = admin.dict()
    managed_user_ids = admin_data.get("managed_users", [])
    
    # Make sure we're using string IDs for MongoDB
    managed_user_ids_str = [str(user_id) for user_id in managed_user_ids]
    
    users = []
    if managed_user_ids_str:
        cursor = db.users.find({"_id": {"$in": managed_user_ids_str}})
        async for document in cursor:
            users.append(UserDB(**document))
    
    return users


async def get_admins_by_superadmin(db: Any, skip: int = 0, limit: int = 100) -> List[AdminUserDB]:
    """Get all admin users (for superadmin)"""
    admins = []
    cursor = db.users.find({"role": UserRole.ADMIN}).skip(skip).limit(limit)
    async for document in cursor:
        admins.append(AdminUserDB(**document))
    return admins



async def get_user_courses(db: Any, user_id: UUID) -> List[Dict[str, Any]]:
    """Get all courses assigned to a user"""
    # Replace with call to the new function
    return await get_user_courses_with_assignments(db, user_id)
async def change_password(db: Any, user_id: UUID, current_password: str, new_password: str) -> bool:
    """Change a user's password"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    hashed_password = get_password_hash(new_password)
    
    # Update in database
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now()}}
    )
    
    return True

# Authentication API Endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Any = Depends(get_database)):
    """
    OAuth2 compatible token endpoint for login
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token_data = {"sub": str(user.id), "role": user.role}
    access_token, expires_at = create_access_token(token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Any = Depends(get_database)):
    """
    Login endpoint that accepts JSON data
    """
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    token_data = {"sub": str(user.id), "role": user.role}
    access_token, expires_at = create_access_token(token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.post("/password/change", response_model=Dict[str, bool])
async def change_password_endpoint(
    password_data: PasswordChangeRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    """
    Change the current user's password
    """
    success = await change_password(
        db, 
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    return {"success": success}

@router.post("/password/reset/request", response_model=Dict[str, bool])
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Any = Depends(get_database)
):
    """
    Request a password reset (would send email in production)
    """
    # In a real application, this would check if the email exists
    # and send a reset token via email
    return {"success": True}

@router.post("/password/reset/confirm", response_model=Dict[str, bool])
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    db: Any = Depends(get_database)
):
    """
    Confirm a password reset using a token
    """
    # In a real application, this would verify the token
    # and reset the user's password
    return {"success": True}

# User Management Endpoints
# @router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def create_user_endpoint(
#     user: UserCreate,
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)
# ):
#     """
#     Create a new user (admin/superadmin only)
#     """
#     return await create_user(db, user)
@router.post("/users", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    users: List[UserCreate],
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Create a new user (admin/superadmin only)
    """
    return await create_user(db, users, created_by=admin_user.id)

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    """
    Get current authenticated user
    """
    return current_user

# @router.get("/users/me/courses", response_model=List[Dict[str, Any]])
# async def read_users_me_courses(
#     current_user: UserDB = Depends(get_current_user),
#     db: Any = Depends(get_database)
# ):
#     """
#     Get courses assigned to current user
#     """
#     return await get_user_courses(db, current_user.id)
@router.get("/users/me/courses", response_model=List[CourseWithAssignmentResponse])
async def read_users_me_courses(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get courses assigned to current user with assignment data
    """
    return await get_user_courses_with_assignments(db, current_user.id)

@router.put("/users/me/courses/{course_id}/completion", response_model=Dict[str, bool])
async def update_course_completion_status(
    course_id: UUID,
    completion_data: CompletionUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update completion status for one of the current user's assigned courses
    """
    # Validate course exists and is assigned to user
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    user_data = current_user.dict()
    assigned_courses = [str(c_id) for c_id in user_data.get("assigned_courses", [])]
    
    if str(course_id) not in assigned_courses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course is not assigned to current user"
        )
    
    # Create update model
    update_data = CourseAssignmentUpdate(
        completed=completion_data.completed
    )
    
    # Update the assignment
    result = await update_course_assignment(db, current_user.id, course_id, update_data)
    
    return {"success": result is not None}


@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get list of users (admin: managed users, superadmin: all users)
    """
    # For admin, return only their managed users
    if admin_user.role == UserRole.ADMIN:
        return await get_users_by_admin(db, admin_user.id)
    
    # For superadmin, return all users
    return await get_users(db, skip, limit)

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get specific user by ID (admin only)
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # If admin (not superadmin), check if they manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = admin_user.dict()
        managed_users = admin_data.get("managed_users", [])
        if user_id not in managed_users and admin_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user"
            )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: UUID,
    user_update: UserUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a user
    """
    updated_user = await update_user(db, user_id, user_update, current_user.id)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return updated_user

@router.delete("/users/{user_id}", response_model=Dict[str, bool])
async def delete_user_endpoint(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a user
    """
    deleted = await delete_user(db, user_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"success": True}

# Admin Management Endpoints
@router.post("/admins", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_endpoint(
    admin: AdminUserCreate,
    db: Any = Depends(get_database),
    superadmin: UserDB = Depends(get_superadmin_user)
):
    """
    Create a new admin user (superadmin only)
    """
    return await create_admin_user(db, admin, superadmin.id)

@router.get("/admins", response_model=List[AdminUserResponse])
async def read_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Any = Depends(get_database),
    superadmin: UserDB = Depends(get_superadmin_user)
):
    """
    Get list of admin users (superadmin only)
    """
    return await get_admins_by_superadmin(db, skip, limit)

@router.post("/admins/{admin_id}/users", response_model=Dict[str, bool])
async def assign_users_to_admin_endpoint(
    admin_id: UUID,
    assignment: UserAssignmentUpdate,
    db: Any = Depends(get_database),
    superadmin: UserDB = Depends(get_superadmin_user)
):
    """
    Assign or remove users from an admin's management (superadmin only)
    """
    success = await assign_users_to_admin(
        db, 
        admin_id, 
        assignment.user_ids, 
        assignment.operation
    )
    return {"success": success}

# Course Assignment Endpoints
@router.post("/courses/assign", response_model=Dict[str, bool])
async def assign_courses_to_user_endpoint(
    assignment: CourseAssignmentUpdate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Assign or remove courses from a user (admin only)
    """
    # If admin (not superadmin), check if they manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = admin_user.dict()
        managed_users = admin_data.get("managed_users", [])
        if assignment.user_id not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to manage courses for this user"
            )
    
    success = await assign_courses_to_user(
        db, 
        assignment.user_id, 
        assignment.course_ids, 
        assignment.operation
    )
    return {"success": success}

@router.get("/users/{user_id}/courses", response_model=List[Dict[str, Any]])
async def read_user_courses(
    user_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get courses assigned to a specific user (admin only)
    """
    # If admin (not superadmin), check if they manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = admin_user.dict()
        managed_users = admin_data.get("managed_users", [])
        if user_id not in managed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view courses for this user"
            )
    
    return await get_user_courses_with_assignments(db, user_id)

from core.module import get_modules_by_course
from core.scenario import get_scenarios_by_module
@router.get("/users/me/progress-dashboard", response_model=Dict[str, Any])
async def get_progress_dashboard(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a comprehensive dashboard of user progress across all courses, modules and scenarios
    """
    # Get assigned courses
    user_courses = await get_user_courses_with_assignments(db, current_user.id)
    
    # Prepare results structure
    dashboard = {
        "courses": [],
        "total_courses": len(user_courses),
        "completed_courses": 0,
        "total_modules": 0,
        "completed_modules": 0,
        "total_scenarios": 0,
        "completed_scenarios": 0,
        "recent_activity": []
    }
    
    # Process each course
    for course in user_courses:
        course_data = {
            "id": course["id"],
            "title": course["title"],
            "description": course["description"],
            "thumbnail_url": course.get("thumbnail_url", ""),
            "completed": course.get("completed", False),
            "modules": [],
            "module_count": 0,
            "completed_modules": 0
        }
        
        # Update course count
        if course.get("completed", False):
            dashboard["completed_courses"] += 1
        
        # Get modules for this course
        course_id = UUID(course["id"]) if isinstance(course["id"], str) else course["id"]
        modules = await get_modules_by_course(db, course_id, current_user)
        
        # Process each module
        for module in modules:
            # Handle different data types (dict or ModuleDB object)
            if isinstance(module, dict):
                module_id = module["id"] if isinstance(module["id"], UUID) else UUID(module["id"])
                module_data = {
                    "id": str(module_id),
                    "title": module["title"],
                    "completed": module.get("completed", False),
                    "scenarios": [],
                    "scenario_count": 0,
                    "completed_scenarios": 0
                }
            else:
                module_id = module.id
                module_data = {
                    "id": str(module_id),
                    "title": module.title,
                    "completed": getattr(module, "completed", False),
                    "scenarios": [],
                    "scenario_count": 0,
                    "completed_scenarios": 0
                }
            
            # Update module counts
            course_data["module_count"] += 1
            dashboard["total_modules"] += 1
            if module_data["completed"]:
                course_data["completed_modules"] += 1
                dashboard["completed_modules"] += 1
            
            # Get scenarios for this module
            scenarios = await get_scenarios_by_module(db, module_id, current_user)
            
            # Process each scenario
            for scenario in scenarios:
                # Handle different data types
                if isinstance(scenario, dict):
                    scenario_id = scenario["id"] if isinstance(scenario["id"], UUID) else UUID(scenario["id"])
                    scenario_data = {
                        "id": str(scenario_id),
                        "title": scenario["title"],
                        "completed": scenario.get("completed", False),
                        "assigned_modes": scenario.get("assigned_modes", []),
                        "mode_progress": scenario.get("mode_progress", {})
                    }
                else:
                    scenario_data = {
                        "id": str(scenario.id),
                        "title": scenario.title,
                        "completed": getattr(scenario, "completed", False),
                        "assigned_modes": getattr(scenario, "assigned_modes", []),
                        "mode_progress": getattr(scenario, "mode_progress", {})
                    }
                
                # Update scenario counts
                module_data["scenario_count"] += 1
                dashboard["total_scenarios"] += 1
                if scenario_data["completed"]:
                    module_data["completed_scenarios"] += 1
                    dashboard["completed_scenarios"] += 1
                
                module_data["scenarios"].append(scenario_data)
            
            course_data["modules"].append(module_data)
        
        dashboard["courses"].append(course_data)
    
    # Get recent activity (last 5 analysis reports)
    reports_cursor = db.analysis.find({"user_id": str(current_user.id)})
    reports_cursor.sort("timestamp", -1)
    reports_cursor.limit(5)
    
    recent_reports = await reports_cursor.to_list(length=5)
    for report in recent_reports:
        # Get session and scenario info
        session_id = report.get("session_id")
        if session_id:
            session = await db.sessions.find_one({"_id": session_id})
            if session:
                # Get scenario name from session
                dashboard["recent_activity"].append({
                    "id": str(report["_id"]),
                    "timestamp": report.get("timestamp", datetime.now()),
                    "scenario_name": session.get("scenario_name", "Unknown Scenario"),
                    "score": report.get("overall_evaluation", {}).get("total_score", 0)
                })
    
    return dashboard

# @router.get("/users/me/completed-scenarios-dashboard", response_model=Dict[str, Any])
# async def get_completed_scenarios_dashboard(
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Get a dashboard of completed scenarios with their analysis reports and details
#     """
#     # Initialize results structure
#     dashboard = {
#         "user_id": str(current_user.id),
#         "user_name": f"{current_user.username}",
#         "completed_scenarios": [],
#         "total_completed": 0,
#         "average_score": 0,
#         "total_analysis_reports": 0
#     }
    
#     # Get all completed scenario assignments for the user
#     completed_assignments = []
#     cursor = db.user_scenario_assignments.find({
#         "user_id": str(current_user.id),
#         "completed": True
#     })
    
#     async for assignment in cursor:
#         completed_assignments.append(assignment)
    
#     dashboard["total_completed"] = len(completed_assignments)
    
#     # Process each completed scenario
#     total_score = 0
#     reports_count = 0
    
#     for assignment in completed_assignments:
#         scenario_id = assignment["scenario_id"]
        
#         # Get scenario details
#         scenario = await db.scenarios.find_one({"_id": scenario_id})
#         if not scenario:
#             continue
        
#         # Get module and course details
#         module = await db.modules.find_one({"_id": assignment["module_id"]})
#         course = await db.courses.find_one({"_id": assignment["course_id"]})
        
#         # Initialize scenario data
#         scenario_data = {
#             "id": scenario_id,
#             "title": scenario.get("title", "Unknown Scenario"),
#             "description": scenario.get("description", ""),
#             "thumbnail_url": scenario.get("thumbnail_url", ""),
#             "module_id": assignment["module_id"],
#             "module_title": module.get("title", "Unknown Module") if module else "Unknown Module",
#             "course_id": assignment["course_id"],
#             "course_title": course.get("title", "Unknown Course") if course else "Unknown Course",
#             "completed_date": assignment.get("completed_date", None),
#             "mode_progress": assignment.get("mode_progress", {}),
#             "analysis_reports": []
#         }
        
#         # Get chat sessions for this scenario
#         # We need to find sessions where avatar_interaction matches the scenario's avatar interactions
#         learn_mode_ai = scenario.get("learn_mode", {}).get("avatar_interaction", None)
#         try_mode_ai = scenario.get("try_mode", {}).get("avatar_interaction", None)
#         assess_mode_ai = scenario.get("assess_mode", {}).get("avatar_interaction", None)
        
#         avatar_interactions = [ai for ai in [learn_mode_ai, try_mode_ai, assess_mode_ai] if ai]
        
#         if avatar_interactions:
#             # Find sessions for this scenario's avatar interactions
#             sessions = []
#             sessions_cursor = db.sessions.find({
#                 "user_id": str(current_user.id),
#                 "avatar_interaction": {"$in": avatar_interactions}
#             })
            
#             async for session in sessions_cursor:
#                 sessions.append(session)
            
#             # For each session, check if analysis report exists
#             for session in sessions:
#                 session_id = str(session["_id"])
                
#                 # Get analysis report
#                 analysis = await db.analysis.find_one({"session_id": session_id})
#                 if analysis:
#                     # Add this analysis to the scenario data
#                     # Convert MongoDB _id to string
#                     analysis["id"] = str(analysis.pop("_id")) if "_id" in analysis else None
                    
#                     # Extract key metrics for dashboard view
#                     analysis_summary = {
#                         "id": analysis["id"],
#                         "session_id": session_id,
#                         "timestamp": analysis.get("timestamp", None),
#                         "scenario_name": session.get("scenario_name", "Unknown"),
#                         "avatar_interaction": session.get("avatar_interaction", None),
#                         "score": analysis.get("overall_evaluation", {}).get("total_score", 0),
#                         "performance_category": analysis.get("overall_evaluation", {}).get("user_performance_category", "Unknown"),
#                         "strengths": analysis.get("overall_evaluation", {}).get("user_strengths", []),
#                         "improvement_areas": analysis.get("overall_evaluation", {}).get("user_improvement_areas", []),
#                         "key_metrics": {}
#                     }
                    
#                     # Add user evaluation metrics if available
#                     if "user_domain_knowledge" in analysis and analysis["user_domain_knowledge"]:
#                         analysis_summary["key_metrics"]["knowledge"] = analysis["user_domain_knowledge"].get("overall_score", 0)
                    
#                     if "user_communication_clarity" in analysis and analysis["user_communication_clarity"]:
#                         analysis_summary["key_metrics"]["communication"] = analysis["user_communication_clarity"].get("overall_score", 0)
                    
#                     if "user_engagement_quality" in analysis and analysis["user_engagement_quality"]:
#                         analysis_summary["key_metrics"]["engagement"] = analysis["user_engagement_quality"].get("overall_score", 0)
                    
#                     if "user_problem_solving" in analysis and analysis["user_problem_solving"]:
#                         analysis_summary["key_metrics"]["problem_solving"] = analysis["user_problem_solving"].get("overall_score", 0)
                    
#                     if "user_learning_adaptation" in analysis and analysis["user_learning_adaptation"]:
#                         analysis_summary["key_metrics"]["learning"] = analysis["user_learning_adaptation"].get("overall_score", 0)
                    
#                     scenario_data["analysis_reports"].append(analysis_summary)
                    
#                     # Update total score for average calculation
#                     if "score" in analysis_summary and analysis_summary["score"]:
#                         total_score += analysis_summary["score"]
#                         reports_count += 1
        
#         # Add this scenario's data to the dashboard
#         dashboard["completed_scenarios"].append(scenario_data)
    
#     # Calculate average score
#     dashboard["total_analysis_reports"] = reports_count
#     if reports_count > 0:
#         dashboard["average_score"] = total_score / reports_count
    
#     # Sort scenarios by completion date (most recent first)
#     dashboard["completed_scenarios"].sort(
#         key=lambda x: x.get("completed_date", datetime.min), 
#         reverse=True
#     )
    
#     return dashboard

@router.get("/users/me/completed-scenarios-dashboard", response_model=Dict[str, Any])
async def get_completed_scenarios_dashboard(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a dashboard of completed scenarios with their analysis reports and mode details
    """
    # Initialize result structure
    dashboard = {
        "completed_scenarios": [],
        "total_completed": 0,
        "scenarios_with_analysis": 0,
        "average_score": 0,
        "completion_by_mode": {
            "learn_mode": 0,
            "try_mode": 0,
            "assess_mode": 0
        }
    }
    
    # Find all scenario assignments for the current user that are completed
    assignments_cursor = db.user_scenario_assignments.find({
        "user_id": str(current_user.id),
        
    })
    print(assignments_cursor,str(current_user.id),type(current_user.id))
    completed_assignments = await assignments_cursor.to_list(length=None)
    print(completed_assignments)
    dashboard["total_completed"] = len(completed_assignments)
    
    # Total score for average calculation
    total_score = 0
    score_count = 0
    
    # Process each completed scenario
    for assignment in completed_assignments:
        scenario_id = assignment["scenario_id"]
        module_id = assignment["module_id"]
        course_id = assignment["course_id"]
        
        # Get scenario details
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        module = await db.modules.find_one({"_id": module_id})
        course = await db.courses.find_one({"_id": course_id})
        
        if not scenario or not module or not course:
            continue
        
        # Prepare the scenario data with basic information
        scenario_data = {
            "id": scenario_id,
            "title": scenario.get("title", "Unknown Scenario"),
            "module_name": module.get("title", "Unknown Module"),
            "course_name": course.get("title", "Unknown Course"),
            "thumbnail_url": scenario.get("thumbnail_url", ""),
            "completed_date": assignment.get("completed_date", datetime.now()),
            "modes_completed": [],
            "mode_progress": assignment.get("mode_progress", {}),
            "analysis_reports": []
        }
        print(scenario_data)
        # Add mode completion information
        mode_progress = assignment.get("mode_progress", {})
        for mode, progress in mode_progress.items():
            if progress.get("completed", False):
                scenario_data["modes_completed"].append(mode)
                dashboard["completion_by_mode"][mode] += 1
        
        # Find analysis reports for this scenario
        # First find the sessions for this scenario
        sessions = await db.sessions.find({
            "user_id": str(current_user.id),
            "scenario_name": {"$regex": scenario.get("title", "")}
        }).to_list(length=None)
        
        session_ids = [str(session["_id"]) for session in sessions]
        
        # Then find analysis reports for these sessions
        if session_ids:
            analysis_reports = await db.analysis.find({
                "session_id": {"$in": session_ids}
            }).to_list(length=None)
            
            # Process each analysis report
            for report in analysis_reports:
                # Extract essential information from the report
                report_data = {
                    "id": str(report["_id"]),
                    "timestamp": report.get("timestamp", datetime.now()),
                    "session_id": report.get("session_id", ""),
                    "score": None,
                    "key_strengths": [],
                    "key_areas_for_improvement": []
                }
                
                # Extract score, trying multiple possible structures based on your model
                overall_eval = report.get("overall_evaluation", {})
                if "total_score" in overall_eval:
                    report_data["score"] = overall_eval["total_score"]
                elif "total_percentage_score" in overall_eval:
                    report_data["score"] = overall_eval["total_percentage_score"]
                elif "total_raw_score" in overall_eval:
                    report_data["score"] = overall_eval["total_raw_score"] * 2.5  # Scale to 100
                
                # Add score to average calculation if available
                if report_data["score"] is not None:
                    total_score += report_data["score"]
                    score_count += 1
                
                # Extract strengths, checking multiple possible field names
                strengths = []
                if "user_strengths" in overall_eval:
                    strengths = overall_eval["user_strengths"]
                elif "strengths" in overall_eval:
                    strengths = overall_eval["strengths"]
                
                report_data["key_strengths"] = strengths[:3] if strengths else []
                
                # Extract areas for improvement, checking multiple possible field names
                improvements = []
                if "user_improvement_areas" in overall_eval:
                    improvements = overall_eval["user_improvement_areas"]
                elif "areas_for_improvement" in overall_eval:
                    improvements = overall_eval["areas_for_improvement"]
                
                report_data["key_areas_for_improvement"] = improvements[:3] if improvements else []
                
                # Add to scenario reports
                scenario_data["analysis_reports"].append(report_data)
            
            # Update count of scenarios with analysis
            if scenario_data["analysis_reports"]:
                dashboard["scenarios_with_analysis"] += 1
        
        # Add to completed scenarios list
        dashboard["completed_scenarios"].append(scenario_data)
    
    # Calculate average score
    if score_count > 0:
        dashboard["average_score"] = round(total_score / score_count, 2)
    
    # Sort completed scenarios by completion date (newest first)
    dashboard["completed_scenarios"].sort(
        key=lambda x: x["completed_date"] if x["completed_date"] else datetime.min, 
        reverse=True
    )
    
    return dashboard
from models.scenario_models import ScenarioModeType
@router.get("/scenario/{scenario_id}/mode/{mode}/analysis", response_model=Dict[str, Any])
async def get_scenario_mode_analysis(
    scenario_id: UUID,
    mode: ScenarioModeType,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get analysis reports for a specific scenario mode that has been completed,
    including session details
    """
    # Check if scenario and mode are assigned to user
    assignment = await db.user_scenario_assignments.find_one({
        "user_id": str(current_user.id),
        "scenario_id": str(scenario_id)
    })
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario assignment not found"
        )
    
    # Check if mode is assigned and has been completed
    mode_progress = assignment.get("mode_progress", {})
    mode_info = mode_progress.get(mode.value, {})
    
    # Get the avatar interaction for this scenario
    scenario_data = await db.scenarios.find_one({"_id": str(scenario_id)})
    if not scenario_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    # Get avatar interaction ID based on mode
    avatar_interaction_id = None
    if mode.value == "learn_mode" and "learn_mode" in scenario_data:
        avatar_interaction_id = scenario_data["learn_mode"].get("avatar_interaction")
    elif mode.value == "try_mode" and "try_mode" in scenario_data:
        avatar_interaction_id = scenario_data["try_mode"].get("avatar_interaction")
    elif mode.value == "assess_mode" and "assess_mode" in scenario_data:
        avatar_interaction_id = scenario_data["assess_mode"].get("avatar_interaction")
    
    if not avatar_interaction_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avatar interaction not found for this {mode.value}"
        )
    
    # Find sessions for this user, scenario, and mode
    sessions = []
    sessions_cursor = db.sessions.find({
        "user_id": str(current_user.id),
        "avatar_interaction": str(avatar_interaction_id)
    })
    
    async for session in sessions_cursor:
        # Find analysis for this session
        analysis = await db.analysis.find_one({"session_id": str(session["_id"])})
        
        session_data = {
            "id": str(session["_id"]),
            "created_at": session.get("created_at"),
            "last_updated": session.get("last_updated"),
            "scenario_name": session.get("scenario_name"),
            "conversation_history": session.get("conversation_history"),
            "analysis": analysis
        }
        
        sessions.append(session_data)
    
    # Return the results
    return {
        "scenario_id": str(scenario_id),
        "mode": mode.value,
        "completed": mode_info.get("completed", False),
        "completed_date": mode_info.get("completed_date"),
        "sessions": sessions,
        "session_count": len(sessions)
    }
    
    

@router.get("/users/me/completed-scenario-analysis", response_model=List[Dict[str, Any]])
async def get_user_completed_scenario_analysis(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get analysis reports for all completed scenario modes for the current user
    """
    # Get all scenario assignments for the user
    scenario_assignments = await db.user_scenario_assignments.find({
        "user_id": str(current_user.id)
    }).to_list(length=None)
    
    results = []
    print(scenario_assignments)
    # Process each scenario assignment
    for assignment in scenario_assignments:
        scenario_id = assignment.get("scenario_id")
        mode_progress = assignment.get("mode_progress", {})
        
        # Get scenario details
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            continue
            
        scenario_name = scenario.get("title", "Unknown Scenario")
        scenario_thumbnail= scenario.get("thumbnail_url", "Unknown Scenario")
        # Check each mode
        for mode, progress in mode_progress.items():
            # If this mode is completed
            if progress.get("completed", False):
                print(progress)
                print(progress)
                # Find the session for this scenario and mode
                sessions = await db.sessions.find({
                    "user_id": str(current_user.id),
                    "avatar_interaction": str(scenario.get(f"{mode}", {}).get("avatar_interaction"))
                }).to_list(length=None)
                # print(sessions)
                for session in sessions:
                    session_id = str(session["_id"])
                    print(session_id,type(session_id))
                    # Get analysis for this session
                    analysis = await db.analysis.find_one({"session_id": session_id})
                    print(analysis)
                    if analysis:
                        # Format result
                        result = {
                            "scenario_id": scenario_id,
                            "scenario_name": scenario_name,
                            "thumbnail_url" : scenario_thumbnail,
                            "mode": mode,
                            "completed_date": progress.get("completed_date"),
                            "session_id": session_id,
                            "analysis_id": str(analysis["_id"]),
                            "analysis_timestamp": analysis.get("timestamp"),
                            "analysis_score": analysis.get("overall_evaluation", {}).get("total_score", 0),
                            "analysis_summary": {
                                "strengths": analysis.get("overall_evaluation", {}).get("user_strengths", []),
                                "improvement_areas": analysis.get("overall_evaluation", {}).get("user_improvement_areas", []),
                            },
                            "session_details": {
                                "created_at": session.get("created_at"),
                                "last_updated": session.get("last_updated"),
                                "conversation_count": len(session.get("conversation_history", [])),
                            }
                        }
                        
                        results.append(result)
    
    # Sort by most recent completed date
    results.sort(key=lambda x: x["completed_date"] if x["completed_date"] else datetime.min, reverse=True)
    
    return results