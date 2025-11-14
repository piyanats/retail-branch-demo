"""Legal PPP09 (ภ.พ.09) data models

ภ.พ.09 = แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
import re

# ============================================================================
# PPP09 Models
# ============================================================================

class PPP09Base(BaseModel):
    """Base PPP09 model"""
    branch_id: str = Field(..., min_length=1, max_length=50, description="รหัสสาขา")
    ppp09_number: Optional[str] = Field(None, max_length=100, description="เลขที่ ภ.พ.09")
    issue_date: Optional[date] = Field(None, description="วันที่ออกเอกสาร")
    expiry_date: Optional[date] = Field(None, description="วันหมดอายุ")
    owner_name: Optional[str] = Field(None, max_length=200, description="ชื่อเจ้าของ/ผู้เสียภาษี")

    # Address fields
    address_number: Optional[str] = Field(None, max_length=50, description="บ้านเลขที่")
    address_moo: Optional[str] = Field(None, max_length=20, description="หมู่ที่")
    address_trok: Optional[str] = Field(None, max_length=100, description="ตรอก")
    address_soi: Optional[str] = Field(None, max_length=100, description="ซอย")
    address_road: Optional[str] = Field(None, max_length=100, description="ถนน")
    address_tambon: Optional[str] = Field(None, max_length=100, description="ตำบล/แขวง")
    address_amphoe: Optional[str] = Field(None, max_length=100, description="อำเภอ/เขต")
    address_province: Optional[str] = Field(None, max_length=100, description="จังหวัด")
    address_postal_code: Optional[str] = Field(None, pattern="^[0-9]{5}$", description="รหัสไปรษณีย์")

    # Land area
    land_area_rai: Optional[float] = Field(None, ge=0, description="เนื้อที่ดิน (ไร่)")
    land_area_ngan: Optional[float] = Field(None, ge=0, le=4, description="เนื้อที่ดิน (งาน)")
    land_area_wa: Optional[float] = Field(None, ge=0, le=100, description="เนื้อที่ดิน (ตารางวา)")
    building_area_sqm: Optional[float] = Field(None, ge=0, description="พื้นที่สิ่งปลูกสร้าง (ตร.ม.)")

    # Tax information
    annual_tax_amount: Optional[float] = Field(None, ge=0, description="จำนวนเงินภาษีต่อปี (บาท)")
    payment_status: Optional[str] = Field(None, pattern="^(paid|unpaid|overdue)$", description="สถานะการชำระ")

    # Remarks
    remarks: Optional[str] = Field(None, max_length=1000, description="หมายเหตุ")

    @validator('branch_id')
    def validate_branch_id(cls, v):
        """Validate branch ID format"""
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError('Branch ID must contain only uppercase letters, numbers, and dashes')
        return v.strip()

    @validator('owner_name', 'address_number', 'address_trok', 'address_soi',
               'address_road', 'address_tambon', 'address_amphoe', 'address_province')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is not None:
            # Allow Thai, English, numbers, spaces, and common punctuation
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\.\,\/]+$'
            if not re.match(pattern, v):
                raise ValueError('Contains invalid characters')
            return v.strip()
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        """Validate expiry date is after issue date"""
        if v is not None and 'issue_date' in values and values['issue_date'] is not None:
            if v <= values['issue_date']:
                raise ValueError('Expiry date must be after issue date')
        return v


class PPP09Create(PPP09Base):
    """Model for creating new PPP09"""
    pass


class PPP09Update(BaseModel):
    """Model for updating PPP09"""
    ppp09_number: Optional[str] = Field(None, max_length=100)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    owner_name: Optional[str] = Field(None, max_length=200)

    # Address
    address_number: Optional[str] = Field(None, max_length=50)
    address_moo: Optional[str] = Field(None, max_length=20)
    address_trok: Optional[str] = Field(None, max_length=100)
    address_soi: Optional[str] = Field(None, max_length=100)
    address_road: Optional[str] = Field(None, max_length=100)
    address_tambon: Optional[str] = Field(None, max_length=100)
    address_amphoe: Optional[str] = Field(None, max_length=100)
    address_province: Optional[str] = Field(None, max_length=100)
    address_postal_code: Optional[str] = Field(None, pattern="^[0-9]{5}$")

    # Land area
    land_area_rai: Optional[float] = Field(None, ge=0)
    land_area_ngan: Optional[float] = Field(None, ge=0, le=4)
    land_area_wa: Optional[float] = Field(None, ge=0, le=100)
    building_area_sqm: Optional[float] = Field(None, ge=0)

    # Tax
    annual_tax_amount: Optional[float] = Field(None, ge=0)
    payment_status: Optional[str] = Field(None, pattern="^(paid|unpaid|overdue)$")

    # Remarks
    remarks: Optional[str] = Field(None, max_length=1000)

    @validator('owner_name', 'address_number', 'address_trok', 'address_soi',
               'address_road', 'address_tambon', 'address_amphoe', 'address_province')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is not None:
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\.\,\/]+$'
            if not re.match(pattern, v):
                raise ValueError('Contains invalid characters')
            return v.strip()
        return v


class PPP09Response(BaseModel):
    """PPP09 response model"""
    ppp09_id: str
    branch_id: str
    ppp09_number: Optional[str] = None
    issue_date: Optional[str] = None  # ISO format date string
    expiry_date: Optional[str] = None  # ISO format date string
    owner_name: Optional[str] = None

    # Address
    address_number: Optional[str] = None
    address_moo: Optional[str] = None
    address_trok: Optional[str] = None
    address_soi: Optional[str] = None
    address_road: Optional[str] = None
    address_tambon: Optional[str] = None
    address_amphoe: Optional[str] = None
    address_province: Optional[str] = None
    address_postal_code: Optional[str] = None

    # Land area
    land_area_rai: Optional[float] = None
    land_area_ngan: Optional[float] = None
    land_area_wa: Optional[float] = None
    building_area_sqm: Optional[float] = None

    # Tax
    annual_tax_amount: Optional[float] = None
    payment_status: Optional[str] = None

    # PDF
    pdf_file_path: Optional[str] = None
    pdf_file_size: Optional[int] = None
    pdf_uploaded_at: Optional[str] = None
    pdf_uploaded_by: Optional[str] = None

    # Remarks
    remarks: Optional[str] = None

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class PPP09Filter(BaseModel):
    """PPP09 filter parameters"""
    branch_id: Optional[str] = Field(None, max_length=50, description="Filter by branch ID")
    province: Optional[str] = Field(None, max_length=100, description="Filter by province")
    payment_status: Optional[str] = Field(None, pattern="^(paid|unpaid|overdue)$", description="Filter by payment status")
    expiring_soon: Optional[bool] = Field(None, description="Filter by expiring soon (within 90 days)")
    search: Optional[str] = Field(None, max_length=100, description="Search by PPP09 number or owner name")
    sort: Optional[str] = Field("created_at", description="Sort field")
    order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @validator('search')
    def sanitize_search(cls, v):
        """Sanitize search query"""
        if v is not None:
            v = re.sub(r'[^\w\s\-\.ก-๙]', '', v)
            return v.strip()
        return v


class PPP09PDFUpload(BaseModel):
    """PPP09 PDF upload metadata"""
    ppp09_id: str
    file_path: str
    file_size: int
    mime_type: str = 'application/pdf'


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_payment_status(status: str) -> bool:
    """Validate payment status"""
    return status in ['paid', 'unpaid', 'overdue']


def calculate_total_land_area_sqm(rai: float = 0, ngan: float = 0, wa: float = 0) -> float:
    """
    Calculate total land area in square meters

    1 ไร่ = 1600 ตร.ม.
    1 งาน = 400 ตร.ม.
    1 ตารางวา = 4 ตร.ม.
    """
    return (rai * 1600) + (ngan * 400) + (wa * 4)


def format_land_area(rai: float = 0, ngan: float = 0, wa: float = 0) -> str:
    """Format land area as Thai format (X ไร่ Y งาน Z ตารางวา)"""
    parts = []
    if rai > 0:
        parts.append(f"{rai} ไร่")
    if ngan > 0:
        parts.append(f"{ngan} งาน")
    if wa > 0:
        parts.append(f"{wa} ตารางวา")
    return " ".join(parts) if parts else "0 ตารางวา"


def is_expiring_soon(expiry_date: date, days: int = 90) -> bool:
    """Check if PPP09 is expiring within specified days"""
    if expiry_date is None:
        return False
    from datetime import datetime, timedelta
    today = datetime.now().date()
    threshold = today + timedelta(days=days)
    return today <= expiry_date <= threshold


def is_expired(expiry_date: date) -> bool:
    """Check if PPP09 is expired"""
    if expiry_date is None:
        return False
    from datetime import datetime
    today = datetime.now().date()
    return expiry_date < today
