# core/tier_user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from models.tier_models import CompanyTier
from models.user_models import UserDB
from core.user import get_current_user
from core.tier_management import tier_manager

# Regular user router
router = APIRouter(prefix="/my-tier", tags=["User - Tier Information"])

async def get_database():
    from database import get_db
    return await get_db()


# ==========================================
# USER TIER INFORMATION ENDPOINTS
# ==========================================

@router.get("/info")
async def get_my_tier_info(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get current user's company tier information"""
    
    try:
        # Get user's company information
        company = await db.companies.find_one({"_id": str(current_user.company_id)})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        tier_config = tier_manager.tier_configs[current_tier]
        
        # Get basic usage information (limited for regular users)
        usage_data = await tier_manager.get_company_limits_and_usage(db, current_user.company_id)
        
        # Filter to show only relevant information for users
        user_relevant_usage = []
        relevant_keys = [
            "chat_sessions_per_month",
            "analysis_reports_per_month"
        ]
        
        for usage in usage_data["usage"]:
            if usage["usage_key"] in relevant_keys:
                user_relevant_usage.append({
                    "name": usage["usage_key"].replace("_", " ").title().replace("Per Month", ""),
                    "current": usage["current_value"],
                    "limit": usage["limit_value"],
                    "remaining": usage["remaining"],
                    "percentage_used": usage["percentage_used"]
                })
        
        # Get available features
        available_features = []
        feature_keys = [
            ("advanced_analytics", "Advanced Analytics"),
            ("custom_avatars", "Custom Avatars"),
            ("knowledge_base", "Knowledge Base"),
            ("company_branding", "Company Branding"),
            ("api_access", "API Access")
        ]
        
        for feature_key, feature_name in feature_keys:
            has_access = await tier_manager.has_feature_access(db, current_user.company_id, feature_key)
            available_features.append({
                "feature": feature_name,
                "available": has_access
            })
        
        return {
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "company_name": company.get("name", "Unknown"),
            "tier": {
                "name": current_tier.value,
                "display_name": tier_config.tier_name,
                "description": tier_config.tier_description
            },
            "usage_summary": user_relevant_usage,
            "available_features": available_features,
            "next_reset": usage_data.get("next_monthly_reset"),
            "account_type": current_user.account_type.value,
            "checked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tier information: {str(e)}")


@router.get("/usage")
async def get_my_usage_summary(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get current user's usage summary"""
    
    try:
        # Get company usage data
        usage_data = await tier_manager.get_company_limits_and_usage(db, current_user.company_id)
        
        # Focus on user-relevant metrics
        user_metrics = {}
        
        for usage in usage_data["usage"]:
            key = usage["usage_key"]
            
            if key == "chat_sessions_per_month":
                user_metrics["chat_sessions"] = {
                    "used": usage["current_value"],
                    "limit": usage["limit_value"],
                    "remaining": usage["remaining"],
                    "status": "warning" if usage["percentage_used"] >= 80 else "good"
                }
            elif key == "analysis_reports_per_month":
                user_metrics["analysis_reports"] = {
                    "used": usage["current_value"], 
                    "limit": usage["limit_value"],
                    "remaining": usage["remaining"],
                    "status": "warning" if usage["percentage_used"] >= 80 else "good"
                }
        
        # Get user's personal usage (sessions and reports created by this user)
        personal_sessions = await db.sessions.count_documents({
            "user_id": str(current_user.id),
            "created_at": {"$gte": datetime.now().replace(day=1)}  # This month
        })
        
        personal_reports = await db.analysis.count_documents({
            "user_id": str(current_user.id),
            "timestamp": {"$gte": datetime.now().replace(day=1)}  # This month
        })
        
        return {
            "user_id": str(current_user.id),
            "company_metrics": user_metrics,
            "personal_usage": {
                "sessions_this_month": personal_sessions,
                "reports_this_month": personal_reports
            },
            "period": datetime.now().strftime("%Y-%m"),
            "next_reset": usage_data.get("next_monthly_reset"),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage summary: {str(e)}")


@router.get("/features")
async def get_my_available_features(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get features available to current user's company"""
    
    try:
        features = [
            ("advanced_analytics", "Advanced Analytics", "Detailed insights and reporting"),
            ("custom_avatars", "Custom Avatars", "Upload and use custom avatar models"),
            ("knowledge_base", "Knowledge Base", "Advanced document and knowledge integration"),
            ("company_branding", "Company Branding", "Custom branding and white-label options"),
            ("api_access", "API Access", "REST API for integrations")
        ]
        
        feature_status = []
        
        for feature_key, feature_name, description in features:
            has_access = await tier_manager.has_feature_access(db, current_user.company_id, feature_key)
            feature_status.append({
                "key": feature_key,
                "name": feature_name,
                "description": description,
                "available": has_access,
                "status": "enabled" if has_access else "upgrade_required"
            })
        
        return {
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "features": feature_status,
            "checked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available features: {str(e)}")


# ==========================================
# USER ACTION CHECKING
# ==========================================

@router.get("/can-i/{action}")
async def can_i_perform_action(
    action: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Check if user can perform a specific action based on company tier"""
    
    try:
        company_id = current_user.company_id
        
        # Map user-friendly actions to system checks
        if action == "start-chat":
            result = await tier_manager.can_start_chat_session(db, company_id)
            action_name = "Start Chat Session"
        elif action == "request-analysis":
            result = await tier_manager.can_generate_analysis(db, company_id)
            action_name = "Request Analysis Report"
        elif action in ["advanced-analytics", "custom-avatars", "knowledge-base", "company-branding", "api-access"]:
            # Feature access checks
            feature_key = action.replace("-", "_")
            has_access = await tier_manager.has_feature_access(db, company_id, feature_key)
            
            return {
                "action": action,
                "action_name": action.replace("-", " ").title(),
                "allowed": has_access,
                "message": "Feature available" if has_access else "Feature requires tier upgrade",
                "type": "feature_access"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        return {
            "action": action,
            "action_name": action_name,
            "allowed": result.allowed,
            "current_usage": result.current_usage,
            "limit": result.limit_value,
            "remaining": result.remaining,
            "message": result.message,
            "type": "usage_limit"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking action: {str(e)}")


# ==========================================
# USER NOTIFICATIONS AND ALERTS
# ==========================================

@router.get("/notifications")
async def get_my_tier_notifications(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get tier-related notifications for current user"""
    
    try:
        notifications = []
        
        # Get company info
        company = await db.companies.find_one({"_id": str(current_user.company_id)})
        if not company:
            return {"notifications": []}
        
        # Check for tier expiry
        if company.get("tier_expires_at"):
            expires_at = company["tier_expires_at"]
            days_until_expiry = (expires_at - datetime.now()).days
            
            if days_until_expiry <= 7:
                notifications.append({
                    "type": "tier_expiry",
                    "priority": "high",
                    "title": "Tier Expiring Soon",
                    "message": f"Your company's {company.get('tier', 'current')} tier expires in {days_until_expiry} days",
                    "action_required": True,
                    "contact_admin": True
                })
            elif days_until_expiry <= 30:
                notifications.append({
                    "type": "tier_expiry",
                    "priority": "medium",
                    "title": "Tier Renewal Reminder", 
                    "message": f"Your company's tier expires in {days_until_expiry} days",
                    "action_required": False,
                    "contact_admin": True
                })
        
        # Check usage warnings
        usage_data = await tier_manager.get_company_limits_and_usage(db, current_user.company_id)
        
        for usage in usage_data["usage"]:
            if usage["limit_value"] > 0 and usage["percentage_used"] >= 90:
                notifications.append({
                    "type": "usage_warning",
                    "priority": "high" if usage["percentage_used"] >= 95 else "medium",
                    "title": f"{usage['usage_key'].replace('_', ' ').title()} Limit Nearly Reached",
                    "message": f"Company usage: {usage['current_value']}/{usage['limit_value']} ({usage['percentage_used']:.1f}%)",
                    "action_required": usage["percentage_used"] >= 95,
                    "contact_admin": True
                })
        
        # Check if user has demo account expiring
        if current_user.account_type.value == "demo" and current_user.demo_expires_at:
            days_until_demo_expiry = (current_user.demo_expires_at - datetime.now()).days
            if days_until_demo_expiry <= 7:
                notifications.append({
                    "type": "demo_expiry",
                    "priority": "high",
                    "title": "Demo Account Expiring",
                    "message": f"Your demo account expires in {days_until_demo_expiry} days",
                    "action_required": True,
                    "contact_admin": True
                })
        
        return {
            "user_id": str(current_user.id),
            "notifications": notifications,
            "total_notifications": len(notifications),
            "high_priority_count": len([n for n in notifications if n["priority"] == "high"]),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


# ==========================================
# TIER COMPARISON FOR USERS
# ==========================================

@router.get("/upgrade-options")
async def get_upgrade_options(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get tier upgrade options available to user's company"""
    
    try:
        # Get current company tier
        company = await db.companies.find_one({"_id": str(current_user.company_id)})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        
        # Show upgrade options
        upgrade_options = []
        
        if current_tier == CompanyTier.BASIC:
            # Can upgrade to Professional or Enterprise
            for tier in [CompanyTier.PROFESSIONAL, CompanyTier.ENTERPRISE]:
                config = tier_manager.tier_configs[tier]
                
                # Get key benefits for this tier
                key_benefits = []
                for limit in config.limits:
                    if limit.is_feature_flag and limit.limit_value == 1:
                        key_benefits.append(limit.limit_name)
                    elif limit.limit_key in ["chat_sessions_per_month", "max_courses", "max_users"]:
                        value_display = "Unlimited" if limit.limit_value == -1 else str(limit.limit_value)
                        key_benefits.append(f"{limit.limit_name}: {value_display}")
                
                upgrade_options.append({
                    "tier": tier.value,
                    "name": config.tier_name,
                    "description": config.tier_description,
                    "key_benefits": key_benefits[:5],  # Top 5 benefits
                    "recommended": tier == CompanyTier.PROFESSIONAL  # Recommend Professional as next step
                })
                
        elif current_tier == CompanyTier.PROFESSIONAL:
            # Can upgrade to Enterprise
            config = tier_manager.tier_configs[CompanyTier.ENTERPRISE]
            
            key_benefits = []
            for limit in config.limits:
                if limit.is_feature_flag and limit.limit_value == 1:
                    # Check if this feature is not available in current tier
                    current_config = tier_manager.tier_configs[current_tier]
                    current_limit = next((l for l in current_config.limits if l.limit_key == limit.limit_key), None)
                    if not current_limit or current_limit.limit_value == 0:
                        key_benefits.append(limit.limit_name)
                elif limit.limit_key in ["chat_sessions_per_month", "max_courses", "max_users"]:
                    value_display = "Unlimited" if limit.limit_value == -1 else str(limit.limit_value)
                    key_benefits.append(f"{limit.limit_name}: {value_display}")
            
            upgrade_options.append({
                "tier": CompanyTier.ENTERPRISE.value,
                "name": config.tier_name,
                "description": config.tier_description,
                "key_benefits": key_benefits[:5],
                "recommended": True
            })
        
        return {
            "current_tier": {
                "name": current_tier.value,
                "display_name": tier_manager.tier_configs[current_tier].tier_name
            },
            "upgrade_options": upgrade_options,
            "contact_info": {
                "message": "Contact your admin to request a tier upgrade",
                "admin_required": current_user.role.value == "user"
            },
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upgrade options: {str(e)}")


# ==========================================
# USER ACTIVITY SUMMARY
# ==========================================

@router.get("/my-activity")
async def get_my_tier_activity(
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get user's activity summary related to tier limits"""
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get user's sessions
        my_sessions = await db.sessions.count_documents({
            "user_id": str(current_user.id),
            "created_at": {"$gte": cutoff_date}
        })
        
        # Get user's analysis reports
        my_reports = await db.analysis.count_documents({
            "user_id": str(current_user.id),
            "timestamp": {"$gte": cutoff_date}
        })
        
        # Get company totals for comparison
        company_sessions = await db.sessions.count_documents({
            "created_at": {"$gte": cutoff_date}
        })
        
        company_reports = await db.analysis.count_documents({
            "timestamp": {"$gte": cutoff_date}
        })
        
        # Calculate user's contribution percentage
        session_percentage = (my_sessions / company_sessions * 100) if company_sessions > 0 else 0
        report_percentage = (my_reports / company_reports * 100) if company_reports > 0 else 0
        
        # Get current month usage for context
        current_month_start = datetime.now().replace(day=1)
        
        my_sessions_this_month = await db.sessions.count_documents({
            "user_id": str(current_user.id),
            "created_at": {"$gte": current_month_start}
        })
        
        my_reports_this_month = await db.analysis.count_documents({
            "user_id": str(current_user.id),
            "timestamp": {"$gte": current_month_start}
        })
        
        return {
            "user_id": str(current_user.id),
            "analysis_period": f"Last {days} days",
            "my_activity": {
                "chat_sessions": my_sessions,
                "analysis_reports": my_reports,
                "sessions_percentage_of_company": round(session_percentage, 1),
                "reports_percentage_of_company": round(report_percentage, 1)
            },
            "current_month": {
                "chat_sessions": my_sessions_this_month,
                "analysis_reports": my_reports_this_month
            },
            "activity_level": "high" if session_percentage > 20 else "medium" if session_percentage > 5 else "low",
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activity summary: {str(e)}")


# ==========================================
# HELP AND GUIDANCE
# ==========================================

@router.get("/help")
async def get_tier_help(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get help information about tiers and limits"""
    
    try:
        # Get current tier for contextual help
        company = await db.companies.find_one({"_id": str(current_user.company_id)})
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC)) if company else CompanyTier.BASIC
        
        help_info = {
            "tier_system_overview": {
                "title": "Understanding Tiers",
                "description": "Our tier system controls access to features and usage limits",
                "key_concepts": [
                    "Each company is assigned a tier that determines available features",
                    "Usage limits reset monthly on the first day of each month",
                    "Feature access is immediate when you upgrade tiers",
                    "Your admin can request tier upgrades"
                ]
            },
            "current_tier_info": {
                "tier": current_tier.value,
                "name": tier_manager.tier_configs[current_tier].tier_name,
                "description": tier_manager.tier_configs[current_tier].tier_description
            },
            "common_questions": [
                {
                    "question": "What happens when I reach my chat session limit?",
                    "answer": "You won't be able to start new chat sessions until the next monthly reset or your admin upgrades the tier."
                },
                {
                    "question": "Can I see my personal usage?", 
                    "answer": "Yes! Use the /my-tier/usage endpoint to see your personal contribution to company usage."
                },
                {
                    "question": "How do I request a tier upgrade?",
                    "answer": "Contact your company admin or superadmin. Only they can request tier upgrades from the boss admin."
                },
                {
                    "question": "What features are available in higher tiers?",
                    "answer": "Use /my-tier/upgrade-options to see what features you could gain with an upgrade."
                },
                {
                    "question": "When do usage limits reset?",
                    "answer": "All monthly usage limits reset on the 1st day of each month at midnight."
                }
            ],
            "troubleshooting": {
                "cant_start_chat": "Check your company's chat session usage. If at limit, wait for monthly reset or ask admin to upgrade.",
                "cant_generate_analysis": "Check analysis report usage limit. Contact admin if you need more reports.",
                "feature_not_available": "The feature requires a higher tier. Ask your admin about upgrading.",
                "demo_account_expired": "Contact your admin to extend your demo account or convert to regular account."
            },
            "contact_info": {
                "for_usage_questions": "Check your usage with /my-tier/usage",
                "for_feature_questions": "Check available features with /my-tier/features", 
                "for_upgrade_requests": "Contact your admin or superadmin",
                "for_technical_issues": "Contact support through your admin"
            }
        }
        
        return help_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching help information: {str(e)}")


@router.get("/limits-explained")
async def get_limits_explained(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get detailed explanation of current tier limits"""
    
    try:
        # Get current usage data
        usage_data = await tier_manager.get_company_limits_and_usage(db, current_user.company_id)
        
        explained_limits = []
        
        for usage in usage_data["usage"]:
            limit_key = usage["usage_key"]
            
            # Create user-friendly explanations
            explanation = {
                "limit_name": usage["usage_key"].replace("_", " ").title(),
                "current_usage": usage["current_value"],
                "limit": usage["limit_value"],
                "remaining": usage["remaining"],
                "status": "good" if usage["percentage_used"] < 70 else "warning" if usage["percentage_used"] < 90 else "critical"
            }
            
            # Add specific explanations
            if limit_key == "chat_sessions_per_month":
                explanation.update({
                    "description": "Total chat sessions your company can start each month",
                    "what_counts": "Each chat conversation with an AI avatar",
                    "when_resets": "1st day of each month",
                    "tips": "Sessions are shared across all company users"
                })
            elif limit_key == "analysis_reports_per_month":
                explanation.update({
                    "description": "AI analysis reports your company can generate each month",
                    "what_counts": "Each detailed performance analysis after a chat session", 
                    "when_resets": "1st day of each month",
                    "tips": "Reports provide valuable insights into conversation quality"
                })
            elif limit_key == "max_courses":
                explanation.update({
                    "description": "Maximum courses your company can create",
                    "what_counts": "Each training course in your company",
                    "when_resets": "Never (lifetime limit)",
                    "tips": "Organize content efficiently to maximize course value"
                })
            elif limit_key == "max_users":
                explanation.update({
                    "description": "Maximum users in your company",
                    "what_counts": "All active users including admins",
                    "when_resets": "Never (lifetime limit)", 
                    "tips": "Includes all roles: users, admins, and superadmins"
                })
            else:
                explanation.update({
                    "description": f"Controls {limit_key.replace('_', ' ')}",
                    "what_counts": "Various activities",
                    "when_resets": "Varies by limit type",
                    "tips": "Check with your admin for specific details"
                })
            
            explained_limits.append(explanation)
        
        return {
            "user_id": str(current_user.id),
            "company_id": str(current_user.company_id),
            "explained_limits": explained_limits,
            "general_info": {
                "monthly_reset_date": "1st day of each month",
                "timezone": "Server timezone (UTC)",
                "shared_limits": "Usage limits are shared across all company users",
                "feature_limits": "Feature access is immediate upon tier upgrade"
            },
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining limits: {str(e)}")


# ==========================================
# UTILITY FUNCTIONS FOR FRONTEND
# ==========================================

async def get_user_tier_widget_data(db: Any, current_user: UserDB) -> Dict[str, Any]:
    """
    Utility function to get tier widget data for frontend dashboard.
    Returns minimal data for displaying tier status widget.
    """
    try:
        # Get company and tier info
        company = await db.companies.find_one({"_id": str(current_user.company_id)})
        if not company:
            return {"error": "Company not found"}
        
        current_tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
        tier_config = tier_manager.tier_configs[current_tier]
        
        # Get key usage metrics
        usage_data = await tier_manager.get_company_limits_and_usage(db, current_user.company_id)
        
        # Find most critical usage
        critical_usage = None
        highest_percentage = 0
        
        for usage in usage_data["usage"]:
            if usage["limit_value"] > 0 and usage["percentage_used"] > highest_percentage:
                highest_percentage = usage["percentage_used"]
                if usage["percentage_used"] >= 80:  # Only show if concerning
                    critical_usage = {
                        "name": usage["usage_key"].replace("_", " ").title(),
                        "percentage": usage["percentage_used"],
                        "remaining": usage["remaining"]
                    }
        
        # Check for urgent notifications
        urgent_notifications = 0
        
        # Tier expiry check
        if company.get("tier_expires_at"):
            days_until_expiry = (company["tier_expires_at"] - datetime.now()).days
            if days_until_expiry <= 7:
                urgent_notifications += 1
        
        # High usage check
        high_usage_items = len([u for u in usage_data["usage"] if u["limit_value"] > 0 and u["percentage_used"] >= 90])
        urgent_notifications += high_usage_items
        
        return {
            "tier": {
                "name": current_tier.value,
                "display_name": tier_config.tier_name,
                "color": "green" if current_tier == CompanyTier.ENTERPRISE else "blue" if current_tier == CompanyTier.PROFESSIONAL else "orange"
            },
            "critical_usage": critical_usage,
            "urgent_notifications": urgent_notifications,
            "next_reset": usage_data.get("next_monthly_reset"),
            "can_upgrade": current_tier != CompanyTier.ENTERPRISE,
            "widget_status": "critical" if urgent_notifications > 0 else "warning" if critical_usage else "good"
        }
        
    except Exception as e:
        return {"error": f"Widget data error: {str(e)}"}


@router.get("/widget")
async def get_tier_widget(
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """Get tier widget data for dashboard"""
    
    widget_data = await get_user_tier_widget_data(db, current_user)
    return widget_data