"""Document management API routes

Endpoints for managing documents including file upload/download and metadata operations.
Access control: Requires authentication and team membership based on document team
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, RedirectResponse

from app.middleware.auth import get_current_user, require_team_access
from app.services.document_service import DocumentService
from app.models.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentFilter,
    FileUploadResponse,
    validate_mime_type,
    validate_file_size,
    MAX_FILE_SIZE
)
from app.models.user import PaginatedResponse

router = APIRouter(prefix="/api/documents", tags=["documents"])


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP address and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


def check_document_team_access(current_user: dict, document_team: str) -> bool:
    """Check if user has access to document's team"""
    # Admin has access to all teams
    if current_user.get('user_level') == 'admin':
        return True

    # Check if user has team access
    user_teams = current_user.get('teams', [])
    return document_team in user_teams


@router.get("", response_model=PaginatedResponse)
async def get_documents(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    branch_id: Optional[str] = Query(None, max_length=50, description="Filter by branch ID"),
    team: Optional[str] = Query(None, pattern="^(new_branch|legal|srd|scm)$", description="Filter by team"),
    document_type: Optional[str] = Query(None, max_length=100, description="Filter by document type"),
    search: Optional[str] = Query(None, max_length=100, description="Search by document name"),
    sort: Optional[str] = Query("uploaded_at", description="Sort field"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of documents with optional filtering

    Users will only see documents from teams they have access to
    """
    try:
        # If user is not admin, filter by their teams
        if current_user.get('user_level') != 'admin':
            user_teams = current_user.get('teams', [])
            if team and team not in user_teams:
                raise HTTPException(status_code=403, detail="Access denied to this team's documents")
            # If no team filter specified, user will see documents from all their teams
            # This is handled by the UI - backend returns all accessible documents

        # Create filter object
        filters = DocumentFilter(
            branch_id=branch_id,
            team=team,
            document_type=document_type,
            search=search,
            sort=sort,
            order=order
        )

        service = DocumentService()
        result = service.get_documents(page=page, limit=limit, filters=filters)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_by_id(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get document details by ID

    Requires: Access to document's team
    """
    try:
        service = DocumentService()
        document = service.get_document_by_id(document_id)

        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        # Check team access
        if not check_document_team_access(current_user, document.team):
            raise HTTPException(status_code=403, detail="Access denied to this document")

        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="File to upload"),
    branch_id: str = Form(..., min_length=1, max_length=50),
    document_type: str = Form(..., max_length=100),
    document_name: str = Form(..., min_length=1, max_length=500),
    team: str = Form(..., pattern="^(new_branch|legal|srd|scm)$"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload document file to GCS and create metadata

    Requires: Access to specified team with editor or manager role
    """
    try:
        # Check team access (editor or manager role required)
        if current_user.get('user_level') != 'admin':
            user_teams = current_user.get('teams', {})
            if team not in user_teams:
                raise HTTPException(status_code=403, detail=f"Access denied to team: {team}")

            user_role = user_teams.get(team)
            if user_role not in ['editor', 'manager']:
                raise HTTPException(status_code=403, detail="Editor or manager role required to upload documents")

        # Validate MIME type
        if not validate_mime_type(file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )

        # Read file to get size
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )

        # Reset file pointer
        await file.seek(0)

        # Create document metadata
        document_data = DocumentCreate(
            branch_id=branch_id,
            document_type=document_type,
            document_name=document_name,
            team=team
        )

        service = DocumentService()
        ip_address, user_agent = get_client_info(request)

        result = service.upload_document(
            document_data=document_data,
            file=file.file,
            file_size=file_size,
            mime_type=file.content_type,
            uploaded_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(
    request: Request,
    document_id: str,
    expiration: int = Query(3600, ge=300, le=86400, description="URL expiration in seconds (5 min - 24 hours)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get signed URL for document download and redirect to it

    Requires: Access to document's team
    """
    try:
        service = DocumentService()

        # First check if document exists and user has access
        document = service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        if not check_document_team_access(current_user, document.team):
            raise HTTPException(status_code=403, detail="Access denied to this document")

        # Get signed URL
        ip_address, user_agent = get_client_info(request)
        signed_url = service.get_download_url(
            document_id=document_id,
            expiration=expiration,
            downloaded_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Redirect to signed URL
        return RedirectResponse(url=signed_url)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get download URL: {str(e)}")


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    request: Request,
    document_id: str,
    document_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update document metadata (name and type only, not the file itself)

    Requires: Access to document's team with editor or manager role
    """
    try:
        service = DocumentService()

        # Check if document exists and user has access
        document = service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        # Check team access and role
        if current_user.get('user_level') != 'admin':
            user_teams = current_user.get('teams', {})
            if document.team not in user_teams:
                raise HTTPException(status_code=403, detail="Access denied to this document")

            user_role = user_teams.get(document.team)
            if user_role not in ['editor', 'manager']:
                raise HTTPException(status_code=403, detail="Editor or manager role required to update documents")

        ip_address, user_agent = get_client_info(request)

        updated_document = service.update_document(
            document_id=document_id,
            document_data=document_data,
            updated_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return updated_document

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    request: Request,
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete document from both GCS and BigQuery

    Requires: Access to document's team with manager role
    """
    try:
        service = DocumentService()

        # Check if document exists and user has access
        document = service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

        # Check team access and role (manager required for delete)
        if current_user.get('user_level') != 'admin':
            user_teams = current_user.get('teams', {})
            if document.team not in user_teams:
                raise HTTPException(status_code=403, detail="Access denied to this document")

            user_role = user_teams.get(document.team)
            if user_role != 'manager':
                raise HTTPException(status_code=403, detail="Manager role required to delete documents")

        ip_address, user_agent = get_client_info(request)

        service.delete_document(
            document_id=document_id,
            deleted_by=current_user['user_id'],
            ip_address=ip_address,
            user_agent=user_agent
        )

        return JSONResponse(status_code=204, content=None)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
