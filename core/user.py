from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timedelta,timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt, JWTError
from passlib.context import CryptContext
from uuid import uuid4
from models.user_models import (
    UserResponse, UserCreate, UserUpdate, UserWithCoursesResponse, UserDB,
    AdminUserResponse, AdminUserCreate, AdminUserDB, BossAdminDB, SuperAdminDB,
    BossAdminResponse, DemoUserCreate, DemoExtensionRequest,
    Token, UserRole, LoginRequest, UserAssignmentUpdate, CourseAssignmentUpdate,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm,
    TokenData, AccountType
)
from models.company_models import CompanyDB, CompanyResponse, CompanyCreate, CompanyUpdate, CompanyAnalytics
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
    from database import get_db
    return await get_db()

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


# Updated User Dependencies
async def get_current_user(db: Any = Depends(get_database), token: str = Depends(oauth2_scheme)):
    """Get current user with demo expiry check"""
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
    
    # Check if demo account has expired
    if user.is_demo_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo account has expired. Please contact your administrator."
        )
    
    return user

# Updated Role-based Dependencies
async def get_admin_user(current_user: Union[UserDB, AdminUserDB] = Depends(get_current_user)):
    """Get admin user (includes ADMIN, SUPERADMIN, BOSS_ADMIN)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Admin role required."
        )
    return current_user

async def get_superadmin_user(current_user: UserDB = Depends(get_current_user)):
    """Get superadmin user (includes SUPERADMIN, BOSS_ADMIN)"""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Superadmin role required."
        )
    return current_user

async def get_boss_admin_user(current_user: UserDB = Depends(get_current_user)):
    """Get boss admin user (BOSS_ADMIN only)"""
    if current_user.role != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Boss admin role required."
        )
    return current_user

# Updated User Operations
async def get_users_by_company(db: Any, company_id: UUID, skip: int = 0, limit: int = 100) -> List[UserDB]:
    """Get users by company"""
    users = []
    cursor = db.users.find({"company_id": company_id}).skip(skip).limit(limit)
    async for document in cursor:
        print(document,"query")
        users.append(UserDB(**document))
    return users

async def get_users(db: Any, skip: int = 0, limit: int = 100, company_id: Optional[UUID] = None) -> List[UserDB]:
    """Get a list of users, optionally filtered by company"""
    users = []
    query = {}
    if company_id:
        query["company_id"] = str(company_id)
        print(type(query),query,"query")
    
    cursor = db.users.find(query).skip(skip).limit(limit)
    async for document in cursor:
        users.append(UserDB(**document))
    return users

async def get_user_by_id(db: Any, user_id: UUID) -> Optional[Union[UserDB, AdminUserDB, BossAdminDB, SuperAdminDB]]:
    """Get a user by ID with proper role-based model"""
    user = await db.users.find_one({"_id": str(user_id)})
    
    if user:
        role = user.get("role")
        if role == UserRole.BOSS_ADMIN:
            return BossAdminDB(**user)
        elif role == UserRole.SUPERADMIN:
            return SuperAdminDB(**user)
        elif role == UserRole.ADMIN:
            return AdminUserDB(**user)
        else:
            return UserDB(**user)
    return None

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
    
    # Check if demo account has expired
    if user.is_demo_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo account has expired. Please contact your administrator."
        )
    
    return user

async def create_user(db: Any, users: List[UserCreate], created_by: Optional[UUID] = None) -> List[UserDB]:
    """Create new users with company validation, demo inheritance, and proper admin relationships"""
    from core.companies import get_company_by_id
    created_users = []
    
    # Get creator info for validation
    creator = None
    if created_by:
        creator = await get_user_by_id(db, created_by)
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid creator"
            )

    for user in users:
        # Validate email uniqueness
        existing_user = await get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user.email} already registered"
            )
        
        # Validate company exists
        company = await get_company_by_id(db, user.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company ID"
            )
        
        # Validate creator permissions and role restrictions
        if creator:
            if creator.role == UserRole.BOSS_ADMIN:
                # Boss admin can only create SuperAdmins
                if user.role != UserRole.SUPERADMIN:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Boss admin can only create SuperAdmins. SuperAdmins should create Admins, and Admins should create Users."
                    )
                # Boss admin can create SuperAdmins in any company they manage
                
            elif creator.role == UserRole.SUPERADMIN:
                # Superadmin can create Admins and Users in their own company
                if creator.company_id != user.company_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="SuperAdmin can only create users in their own company"
                    )
                if user.role not in [UserRole.ADMIN, UserRole.USER]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="SuperAdmin can only create Admins and Users"
                    )
                    
            elif creator.role == UserRole.ADMIN:
                # Admin can only create regular users in their own company
                if creator.company_id != user.company_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin can only create users in their own company"
                    )
                if user.role != UserRole.USER:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin can only create regular Users"
                    )
        
        user_dict = user.dict()
        # user_dict['company_id'] = str(user_dict['company_id'])
        print(user_dict)
        hashed_password = get_password_hash(user_dict.pop("password"))

        assignee_emp_id = None
        if creator and creator.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            assignee_emp_id = creator.emp_id

        # ===== DEMO INHERITANCE LOGIC =====
        if creator and creator.account_type == AccountType.DEMO:
            user_dict["account_type"] = AccountType.DEMO
            
            creator_expiry = creator.demo_expires_at
            user_expiry =creator.demo_expires_at #user_dict.get("demo_expires_at")
            
            if creator_expiry and creator_expiry.tzinfo is None:
                creator_expiry = creator_expiry.replace(tzinfo=timezone.utc)
            if user_expiry and user_expiry.tzinfo is None:
                user_expiry = user_expiry.replace(tzinfo=timezone.utc)
            if creator_expiry:
                if user_expiry:
                    user_dict["demo_expires_at"] = min(creator_expiry, user_expiry)
                else:
                    user_dict["demo_expires_at"] = creator_expiry
            elif user_expiry:
                user_dict["demo_expires_at"] = user_expiry
            else:
                user_dict["demo_expires_at"] = datetime.now() + timedelta(weeks=1)
                
            print(f"Demo inheritance: User {user.email} inherits demo status from creator, expires at {user_dict['demo_expires_at']}")
        
        elif user_dict.get("account_type") == AccountType.DEMO:
            if not creator or creator.role not in [UserRole.BOSS_ADMIN, UserRole.SUPERADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only boss admin and superadmin can create demo users explicitly"
                )
            
            if not user_dict.get("demo_expires_at"):
                user_dict["demo_expires_at"] = datetime.now() + timedelta(weeks=1)

        # Determine user model based on role and create appropriate document
        if user.role == UserRole.BOSS_ADMIN:
            user_db = BossAdminDB(
                **user_dict,
                hashed_password=hashed_password,
                assignee_emp_id=assignee_emp_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                managed_companies=[]
            )
        elif user.role == UserRole.SUPERADMIN:
            user_db = SuperAdminDB(
                **user_dict,
                hashed_password=hashed_password,
                assignee_emp_id=assignee_emp_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                managed_users=[]
            )
        elif user.role == UserRole.ADMIN:
            user_db = AdminUserDB(
                **user_dict,
                hashed_password=hashed_password,
                assignee_emp_id=assignee_emp_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                managed_users=[]
            )
        else:
            user_db = UserDB(
                **user_dict,
                hashed_password=hashed_password,
                assignee_emp_id=assignee_emp_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        # Insert into database
        user_dict = user_db.dict(by_alias=True)
        
        if "_id" in user_dict:
            user_dict["_id"] = str(user_dict["_id"])

        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": str(result.inserted_id)})

        # ===== MANAGED USERS RELATIONSHIP =====
        if creator:
            if creator.role == UserRole.ADMIN:
                # Admin manages regular users they create
                if user.role == UserRole.USER:
                    await db.users.update_one(
                        {"_id": str(creator.id)},
                        {"$addToSet": {"managed_users": str(user_db.id)}}
                    )
            elif creator.role == UserRole.SUPERADMIN:
                # SuperAdmin manages admins and users they create in their company
                if user.role in [UserRole.ADMIN, UserRole.USER]:
                    await db.users.update_one(
                        {"_id": str(creator.id)},
                        {"$addToSet": {"managed_users": str(user_db.id)}}
                    )
            elif creator.role == UserRole.BOSS_ADMIN:
                # Boss admin manages companies through SuperAdmins, not individual users directly
                # But if they create a superadmin, they manage that company
                if user.role == UserRole.SUPERADMIN:
                    await db.users.update_one(
                        {"_id": str(creator.id)},
                        {"$addToSet": {"managed_companies": str(user.company_id)}}
                    )
        
        created_users.append(UserDB(**created_user))

    return created_users

async def extend_demo_user(db: Any, extension_request: DemoExtensionRequest, extended_by: UUID) -> bool:
    """Extend demo user account with optional cascading to created users"""
    # Get the user to extend
    user = await get_user_by_id(db, extension_request.user_id)
    if not user or user.account_type != AccountType.DEMO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a demo account"
        )
    
    # Get the person making the extension
    extender = await get_user_by_id(db, extended_by)
    if not extender or extender.role not in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can extend demo accounts"
        )
    
    # Check company permissions
    if extender.role != UserRole.BOSS_ADMIN and extender.company_id != user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only extend demo accounts in your own company"
        )
    
    # Calculate new expiry date
    current_expiry = user.demo_expires_at or datetime.now()
    if current_expiry < datetime.now():
        # If already expired, extend from now
        new_expiry = datetime.now() + timedelta(days=extension_request.extension_days)
    else:
        # If not expired, extend from current expiry
        new_expiry = current_expiry + timedelta(days=extension_request.extension_days)
    
    # Update the main user
    await db.users.update_one(
        {"_id": str(extension_request.user_id)},
        {"$set": {"demo_expires_at": new_expiry, "updated_at": datetime.now()}}
    )
    
    # CASCADE EXTENSION: If this user is an admin/superadmin, extend all users they created
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        # Find all demo users created by this user (have assignee_emp_id matching this user's emp_id)
        cascade_users = []
        cursor = db.users.find({
            "assignee_emp_id": user.emp_id,
            "account_type": AccountType.DEMO,
            "company_id": str(user.company_id)
        })
        
        async for cascade_user_doc in cursor:
            cascade_user = UserDB(**cascade_user_doc)
            # Only extend if their current expiry is before or same as the new expiry
            if cascade_user.demo_expires_at and cascade_user.demo_expires_at <= new_expiry:
                cascade_users.append(str(cascade_user.id))
        
        # Extend all cascaded users
        if cascade_users:
            await db.users.update_many(
                {"_id": {"$in": cascade_users}},
                {"$set": {"demo_expires_at": new_expiry, "updated_at": datetime.now()}}
            )
            
            print(f"Extended {len(cascade_users)} cascade users along with primary user {user.email}")
    
    return True

async def get_company_analytics(db: Any, company_id: UUID, user_id: UUID) -> Dict[str, Any]:
    """Get analytics for a specific company"""
    from core.companies import get_company_by_id
    
    # Get the requesting user
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if user.role == UserRole.BOSS_ADMIN:
        # Boss admin can see any company's analytics
        pass
    elif user.role == UserRole.SUPERADMIN and user.company_id == company_id:
        # Superadmin can see their own company's analytics
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's analytics"
        )
    
    # Get company info
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Calculate analytics
    total_users = await db.users.count_documents({"company_id": str(company_id)})
    total_admins = await db.users.count_documents({
        "company_id": str(company_id), 
        "role": {"$in": [UserRole.ADMIN, UserRole.SUPERADMIN]}
    })
    demo_users = await db.users.count_documents({
        "company_id": str(company_id), 
        "account_type": AccountType.DEMO
    })
    expired_demos = await db.users.count_documents({
        "company_id": str(company_id), 
        "account_type": AccountType.DEMO,
        "demo_expires_at": {"$lt": datetime.now()}
    })
    
    return {
        "company_id": str(company_id),
        "company_name": company.name,
        "total_users": total_users,
        "total_admins": total_admins,
        "demo_users": demo_users,
        "expired_demo_users": expired_demos,
        "generated_at": datetime.now()
    }

async def get_all_companies_analytics(db: Any, user_id: UUID) -> List[Dict[str, Any]]:
    """Get analytics for all companies (boss admin only)"""
    # Get the requesting user
    user = await get_user_by_id(db, user_id)
    if not user or user.role != UserRole.BOSS_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only boss admins can view all companies analytics"
        )
    
    # Get all companies
    companies = []
    cursor = db.companies.find()
    async for company_doc in cursor:
        company = CompanyDB(**company_doc)
        analytics = await get_company_analytics(db, company.id, user_id)
        companies.append(analytics)
    
    return companies

# Updated delete and update methods with company validation
async def update_user(db: Any, user_id: UUID, update_data: UserUpdate, updated_by: UUID) -> Optional[UserDB]:
    """Update a user with company validation"""
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
        # Admins can update users they manage and themselves (same company only)
        if updater.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can only update users in the same company"
            )
        
        admin = await db.users.find_one({
            "_id": str(updated_by), 
            "managed_users": str(user_id)
        })
        if not admin and updater.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can only update managed users or themselves"
            )
        
        # Admins can't change roles to superadmin or boss admin
        if update_data.role in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot promote users to superadmin or boss admin"
            )
    elif updater.role == UserRole.SUPERADMIN:
        # Superadmin can update users in their company
        if updater.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superadmin can only update users in the same company"
            )
        
        # Superadmin can't change roles to boss admin
        if update_data.role == UserRole.BOSS_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superadmin cannot promote users to boss admin"
            )
    elif updater.role == UserRole.BOSS_ADMIN:
        # Boss admin can update any user
        pass
    
    # Prepare update data
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.now()
    # update_dict["company_id"]= str(update_dict["company_id"]) 
    
    # Update in database
    await db.users.update_one(
        {"_id": str(user_id)},
        {"$set": update_dict}
    )
    
    updated_user = await db.users.find_one({"_id": str(user_id)})
    if updated_user:
        return UserDB(**updated_user)
    return None

async def delete_user(db: Any, user_id: UUID, deleted_by: UUID) -> bool:
    """Delete a user with company validation"""
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
        # Admins can delete users they manage (same company, not other admins)
        if deleter.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin can only delete users in the same company"
            )
        
        if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
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
    elif deleter.role == UserRole.SUPERADMIN:
        # Superadmin can delete users in their company (not boss admins)
        if deleter.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superadmin can only delete users in the same company"
            )
        
        if user.role == UserRole.BOSS_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superadmin cannot delete boss admins"
            )
    elif deleter.role == UserRole.BOSS_ADMIN:
        # Boss admin can delete any user
        pass
    
    # Delete from database
    result = await db.users.delete_one({"_id": str(user_id)})
    
    # Remove user from any admin's managed_users
    if result.deleted_count > 0:
        await db.users.update_many(
            {"managed_users": str(user_id)},
            {"$pull": {"managed_users": str(user_id)}}
        )
    
    return result.deleted_count > 0

# API Endpoints

# Authentication Endpoints
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Any = Depends(get_database)):
    """OAuth2 compatible token endpoint for login"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token_data = {"sub": str(user.id), "role": user.role, "company_id": str(user.company_id)}
    access_token, expires_at = create_access_token(token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_at": expires_at,
        "user_role": user.role,
        "company_id": str(user.company_id),
        "account_type": user.account_type,
        "is_demo_expired": user.is_demo_expired()
    }

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Any = Depends(get_database)):
    """Login endpoint that accepts JSON data"""
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    token_data = {"sub": str(user.id), "role": user.role, "company_id": str(user.company_id)}
    access_token, expires_at = create_access_token(token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_at": expires_at,
        "user_role": user.role,
        "company_id": str(user.company_id),
        "account_type": user.account_type,
        "is_demo_expired": user.is_demo_expired()
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
@router.post("/users", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    users: List[UserCreate],
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Create new users with automatic demo inheritance
    
    - If creator is demo user: new users automatically become demo with same/earlier expiry
    - If creator is regular user: can explicitly create demo users (boss admin/superadmin only)
    - Demo inheritance ensures all users under a demo hierarchy expire together
    """
    created_users = await create_user(db, users, created_by=admin_user.id)
    
    # Return with demo status info
    response_users = []
    for user in created_users:
        response_users.append(UserResponse(
            **user.dict(),
            is_demo_expired=user.is_demo_expired()
        ))
    
    return response_users

@router.post("/users/extend-demo", response_model=Dict[str, bool])
async def extend_demo_users_endpoint(
    extension_request: DemoExtensionRequest,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Extend demo user account and optionally cascade to created users
    """
    success = await extend_demo_user(db, extension_request, admin_user.id)
    return {"success": success}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    """Get current authenticated user"""
    # Create response with proper is_demo_expired value
    user_dict = current_user.dict()
    user_dict["is_demo_expired"] = current_user.is_demo_expired()  # Call the method
    return UserResponse(**user_dict)

@router.get("/users/me/courses", response_model=List[CourseWithAssignmentResponse])
async def read_users_me_courses(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get courses assigned to current user with assignment data"""
    return await get_user_courses_with_assignments(db, current_user.id)

@router.put("/users/me/courses/{course_id}/completion", response_model=Dict[str, bool])
async def update_course_completion_status(
    course_id: UUID,
    completion_data: CompletionUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Update completion status for one of the current user's assigned courses"""
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

@router.get("/users", response_model=List[UserWithCoursesResponse])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    company_id: Optional[UUID] = Query(None, description="Filter by company (boss admin only)"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get list of users"""
    users = []
    
    if admin_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can view users from any company or all users
        if company_id:
            users = await get_users_by_company(db, company_id, skip, limit)
        else:
            users = await get_users(db, skip, limit)
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin can view all users in their company
        users = await get_users_by_company(db, admin_user.company_id, skip, limit)
    elif admin_user.role == UserRole.ADMIN:
        # Admin can view only their managed users
        users = await get_users_by_admin(db, admin_user.id)
    
    # Convert to response format with proper is_demo_expired value
    response_users = []
    for user in users:
        user_dict = user.dict()
        user_dict["is_demo_expired"] = user.is_demo_expired()  # Call the method
        response_users.append(UserWithCoursesResponse(**user_dict))
    
    return response_users

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get specific user by ID"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permissions
    if admin_user.role == UserRole.BOSS_ADMIN:
        # Boss admin can view any user
        pass
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin can view users in their company
        if admin_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view users from other companies"
            )
    elif admin_user.role == UserRole.ADMIN:
        # Admin can view managed users and themselves
        if admin_user.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view users from other companies"
            )
        
        admin_data = admin_user.dict()
        managed_users = admin_data.get("managed_users", [])
        if user_id not in managed_users and admin_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user"
            )
    
    # Create response with proper is_demo_expired value
    user_dict = user.dict()
    user_dict["is_demo_expired"] = user.is_demo_expired()  # Call the method
    return UserResponse(**user_dict)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: UUID,
    user_update: UserUpdate,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Update a user"""
    updated_user = await update_user(db, user_id, user_update, current_user.id)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Create response with proper is_demo_expired value
    user_dict = updated_user.dict()
    user_dict["is_demo_expired"] = updated_user.is_demo_expired()  # Call the method
    return UserResponse(**user_dict)

@router.delete("/users/{user_id}", response_model=Dict[str, bool])
async def delete_user_endpoint(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Delete a user"""
    deleted = await delete_user(db, user_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"success": True}

# Analytics Endpoints
@router.get("/analytics/company/{company_id}", response_model=Dict[str, Any])
async def get_company_analytics_endpoint(
    company_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get analytics for a specific company"""
    return await get_company_analytics(db, company_id, current_user.id)

@router.get("/analytics/companies", response_model=List[Dict[str, Any]])
async def get_all_companies_analytics_endpoint(
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Get analytics for all companies (boss admin only)"""
    return await get_all_companies_analytics(db, boss_admin.id)

# Demo User Management
@router.get("/demo-users/expiring", response_model=List[UserResponse])
async def get_expiring_demo_users(
    days: int = Query(7, ge=1, le=30, description="Days until expiry"),
    include_cascaded: bool = Query(True, description="Include users created by demo admins"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get demo users expiring within specified days
    - include_cascaded: Also show users created by demo admins/superadmins
    """
    expiry_date = datetime.now() + timedelta(days=days)
    
    query = {
        "account_type": AccountType.DEMO,
        "demo_expires_at": {"$lte": expiry_date, "$gte": datetime.now()}
    }
    
    # Add company filter based on user role
    if admin_user.role != UserRole.BOSS_ADMIN:
        query["company_id"] = str(admin_user.company_id)
    
    users = []
    cursor = db.users.find(query)
    async for user_doc in cursor:
        user = UserDB(**user_doc)
        user_dict = user.dict()
        user_dict["is_demo_expired"] = user.is_demo_expired()  # Call the method
        users.append(UserResponse(**user_dict))
    
    return users

@router.get("/demo-users/expired", response_model=List[UserResponse])
async def get_expired_demo_users(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get expired demo users"""
    query = {
        "account_type": AccountType.DEMO,
        "demo_expires_at": {"$lt": datetime.now()}
    }
    
    # Add company filter based on user role
    if admin_user.role != UserRole.BOSS_ADMIN:
        query["company_id"] = str(admin_user.company_id)
    
    users = []
    cursor = db.users.find(query)
    async for user_doc in cursor:
        user = UserDB(**user_doc)
        user_dict = user.dict()
        user_dict["is_demo_expired"] = user.is_demo_expired()  # Call the method
        users.append(UserResponse(**user_dict))
    
    return users

# Password Management (keeping existing endpoints)
@router.post("/password/change", response_model=Dict[str, bool])
async def change_password_endpoint(
    password_data: PasswordChangeRequest,
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_database)
):
    """Change the current user's password"""
    from core.user import change_password  # Import existing function
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
    """Request a password reset (would send email in production)"""
    return {"success": True}

@router.post("/password/reset/confirm", response_model=Dict[str, bool])
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    db: Any = Depends(get_database)
):
    """Confirm a password reset using a token"""
    return {"success": True}

# Legacy functions (keeping for compatibility)
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
        {"_id": str(user_id)},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now()}}
    )
    
    return True

# Progress Dashboard (keeping existing functionality with company filtering)
from core.module import get_modules_by_course
from core.scenario import get_scenarios_by_module

@router.get("/users/me/progress-dashboard", response_model=Dict[str, Any])
async def get_progress_dashboard(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a comprehensive dashboard of user progress across all courses, modules and scenarios"""
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
        "recent_activity": [],
        "user_info": {
            "company_id": str(current_user.company_id),
            "account_type": current_user.account_type,
            "is_demo": current_user.account_type == AccountType.DEMO,
            "demo_expires_at": current_user.demo_expires_at,
            "is_demo_expired": current_user.is_demo_expired()
        }
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

# Add these 4 new endpoint functions to your user.py

@router.get("/users/{user_id}/detailed", response_model=Dict[str, Any])
async def get_user_detailed(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    from core.companies import get_company_by_id
    """Get detailed user information for view/edit operations"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permissions
    can_view = False
    admin_data = None
    
    if current_user.role == UserRole.BOSS_ADMIN:
        can_view = True
    elif current_user.role == UserRole.SUPERADMIN:
        if current_user.company_id == user.company_id:
            can_view = True
    elif current_user.role == UserRole.ADMIN:
        if current_user.company_id == user.company_id:
            admin_data = await db.users.find_one({"_id": str(current_user.id)})
            managed_users = admin_data.get("managed_users", [])
            if str(user_id) in managed_users or current_user.id == user_id:
                can_view = True
    elif current_user.role == UserRole.USER:
        if current_user.id == user_id:
            can_view = True
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    # Get company information
    company = await get_company_by_id(db, user.company_id)
    
    # Get creator information if available
    creator_info = None
    if hasattr(user, 'assignee_emp_id') and user.assignee_emp_id:
        creator = await db.users.find_one({"emp_id": user.assignee_emp_id})
        if creator:
            creator_info = {
                "id": creator["_id"],
                "username": creator.get("username"),
                "email": creator.get("email"),
                "role": creator.get("role")
            }
    
    # Get managed users if this user is an admin/superadmin
    managed_users_info = []
    if hasattr(user, 'managed_users') and user.managed_users:
        for managed_user_id in user.managed_users:
            managed_user = await db.users.find_one({"_id": managed_user_id})
            if managed_user:
                managed_users_info.append({
                    "id": managed_user["_id"],
                    "username": managed_user.get("username"),
                    "email": managed_user.get("email"),
                    "role": managed_user.get("role"),
                    "account_type": managed_user.get("account_type"),
                    "is_active": managed_user.get("is_active")
                })
    
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "emp_id": user.emp_id,
            "role": user.role,
            "account_type": user.account_type,
            "is_active": user.is_active,
            "demo_expires_at": user.demo_expires_at,
            "is_demo_expired": user.is_demo_expired(),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "assignee_emp_id": getattr(user, 'assignee_emp_id', None)
        },
        "company": {
            "id": str(company.id),
            "name": company.name,
            "company_type": company.company_type,
            "status": company.status
        } if company else None,
        "creator": creator_info,
        "managed_users": managed_users_info,
        "permissions": {
            "can_edit": can_view and (current_user.role != UserRole.USER or current_user.id == user_id),
            "can_delete": current_user.role in [UserRole.BOSS_ADMIN, UserRole.SUPERADMIN] or 
                         (current_user.role == UserRole.ADMIN and admin_data and str(user_id) in admin_data.get("managed_users", [])),
            "can_extend_demo": user.account_type == AccountType.DEMO and current_user.role != UserRole.USER,
            "can_assign_courses": current_user.role != UserRole.USER
        }
    }

@router.put("/users/{user_id}/detailed", response_model=UserResponse)
async def update_user_detailed(
    user_id: UUID,
    user_update: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Update user with detailed validation and permission checks"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permissions
    can_edit = False
    
    if current_user.role == UserRole.BOSS_ADMIN:
        can_edit = True
    elif current_user.role == UserRole.SUPERADMIN:
        if current_user.company_id == user.company_id:
            can_edit = True
            if user_update.get("role") == UserRole.BOSS_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Superadmin cannot promote users to boss admin"
                )
    elif current_user.role == UserRole.ADMIN:
        if current_user.company_id == user.company_id:
            admin_data = await db.users.find_one({"_id": str(current_user.id)})
            managed_users = admin_data.get("managed_users", [])
            if str(user_id) in managed_users or current_user.id == user_id:
                can_edit = True
                if user_update.get("role") in [UserRole.ADMIN, UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin cannot promote users to admin roles"
                    )
    elif current_user.role == UserRole.USER:
        if current_user.id == user_id:
            can_edit = True
            allowed_fields = {"username", "password"}
            if not set(user_update.keys()).issubset(allowed_fields):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Users can only update username and password"
                )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this user"
        )
    
    # Handle password update separately
    if "password" in user_update:
        if len(user_update["password"]) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        user_update["hashed_password"] = get_password_hash(user_update.pop("password"))
    
    # Prepare update data
    update_dict = {k: v for k, v in user_update.items() if v is not None}
    update_dict["updated_at"] = datetime.now()
    
    # Update in database
    await db.users.update_one(
        {"_id": str(user_id)},
        {"$set": update_dict}
    )
    
    updated_user = await db.users.find_one({"_id": str(user_id)})
    if updated_user:
        if updated_user.get("role") == UserRole.BOSS_ADMIN:
            user_obj = BossAdminDB(**updated_user)
        elif updated_user.get("role") == UserRole.SUPERADMIN:
            user_obj = SuperAdminDB(**updated_user)
        elif updated_user.get("role") == UserRole.ADMIN:
            user_obj = AdminUserDB(**updated_user)
        else:
            user_obj = UserDB(**updated_user)
        
        return UserResponse(
            **user_obj.dict(),
            is_demo_expired=user_obj.is_demo_expired() if hasattr(user_obj, 'is_demo_expired') else False
        )
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")

