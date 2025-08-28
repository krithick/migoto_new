# core/tier_management.py

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from models.tier_models import (
    CompanyTier, TierConfiguration, CompanyUsage, CompanyUsageEntry, 
    LimitCheckResult, DEFAULT_TIER_CONFIGS, LimitPeriod, TierLimit
)
from models.company_models import CompanyDB
from models.user_models import UserDB, UserRole
from rich.console import Console
console = Console()

class TierManager:
    """Service for managing company tiers, limits, and usage"""
    
    def __init__(self):
        self.tier_configs = DEFAULT_TIER_CONFIGS.copy()
    
    async def initialize_tier_system(self, db: Any):
        """Initialize tier system in database"""
        try:
            # Create tier_configurations collection with default configs
            for tier, config in DEFAULT_TIER_CONFIGS.items():
                existing = await db.tier_configurations.find_one({"tier": tier.value})
                if not existing:
                    config_dict = config.dict()
                    await db.tier_configurations.insert_one(config_dict)
                    print(f"✅ Created tier configuration: {tier.value}")
            
            # Initialize usage tracking for existing companies
            await self._initialize_usage_tracking(db)
            print("✅ Tier system initialization complete")
            
        except Exception as e:
            print(f"❌ Error initializing tier system: {e}")
            raise
    
    async def _initialize_usage_tracking(self, db: Any):
        """Initialize usage tracking for all existing companies"""
        companies = []
        cursor = db.companies.find({})
        async for company in cursor:
            # Check if usage tracking already exists
            existing_usage = await db.company_usage.find_one({"company_id": company["_id"]})
            if not existing_usage:
                # Create initial usage tracking
                usage = CompanyUsage(
                    company_id=UUID(company["_id"]),
                    current_period=datetime.now().strftime("%Y-%m"),
                    usage_entries=[],
                    last_updated=datetime.now()
                )
                
                usage_dict = usage.dict()
                usage_dict["company_id"] = str(usage_dict["company_id"])
                await db.company_usage.insert_one(usage_dict)
    
    # ==========================================
    # LIMIT CHECKING METHODS
    # ==========================================
    
    async def can_create_course(self, db: Any, company_id: UUID) -> LimitCheckResult:
        """Check if company can create another course"""
        test=await self._check_limit(db, company_id, "max_courses")
        print("test",test)
        console.print(f"[red]test{test}[/red]")
        return test
    
    async def can_create_module(self, db: Any, company_id: UUID, course_id: UUID) -> LimitCheckResult:
        """Check if company can create another module in a course - FIXED"""
        limit_result = await self._check_limit(db, company_id, "max_modules_per_course")
    
        if limit_result.limit_value != -1:  # If not unlimited
            # 🔥 FIX: Count modules that belong to this course
            # Your modules collection should have a reference to the course
            current_modules = 0
        
            # Check if modules reference courses directly
            try:
                current_modules = await db.modules.count_documents({
                "course_id": str(course_id),  # If modules have course_id field
                "is_archived": {"$ne": True}
                })
            except:
                # Alternative: Check if course has modules array
                course = await db.courses.find_one({"_id": str(course_id)})
                if course and "modules" in course:
                    # Count non-archived modules in the modules array
                    module_ids = course.get("modules", [])
                    current_modules = await db.modules.count_documents({
                    "_id": {"$in": [str(mid) for mid in module_ids]},
                    "is_archived": {"$ne": True}
                    })
        
            limit_result.current_usage = current_modules
            limit_result.remaining = max(0, limit_result.limit_value - current_modules)
            limit_result.allowed = current_modules < limit_result.limit_value
        
            if not limit_result.allowed:
                limit_result.message = f"Module limit reached for this course: {current_modules}/{limit_result.limit_value}"
            else:
                limit_result.message = f"Can add {limit_result.remaining} more modules to this course"
    
        return limit_result
    
    async def can_create_scenario(self, db: Any, company_id: UUID, module_id: UUID) -> LimitCheckResult:
        """Check if company can create another scenario in a module - FIXED"""
        limit_result = await self._check_limit(db, company_id, "max_scenarios_per_module")
    
        if limit_result.limit_value != -1:  # If not unlimited
            # 🔥 FIX: Count scenarios that belong to this module
            current_scenarios = 0
        
            try:
                current_scenarios = await db.scenarios.count_documents({
                "module_id": str(module_id),  # If scenarios have module_id field
                "is_archived": {"$ne": True}
                })
            except:
                # Alternative: Check if module has scenarios array
                module = await db.modules.find_one({"_id": str(module_id)})
                if module and "scenarios" in module:
                    scenario_ids = module.get("scenarios", [])
                    current_scenarios = await db.scenarios.count_documents({
                    "_id": {"$in": [str(sid) for sid in scenario_ids]},
                    "is_archived": {"$ne": True}
                    })
        
            limit_result.current_usage = current_scenarios
            limit_result.remaining = max(0, limit_result.limit_value - current_scenarios)
            limit_result.allowed = current_scenarios < limit_result.limit_value
        
            if not limit_result.allowed:
                limit_result.message = f"Scenario limit reached for this module: {current_scenarios}/{limit_result.limit_value}"
            else:
                limit_result.message = f"Can add {limit_result.remaining} more scenarios to this module"
    
        return limit_result
    async def can_create_user(self, db: Any, company_id: UUID) -> LimitCheckResult:
        """Check if company can create another user"""
        current_users = await db.users.count_documents({"company_id": str(company_id)})
        limit_result = await self._check_limit(db, company_id, "max_users")
        
        if limit_result.limit_value != -1:  # If not unlimited
            limit_result.current_usage = current_users
            limit_result.remaining = max(0, limit_result.limit_value - current_users)
            limit_result.allowed = current_users < limit_result.limit_value
        
        return limit_result
    
    async def can_start_chat_session(self, db: Any, company_id: UUID) -> LimitCheckResult:
        """Check if company can start another chat session (for TTS/STT)"""
        return await self._check_usage_limit(db, company_id, "chat_sessions_per_month")
    
    async def can_generate_analysis(self, db: Any, company_id: UUID) -> LimitCheckResult:
        """Check if company can generate another analysis report"""
        return await self._check_usage_limit(db, company_id, "analysis_reports_per_month")
    
    async def has_feature_access(self, db: Any, company_id: UUID, feature_key: str) -> bool:
        """Check if company has access to a specific feature"""
        try:
            limit_result = await self._check_limit(db, company_id, feature_key)
            return limit_result.limit_value == 1  # Features are boolean (0 or 1)
        except:
            return False
    
    # ==========================================
    # USAGE TRACKING METHODS
    # ==========================================
    
    async def track_chat_session(self, db: Any, company_id: UUID, session_count: int = 1):
        """Track chat session usage"""
        await self._increment_usage(db, company_id, "chat_sessions_per_month", session_count)
    
    async def track_analysis_generation(self, db: Any, company_id: UUID, report_count: int = 1):
        """Track analysis report generation"""
        await self._increment_usage(db, company_id, "analysis_reports_per_month", report_count)
    
    async def reset_monthly_usage(self, db: Any, company_id: Optional[UUID] = None):
        """Reset monthly usage counters - FIXED"""
        try:
            current_period = datetime.now().strftime("%Y-%m")
        
            if company_id:
                # Reset for specific company
                await self._reset_company_usage(db, company_id, current_period)
            else:
                # Reset for all companies
                cursor = db.companies.find({})
                async for company in cursor:
                    await self._reset_company_usage(db, UUID(company["_id"]), current_period)
        
            console.print(f"[green]✅ Monthly usage reset completed for period {current_period}[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ Error resetting monthly usage: {e}[/red]")
            raise
    
    # ==========================================
    # TIER MANAGEMENT METHODS
    # ==========================================
    
    async def upgrade_company_tier(
        self, 
        db: Any, 
        company_id: UUID, 
        new_tier: CompanyTier, 
        upgraded_by: UUID,
        expires_at: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Upgrade company to new tier"""
        try:
            # Validate new tier exists
            if new_tier not in DEFAULT_TIER_CONFIGS:
                raise ValueError(f"Invalid tier: {new_tier}")
            
            # Update company record
            update_data = {
                "tier": new_tier.value,
                "tier_upgraded_by": str(upgraded_by),
                "tier_upgraded_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            if expires_at:
                update_data["tier_expires_at"] = expires_at
            if notes:
                update_data["tier_notes"] = notes
            
            result = await db.companies.update_one(
                {"_id": str(company_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Upgraded company {company_id} to {new_tier.value}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error upgrading company tier: {e}")
            return False
    
    async def get_company_limits_and_usage(self, db: Any, company_id: UUID) -> Dict[str, Any]:
        """Get complete limits and usage info for a company - FIXED"""
        try:
            # Get company info
            company = await db.companies.find_one({"_id": str(company_id)})
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
        
            tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
            tier_config = self.tier_configs[tier]
        
            # Get current usage
            usage_doc = await db.company_usage.find_one({"company_id": str(company_id)})
            current_usage = {}
            if usage_doc:
                for entry in usage_doc.get("usage_entries", []):
                    current_usage[entry["usage_key"]] = entry["current_value"]
        
            # Build response
            limits_info = []
            usage_info = []
            warnings = []
        
            for limit in tier_config.limits:
                limit_info = {
                "limit_key": limit.limit_key,
                "limit_name": limit.limit_name,
                "limit_type": limit.limit_type.value,
                "limit_value": limit.limit_value,
                "reset_period": limit.reset_period.value,
                "description": limit.description,
                "is_feature_flag": limit.is_feature_flag
                }
                limits_info.append(limit_info)
            
                # Get current usage for this limit
                current_value = current_usage.get(limit.limit_key, 0)
            
                # 🔥 FIX: Get real counts for content limits
                if limit.limit_key == "max_courses":
                    current_value = await db.courses.count_documents({
                    "company_id": str(company_id),
                    "is_archived": {"$ne": True}
                    })
                elif limit.limit_key == "max_users":
                    current_value = await db.users.count_documents({"company_id": str(company_id)})
                elif limit.limit_key == "max_modules_per_course":
                    # This is per-course, so show total modules for this company
                    current_value = await db.modules.count_documents({
                    "company_id": str(company_id),
                    "is_archived": {"$ne": True}
                    })
                elif limit.limit_key == "max_scenarios_per_module":
                    # This is per-module, so show total scenarios for this company
                    current_value = await db.scenarios.count_documents({
                    "company_id": str(company_id),
                    "is_archived": {"$ne": True}
                    })
            
                usage_entry = {
                "usage_key": limit.limit_key,
                "current_value": current_value,
                "limit_value": limit.limit_value,
                "remaining": max(0, limit.limit_value - current_value) if limit.limit_value != -1 else -1,
                "percentage_used": (current_value / limit.limit_value * 100) if limit.limit_value > 0 else 0
                }
                usage_info.append(usage_entry)
            
                # Generate warnings for high usage
                if limit.limit_value > 0 and current_value / limit.limit_value >= 0.8:
                    warnings.append(f"{limit.limit_name}: {current_value}/{limit.limit_value} (80%+ used)")
        
            return {
            "company_id": str(company_id),
            "company_name": company.get("name", "Unknown"),
            "tier": tier.value,
            "tier_expires_at": company.get("tier_expires_at"),
            "limits": limits_info,
            "usage": usage_info,
            "warnings": warnings,
            "next_monthly_reset": self._get_next_reset_date(LimitPeriod.MONTHLY),
            "generated_at": datetime.now()
            }
        
        except Exception as e:
            console.print(f"[red]❌ Error getting company limits: {e}[/red]")
            raise HTTPException(status_code=500, detail=str(e))
    # ==========================================
    # FLEXIBLE TIER CONFIGURATION
    # ==========================================
    
    async def add_custom_limit(
        self, 
        db: Any, 
        tier: CompanyTier, 
        limit: TierLimit,
        updated_by: UUID
    ) -> bool:
        """Add a new custom limit to a tier (for flexible pricing)"""
        try:
            # Update tier configuration in database
            result = await db.tier_configurations.update_one(
                {"tier": tier.value},
                {
                    "$push": {"limits": limit.dict()},
                    "$set": {
                        "updated_at": datetime.now(),
                        "updated_by": str(updated_by)
                    }
                }
            )
            
            if result.modified_count > 0:
                # Update in-memory config
                if tier in self.tier_configs:
                    self.tier_configs[tier].limits.append(limit)
                print(f"✅ Added custom limit '{limit.limit_key}' to tier {tier.value}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error adding custom limit: {e}")
            return False
    
    async def update_limit_value(
        self, 
        db: Any, 
        tier: CompanyTier, 
        limit_key: str, 
        new_value: int,
        updated_by: UUID
    ) -> bool:
        """Update the value of an existing limit"""
        try:
            result = await db.tier_configurations.update_one(
                {"tier": tier.value, "limits.limit_key": limit_key},
                {
                    "$set": {
                        "limits.$.limit_value": new_value,
                        "updated_at": datetime.now(),
                        "updated_by": str(updated_by)
                    }
                }
            )
            
            if result.modified_count > 0:
                # Update in-memory config
                if tier in self.tier_configs:
                    for limit in self.tier_configs[tier].limits:
                        if limit.limit_key == limit_key:
                            limit.limit_value = new_value
                            break
                print(f"✅ Updated limit '{limit_key}' to {new_value} for tier {tier.value}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error updating limit value: {e}")
            return False
    
    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================
    
    async def _check_limit(self, db: Any, company_id: UUID, limit_key: str) -> LimitCheckResult:
        """Check a specific limit for a company - FIXED VERSION"""
        try:
            # Get company tier
            company = await db.companies.find_one({"_id": str(company_id)})
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
        
            tier = CompanyTier(company.get("tier", CompanyTier.BASIC))
            tier_config = self.tier_configs[tier]
        
            # Find the specific limit
            target_limit = None
            for limit in tier_config.limits:
                if limit.limit_key == limit_key:
                    target_limit = limit
                    break
        
            if not target_limit:
                return LimitCheckResult(
                allowed=True,
                current_usage=0,
                limit_value=-1,
                remaining=-1,
                limit_key=limit_key,
                limit_name=limit_key.replace("_", " ").title(),
                reset_period=LimitPeriod.LIFETIME,
                message="No limit defined (unlimited)"
                )
        
            if target_limit.limit_value == -1:
                return LimitCheckResult(
                allowed=True,
                current_usage=0,
                limit_value=-1,
                remaining=-1,
                limit_key=limit_key,
                limit_name=target_limit.limit_name,
                reset_period=target_limit.reset_period,
                message="Unlimited"
            )
        
            if target_limit.is_feature_flag:
                return LimitCheckResult(
                allowed=target_limit.limit_value == 1,
                current_usage=0,
                limit_value=target_limit.limit_value,
                remaining=0,
                limit_key=limit_key,
                limit_name=target_limit.limit_name,
                reset_period=target_limit.reset_period,
                message="Feature enabled" if target_limit.limit_value == 1 else "Feature disabled"
            )
        
            # 🔥 FIX: Calculate actual current usage
            current_usage = 0
        
            if limit_key == "max_courses":
                current_usage = await db.courses.count_documents({
                "company_id": str(company_id),
                "is_archived": {"$ne": True}  # 🔥 FIXED: Use your actual field name
                })
            
            elif limit_key == "max_users":
                current_usage = await db.users.count_documents({
                "company_id": str(company_id)
                # 🔥 REMOVED: is_active check since you might not have this field
            })
            
            elif limit_key in ["chat_sessions_per_month", "analysis_reports_per_month"]:
                # Get from usage tracking
                usage_doc = await db.company_usage.find_one({"company_id": str(company_id)})
                if usage_doc:
                    for entry in usage_doc.get("usage_entries", []):
                        if entry["usage_key"] == limit_key:
                            current_usage = entry["current_value"]
                            break
        
            # Calculate remaining and allowed status
            remaining = max(0, target_limit.limit_value - current_usage)
            allowed = current_usage < target_limit.limit_value
        
            message = f"Limit reached: {current_usage}/{target_limit.limit_value}" if not allowed else f"Available: {remaining} remaining"
        
            return LimitCheckResult(
                allowed=allowed,
                current_usage=current_usage,
                limit_value=target_limit.limit_value,
                remaining=remaining,
                limit_key=limit_key,
                limit_name=target_limit.limit_name,
                reset_period=target_limit.reset_period,
                next_reset=self._get_next_reset_date(target_limit.reset_period),
                message=message
            )
        
        except Exception as e:
            console.print(f"[red]❌ Error checking limit: {e}[/red]")
            raise HTTPException(status_code=500, detail=f"Error checking limit: {str(e)}")
    
    async def _check_usage_limit(self, db: Any, company_id: UUID, usage_key: str) -> LimitCheckResult:
        """Check usage-based limits (monthly, etc.)"""
        try:
            # Get the limit definition
            limit_result = await self._check_limit(db, company_id, usage_key)
            
            if limit_result.limit_value == -1:  # Unlimited
                return limit_result
            
            # Get current usage
            usage_doc = await db.company_usage.find_one({"company_id": str(company_id)})
            current_usage = 0
            
            if usage_doc:
                for entry in usage_doc.get("usage_entries", []):
                    if entry["usage_key"] == usage_key:
                        current_usage = entry["current_value"]
                        break
            
            # Check if we've hit the limit
            remaining = max(0, limit_result.limit_value - current_usage)
            allowed = current_usage < limit_result.limit_value
            
            limit_result.current_usage = current_usage
            limit_result.remaining = remaining
            limit_result.allowed = allowed
            
            if not allowed:
                limit_result.message = f"Limit exceeded: {current_usage}/{limit_result.limit_value}"
            else:
                limit_result.message = f"Available: {remaining} remaining"
            
            return limit_result
            
        except Exception as e:
            print(f"❌ Error checking usage limit: {e}")
            raise
    
    async def _increment_usage(self, db: Any, company_id: UUID, usage_key: str, amount: int = 1):
        """Increment usage counter - FIXED VERSION"""
        try:
            current_period = datetime.now().strftime("%Y-%m")
        
            # Ensure usage document exists
            await db.company_usage.update_one(
                {"company_id": str(company_id)},
                {
                    "$setOnInsert": {
                    "company_id": str(company_id),
                    "current_period": current_period,
                    "usage_entries": [],
                    "last_updated": datetime.now()
                    }
                },
                upsert=True
            )
        
            # Check if usage entry exists for this key
            usage_doc = await db.company_usage.find_one({
            "company_id": str(company_id),
            "usage_entries.usage_key": usage_key
            })
        
            if usage_doc:
                # Update existing entry
                await db.company_usage.update_one(
                    {
                    "company_id": str(company_id),
                    "usage_entries.usage_key": usage_key
                    },
                    {
                    "$inc": {"usage_entries.$.current_value": amount},
                    "$set": {"last_updated": datetime.now()}
                    }
                )
            else:
                # Create new usage entry
                new_entry = {
                "usage_key": usage_key,
                "current_value": amount,
                "period_start": datetime.now().replace(day=1),  # Start of month
                "last_reset": datetime.now().replace(day=1)
                }
            
                await db.company_usage.update_one(
                {"company_id": str(company_id)},
                {
                    "$push": {"usage_entries": new_entry},
                    "$set": {"last_updated": datetime.now()}
                }
                )
        
            console.print(f"[green]✅ Tracked {amount} {usage_key} for company {company_id}[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ Error incrementing usage: {e}[/red]")
            raise
    
    async def _reset_company_usage(self, db: Any, company_id: UUID, new_period: str):
        """Reset usage counters for a company - FIXED"""
        try:
            # Archive current usage to history
            current_usage = await db.company_usage.find_one({"company_id": str(company_id)})
            if current_usage and current_usage.get("usage_entries"):
                # Create history record
                history_record = {
                "company_id": str(company_id),
                "period": current_usage.get("current_period", "unknown"),
                "usage_entries": current_usage["usage_entries"],
                "archived_at": datetime.now()
                }
                await db.company_usage_history.insert_one(history_record)
        
            # Reset current usage
            await db.company_usage.update_one(
                {"company_id": str(company_id)},
                {
                    "$set": {
                    "current_period": new_period,
                    "usage_entries": [],
                    "last_updated": datetime.now()
                    }
                }
            )
        
        except Exception as e:
            console.print(f"[red]❌ Error resetting company usage: {e}[/red]")
            raise

    
    def _get_next_reset_date(self, period: LimitPeriod) -> Optional[datetime]:
        """Calculate next reset date based on period"""
        now = datetime.now()
        
        if period == LimitPeriod.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == LimitPeriod.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        elif period == LimitPeriod.MONTHLY:
            if now.month == 12:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, now.month + 1, 1)
        elif period == LimitPeriod.ANNUALLY:
            return datetime(now.year + 1, 1, 1)
        else:
            return None  # LIFETIME never resets


# Global instance
tier_manager = TierManager()