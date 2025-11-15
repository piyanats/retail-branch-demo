"""Legal PPP09 (ภ.พ.09) management API routes

Endpoints for managing ภ.พ.09 (แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง) documents.
Access control: Requires authentication and legal team membership
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, RedirectResponse

from app.middleware.auth import get_current_user, require_team_access
from app.services.legal_ppp09_service import LegalPPP09Service
from app.models.legal_ppp09 import (
    PPP09Create,
    PPP09Update,
    PPP09Response,
    PPP09Filter
)
from app.models.user import PaginatedResponse

router = APIRouter(prefix="/api/legal/ppp09", tags=["legal-ppp09"])


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP address and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.get("", response_model=PaginatedResponse)
async def get_ppp09_list(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    branch_id: Optional[str] = Query(None, max_length=50, description="Filter by branch ID"),
    province: Optional[str] = Query(None, max_length=100, description="Filter by province"),
    payment_status: Optional[str] = Query(None, pattern="^(paid|unpaid|overdue)$", description="Filter by payment status"),
    expiring_soon: Optional[bool] = Query(None, description="Filter by expiring soon (within 90 days)"),
    search: Optional[str] = Query(None, max_length=100, description="Search by PPP09 number or owner name"),
    sort: Optional[str] = Query("created_at", description="Sort field"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(require_team_access(["legal"], ["viewer", "editor", "manager"]))
):
    """
    Get paginated list of PPP09 records with optional filtering

    Requires: legal team access (viewer, editor, or manager role)
    """
    try:
        # Create filter object
        filters = PPP09Filter(
            branch_id=branch_id,
            province=province,
            payment_status=payment_status,
            expiring_soon=expiring_soon,
            search=search,
            sort=sort,
            order=order
        )

        service = LegalPPP09Service()
        result = service.get_ppp09_list(page=page, limit=limit, filters=filters)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PPP09 list: {str(e)}")


@router.get("/{ppp09_id}", response_model=PPP09Response)
async def get_ppp09_by_id(
    ppp09_id: str,
    current_user: dict = Depends(require_team_access(["legal"], ["viewer", "editor", "manager"]))
):
    """
    Get PPP09 details by ID

    Requires: legal team access
    """
    try:
        service = LegalPPP09Service()
        ppp09 = service.get_ppp09_by_id(ppp09_id)

        if not ppp09:
            raise HTTPException(status_code=404, detail=f"PPP09 {ppp09_id} not found")

        return ppp09

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PPP09: {str(e)}")


@router.post("", response_model=PPP09Response, status_code=201)
async def create_ppp09(
    request: Request,
    ppp09_data: PPP09Create,
    current_user: dict = Depends(require_team_access(["legal"], ["editor", "manager"]))
):
    """
    Create new PPP09 record

    Requires: legal team with editor or manager role
    """
    try:
        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        ppp09 = service.create_ppp09(
            ppp09_data=ppp09_data,
            created_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return ppp09

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PPP09: {str(e)}")


@router.put("/{ppp09_id}", response_model=PPP09Response)
async def update_ppp09(
    request: Request,
    ppp09_id: str,
    ppp09_data: PPP09Update,
    current_user: dict = Depends(require_team_access(["legal"], ["editor", "manager"]))
):
    """
    Update PPP09 information

    Requires: legal team with editor or manager role
    """
    try:
        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        ppp09 = service.update_ppp09(
            ppp09_id=ppp09_id,
            ppp09_data=ppp09_data,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return ppp09

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update PPP09: {str(e)}")


@router.delete("/{ppp09_id}", status_code=204)
async def delete_ppp09(
    request: Request,
    ppp09_id: str,
    current_user: dict = Depends(require_team_access(["legal"], ["manager"]))
):
    """
    Delete PPP09 record

    Requires: legal team with manager role
    """
    try:
        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        service.delete_ppp09(
            ppp09_id=ppp09_id,
            deleted_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return JSONResponse(status_code=204, content=None)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PPP09: {str(e)}")


@router.post("/{ppp09_id}/upload-pdf", response_model=dict, status_code=201)
async def upload_ppp09_pdf(
    request: Request,
    ppp09_id: str,
    file: UploadFile = File(..., description="PDF file to upload (max 10MB)"),
    current_user: dict = Depends(require_team_access(["legal"], ["editor", "manager"]))
):
    """
    Upload PDF file for PPP09 record

    Requires: legal team with editor or manager role
    Max file size: 10MB
    """
    try:
        # Validate file type
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read file to get size
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="PDF file size exceeds 10MB limit")

        # Reset file pointer
        await file.seek(0)

        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        file_path = service.upload_ppp09_pdf(
            ppp09_id=ppp09_id,
            file=file.file,
            file_size=file_size,
            uploaded_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "message": "PDF uploaded successfully",
            "ppp09_id": ppp09_id,
            "file_path": file_path,
            "file_size": file_size
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")


@router.get("/{ppp09_id}/download-pdf")
async def download_ppp09_pdf(
    request: Request,
    ppp09_id: str,
    expiration: int = Query(3600, ge=300, le=86400, description="URL expiration in seconds (5 min - 24 hours)"),
    current_user: dict = Depends(require_team_access(["legal"], ["viewer", "editor", "manager"]))
):
    """
    Get signed URL for PPP09 PDF download and redirect to it

    Requires: legal team access
    """
    try:
        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        signed_url = service.get_ppp09_pdf_download_url(
            ppp09_id=ppp09_id,
            expiration=expiration,
            downloaded_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Redirect to signed URL
        return RedirectResponse(url=signed_url)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF download URL: {str(e)}")


@router.delete("/{ppp09_id}/pdf", status_code=204)
async def delete_ppp09_pdf(
    request: Request,
    ppp09_id: str,
    current_user: dict = Depends(require_team_access(["legal"], ["manager"]))
):
    """
    Delete PDF file from PPP09 record

    Requires: legal team with manager role
    """
    try:
        service = LegalPPP09Service()
        ip_address, user_agent = get_client_info(request)

        service.delete_ppp09_pdf(
            ppp09_id=ppp09_id,
            deleted_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return JSONResponse(status_code=204, content=None)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")