@router.get("/users/{user_id}/managed-users", response_model=List[Dict[str, Any]])
async def get_managed_users(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get users managed by a specific admin/superadmin"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check permissions
    if (current_user.role != UserRole.BOSS_ADMIN and 
        current_user.id != user_id and 
        current_user.company_id != user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's managed users"
        )
    
    if not hasattr(user, 'managed_users') or not user.managed_users:
        return []
    
    managed_users = []
    for managed_user_id in user.managed_users:
        managed_user = await db.users.find_one({"_id": managed_user_id})
        if managed_user:
            is_demo_expired = False
            if (managed_user.get("account_type") == AccountType.DEMO and 
                managed_user.get("demo_expires_at")):
                is_demo_expired = datetime.now() > managed_user["demo_expires_at"]
            
            managed_users.append({
                "id": managed_user["_id"],
                "email": managed_user.get("email"),
                "username": managed_user.get("username"),
                "emp_id": managed_user.get("emp_id"),
                "role": managed_user.get("role"),
                "account_type": managed_user.get("account_type"),
                "is_active": managed_user.get("is_active"),
                "demo_expires_at": managed_user.get("demo_expires_at"),
                "is_demo_expired": is_demo_expired,
                "created_at": managed_user.get("created_at"),
                "updated_at": managed_user.get("updated_at")
            })
    
    return managed_users

@router.post("/users/{user_id}/assign-users", response_model=Dict[str, bool])
async def assign_users_to_manager(
    user_id: UUID,
    assignment_data: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_superadmin_user)
):
    """Assign users to an admin/superadmin's management"""
    manager = await get_user_by_id(db, user_id)
    if not manager:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")
    
    if manager.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign users to admins and superadmins"
        )
    
    user_ids = assignment_data.get("user_ids", [])
    operation = assignment_data.get("operation", "add")  # add or remove
    
    if operation not in ["add", "remove"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operation must be 'add' or 'remove'"
        )
    
    # Validate all user IDs exist and are in the same company
    for target_user_id in user_ids:
        target_user = await get_user_by_id(db, UUID(target_user_id))
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {target_user_id} not found"
            )
        
        if target_user.company_id != manager.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only assign users from the same company"
            )
        
        if target_user.role in [UserRole.SUPERADMIN, UserRole.BOSS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign superadmins or boss admins as managed users"
            )
    
    # Perform the operation
    if operation == "add":
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$addToSet": {"managed_users": {"$each": user_ids}}}
        )
    else:  # remove
        await db.users.update_one(
            {"_id": str(user_id)},
            {"$pull": {"managed_users": {"$in": user_ids}}}
        )
    
    return {"success": True}

