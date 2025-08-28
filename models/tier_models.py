# models/tier_models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class CompanyTier(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional" 
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"  # For mother company


class LimitType(str, Enum):
    """Types of limits that can be applied"""
    CONTENT_CREATION = "content_creation"
    USAGE_CONSUMPTION = "usage_consumption"
    FEATURE_ACCESS = "feature_access"
    CHAT_SESSIONS = "chat_sessions"


class LimitPeriod(str, Enum):
    """Period for limit reset"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    LIFETIME = "lifetime"  # Never resets


class TierLimit(BaseModel):
    """Individual limit definition"""
    limit_key: str = Field(..., description="Unique key for this limit (e.g., 'max_courses', 'chat_sessions_per_month')")
    limit_name: str = Field(..., description="Human readable name")
    limit_type: LimitType = Field(..., description="Category of this limit")
    limit_value: int = Field(..., description="Limit value (-1 means unlimited)")
    reset_period: LimitPeriod = Field(default=LimitPeriod.MONTHLY, description="When this limit resets")
    description: Optional[str] = Field(None, description="Description of what this limit does")
    is_feature_flag: bool = Field(default=False, description="True if this is a boolean feature flag")


class TierConfiguration(BaseModel):
    """Complete tier configuration with all limits"""
    tier: CompanyTier
    tier_name: str
    tier_description: str
    limits: List[TierLimit] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[UUID] = None


class CompanyUsageEntry(BaseModel):
    """Individual usage entry"""
    usage_key: str = Field(..., description="Matches limit_key from TierLimit")
    current_value: int = Field(default=0, description="Current usage amount")
    period_start: datetime = Field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    last_reset: datetime = Field(default_factory=datetime.now)


class CompanyUsage(BaseModel):
    """Current usage tracking for a company"""
    company_id: UUID
    current_period: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m"))  # "2025-08"
    usage_entries: List[CompanyUsageEntry] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class UsageHistory(BaseModel):
    """Historical usage data"""
    company_id: UUID
    period: str  # "2025-07", "2025-06", etc.
    usage_entries: List[CompanyUsageEntry] = Field(default_factory=list)
    archived_at: datetime = Field(default_factory=datetime.now)


class LimitCheckResult(BaseModel):
    """Result of checking if action is allowed"""
    allowed: bool
    current_usage: int
    limit_value: int
    remaining: int
    limit_key: str
    limit_name: str
    reset_period: LimitPeriod
    next_reset: Optional[datetime] = None
    message: Optional[str] = None


class TierUpgradeRequest(BaseModel):
    """Request to upgrade company tier"""
    company_id: UUID
    new_tier: CompanyTier
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None  # For temporary upgrades


# ============================================
# DEFAULT TIER CONFIGURATIONS
# ============================================

DEFAULT_TIER_CONFIGS = {
    CompanyTier.BASIC: TierConfiguration(
        tier=CompanyTier.BASIC,
        tier_name="Basic Plan",
        tier_description="Perfect for small teams getting started with AI training",
        limits=[
            # Content Creation Limits
            TierLimit(
                limit_key="max_courses",
                limit_name="Maximum Courses",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=5,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of courses that can be created"
            ),
            TierLimit(
                limit_key="max_modules_per_course",
                limit_name="Maximum Modules per Course",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=10,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum modules allowed per course"
            ),
            TierLimit(
                limit_key="max_scenarios_per_module",
                limit_name="Maximum Scenarios per Module",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=5,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum scenarios allowed per module"
            ),
            TierLimit(
                limit_key="max_users",
                limit_name="Maximum Users",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=25,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of users in the company"
            ),
            
            # Chat-based Usage Limits (NEW APPROACH)
            TierLimit(
                limit_key="chat_sessions_per_month",
                limit_name="Chat Sessions per Month",
                limit_type=LimitType.CHAT_SESSIONS,
                limit_value=100,  # Total chats per company per month
                reset_period=LimitPeriod.MONTHLY,
                description="Total chat sessions (with TTS/STT) allowed per month for entire company"
            ),
            TierLimit(
                limit_key="analysis_reports_per_month",
                limit_name="Analysis Reports per Month",
                limit_type=LimitType.USAGE_CONSUMPTION,
                limit_value=50,
                reset_period=LimitPeriod.MONTHLY,
                description="Number of AI analysis reports that can be generated"
            ),
            
            # Feature Access (Boolean flags)
            TierLimit(
                limit_key="advanced_analytics",
                limit_name="Advanced Analytics",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,  # 0 = disabled, 1 = enabled
                reset_period=LimitPeriod.LIFETIME,
                description="Access to detailed analytics and insights",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="custom_avatars",
                limit_name="Custom Avatar Upload",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,
                reset_period=LimitPeriod.LIFETIME,
                description="Ability to upload and use custom avatars",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="knowledge_base",
                limit_name="Knowledge Base Integration",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,
                reset_period=LimitPeriod.LIFETIME,
                description="Advanced knowledge base and document integration",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="company_branding",
                limit_name="Company Branding",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,
                reset_period=LimitPeriod.LIFETIME,
                description="Custom branding and white-label options",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="api_access",
                limit_name="API Access",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,
                reset_period=LimitPeriod.LIFETIME,
                description="Access to REST API for integrations",
                is_feature_flag=True
            ),
        ]
    ),
    
    CompanyTier.PROFESSIONAL: TierConfiguration(
        tier=CompanyTier.PROFESSIONAL,
        tier_name="Professional Plan",
        tier_description="Ideal for growing companies with advanced training needs",
        limits=[
            # Content Creation Limits
            TierLimit(
                limit_key="max_courses",
                limit_name="Maximum Courses",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=25,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of courses that can be created"
            ),
            TierLimit(
                limit_key="max_modules_per_course",
                limit_name="Maximum Modules per Course",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=25,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum modules allowed per course"
            ),
            TierLimit(
                limit_key="max_scenarios_per_module",
                limit_name="Maximum Scenarios per Module",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=15,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum scenarios allowed per module"
            ),
            TierLimit(
                limit_key="max_users",
                limit_name="Maximum Users",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=100,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of users in the company"
            ),
            
            # Chat-based Usage Limits
            TierLimit(
                limit_key="chat_sessions_per_month",
                limit_name="Chat Sessions per Month",
                limit_type=LimitType.CHAT_SESSIONS,
                limit_value=500,  # More chats for professional tier
                reset_period=LimitPeriod.MONTHLY,
                description="Total chat sessions (with TTS/STT) allowed per month for entire company"
            ),
            TierLimit(
                limit_key="analysis_reports_per_month",
                limit_name="Analysis Reports per Month",
                limit_type=LimitType.USAGE_CONSUMPTION,
                limit_value=250,
                reset_period=LimitPeriod.MONTHLY,
                description="Number of AI analysis reports that can be generated"
            ),
            
            # Feature Access (Most enabled for Professional)
            TierLimit(
                limit_key="advanced_analytics",
                limit_name="Advanced Analytics",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,  # Enabled
                reset_period=LimitPeriod.LIFETIME,
                description="Access to detailed analytics and insights",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="custom_avatars",
                limit_name="Custom Avatar Upload",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,  # Enabled
                reset_period=LimitPeriod.LIFETIME,
                description="Ability to upload and use custom avatars",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="knowledge_base",
                limit_name="Knowledge Base Integration",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,  # Enabled
                reset_period=LimitPeriod.LIFETIME,
                description="Advanced knowledge base and document integration",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="company_branding",
                limit_name="Company Branding",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,  # Enabled
                reset_period=LimitPeriod.LIFETIME,
                description="Custom branding and white-label options",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="api_access",
                limit_name="API Access",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=0,  # Still disabled
                reset_period=LimitPeriod.LIFETIME,
                description="Access to REST API for integrations",
                is_feature_flag=True
            ),
        ]
    ),
    
    CompanyTier.ENTERPRISE: TierConfiguration(
        tier=CompanyTier.ENTERPRISE,
        tier_name="Enterprise Plan",
        tier_description="Full-featured solution for large organizations",
        limits=[
            # Content Creation Limits (Higher)
            TierLimit(
                limit_key="max_courses",
                limit_name="Maximum Courses",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=100,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of courses that can be created"
            ),
            TierLimit(
                limit_key="max_modules_per_course",
                limit_name="Maximum Modules per Course",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=50,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum modules allowed per course"
            ),
            TierLimit(
                limit_key="max_scenarios_per_module",
                limit_name="Maximum Scenarios per Module",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=30,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum scenarios allowed per module"
            ),
            TierLimit(
                limit_key="max_users",
                limit_name="Maximum Users",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=500,
                reset_period=LimitPeriod.LIFETIME,
                description="Maximum number of users in the company"
            ),
            
            # Chat-based Usage Limits (High)
            TierLimit(
                limit_key="chat_sessions_per_month",
                limit_name="Chat Sessions per Month",
                limit_type=LimitType.CHAT_SESSIONS,
                limit_value=2000,  # High volume for enterprise
                reset_period=LimitPeriod.MONTHLY,
                description="Total chat sessions (with TTS/STT) allowed per month for entire company"
            ),
            TierLimit(
                limit_key="analysis_reports_per_month",
                limit_name="Analysis Reports per Month",
                limit_type=LimitType.USAGE_CONSUMPTION,
                limit_value=1000,
                reset_period=LimitPeriod.MONTHLY,
                description="Number of AI analysis reports that can be generated"
            ),
            
            # Feature Access (All enabled)
            TierLimit(
                limit_key="advanced_analytics",
                limit_name="Advanced Analytics",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Access to detailed analytics and insights",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="custom_avatars",
                limit_name="Custom Avatar Upload",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Ability to upload and use custom avatars",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="knowledge_base",
                limit_name="Knowledge Base Integration",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Advanced knowledge base and document integration",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="company_branding",
                limit_name="Company Branding",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Custom branding and white-label options",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="api_access",
                limit_name="API Access",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,  # Now enabled for enterprise
                reset_period=LimitPeriod.LIFETIME,
                description="Access to REST API for integrations",
                is_feature_flag=True
            ),
        ]
    ),
    
    CompanyTier.UNLIMITED: TierConfiguration(
        tier=CompanyTier.UNLIMITED,
        tier_name="Unlimited (Mother Company)",
        tier_description="Unlimited access for mother company and system administration",
        limits=[
            # All limits set to -1 (unlimited)
            TierLimit(
                limit_key="max_courses",
                limit_name="Maximum Courses",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=-1,  # Unlimited
                reset_period=LimitPeriod.LIFETIME,
                description="Unlimited courses"
            ),
            TierLimit(
                limit_key="max_modules_per_course",
                limit_name="Maximum Modules per Course",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=-1,
                reset_period=LimitPeriod.LIFETIME,
                description="Unlimited modules per course"
            ),
            TierLimit(
                limit_key="max_scenarios_per_module",
                limit_name="Maximum Scenarios per Module",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=-1,
                reset_period=LimitPeriod.LIFETIME,
                description="Unlimited scenarios per module"
            ),
            TierLimit(
                limit_key="max_users",
                limit_name="Maximum Users",
                limit_type=LimitType.CONTENT_CREATION,
                limit_value=-1,
                reset_period=LimitPeriod.LIFETIME,
                description="Unlimited users"
            ),
            TierLimit(
                limit_key="chat_sessions_per_month",
                limit_name="Chat Sessions per Month",
                limit_type=LimitType.CHAT_SESSIONS,
                limit_value=-1,  # Unlimited
                reset_period=LimitPeriod.MONTHLY,
                description="Unlimited chat sessions"
            ),
            TierLimit(
                limit_key="analysis_reports_per_month",
                limit_name="Analysis Reports per Month",
                limit_type=LimitType.USAGE_CONSUMPTION,
                limit_value=-1,
                reset_period=LimitPeriod.MONTHLY,
                description="Unlimited analysis reports"
            ),
            
            # All features enabled
            TierLimit(
                limit_key="advanced_analytics",
                limit_name="Advanced Analytics",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Full analytics access",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="custom_avatars",
                limit_name="Custom Avatar Upload",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Custom avatar support",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="knowledge_base",
                limit_name="Knowledge Base Integration",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Full knowledge base access",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="company_branding",
                limit_name="Company Branding",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Full branding capabilities",
                is_feature_flag=True
            ),
            TierLimit(
                limit_key="api_access",
                limit_name="API Access",
                limit_type=LimitType.FEATURE_ACCESS,
                limit_value=1,
                reset_period=LimitPeriod.LIFETIME,
                description="Full API access",
                is_feature_flag=True
            ),
        ]
    )
}