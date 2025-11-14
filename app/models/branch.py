"""Branch data models"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import re

# ============================================================================
# Branch Models
# ============================================================================

class BranchBase(BaseModel):
    """Base branch model with common fields"""
    branch_id: str = Field(..., min_length=1, max_length=50, description="รหัสสาขา")
    branch_name: str = Field(..., min_length=2, max_length=200, description="ชื่อสาขา")
    address: Optional[str] = Field(None, max_length=500, description="ที่อยู่")
    province: Optional[str] = Field(None, max_length=100, description="จังหวัด")
    district: Optional[str] = Field(None, max_length=100, description="เขต/อำเภอ")
    postal_code: Optional[str] = Field(None, pattern="^[0-9]{5}$", description="รหัสไปรษณีย์ (5 หลัก)")
    phone: Optional[str] = Field(None, pattern="^[0-9\-\s\(\)]+$", description="เบอร์โทรศัพท์")
    status: str = Field(..., pattern="^(active|opening|closed)$", description="สถานะสาขา")
    dc_code: Optional[str] = Field(None, max_length=50, description="รหัส Distribution Center")
    opening_date: Optional[date] = Field(None, description="วันที่เปิดสาขา")

    @validator('branch_id')
    def validate_branch_id(cls, v):
        """Validate branch ID format"""
        # Allow alphanumeric and dash only
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError('Branch ID must contain only uppercase letters, numbers, and dashes')
        return v.strip()

    @validator('branch_name', 'address', 'province', 'district')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is not None:
            # Allow Thai, English, numbers, spaces, and common punctuation
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\.\,\/\(\)]+$'
            if not re.match(pattern, v):
                raise ValueError('Contains invalid characters')
            return v.strip()
        return v

    @validator('dc_code')
    def validate_dc_code(cls, v):
        """Validate DC code format"""
        if v is not None:
            # Allow alphanumeric only
            if not re.match(r'^[A-Z0-9]+$', v):
                raise ValueError('DC code must contain only uppercase letters and numbers')
            return v.strip()
        return v


class BranchCreate(BranchBase):
    """Model for creating new branch"""
    pass


class BranchUpdate(BaseModel):
    """Model for updating branch"""
    branch_name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    province: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, pattern="^[0-9]{5}$")
    phone: Optional[str] = Field(None, pattern="^[0-9\-\s\(\)]+$")
    status: Optional[str] = Field(None, pattern="^(active|opening|closed)$")
    dc_code: Optional[str] = Field(None, max_length=50)
    opening_date: Optional[date] = None

    @validator('branch_name', 'address', 'province', 'district')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is not None:
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\.\,\/\(\)]+$'
            if not re.match(pattern, v):
                raise ValueError('Contains invalid characters')
            return v.strip()
        return v

    @validator('dc_code')
    def validate_dc_code(cls, v):
        """Validate DC code format"""
        if v is not None:
            if not re.match(r'^[A-Z0-9]+$', v):
                raise ValueError('DC code must contain only uppercase letters and numbers')
            return v.strip()
        return v


class BranchResponse(BaseModel):
    """Branch response model"""
    branch_id: str
    branch_name: str
    address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    status: str
    dc_code: Optional[str] = None
    opening_date: Optional[str] = None  # ISO format date string
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class BranchDetailResponse(BranchResponse):
    """Detailed branch response with related data"""
    document_count: Optional[int] = 0
    has_ppp09: Optional[bool] = False


class BranchFilter(BaseModel):
    """Branch filter parameters"""
    search: Optional[str] = Field(None, max_length=100, description="Search by branch ID, name, or address")
    province: Optional[str] = Field(None, max_length=100, description="Filter by province")
    district: Optional[str] = Field(None, max_length=100, description="Filter by district")
    status: Optional[str] = Field(None, pattern="^(active|opening|closed)$", description="Filter by status")
    dc_code: Optional[str] = Field(None, max_length=50, description="Filter by DC code")
    sort: Optional[str] = Field("created_at", description="Sort field")
    order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @validator('search')
    def sanitize_search(cls, v):
        """Sanitize search query"""
        if v is not None:
            # Remove special characters that could cause SQL injection
            v = re.sub(r'[^\w\s\-\.ก-๙]', '', v)
            return v.strip()
        return v


# ============================================================================
# Branch Statistics Models
# ============================================================================

class BranchStats(BaseModel):
    """Branch statistics"""
    total_branches: int = 0
    active_branches: int = 0
    opening_branches: int = 0
    closed_branches: int = 0
    branches_by_province: List[dict] = []
    branches_by_dc: List[dict] = []


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_branch_status(status: str) -> bool:
    """Validate branch status"""
    return status in ['active', 'opening', 'closed']


def validate_postal_code(postal_code: str) -> bool:
    """Validate Thai postal code (5 digits)"""
    return bool(re.match(r'^[0-9]{5}$', postal_code))


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's all digits and reasonable length (9-10 digits for Thai numbers)
    return bool(re.match(r'^[0-9]{9,10}$', cleaned))