async def extend_demo_user_with_hierarchy(db: Any, extension_request: DemoExtensionRequest, extended_by: UUID) -> Dict[str, Any]:
    """
    Extend demo user account with hierarchical cascading
    
    Cascade Logic:
    - Boss Admin extends SuperAdmin -> Extends all admins and users in that company
    - Boss Admin/SuperAdmin extends Admin -> Extends all users managed by that admin
    - Admin extends User -> Only extends that user
    """
    # Get the user to extend
    user = await get_user_by_id(db, extension_request.user_id)
    if not user or user.account_type != AccountType.DEMO or user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SuperAdmins Can be Extended"
        )
    
    # Get the person making the extension
    extender = await get_user_by_id(db, extended_by)
    if not extender or extender.role not in [UserRole.BOSS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Boss admin can extend demo accounts"
        )
    
    # Check company permissions
    # if extender.role != UserRole.BOSS_ADMIN and extender.company_id != user.company_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Can only extend demo accounts in your own company"
    #     )
    
    # Calculate new expiry date
    current_expiry = user.demo_expires_at or datetime.now()
    if current_expiry < datetime.now():
        new_expiry = datetime.now() + timedelta(days=extension_request.extension_days)
    else:
        new_expiry = current_expiry + timedelta(days=extension_request.extension_days)
    
    # Track all users that will be extended
    extended_users = []
    cascade_count = 0
    
    # Update the main user
    await db.users.update_one(
        {"_id": str(extension_request.user_id)},
        {"$set": {"demo_expires_at": new_expiry, "updated_at": datetime.now()}}
    )
    extended_users.append({
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "type": "primary"
    })
    
    # HIERARCHICAL CASCADE LOGIC
    if user.role == UserRole.SUPERADMIN:
        # If extending a SuperAdmin, extend all admins and users in their company
        print(f"Extending SuperAdmin {user.email} - cascading to entire company")
        
        # Find all demo users in the same company (admins and regular users)
        cascade_query = {
            "company_id": user.company_id,
            "account_type": AccountType.DEMO,
            "_id": {"$ne": str(user.id)},  # Don't include the main user again
            "role": {"$in": [UserRole.ADMIN, UserRole.USER]}  # Don't cascade to other superadmins
        }
        print(cascade_query,"cascade_query")
        cursor =  db.users.find(cascade_query)
        print(cursor,"cursor")
        cascade_user_ids = []
        cursor_count = await db.users.count_documents(cascade_query)
        print(f"Number of documents found: {cursor_count}")
        async for cascade_user_doc in cursor:
            print(cascade_user_doc,"cascade_user_doc")
            cascade_user = UserDB(**cascade_user_doc)
            # Only extend if their current expiry is before or same as the new expiry
            if cascade_user.demo_expires_at and cascade_user.demo_expires_at <= new_expiry:
                cascade_user_ids.append(str(cascade_user.id))
                extended_users.append({
                    "id": str(cascade_user.id),
                    "email": cascade_user.email,
                    "role": cascade_user.role,
                    "type": "company_cascade"
                })
        
        if cascade_user_ids:
            await db.users.update_many(
                {"_id": {"$in": cascade_user_ids}},
                {"$set": {"demo_expires_at": new_expiry, "updated_at": datetime.now()}}
            )
            cascade_count = len(cascade_user_ids)
    
    # elif user.role == UserRole.ADMIN:
    #     # If extending an Admin, extend all users they manage
    #     print(f"Extending Admin {user.email} - cascading to managed users")
        
    #     # Find users managed by this admin
    #     admin_data = await db.users.find_one({"_id": str(user.id)})
    #     managed_user_ids = admin_data.get("managed_users", [])
        
    #     if managed_user_ids:
    #         # Find demo users among managed users
    #         cascade_query = {
    #             "_id": {"$in": managed_user_ids},
    #             "account_type": AccountType.DEMO,
    #             "company_id": str(user.company_id)
    #         }
            
    #         cursor = db.users.find(cascade_query)
    #         cascade_user_ids = []
            
    #         async for cascade_user_doc in cursor:
    #             cascade_user = UserDB(**cascade_user_doc)
    #             if cascade_user.demo_expires_at and cascade_user.demo_expires_at <= new_expiry:
    #                 cascade_user_ids.append(str(cascade_user.id))
    #                 extended_users.append({
    #                     "id": str(cascade_user.id),
    #                     "email": cascade_user.email,
    #                     "role": cascade_user.role,
    #                     "type": "managed_cascade"
    #                 })
            
    #         if cascade_user_ids:
    #             await db.users.update_many(
    #                 {"_id": {"$in": cascade_user_ids}},
    #                 {"$set": {"demo_expires_at": new_expiry, "updated_at": datetime.now()}}
    #             )
    #             cascade_count = len(cascade_user_ids)
    
    # else:
    #     # If extending a regular user, no cascade needed
    #     print(f"Extending regular user {user.email} - no cascade")
    
    return {
        "success": True,
        "primary_user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "new_expiry": new_expiry
        },
        "cascade_count": cascade_count,
        "total_extended": len(extended_users),
        "extended_users": extended_users,
        "extension_days": extension_request.extension_days
    }

