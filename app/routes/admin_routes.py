"""Admin routes for user management

This module provides admin-only endpoints for:
- User CRUD operations
- User team management
- User permissions
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional

from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserTeamCreate,
    UserTeamUpdate,
    UserTeamResponse,
    PaginatedResponse,
    PaginationParams,
    UserFilter
)
from app.services.user_service import UserService
from app.middleware.auth import get_current_admin_user


router = APIRouter(prefix="/admin", tags=["admin"])


def get_request_info(request: Request) -> tuple[str, str]:
    """Extract IP address and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    return ip_address, user_agent


# ============================================================================
# User Management Routes
# ============================================================================

@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, max_length=100, description="Search by email or name"),
    user_level: Optional[str] = Query(None, pattern="^(admin|manager|editor|viewer)$", description="Filter by user level"),
    status: Optional[str] = Query(None, pattern="^(active|inactive)$", description="Filter by status"),
    sort: Optional[str] = Query("created_at", description="Sort field"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get paginated list of users with optional filtering

    Requires: Admin access
    """
    user_service = UserService()

    # Create filter object
    filters = UserFilter(
        search=search,
        user_level=user_level,
        status=status,
        sort=sort,
        order=order
    )

    try:
        result = user_service.get_users(page=page, limit=limit, filters=filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get user details by ID

    Requires: Admin access
    """
    user_service = UserService()

    try:
        user = user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Create new user

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    try:
        user = user_service.create_user(
            user_data=user_data,
            created_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return user
    except ValueError as e:
        # User already exists or validation error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Update user information

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    try:
        user = user_service.update_user(
            user_id=user_id,
            user_data=user_data,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return user
    except ValueError as e:
        # User not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.post("/users/{user_id}/deactivate", status_code=204)
async def deactivate_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Deactivate user (soft delete)

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    # Prevent self-deactivation
    if user_id == current_user['user_id']:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    try:
        user_service.deactivate_user(
            user_id=user_id,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return None
    except ValueError as e:
        # User not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate user: {str(e)}")


@router.post("/users/{user_id}/activate", status_code=204)
async def activate_user(
    request: Request,
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Activate user

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    try:
        user_service.activate_user(
            user_id=user_id,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return None
    except ValueError as e:
        # User not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")


# ============================================================================
# User Team Management Routes
# ============================================================================

@router.get("/users/{user_id}/teams")
async def get_user_teams(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get all teams for a user

    Requires: Admin access
    """
    user_service = UserService()

    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        teams = user_service.get_user_teams(user_id)
        return {"user_id": user_id, "teams": teams}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user teams: {str(e)}")


@router.post("/users/{user_id}/teams", response_model=UserTeamResponse, status_code=201)
async def add_user_to_team(
    request: Request,
    user_id: str,
    team_name: str = Query(..., pattern="^(new_branch|legal|srd|scm)$", description="Team name"),
    role: str = Query(..., pattern="^(viewer|editor|manager)$", description="Role in team"),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Add user to team with role

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    # Create user team data
    user_team_data = UserTeamCreate(
        user_id=user_id,
        team_name=team_name,
        role=role
    )

    try:
        user_team = user_service.add_user_to_team(
            user_team_data=user_team_data,
            created_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return user_team
    except ValueError as e:
        # User not found or already in team
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user to team: {str(e)}")


@router.put("/teams/{user_team_id}", response_model=UserTeamResponse)
async def update_user_team_role(
    request: Request,
    user_team_id: str,
    role: str = Query(..., pattern="^(viewer|editor|manager)$", description="New role"),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Update user's role in team

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    # Create role update data
    role_data = UserTeamUpdate(role=role)

    try:
        user_team = user_service.update_user_team_role(
            user_team_id=user_team_id,
            role_data=role_data,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return user_team
    except ValueError as e:
        # User team not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user team role: {str(e)}")


@router.delete("/teams/{user_team_id}", status_code=204)
async def remove_user_from_team(
    request: Request,
    user_team_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Remove user from team

    Requires: Admin access
    """
    user_service = UserService()
    ip_address, user_agent = get_request_info(request)

    try:
        user_service.remove_user_from_team(
            user_team_id=user_team_id,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return None
    except ValueError as e:
        # User team not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove user from team: {str(e)}")
