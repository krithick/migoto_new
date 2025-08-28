# core/tier_admin_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from models.tier_models import CompanyTier, TierLimit, LimitType, LimitPeriod
from models.company_models import CompanyLimitsResponse, TierComparisonResponse, UsageAlertResponse
from models.user_models import UserDB, UserRole
from core.user import get_admin_user
from core.tier_management import tier_manager

# Admin/SuperAdmin router
router = APIRouter(prefix="/tiers", tags=["Admin - Tier Management"])

async def get_database():
    from database import get_db
    return await get_db()


# ==========================================
# TIER INFORMATION ENDPOINTS
# ==========================================

@router.get("/available", response_model=TierComparisonResponse)
async def get_available_tiers(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get all available tiers and their features"""
    try:
        available_tiers = []
        
        # Get current user's company tier
        user_company = await db.companies.find_one({"_id": str(admin_user.company_id)})
        current_tier = CompanyTier(user_company.get("tier", CompanyTier.BASIC)) if user_company else CompanyTier.BASIC
        
        # Build tier comparison
        for tier, config in tier_manager.tier_configs.items():
            tier_info = {
                "tier": tier.value,
                "tier_name": config.tier_name,
                "tier_description": config.tier_description,
                "is_current": tier == current_tier,
                "limits": []
            }
            
            # Add limit details
            for limit in config.limits:
                limit_info = {
                    "limit_key": limit.limit_key,
                    "limit_name": limit.limit_name,
                    "limit_value": limit.limit_value,
                    "limit_type": limit.limit_type.value,
                    "description": limit.description,
                    "is_feature_flag": limit.is_feature_flag,
                    "display_value": "Unlimited" if limit.limit_value == -1 else str(limit.limit_value)
                }
                tier_info["limits"].append(limit_info)
            
            available_tiers.append(tier_info)
        
        # Generate upgrade recommendations
        upgrade_recommendations = []
        if current_tier == CompanyTier.BASIC:
            upgrade_recommendations.append("Upgrade to Professional for advanced analytics and custom avatars")
        elif current_tier == CompanyTier.PROFESSIONAL:
            upgrade_recommendations.append("Upgrade to Enterprise for API access and higher limits")
        
        return TierComparisonResponse(
            available_tiers=available_tiers,
            current_tier=current_tier,
            current_company_id=admin_user.company_id,
            upgrade_recommendations=upgrade_recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tier information: {str(e)}")


@router.get("/{company_id}/limits", response_model=CompanyLimitsResponse)
async def get_company_limits(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get company's current limits and usage"""
    
    # Check permissions - admin can only view their own company, boss admin can view any
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's limits"
        )
    
    try:
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        return CompanyLimitsResponse(**limits_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company limits: {str(e)}")


@router.get("/{company_id}/usage-history")
async def get_company_usage_history(
    company_id: UUID,
    months: int = Query(3, ge=1, le=12, description="Number of months of history"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get historical usage data for a company"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's usage history"
        )
    
    try:
        # Get usage history from database
        history = []
        history_cursor = db.company_usage_history.find({
            "company_id": str(company_id)
        }).sort("period", -1).limit(months)
        
        async for record in history_cursor:
            history.append({
                "period": record.get("period"),
                "usage_entries": record.get("usage_entries", []),
                "archived_at": record.get("archived_at")
            })
        
        return {
            "company_id": str(company_id),
            "months_requested": months,
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage history: {str(e)}")


# ==========================================
# LIMIT CHECKING ENDPOINTS
# ==========================================

@router.get("/{company_id}/check-limits", response_model=Dict[str, Any])
async def check_company_limits(
    company_id: UUID,
    action: str = Query(..., description="Action to check (create_course, create_user, chat_session, etc.)"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Check if company can perform a specific action"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check limits for this company"
        )
    
    try:
        # Map actions to check functions
        if action == "create_course":
            result = await tier_manager.can_create_course(db, company_id)
        elif action == "create_user":
            result = await tier_manager.can_create_user(db, company_id)
        elif action == "chat_session":
            result = await tier_manager.can_start_chat_session(db, company_id)
        elif action == "analysis_report":
            result = await tier_manager.can_generate_analysis(db, company_id)
        elif action.startswith("create_module:"):
            course_id = UUID(action.split(":")[1])
            result = await tier_manager.can_create_module(db, company_id, course_id)
        elif action.startswith("create_scenario:"):
            module_id = UUID(action.split(":")[1])
            result = await tier_manager.can_create_scenario(db, company_id, module_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        return {
            "company_id": str(company_id),
            "action": action,
            "allowed": result.allowed,
            "current_usage": result.current_usage,
            "limit_value": result.limit_value,
            "remaining": result.remaining,
            "message": result.message,
            "next_reset": result.next_reset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking limits: {str(e)}")


@router.get("/{company_id}/feature-access/{feature_key}")
async def check_feature_access(
    company_id: UUID,
    feature_key: str,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Check if company has access to a specific feature"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check features for this company"
        )
    
    try:
        has_access = await tier_manager.has_feature_access(db, company_id, feature_key)
        
        return {
            "company_id": str(company_id),
            "feature_key": feature_key,
            "has_access": has_access
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking feature access: {str(e)}")


# ==========================================
# ANALYTICS AND MONITORING
# ==========================================

@router.get("/{company_id}/usage-alerts", response_model=List[UsageAlertResponse])
async def get_usage_alerts(
    company_id: UUID,
    threshold: float = Query(0.8, ge=0.1, le=1.0, description="Alert threshold (0.8 = 80%)"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get usage alerts for companies approaching their limits"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view alerts for this company"
        )
    
    try:
        # Get current limits and usage
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        alerts = []
        
        for usage_info in limits_data["usage"]:
            if usage_info["limit_value"] > 0:  # Skip unlimited limits
                percentage_used = usage_info["percentage_used"] / 100
                
                if percentage_used >= threshold:
                    alert_type = "limit_reached" if percentage_used >= 1.0 else "warning"
                    
                    # Find corresponding limit info for better messaging
                    limit_name = usage_info["usage_key"].replace("_", " ").title()
                    for limit_info in limits_data["limits"]:
                        if limit_info["limit_key"] == usage_info["usage_key"]:
                            limit_name = limit_info["limit_name"]
                            break
                    
                    alert = UsageAlertResponse(
                        company_id=company_id,
                        alert_type=alert_type,
                        limit_key=usage_info["usage_key"],
                        limit_name=limit_name,
                        current_usage=usage_info["current_value"],
                        limit_value=usage_info["limit_value"],
                        percentage_used=percentage_used * 100,
                        message=f"{limit_name}: {usage_info['current_value']}/{usage_info['limit_value']} ({percentage_used*100:.1f}% used)",
                        recommended_action="Consider upgrading tier" if percentage_used >= 0.9 else "Monitor usage closely"
                    )
                    alerts.append(alert)
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage alerts: {str(e)}")


# ==========================================
# COMPANY DASHBOARD INTEGRATION
# ==========================================

@router.get("/{company_id}/dashboard-summary")
async def get_tier_dashboard_summary(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get tier summary for company dashboard"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this company's tier dashboard"
        )
    
    try:
        # Get basic tier information
        company = await db.companies.find_one({"_id": str(company_id)})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        
        # Get key usage metrics
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        
        # Extract key metrics for dashboard
        key_metrics = []
        for usage in limits_data["usage"]:
            if usage["usage_key"] in ["chat_sessions_per_month", "analysis_reports_per_month", "max_users", "max_courses"]:
                key_metrics.append({
                    "name": usage["usage_key"].replace("_", " ").title(),
                    "current": usage["current_value"],
                    "limit": usage["limit_value"],
                    "percentage": usage["percentage_used"],
                    "status": "warning" if usage["percentage_used"] >= 80 else "good"
                })
        
        # Get alerts count
        alerts = await get_usage_alerts(company_id, 0.8, db, admin_user)
        alerts_count = len(alerts) if isinstance(alerts, list) else 0
        
        # Check if tier is expiring soon
        tier_expiry_warning = None
        if company.get("tier_expires_at"):
            expires_at = company["tier_expires_at"]
            days_until_expiry = (expires_at - datetime.now()).days
            if days_until_expiry <= 30:
                tier_expiry_warning = f"Tier expires in {days_until_expiry} days"
        
        return {
            "company_id": str(company_id),
            "company_name": company.get("name", "Unknown"),
            "current_tier": {
                "name": current_tier.value,
                "display_name": tier_manager.tier_configs[current_tier].tier_name,
                "expires_at": company.get("tier_expires_at")
            },
            "key_metrics": key_metrics,
            "alerts_count": alerts_count,
            "tier_expiry_warning": tier_expiry_warning,
            "next_reset": limits_data.get("next_monthly_reset"),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard summary: {str(e)}")


# ==========================================
# USAGE TRACKING HELPERS
# ==========================================

@router.post("/{company_id}/track-usage")
async def track_usage_manually(
    company_id: UUID,
    usage_type: str = Body(..., description="Usage type (chat_sessions_per_month, analysis_reports_per_month)"),
    amount: int = Body(1, description="Amount to track"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Manually track usage (for testing or corrections)"""
    
    # Check permissions - only for own company or boss admin
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to track usage for this company"
        )
    
    try:
        if usage_type == "chat_sessions":
            await tier_manager.track_chat_session(db, company_id, amount)
        elif usage_type == "analysis_reports":
            await tier_manager.track_analysis_generation(db, company_id, amount)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown usage type: {usage_type}")
        
        return {
            "success": True,
            "company_id": str(company_id),
            "usage_type": usage_type,
            "amount_tracked": amount,
            "tracked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking usage: {str(e)}")


# ==========================================
# FEATURE ACCESS HELPERS
# ==========================================

@router.get("/{company_id}/features")
async def get_company_features(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get all feature access status for company"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view features for this company"
        )
    
    try:
        features = [
            "advanced_analytics",
            "custom_avatars",
            "knowledge_base",
            "company_branding",
            "api_access"
        ]
        
        feature_access = {}
        for feature in features:
            has_access = await tier_manager.has_feature_access(db, company_id, feature)
            feature_access[feature] = {
                "enabled": has_access,
                "feature_name": feature.replace("_", " ").title()
            }
        
        return {
            "company_id": str(company_id),
            "features": feature_access,
            "checked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feature access: {str(e)}")


# ==========================================
# QUICK LIMIT CHECKS FOR UI
# ==========================================

@router.get("/{company_id}/quick-checks")
async def get_quick_limit_checks(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get quick limit checks for common actions (for UI buttons)"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to check limits for this company"
        )
    
    try:
        checks = {}
        
        # Check common actions
        actions = [
            ("can_create_course", tier_manager.can_create_course),
            ("can_create_user", tier_manager.can_create_user),
            ("can_start_chat", tier_manager.can_start_chat_session),
            ("can_generate_analysis", tier_manager.can_generate_analysis)
        ]
        
        for action_name, check_function in actions:
            try:
                result = await check_function(db, company_id)
                checks[action_name] = {
                    "allowed": result.allowed,
                    "remaining": result.remaining,
                    "message": result.message
                }
            except Exception as e:
                checks[action_name] = {
                    "allowed": False,
                    "remaining": 0,
                    "message": f"Error: {str(e)}"
                }
        
        return {
            "company_id": str(company_id),
            "checks": checks,
            "checked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing quick checks: {str(e)}")


# ==========================================
# TIER UPGRADE REQUEST (for future)
# ==========================================

@router.post("/{company_id}/request-upgrade")
async def request_tier_upgrade(
    company_id: UUID,
    requested_tier: CompanyTier = Body(...),
    reason: Optional[str] = Body(None),
    contact_email: Optional[str] = Body(None),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Submit a tier upgrade request (for boss admin review)"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request upgrade for this company"
        )
    
    try:
        # Get current company info
        company = await db.companies.find_one({"_id": str(company_id)})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        
        # Create upgrade request record
        upgrade_request = {
            "company_id": str(company_id),
            "company_name": company.get("name"),
            "current_tier": current_tier.value,
            "requested_tier": requested_tier.value,
            "requested_by": str(admin_user.id),
            "requester_email": admin_user.email,
            "contact_email": contact_email or admin_user.email,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Save to database (create collection if needed)
        await db.tier_upgrade_requests.insert_one(upgrade_request)
        
        return {
            "success": True,
            "request_id": str(upgrade_request.get("_id", "generated")),
            "message": "Upgrade request submitted successfully",
            "current_tier": current_tier.value,
            "requested_tier": requested_tier.value,
            "status": "pending_review"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting upgrade request: {str(e)}")


# ==========================================
# USAGE OPTIMIZATION SUGGESTIONS
# ==========================================

@router.get("/{company_id}/optimization-suggestions")
async def get_optimization_suggestions(
    company_id: UUID,
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """Get suggestions for optimizing usage and costs"""
    
    # Check permissions
    if admin_user.role != UserRole.BOSS_ADMIN and admin_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view optimization suggestions for this company"
        )
    
    try:
        # Get current usage data
        limits_data = await tier_manager.get_company_limits_and_usage(db, company_id)
        suggestions = []
        
        # Analyze usage patterns and generate suggestions
        for usage in limits_data["usage"]:
            usage_key = usage["usage_key"]
            current_value = usage["current_value"]
            limit_value = usage["limit_value"]
            percentage = usage["percentage_used"]
            
            if limit_value > 0:  # Skip unlimited
                if percentage < 20:  # Very low usage
                    if usage_key in ["chat_sessions_per_month", "analysis_reports_per_month"]:
                        suggestions.append({
                            "type": "cost_optimization",
                            "priority": "low",
                            "title": f"Low {usage_key.replace('_', ' ')} usage",
                            "description": f"You're only using {percentage:.1f}% of your {usage_key.replace('_', ' ')} allowance",
                            "recommendation": "Consider downgrading if this trend continues",
                            "potential_savings": "Consider lower tier"
                        })
                
                elif percentage > 90:  # Very high usage
                    suggestions.append({
                        "type": "upgrade_recommendation",
                        "priority": "high",
                        "title": f"High {usage_key.replace('_', ' ')} usage",
                        "description": f"You're using {percentage:.1f}% of your {usage_key.replace('_', ' ')} limit",
                        "recommendation": "Consider upgrading to avoid hitting limits",
                        "potential_benefits": "Higher limits and additional features"
                    })
                
                elif 70 <= percentage <= 90:  # Moderate-high usage
                    suggestions.append({
                        "type": "monitoring_alert",
                        "priority": "medium",
                        "title": f"Monitor {usage_key.replace('_', ' ')} usage",
                        "description": f"You're using {percentage:.1f}% of your allowance",
                        "recommendation": "Monitor closely and plan for potential upgrade",
                        "action": "Set up usage alerts"
                    })
        
        # Add feature-based suggestions
        company = await db.companies.find_one({"_id": str(company_id)})
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        
        if current_tier == CompanyTier.BASIC:
            suggestions.append({
                "type": "feature_upgrade",
                "priority": "medium", 
                "title": "Unlock Advanced Features",
                "description": "Professional tier includes advanced analytics, custom avatars, and knowledge base integration",
                "recommendation": "Upgrade to Professional for enhanced capabilities",
                "potential_benefits": "Better insights and customization options"
            })
        
        return {
            "company_id": str(company_id),
            "current_tier": current_tier.value,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating optimization suggestions: {str(e)}")