# Update the API endpoint to use the new function
@router.post("/users/extend-demo-hierarchy", response_model=Dict[str, Any])
async def extend_demo_users_with_hierarchy_endpoint(
    extension_request: DemoExtensionRequest,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Extend demo user account with full hierarchical cascading
    
    - Boss Admin extends SuperAdmin -> Extends all company users
    - Boss Admin/SuperAdmin extends Admin -> Extends all managed users  
    - Admin extends User -> Only that user
    """
    result = await extend_demo_user_with_hierarchy(db, extension_request, admin_user.id)
    return result


# Existing methods
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
                            "analysis":analysis,
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
@router.get("/admin/users/{user_id}/scenario-sessions", response_model=List[Dict[str, Any]])
async def get_user_scenario_sessions(
    user_id: UUID,
    scenario_id: Optional[UUID] = Query(None, description="Filter by specific scenario ID"),
    mode: Optional[str] = Query("assess_mode", description="Filter by mode (assess_mode, learn_mode, try_mode, or 'all')"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)  # Only admins can access this
):
    """
    Get all chat sessions and their analysis for a specific user, optionally filtered by scenario.
    
    - Filter by specific scenario ID
    - Filter by mode (assess_mode is default)
    - Returns chat sessions with associated scenario, module, and course details
    - Includes analysis reports if available
    """
    # Check if admin is allowed to manage this user
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and admin_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view data for users you manage"
                )
    
    # Get scenario assignments for the user
    scenario_assignments = []
    
    # Build query based on filters
    query = {"user_id": str(user_id)}
    
    # Add scenario filter if provided
    if scenario_id:
        query["scenario_id"] = str(scenario_id)
    
    # Add mode filter if not "all"
    if mode != "all":
        query["assigned_modes"] = mode
    
    # Execute query
    cursor = db.user_scenario_assignments.find(query).skip(skip).limit(limit)
    async for assignment in cursor:
        scenario_assignments.append(assignment)
    
    # Prepare results array
    results = []
    
    # Process each scenario assignment
    for assignment in scenario_assignments:
        scenario_id = assignment["scenario_id"]
        module_id = assignment["module_id"]
        course_id = assignment["course_id"]
        
        # Get scenario, module, and course details
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        module = await db.modules.find_one({"_id": module_id})
        course = await db.courses.find_one({"_id": course_id})
        
        if not scenario or not module or not course:
            continue
            
        # Get the avatar interaction ID based on mode(s)
        avatar_interaction_ids = []
        
        if mode == "all":
            # Get all avatar interaction IDs
            if "learn_mode" in scenario and "avatar_interaction" in scenario["learn_mode"]:
                avatar_interaction_ids.append(scenario["learn_mode"]["avatar_interaction"])
            if "try_mode" in scenario and "avatar_interaction" in scenario["try_mode"]:
                avatar_interaction_ids.append(scenario["try_mode"]["avatar_interaction"])
            if "assess_mode" in scenario and "avatar_interaction" in scenario["assess_mode"]:
                avatar_interaction_ids.append(scenario["assess_mode"]["avatar_interaction"])
        else:
            # Get avatar interaction ID for the specific mode
            if mode in scenario and "avatar_interaction" in scenario[mode]:
                avatar_interaction_ids.append(scenario[mode]["avatar_interaction"])
        
        # Find chat sessions for this scenario's avatar interactions
        for avatar_interaction_id in avatar_interaction_ids:
            sessions_cursor = db.sessions.find({
                "user_id": str(user_id),
                "avatar_interaction": str(avatar_interaction_id)
            })
            
            async for session in sessions_cursor:
                # Get analysis report for this session if it exists
                analysis = await db.analysis.find_one({"session_id": str(session["_id"])})
                
                # Create session result object
                session_result = {
                    "session_id": str(session["_id"]),
                    "session_created_at": session.get("created_at"),
                    "session_last_updated": session.get("last_updated"),
                    "scenario_id": scenario_id,
                    "scenario_name": scenario.get("title", "Unknown"),
                    "scenario_thumbnail": scenario.get("thumbnail_url"),
                    "mode": next((m for m in ["learn_mode", "try_mode", "assess_mode"] 
                                if m in scenario and "avatar_interaction" in scenario[m] 
                                and scenario[m]["avatar_interaction"] == avatar_interaction_id), 
                                "unknown"),
                    "module_id": module_id,
                    "module_name": module.get("title", "Unknown"),
                    "course_id": course_id,
                    "course_name": course.get("title", "Unknown"),
                    "message_count": len(session.get("conversation_history", [])),
                    "has_analysis": analysis is not None,
                }
                
                # Add analysis data if available
                if analysis:
                    overall_eval = analysis.get("overall_evaluation", {})
                    session_result["analysis"] = {
                        "analysis_id": str(analysis["_id"]),
                        "timestamp": analysis.get("timestamp"),
                        "total_score": overall_eval.get("total_score") or overall_eval.get("total_percentage_score"),
                        "performance_category": overall_eval.get("performance_category") or overall_eval.get("user_performance_category"),
                        "strengths": overall_eval.get("strengths") or overall_eval.get("user_strengths", []),
                        "improvement_areas": overall_eval.get("areas_for_improvement") or overall_eval.get("user_improvement_areas", [])
                    }
                
                results.append(session_result)
    
    # Sort by most recent sessions first
    results.sort(key=lambda x: x.get("session_last_updated", datetime.min), reverse=True)
    
    return results

