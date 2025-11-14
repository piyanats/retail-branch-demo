"""Document data models"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# ============================================================================
# Document Models
# ============================================================================

class DocumentBase(BaseModel):
    """Base document model"""
    branch_id: str = Field(..., min_length=1, max_length=50, description="รหัสสาขา")
    document_type: str = Field(..., max_length=100, description="ประเภทเอกสาร")
    document_name: str = Field(..., min_length=1, max_length=500, description="ชื่อเอกสาร")
    team: str = Field(..., pattern="^(new_branch|legal|srd|scm)$", description="ทีมที่รับผิดชอบ")

    @validator('branch_id')
    def validate_branch_id(cls, v):
        """Validate branch ID format"""
        if not re.match(r'^[A-Z0-9\-]+$', v):
            raise ValueError('Branch ID must contain only uppercase letters, numbers, and dashes')
        return v.strip()

    @validator('document_name')
    def sanitize_document_name(cls, v):
        """Sanitize document name"""
        # Allow Thai, English, numbers, spaces, and common punctuation
        pattern = r'^[a-zA-Z0-9ก-๙\s\-\_\.]+$'
        if not re.match(pattern, v):
            raise ValueError('Document name contains invalid characters')
        return v.strip()


class DocumentCreate(DocumentBase):
    """Model for document metadata (before file upload)"""
    pass


class DocumentUpload(BaseModel):
    """Model for file upload response"""
    document_id: str
    file_path: str
    file_size: int
    mime_type: str


class DocumentUpdate(BaseModel):
    """Model for updating document metadata"""
    document_name: Optional[str] = Field(None, min_length=1, max_length=500)
    document_type: Optional[str] = Field(None, max_length=100)

    @validator('document_name')
    def sanitize_document_name(cls, v):
        """Sanitize document name"""
        if v is not None:
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\_\.]+$'
            if not re.match(pattern, v):
                raise ValueError('Document name contains invalid characters')
            return v.strip()
        return v


class DocumentResponse(BaseModel):
    """Document response model"""
    document_id: str
    branch_id: str
    document_type: str
    document_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    team: str
    uploaded_at: Optional[str] = None
    uploaded_by: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentFilter(BaseModel):
    """Document filter parameters"""
    branch_id: Optional[str] = Field(None, max_length=50, description="Filter by branch ID")
    team: Optional[str] = Field(None, pattern="^(new_branch|legal|srd|scm)$", description="Filter by team")
    document_type: Optional[str] = Field(None, max_length=100, description="Filter by document type")
    search: Optional[str] = Field(None, max_length=100, description="Search by document name")
    sort: Optional[str] = Field("uploaded_at", description="Sort field")
    order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order")

    @validator('search')
    def sanitize_search(cls, v):
        """Sanitize search query"""
        if v is not None:
            v = re.sub(r'[^\w\s\-\.ก-๙]', '', v)
            return v.strip()
        return v


# ============================================================================
# File Upload Models
# ============================================================================

class FileUploadRequest(BaseModel):
    """File upload request metadata"""
    branch_id: str
    document_type: str
    document_name: str
    team: str
    mime_type: str
    file_size: int


class FileUploadResponse(BaseModel):
    """File upload response"""
    document_id: str
    file_path: str
    signed_url: Optional[str] = None  # For direct download
    expires_at: Optional[str] = None


# ============================================================================
# Document Type Definitions
# ============================================================================

# Document types by team
DOCUMENT_TYPES = {
    'new_branch': [
        'site_survey',           # แบบสำรวจสถานที่
        'proposal',              # ข้อเสนอโครงการ
        'timeline',              # timeline การเปิดสาขา
        'budget',                # งบประมาณ
        'approval',              # เอกสารอนุมัติ
        'other'                  # เอกสารอื่นๆ
    ],
    'legal': [
        'contract',              # สัญญา
        'license',               # ใบอนุญาต
        'ppp09',                 # ภ.พ.09
        'ppp20',                 # ภ.พ.20
        'title_deed',            # โฉนดที่ดิน
        'power_of_attorney',     # หนังสือมอบอำนาจ
        'other'                  # เอกสารกฎหมายอื่นๆ
    ],
    'srd': [
        'floor_plan',            # แปลนผัง
        'layout',                # layout ร้าน
        'design',                # ดีไซน์
        'rendering',             # รูป rendering
        'specification',         # specification
        'other'                  # เอกสาร SRD อื่นๆ
    ],
    'scm': [
        'dc_assignment',         # เอกสารมอบหมาย DC
        'logistics_plan',        # แผนจัดส่ง
        'inventory_plan',        # แผนสต็อก
        'supplier_info',         # ข้อมูลซัพพลายเออร์
        'other'                  # เอกสาร SCM อื่นๆ
    ]
}

# Allowed MIME types
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/zip',
    'application/x-rar-compressed'
]

# Maximum file size (in bytes) - 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_document_type(team: str, document_type: str) -> bool:
    """Validate document type for team"""
    return document_type in DOCUMENT_TYPES.get(team, [])


def validate_mime_type(mime_type: str) -> bool:
    """Validate MIME type"""
    return mime_type in ALLOWED_MIME_TYPES


def validate_file_size(file_size: int) -> bool:
    """Validate file size"""
    return 0 < file_size <= MAX_FILE_SIZE


def get_file_extension(mime_type: str) -> str:
    """Get file extension from MIME type"""
    mime_to_ext = {
        'application/pdf': '.pdf',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar'
    }
    return mime_to_ext.get(mime_type, '')
