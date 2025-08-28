# core/tier_utils.py

"""
TIER SYSTEM UTILITY FUNCTIONS
==============================

These are the enforcement functions that you import into your existing endpoints
to add tier checking without modifying the route files.

Import these into your existing endpoint files to add tier restrictions.
"""

from fastapi import HTTPException, status
from typing import Any, UUID
from core.tier_management import tier_manager


# ==========================================
# CONTENT CREATION LIMIT ENFORCEMENT
# ==========================================

async def enforce_content_creation_limit(db: Any, company_id: UUID, content_type: str, **kwargs) -> bool:
    """
    Utility function to check content creation limits.
    
    Usage examples:
    - await enforce_content_creation_limit(db, company_id, "course")
    - await enforce_content_creation_limit(db, company_id, "module", course_id=course_id)
    - await enforce_content_creation_limit(db, company_id, "scenario", module_id=module_id)
    - await enforce_content_creation_limit(db, company_id, "user")
    
    Args:
        db: Database connection
        company_id: Company UUID
        content_type: "course", "module", "scenario", or "user"
        **kwargs: Additional parameters like course_id for modules, module_id for scenarios
    
    Raises:
        HTTPException: If limit is exceeded (429 Too Many Requests)
    
    Returns:
        True if allowed (for success indication)
    """
    try:
        if content_type == "course":
            result = await tier_manager.can_create_course(db, company_id)
        elif content_type == "user":
            result = await tier_manager.can_create_user(db, company_id)
        elif content_type == "module":
            course_id = kwargs.get("course_id")
            if not course_id:
                raise ValueError("course_id required for module creation check")
            result = await tier_manager.can_create_module(db, company_id, course_id)
        elif content_type == "scenario":
            module_id = kwargs.get("module_id")
            if not module_id:
                raise ValueError("module_id required for scenario creation check")
            result = await tier_manager.can_create_scenario(db, company_id, module_id)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cannot create {content_type}. {result.message}. Current usage: {result.current_usage}/{result.limit_value}. Upgrade your plan for higher limits."
            )
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error enforcing {content_type} creation limit: {e}")
        return True  # Allow on error to avoid breaking functionality


# ==========================================
# CHAT SESSION LIMIT ENFORCEMENT
# ==========================================

async def enforce_chat_session_limit(db: Any, company_id: UUID) -> bool:
    """
    Utility function to check and enforce chat session limits.
    Call this before starting any chat session that uses TTS/STT.
    
    Usage:
    - await enforce_chat_session_limit(db, current_user.company_id)
    
    Args:
        db: Database connection
        company_id: Company UUID
    
    Raises:
        HTTPException: If limit is exceeded (429 Too Many Requests)
    
    Returns:
        True if allowed, and automatically tracks the usage
    """
    try:
        result = await tier_manager.can_start_chat_session(db, company_id)
        
        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Chat session limit exceeded. {result.message}. Current usage: {result.current_usage}/{result.limit_value}. Upgrade your plan for more sessions."
            )
        
        # If allowed, track the usage
        await tier_manager.track_chat_session(db, company_id, 1)
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error enforcing chat session limit: {e}")
        return True  # Allow on error to avoid breaking functionality


# ==========================================
# ANALYSIS REPORT LIMIT ENFORCEMENT  
# ==========================================

async def enforce_analysis_limit(db: Any, company_id: UUID) -> bool:
    """
    Utility function to check and enforce analysis report limits.
    Call this before generating any analysis report.
    
    Usage:
    - await enforce_analysis_limit(db, current_user.company_id)
    
    Args:
        db: Database connection
        company_id: Company UUID
    
    Raises:
        HTTPException: If limit is exceeded (429 Too Many Requests)
    
    Returns:
        True if allowed, and automatically tracks the usage
    """
    try:
        result = await tier_manager.can_generate_analysis(db, company_id)
        
        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Analysis report limit exceeded. {result.message}. Current usage: {result.current_usage}/{result.limit_value}. Upgrade your plan for more reports."
            )
        
        # If allowed, track the usage
        await tier_manager.track_analysis_generation(db, company_id, 1)
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error enforcing analysis limit: {e}")
        return True  # Allow on error


# ==========================================
# FEATURE ACCESS CHECKING
# ==========================================

