"""User data models"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# ============================================================================
# User Models
# ============================================================================

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    user_level: str = Field(..., regex="^(admin|manager|editor|viewer)$")

    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters"""
        # Allow only alphanumeric, spaces, Thai characters, dash, dot
        pattern = r'^[a-zA-Z0-9ก-๙\s\-\.]+$'
        if not re.match(pattern, v):
            raise ValueError('Name contains invalid characters')
        return v.strip()

class UserCreate(UserBase):
    """Model for creating new user"""
    pass

class UserUpdate(BaseModel):
    """Model for updating user"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    user_level: Optional[str] = Field(None, regex="^(admin|manager|editor|viewer)$")
    is_active: Optional[bool] = None

    @validator('name')
    def sanitize_name(cls, v):
        if v is not None:
            pattern = r'^[a-zA-Z0-9ก-๙\s\-\.]+$'
            if not re.match(pattern, v):
                raise ValueError('Name contains invalid characters')
            return v.strip()
        return v

class UserResponse(BaseModel):
    """User response model"""
    user_id: str
    email: str
    name: str
    user_level: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    team_count: Optional[int] = 0

    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    """Detailed user response with teams"""
    teams: List[dict] = []

# ============================================================================
# User Team Models
# ============================================================================

class UserTeamBase(BaseModel):
    """Base user team model"""
    team_name: str = Field(..., regex="^(new_branch|legal|srd|scm)$")
    role: str = Field(..., regex="^(viewer|editor|manager)$")

class UserTeamCreate(UserTeamBase):
    """Model for adding user to team"""
    user_id: str

class UserTeamUpdate(BaseModel):
    """Model for updating user team role"""
    role: str = Field(..., regex="^(viewer|editor|manager)$")

class UserTeamResponse(BaseModel):
    """User team response model"""
    user_team_id: str
    user_id: str
    team_name: str
    role: str
    created_at: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

# ============================================================================
# Pagination Models
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[dict]
    total: int
    page: int
    limit: int
    total_pages: int

# ============================================================================
# Filter Models
# ============================================================================

class UserFilter(BaseModel):
    """User filter parameters"""
    search: Optional[str] = Field(None, max_length=100, description="Search by email or name")
    user_level: Optional[str] = Field(None, regex="^(admin|manager|editor|viewer)$")
    status: Optional[str] = Field(None, regex="^(active|inactive)$")
    sort: Optional[str] = Field("created_at", description="Sort field")
    order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="Sort order")

    @validator('search')
    def sanitize_search(cls, v):
        """Sanitize search query"""
        if v is not None:
            # Remove special characters that could cause SQL injection
            v = re.sub(r'[^\w\s\-\.@ก-๙]', '', v)
            return v.strip()
        return v

# ============================================================================
# Validation Helpers
# ============================================================================

def validate_user_level(level: str) -> bool:
    """Validate user level"""
    return level in ['admin', 'manager', 'editor', 'viewer']

def validate_team_name(team: str) -> bool:
    """Validate team name"""
    return team in ['new_branch', 'legal', 'srd', 'scm']

def validate_team_role(role: str) -> bool:
    """Validate team role"""
    return role in ['viewer', 'editor', 'manager']

def get_role_level(role: str) -> int:
    """Get numeric level for role comparison"""
    role_hierarchy = {'viewer': 1, 'editor': 2, 'manager': 3}
    return role_hierarchy.get(role, 0)

def can_role_perform_action(user_role: str, required_role: str) -> bool:
    """Check if user role can perform action requiring specific role"""
    return get_role_level(user_role) >= get_role_level(required_role)
