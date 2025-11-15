"""Branch management API routes

Endpoints for managing branch data including CRUD operations and statistics.
Access control: Requires authentication and team membership (new_branch, admin)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.middleware.auth import get_current_user, require_team_access
from app.services.branch_service import BranchService
from app.models.branch import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchDetailResponse,
    BranchFilter,
    BranchStats
)
from app.models.user import PaginatedResponse

router = APIRouter(prefix="/api/branches", tags=["branches"])


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP address and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.get("", response_model=PaginatedResponse)
async def get_branches(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, max_length=100, description="Search by branch ID, name, or address"),
    province: Optional[str] = Query(None, max_length=100, description="Filter by province"),
    district: Optional[str] = Query(None, max_length=100, description="Filter by district"),
    status: Optional[str] = Query(None, pattern="^(active|opening|closed)$", description="Filter by status"),
    dc_code: Optional[str] = Query(None, max_length=50, description="Filter by DC code"),
    sort: Optional[str] = Query("created_at", description="Sort field"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of branches with optional filtering

    Requires: Any authenticated user with team access
    """
    try:
        # Create filter object
        filters = BranchFilter(
            search=search,
            province=province,
            district=district,
            status=status,
            dc_code=dc_code,
            sort=sort,
            order=order
        )

        service = BranchService()
        result = service.get_branches(page=page, limit=limit, filters=filters)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branches: {str(e)}")


@router.get("/stats", response_model=BranchStats)
async def get_branch_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get branch statistics including counts by status, province, and DC

    Requires: Any authenticated user
    """
    try:
        service = BranchService()
        stats = service.get_branch_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branch statistics: {str(e)}")


@router.get("/{branch_id}", response_model=BranchDetailResponse)
async def get_branch_by_id(
    branch_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get branch details by ID including document count and PPP09 status

    Requires: Any authenticated user
    """
    try:
        service = BranchService()
        branch = service.get_branch_by_id(branch_id)

        if not branch:
            raise HTTPException(status_code=404, detail=f"Branch {branch_id} not found")

        return branch

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branch: {str(e)}")


@router.post("", response_model=BranchResponse, status_code=201)
async def create_branch(
    request: Request,
    branch_data: BranchCreate,
    current_user: dict = Depends(require_team_access(["new_branch"], ["editor", "manager"]))
):
    """
    Create new branch

    Requires: new_branch team with editor or manager role, or admin
    """
    try:
        service = BranchService()
        ip_address, user_agent = get_client_info(request)

        branch = service.create_branch(
            branch_data=branch_data,
            created_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return branch

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create branch: {str(e)}")


@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    request: Request,
    branch_id: str,
    branch_data: BranchUpdate,
    current_user: dict = Depends(require_team_access(["new_branch"], ["editor", "manager"]))
):
    """
    Update branch information

    Requires: new_branch team with editor or manager role, or admin
    """
    try:
        service = BranchService()
        ip_address, user_agent = get_client_info(request)

        branch = service.update_branch(
            branch_id=branch_id,
            branch_data=branch_data,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return branch

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update branch: {str(e)}")


@router.delete("/{branch_id}", status_code=204)
async def delete_branch(
    request: Request,
    branch_id: str,
    current_user: dict = Depends(require_team_access(["new_branch"], ["manager"]))
):
    """
    Delete branch

    Requires: new_branch team with manager role, or admin
    """
    try:
        service = BranchService()
        ip_address, user_agent = get_client_info(request)

        service.delete_branch(
            branch_id=branch_id,
            deleted_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return JSONResponse(status_code=204, content=None)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete branch: {str(e)}")