async def check_feature_permission(db: Any, company_id: UUID, feature_key: str) -> bool:
    """
    Utility function to check if company has access to a feature.
    
    Usage:
    - has_analytics = await check_feature_permission(db, company_id, "advanced_analytics")
    - has_avatars = await check_feature_permission(db, company_id, "custom_avatars")
    
    Available features:
    - "advanced_analytics"
    - "custom_avatars" 
    - "knowledge_base"
    - "company_branding"
    - "api_access"
    
    Args:
        db: Database connection
        company_id: Company UUID  
        feature_key: Feature identifier string
    
    Returns:
        True if feature is available, False otherwise
    """
    try:
        return await tier_manager.has_feature_access(db, company_id, feature_key)
    except Exception as e:
        print(f"❌ Error checking feature permission: {e}")
        return False  # Deny on error for security


# ==========================================
# FEATURE ACCESS ENFORCEMENT
# ==========================================

async def enforce_feature_access(db: Any, company_id: UUID, feature_key: str, feature_name: str = None) -> bool:
    """
    Utility function to enforce feature access - raises exception if not allowed.
    
    Usage:
    - await enforce_feature_access(db, company_id, "advanced_analytics", "Advanced Analytics")
    - await enforce_feature_access(db, company_id, "custom_avatars", "Custom Avatar Upload")
    
    Args:
        db: Database connection
        company_id: Company UUID
        feature_key: Feature identifier string
        feature_name: Human-readable feature name for error messages
    
    Raises:
        HTTPException: If feature is not available (403 Forbidden)
    
    Returns:
        True if feature is available
    """
    try:
        has_access = await check_feature_permission(db, company_id, feature_key)
        
        if not has_access:
            display_name = feature_name or feature_key.replace("_", " ").title()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{display_name} not available in your current plan. Please upgrade to access this feature."
            )
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error enforcing feature access: {e}")
        return False


# ==========================================
# TIER VALIDATION HELPERS
# ==========================================

async def get_company_tier_info(db: Any, company_id: UUID) -> dict:
    """
    Get basic tier information for a company.
    
    Usage:
    - tier_info = await get_company_tier_info(db, company_id)
    
    Returns:
        Dictionary with tier information or error details
    """
    try:
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        return {
            "success": True,
            "tier": limits_data.get("tier"),
            "tier_expires_at": limits_data.get("tier_expires_at"),
            "warnings": limits_data.get("warnings", []),
            "has_warnings": len(limits_data.get("warnings", [])) > 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tier": "unknown"
        }


async def check_tier_warnings(db: Any, company_id: UUID) -> list:
    """
    Check if company has any tier-related warnings.
    
    Usage:
    - warnings = await check_tier_warnings(db, company_id)
    
    Returns:
        List of warning messages
    """
    try:
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        return limits_data.get("warnings", [])
    except Exception as e:
        print(f"❌ Error checking tier warnings: {e}")
        return []


# ==========================================
# BATCH OPERATIONS FOR MULTIPLE CHECKS
# ==========================================

async def check_multiple_limits(db: Any, company_id: UUID, checks: list) -> dict:
    """
    Check multiple limits at once for efficiency.
    
    Usage:
    - results = await check_multiple_limits(db, company_id, [
        "create_course", "create_user", "chat_session", "analysis_report"
      ])
    
    Args:
        db: Database connection
        company_id: Company UUID
        checks: List of check types
    
    Returns:
        Dictionary with check results
    """
    results = {}
    
    for check_type in checks:
        try:
            if check_type == "create_course":
                result = await tier_manager.can_create_course(db, company_id)
            elif check_type == "create_user":
                result = await tier_manager.can_create_user(db, company_id)
            elif check_type == "chat_session":
                result = await tier_manager.can_start_chat_session(db, company_id)
            elif check_type == "analysis_report":
                result = await tier_manager.can_generate_analysis(db, company_id)
            else:
                results[check_type] = {"allowed": False, "message": f"Unknown check type: {check_type}"}
                continue
                
            results[check_type] = {
                "allowed": result.allowed,
                "current_usage": result.current_usage,
                "limit_value": result.limit_value,
                "remaining": result.remaining,
                "message": result.message
            }
        except Exception as e:
            results[check_type] = {"allowed": False, "message": f"Error: {str(e)}"}
    
    return results


# ==========================================
# ERROR HANDLING HELPERS
# ==========================================

