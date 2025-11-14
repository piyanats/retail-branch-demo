"""Data models package"""

from app.models.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserTeamBase,
    UserTeamCreate,
    UserTeamUpdate,
    UserTeamResponse,
    PaginatedResponse,
    PaginationParams,
    UserFilter
)

from app.models.branch import (
    BranchBase,
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchDetailResponse,
    BranchFilter,
    BranchStats
)

from app.models.document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpload,
    DocumentUpdate,
    DocumentResponse,
    DocumentFilter,
    FileUploadRequest,
    FileUploadResponse,
    DOCUMENT_TYPES,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE
)

from app.models.legal_ppp09 import (
    PPP09Base,
    PPP09Create,
    PPP09Update,
    PPP09Response,
    PPP09Filter,
    PPP09PDFUpload
)

__all__ = [
    # User models
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserDetailResponse',
    'UserTeamBase',
    'UserTeamCreate',
    'UserTeamUpdate',
    'UserTeamResponse',
    'PaginatedResponse',
    'PaginationParams',
    'UserFilter',
    # Branch models
    'BranchBase',
    'BranchCreate',
    'BranchUpdate',
    'BranchResponse',
    'BranchDetailResponse',
    'BranchFilter',
    'BranchStats',
    # Document models
    'DocumentBase',
    'DocumentCreate',
    'DocumentUpload',
    'DocumentUpdate',
    'DocumentResponse',
    'DocumentFilter',
    'FileUploadRequest',
    'FileUploadResponse',
    'DOCUMENT_TYPES',
    'ALLOWED_MIME_TYPES',
    'MAX_FILE_SIZE',
    # PPP09 models
    'PPP09Base',
    'PPP09Create',
    'PPP09Update',
    'PPP09Response',
    'PPP09Filter',
    'PPP09PDFUpload',
]
