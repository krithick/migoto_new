# core/tier_boss_admin_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from models.tier_models import CompanyTier, TierLimit, LimitType, LimitPeriod, TierUpgradeRequest
from models.company_models import CompanyLimitsResponse, TierComparisonResponse, UsageAlertResponse
from models.user_models import UserDB, UserRole
from core.user import get_boss_admin_user
from core.tier_management import tier_manager

# Boss Admin only router
router = APIRouter(prefix="/admin/tiers", tags=["Boss Admin - Tier Management"])

async def get_database():
    from database import get_db
    return await get_db()


# ==========================================
# TIER MANAGEMENT ENDPOINTS (Boss Admin Only)
# ==========================================

@router.put("/{company_id}/tier", response_model=Dict[str, Any])
async def upgrade_company_tier(
    company_id: UUID,
    upgrade_request: TierUpgradeRequest,
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Upgrade or downgrade company tier (Boss Admin only)"""
    
    try:
        success = await tier_manager.upgrade_company_tier(
            db=db,
            company_id=company_id,
            new_tier=upgrade_request.new_tier,
            upgraded_by=boss_admin.id,
            expires_at=upgrade_request.expires_at,
            notes=upgrade_request.reason
        )
        
        if success:
            # Get updated company info
            updated_company = await db.companies.find_one({"_id": str(company_id)})
            
            return {
                "success": True,
                "company_id": str(company_id),
                "new_tier": upgrade_request.new_tier.value,
                "upgraded_by": str(boss_admin.id),
                "upgraded_at": datetime.now(),
                "expires_at": upgrade_request.expires_at,
                "company_name": updated_company.get("name", "Unknown") if updated_company else "Unknown"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to upgrade company tier"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upgrading tier: {str(e)}")


@router.post("/custom-limit", response_model=Dict[str, bool])
async def add_custom_limit_to_tier(
    tier: CompanyTier = Body(...),
    limit_key: str = Body(...),
    limit_name: str = Body(...),
    limit_type: LimitType = Body(...),
    limit_value: int = Body(...),
    reset_period: LimitPeriod = Body(LimitPeriod.MONTHLY),
    description: Optional[str] = Body(None),
    is_feature_flag: bool = Body(False),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Add a custom limit to a tier for flexible pricing (Boss Admin only)"""
    
    try:
        new_limit = TierLimit(
            limit_key=limit_key,
            limit_name=limit_name,
            limit_type=limit_type,
            limit_value=limit_value,
            reset_period=reset_period,
            description=description,
            is_feature_flag=is_feature_flag
        )
        
        success = await tier_manager.add_custom_limit(
            db=db,
            tier=tier,
            limit=new_limit,
            updated_by=boss_admin.id
        )
        
        return {"success": success}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding custom limit: {str(e)}")


@router.put("/update-limit", response_model=Dict[str, bool])
async def update_tier_limit(
    tier: CompanyTier = Body(...),
    limit_key: str = Body(...),
    new_value: int = Body(...),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Update the value of an existing limit (Boss Admin only)"""
    
    try:
        success = await tier_manager.update_limit_value(
            db=db,
            tier=tier,
            limit_key=limit_key,
            new_value=new_value,
            updated_by=boss_admin.id
        )
        
        return {"success": success}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating limit: {str(e)}")


@router.post("/{company_id}/reset-usage", response_model=Dict[str, bool])
async def reset_company_usage(
    company_id: UUID,
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Reset monthly usage for a company (Boss Admin only)"""
    
    try:
        await tier_manager.reset_monthly_usage(db, company_id)
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting usage: {str(e)}")


@router.post("/reset-all-usage", response_model=Dict[str, Any])
async def reset_all_companies_usage(
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Reset monthly usage for all companies (Boss Admin only)"""
    
    try:
        await tier_manager.reset_monthly_usage(db)
        
        # Count total companies affected
        company_count = await db.companies.count_documents({})
        
        return {
            "success": True,
            "companies_affected": company_count,
            "reset_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting all usage: {str(e)}")


@router.get("/system/tier-analytics", response_model=Dict[str, Any])
async def get_system_tier_analytics(
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Get system-wide tier analytics (Boss Admin only)"""
    
    try:
        # Count companies by tier
        tier_distribution = {}
        for tier in CompanyTier:
            count = await db.companies.count_documents({"tier": tier.value})
            tier_distribution[tier.value] = count
        
        # Get usage statistics
        total_companies = await db.companies.count_documents({})
        active_companies = await db.companies.count_documents({"status": "active"})
        
        # Get top usage companies (simplified)
        high_usage_companies = []
        cursor = db.company_usage.find({}).limit(10)
        async for usage_doc in cursor:
            total_usage = sum(entry.get("current_value", 0) for entry in usage_doc.get("usage_entries", []))
            if total_usage > 0:
                company = await db.companies.find_one({"_id": usage_doc["company_id"]})
                high_usage_companies.append({
                    "company_id": usage_doc["company_id"],
                    "company_name": company.get("name", "Unknown") if company else "Unknown",
                    "tier": company.get("tier", "basic") if company else "basic",
                    "total_usage": total_usage
                })
        
        # Sort by usage
        high_usage_companies.sort(key=lambda x: x["total_usage"], reverse=True)
        
        return {
            "tier_distribution": tier_distribution,
            "total_companies": total_companies,
            "active_companies": active_companies,
            "high_usage_companies": high_usage_companies[:5],  # Top 5
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system analytics: {str(e)}")


@router.get("/tier-configurations", response_model=List[Dict[str, Any]])
async def get_all_tier_configurations(
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Get all tier configurations for management (Boss Admin only)"""
    
    try:
        configurations = []
        cursor = db.tier_configurations.find({})
        
        async for config in cursor:
            # Clean up the configuration for response
            config["id"] = str(config.pop("_id"))
            configurations.append(config)
        
        return configurations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tier configurations: {str(e)}")


@router.put("/tier-configurations/{tier}", response_model=Dict[str, bool])
async def update_tier_configuration(
    tier: CompanyTier,
    configuration_update: Dict[str, Any] = Body(...),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Update entire tier configuration (Boss Admin only)"""
    
    try:
        # Update configuration in database
        result = await db.tier_configurations.update_one(
            {"tier": tier.value},
            {
                "$set": {
                    **configuration_update,
                    "updated_at": datetime.now(),
                    "updated_by": str(boss_admin.id)
                }
            }
        )
        
        if result.modified_count > 0:
            # Refresh tier manager's in-memory configs
            await tier_manager.initialize_tier_system(db)
            return {"success": True}
        else:
            return {"success": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tier configuration: {str(e)}")


@router.get("/companies-by-tier/{tier}")
async def get_companies_by_tier(
    tier: CompanyTier,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Get all companies in a specific tier (Boss Admin only)"""
    
    try:
        companies = []
        cursor = db.companies.find({"tier": tier.value}).skip(skip).limit(limit)
        
        async for company in cursor:
            # Get basic usage info
            usage_doc = await db.company_usage.find_one({"company_id": company["_id"]})
            total_usage = 0
            if usage_doc:
                total_usage = sum(entry.get("current_value", 0) for entry in usage_doc.get("usage_entries", []))
            
            companies.append({
                "id": company["_id"],
                "name": company.get("name"),
                "status": company.get("status"),
                "created_at": company.get("created_at"),
                "tier_upgraded_at": company.get("tier_upgraded_at"),
                "tier_expires_at": company.get("tier_expires_at"),
                "total_users": await db.users.count_documents({"company_id": company["_id"]}),
                "total_usage": total_usage
            })
        
        # Get total count for pagination
        total_count = await db.companies.count_documents({"tier": tier.value})
        
        return {
            "companies": companies,
            "total_count": total_count,
            "tier": tier.value,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching companies by tier: {str(e)}")


@router.get("/usage-trends", response_model=Dict[str, Any])
async def get_system_usage_trends(
    months: int = Query(6, ge=1, le=12),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Get system-wide usage trends over time (Boss Admin only)"""
    
    try:
        # Get historical usage data
        trends = {}
        
        # Get usage history for the last N months
        cursor = db.company_usage_history.find({}).sort("period", -1).limit(months * 50)  # Rough estimate
        
        async for record in cursor:
            period = record.get("period")
            if period not in trends:
                trends[period] = {
                    "chat_sessions": 0,
                    "analysis_reports": 0,
                    "companies_active": 0
                }
            
            # Aggregate usage data
            for entry in record.get("usage_entries", []):
                usage_key = entry.get("usage_key")
                value = entry.get("current_value", 0)
                
                if usage_key == "chat_sessions_per_month":
                    trends[period]["chat_sessions"] += value
                elif usage_key == "analysis_reports_per_month":
                    trends[period]["analysis_reports"] += value
            
            trends[period]["companies_active"] += 1
        
        # Sort trends by period
        sorted_trends = dict(sorted(trends.items(), reverse=True))
        
        return {
            "usage_trends": sorted_trends,
            "months_analyzed": len(sorted_trends),
            "generated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage trends: {str(e)}")


@router.post("/bulk-tier-update", response_model=Dict[str, Any])
async def bulk_tier_update(
    company_ids: List[UUID] = Body(...),
    new_tier: CompanyTier = Body(...),
    expires_at: Optional[datetime] = Body(None),
    reason: Optional[str] = Body(None),
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Update multiple companies to the same tier (Boss Admin only)"""
    
    try:
        successful_updates = 0
        failed_updates = []
        
        for company_id in company_ids:
            try:
                success = await tier_manager.upgrade_company_tier(
                    db=db,
                    company_id=company_id,
                    new_tier=new_tier,
                    upgraded_by=boss_admin.id,
                    expires_at=expires_at,
                    notes=reason
                )
                
                if success:
                    successful_updates += 1
                else:
                    failed_updates.append(str(company_id))
                    
            except Exception as e:
                failed_updates.append(f"{company_id}: {str(e)}")
        
        return {
            "success": True,
            "successful_updates": successful_updates,
            "failed_updates": failed_updates,
            "total_requested": len(company_ids),
            "new_tier": new_tier.value,
            "updated_by": str(boss_admin.id),
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing bulk tier update: {str(e)}")


@router.delete("/tier-configurations/{tier}/limits/{limit_key}")
async def remove_limit_from_tier(
    tier: CompanyTier,
    limit_key: str,
    db: Any = Depends(get_database),
    boss_admin: UserDB = Depends(get_boss_admin_user)
):
    """Remove a specific limit from a tier configuration (Boss Admin only)"""
    
    try:
        # Remove the limit from the tier configuration
        result = await db.tier_configurations.update_one(
            {"tier": tier.value},
            {
                "$pull": {"limits": {"limit_key": limit_key}},
                "$set": {
                    "updated_at": datetime.now(),
                    "updated_by": str(boss_admin.id)
                }
            }
        )
        
        if result.modified_count > 0:
            # Refresh tier manager's in-memory configs
            await tier_manager.initialize_tier_system(db)
            return {"success": True}
        else:
            return {"success": False, "message": "Limit not found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing limit from tier: {str(e)}")