def handle_tier_limit_error(e: HTTPException, context: str = "") -> dict:
    """
    Standard way to handle tier limit errors for API responses.
    
    Usage:
    try:
        await enforce_content_creation_limit(db, company_id, "course")
    except HTTPException as e:
        return handle_tier_limit_error(e, "course creation")
    
    Args:
        e: The HTTPException raised by tier enforcement
        context: Additional context for the error
    
    Returns:
        Dictionary with error details and suggested actions
    """
    if e.status_code == 429:  # Too Many Requests
        return {
            "error": "limit_exceeded",
            "message": e.detail,
            "context": context,
            "suggested_action": "upgrade_plan",
            "upgrade_info": "/tiers/available",  # Link to tier comparison
            "status_code": 429
        }
    elif e.status_code == 403:  # Forbidden (feature access)
        return {
            "error": "feature_not_available",
            "message": e.detail,
            "context": context,
            "suggested_action": "upgrade_plan",
            "upgrade_info": "/tiers/available",
            "status_code": 403
        }
    else:
        return {
            "error": "tier_check_failed",
            "message": e.detail,
            "context": context,
            "status_code": e.status_code
        }


# ==========================================
# INTEGRATION EXAMPLES
# ==========================================

"""
HOW TO USE THESE FUNCTIONS IN YOUR EXISTING CODE:
=================================================

1. IMPORT INTO YOUR ENDPOINT FILES:

```python
# At the top of core/course.py, core/module.py, etc.
from core.tier_utils import (
    enforce_content_creation_limit,
    enforce_chat_session_limit, 
    enforce_analysis_limit,
    check_feature_permission,
    enforce_feature_access
)
```

2. ADD TO COURSE CREATION (core/course.py):

```python
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    course: CourseCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    # 🔥 ADD THIS LINE
    await enforce_content_creation_limit(db, admin_user.company_id, "course")
    
    # Your existing code unchanged
    return await create_course(db, course, admin_user.id, admin_user.role)
```

3. ADD TO MODULE CREATION (core/module.py):

```python 
@router.post("/courses/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module_endpoint(
    course_id: UUID,
    module: ModuleCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    # 🔥 ADD THIS LINE
    await enforce_content_creation_limit(db, admin_user.company_id, "module", course_id=course_id)
    
    # Your existing code unchanged
    return await create_module(db, course_id, module, admin_user.id, admin_user.role)
```

4. ADD TO SCENARIO CREATION (core/scenario.py):

```python
@router.post("/modules/{module_id}/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario_endpoint(
    module_id: UUID,
    scenario: ScenarioCreate,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    # 🔥 ADD THIS LINE
    await enforce_content_creation_limit(db, admin_user.company_id, "scenario", module_id=module_id)
    
    # Your existing code unchanged
    return await create_scenario(db, module_id, scenario, admin_user.id)
```

5. ADD TO USER CREATION (core/user.py):

```python
@router.post("/users", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    users: List[UserCreate],
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    # 🔥 ADD THESE LINES
    for _ in users:
        await enforce_content_creation_limit(db, admin_user.company_id, "user")
    
    # Your existing code unchanged
    created_users = await create_user(db, users, created_by=admin_user.id)
    return [UserResponse(**user.dict(), is_demo_expired=user.is_demo_expired()) for user in created_users]
```

6. ADD TO CHAT SESSION CREATION (wherever you start chat sessions):

```python
# Before creating any chat session with TTS/STT
await enforce_chat_session_limit(db, current_user.company_id)

# Then proceed with your existing chat session creation
session_id = await create_chat_session(...)
```

7. ADD TO ANALYSIS GENERATION (in your sessionAnalyser endpoint):

```python
@app.get("/sessionAnalyser/{id}")
async def get_session_analysis(
    id: str,
    db: MongoDB = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # 🔥 ADD THIS LINE
    await enforce_analysis_limit(db, current_user.company_id)
    
    # Your existing analysis code unchanged
    session2 = await db.get_session_raw(id)
    analysis = await db.get_session_analysis(id)
    # ... rest of your existing code
```

8. ADD FEATURE CHECKS TO PREMIUM FEATURES:

```python
# For advanced analytics endpoints:
await enforce_feature_access(db, company_id, "advanced_analytics", "Advanced Analytics")

# For custom avatar uploads:
await enforce_feature_access(db, company_id, "custom_avatars", "Custom Avatar Upload")

# For knowledge base features:  
await enforce_feature_access(db, company_id, "knowledge_base", "Knowledge Base Integration")
```

MINIMAL INTEGRATION - Just add ONE line to each endpoint where you want limits!
"""