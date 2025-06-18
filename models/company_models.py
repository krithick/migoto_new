# models/company_models.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DEMO = "demo"


class CompanyType(str, Enum):
    CLIENT = "client"           # Regular client company
    SUBSIDIARY = "subsidiary"   # Subsidiary of mother company
    MOTHER = "mother"          # Mother company (has boss admin)


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    company_type: CompanyType = CompanyType.CLIENT
    parent_company_id: Optional[UUID] = None  # For subsidiaries
    status: CompanyStatus = CompanyStatus.ACTIVE
    
    @validator('parent_company_id')
    def validate_parent_company(cls, v, values):
        if values.get('company_type') == CompanyType.SUBSIDIARY and not v:
            raise ValueError("Subsidiary companies must have a parent company")
        if values.get('company_type') != CompanyType.SUBSIDIARY and v:
            raise ValueError("Only subsidiary companies can have a parent company")
        return v


class CompanyDB(CompanyBase):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    company_type: CompanyType
    parent_company_id: Optional[UUID] = None
    status: CompanyStatus = CompanyStatus.ACTIVE
    
    # Tracking fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[UUID] = None  # Boss admin who created this company
    
    # Statistics (can be calculated or cached)
    # total_users: int = 0
    # total_admins: int = 0
    # total_superadmins: int = 0
    # total_courses: int = 0
    # total_modules: int = 0
    # total_scenarios: int = 0
    
    # Demo settings (if applicable)
    demo_expires_at: Optional[datetime] = None
    demo_features_enabled: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


class CompanyResponse(CompanyBase):
    id: UUID
    company_type: CompanyType
    parent_company_id: Optional[UUID] = None
    status: CompanyStatus
    created_at: datetime
    updated_at: datetime
    # Add calculated fields
    total_users: int = 0
    total_admins: int = 0
    total_superadmins: int = 0
    total_courses: int = 0
    total_modules: int = 0
    total_scenarios: int = 0
    demo_expires_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {UUID: lambda v: str(v)}

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    status: Optional[CompanyStatus] = None


class CompanyAnalytics(BaseModel):
    """Analytics data for a company"""
    company_id: UUID
    company_name: str
    
    # User statistics
    user_stats: Dict[str, int] = Field(default_factory=dict)
    
    # Course progress statistics
    course_completion_stats: Dict[str, Any] = Field(default_factory=dict)
    
    # Usage statistics
    usage_stats: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Date range for the analytics
    analytics_period: Dict[str, datetime] = Field(default_factory=dict)
    
    # Last updated
    last_updated: datetime = Field(default_factory=datetime.now)