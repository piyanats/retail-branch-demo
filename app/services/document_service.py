"""Document management service

This service handles all document operations including:
- Document CRUD operations
- File upload to Google Cloud Storage
- File download with signed URLs
- File deletion from GCS
- Document search and filtering
"""

from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime, timedelta
import uuid
import math
import json
import os

from app.services.bigquery_service import BigQueryService
from app.services.storage_service import StorageService
from app.models.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentFilter,
    FileUploadResponse,
    validate_mime_type,
    validate_file_size,
    get_file_extension,
    MAX_FILE_SIZE
)
from app.models.user import PaginatedResponse
from app.config import settings


class DocumentService:
    """Service for document management operations"""

    def __init__(self):
        self.bq = BigQueryService()
        self.storage = StorageService()
        self.dataset_id = settings.DATASET_ID

    def _get_table_id(self, table_name: str) -> str:
        """Get full table ID"""
        return f"{settings.PROJECT_ID}.{self.dataset_id}.{table_name}"

    def _log_audit(
        self,
        user_id: str,
        user_email: str,
        action_type: str,
        resource_id: Optional[str] = None,
        action_detail: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> None:
        """Log action to audit_logs table"""
        log_data = {
            'log_id': str(uuid.uuid4()),
            'user_id': user_id,
            'user_email': user_email,
            'action_type': action_type,
            'resource_type': 'document',
            'resource_id': resource_id,
            'action_detail': action_detail,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'status': status,
            'error_message': error_message,
            'created_at': datetime.now().isoformat()
        }

        try:
            self.bq.insert_rows(self._get_table_id('audit_logs'), [log_data])
        except Exception as e:
            print(f"Warning: Failed to log audit: {e}")

    # ========================================================================
    # Document CRUD Operations
    # ========================================================================

    def get_documents(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[DocumentFilter] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of documents with optional filtering

        Args:
            page: Page number (starts from 1)
            limit: Items per page (max 100)
            filters: Optional filters

        Returns:
            PaginatedResponse with documents data
        """
        from google.cloud import bigquery

        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            if filters.branch_id:
                where_clauses.append("branch_id = @branch_id")
                params.append(bigquery.ScalarQueryParameter("branch_id", "STRING", filters.branch_id))

            if filters.team:
                where_clauses.append("team = @team")
                params.append(bigquery.ScalarQueryParameter("team", "STRING", filters.team))

            if filters.document_type:
                where_clauses.append("document_type = @document_type")
                params.append(bigquery.ScalarQueryParameter("document_type", "STRING", filters.document_type))

            if filters.search:
                where_clauses.append("LOWER(document_name) LIKE @search")
                params.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{filters.search.lower()}%"))

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM `{self._get_table_id('documents')}`
            {where_sql}
        """
        count_result = self.bq.query(count_sql, params)
        total = count_result[0]['total'] if count_result else 0

        # Calculate pagination
        total_pages = math.ceil(total / limit)
        offset = (page - 1) * limit

        # Get sort column and order
        sort_column = filters.sort if filters and filters.sort else "uploaded_at"
        sort_order = filters.order.upper() if filters and filters.order else "DESC"

        # Validate sort column
        valid_sort_columns = ['document_name', 'document_type', 'file_size', 'uploaded_at', 'branch_id', 'team']
        if sort_column not in valid_sort_columns:
            sort_column = 'uploaded_at'

        # Get documents
        documents_sql = f"""
            SELECT
                document_id,
                branch_id,
                document_type,
                document_name,
                file_path,
                file_size,
                mime_type,
                team,
                CAST(uploaded_at AS STRING) as uploaded_at,
                uploaded_by
            FROM `{self._get_table_id('documents')}`
            {where_sql}
            ORDER BY {sort_column} {sort_order}
            LIMIT @limit OFFSET @offset
        """

        # Add pagination parameters
        params.extend([
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset)
        ])

        documents = self.bq.query(documents_sql, params)

        return PaginatedResponse(
            data=documents,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    def get_document_by_id(self, document_id: str) -> Optional[DocumentResponse]:
        """
        Get document by ID

        Args:
            document_id: Document ID

        Returns:
            DocumentResponse or None if not found
        """
        from google.cloud import bigquery

        sql = f"""
            SELECT
                document_id,
                branch_id,
                document_type,
                document_name,
                file_path,
                file_size,
                mime_type,
                team,
                CAST(uploaded_at AS STRING) as uploaded_at,
                uploaded_by
            FROM `{self._get_table_id('documents')}`
            WHERE document_id = @document_id
        """

        params = [bigquery.ScalarQueryParameter("document_id", "STRING", document_id)]
        documents = self.bq.query(sql, params)

        if not documents:
            return None

        return DocumentResponse(**documents[0])

    def create_document_metadata(
        self,
        document_data: DocumentCreate,
        file_path: str,
        file_size: int,
        mime_type: str,
        uploaded_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DocumentResponse:
        """
        Create document metadata in BigQuery

        Args:
            document_data: Document metadata
            file_path: GCS file path
            file_size: File size in bytes
            mime_type: File MIME type
            uploaded_by: User ID of uploader
            ip_address: IP address
            user_agent: User agent

        Returns:
            DocumentResponse
        """
        document_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        document_dict = {
            'document_id': document_id,
            'branch_id': document_data.branch_id,
            'document_type': document_data.document_type,
            'document_name': document_data.document_name,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'team': document_data.team,
            'uploaded_at': now,
            'uploaded_by': uploaded_by
        }

        try:
            self.bq.insert_rows(self._get_table_id('documents'), [document_dict])

            # Log audit
            self._log_audit(
                user_id=uploaded_by,
                user_email="system",
                action_type="document_upload",
                resource_id=document_id,
                action_detail=json.dumps({
                    'document_name': document_data.document_name,
                    'branch_id': document_data.branch_id,
                    'team': document_data.team,
                    'file_size': file_size
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return DocumentResponse(**document_dict)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=uploaded_by,
                user_email="system",
                action_type="document_upload",
                resource_id=document_id,
                action_detail=f"Failed to create document metadata",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def upload_document(
        self,
        document_data: DocumentCreate,
        file: BinaryIO,
        file_size: int,
        mime_type: str,
        uploaded_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> FileUploadResponse:
        """
        Upload document file to GCS and create metadata

        Args:
            document_data: Document metadata
            file: File binary stream
            file_size: File size in bytes
            mime_type: File MIME type
            uploaded_by: User ID of uploader
            ip_address: IP address
            user_agent: User agent

        Returns:
            FileUploadResponse with document ID and file path

        Raises:
            ValueError: If file validation fails
        """
        # Validate MIME type
        if not validate_mime_type(mime_type):
            raise ValueError(f"Unsupported file type: {mime_type}")

        # Validate file size
        if not validate_file_size(file_size):
            raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB")

        # Generate unique filename
        document_id = str(uuid.uuid4())
        file_extension = get_file_extension(mime_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Folder structure: {team}/{branch_id}/{document_type}/
        folder = f"{document_data.team}/{document_data.branch_id}/{document_data.document_type}"
        filename = f"{timestamp}_{document_id}{file_extension}"

        try:
            # Upload to GCS
            upload_result = self.storage.upload_file(
                file=file,
                folder=folder,
                filename=filename,
                content_type=mime_type
            )

            file_path = upload_result['blob_name']

            # Create metadata in BigQuery
            document = self.create_document_metadata(
                document_data=document_data,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                uploaded_by=uploaded_by,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Generate signed URL for download (valid for 1 hour)
            signed_url = self.storage.generate_signed_url(file_path, expiration=3600)

            return FileUploadResponse(
                document_id=document.document_id,
                file_path=file_path,
                signed_url=signed_url,
                expires_at=(datetime.now() + timedelta(hours=1)).isoformat()
            )

        except Exception as e:
            # If BigQuery insert failed but GCS upload succeeded, try to delete the file
            if 'file_path' in locals():
                try:
                    self.storage.delete_file(file_path)
                except:
                    pass
            raise

    def update_document(
        self,
        document_id: str,
        document_data: DocumentUpdate,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DocumentResponse:
        """
        Update document metadata

        Args:
            document_id: Document ID
            document_data: Document update data
            updated_by: User ID of updater
            ip_address: IP address
            user_agent: User agent

        Returns:
            DocumentResponse

        Raises:
            ValueError: If document not found
        """
        from google.cloud import bigquery

        # Check if document exists
        existing_doc = self.get_document_by_id(document_id)
        if not existing_doc:
            raise ValueError(f"Document {document_id} not found")

        # Build update SET clause
        update_fields = []
        params = []
        changes = {}

        if document_data.document_name is not None:
            update_fields.append("document_name = @document_name")
            params.append(bigquery.ScalarQueryParameter("document_name", "STRING", document_data.document_name))
            changes['document_name'] = {'old': existing_doc.document_name, 'new': document_data.document_name}

        if document_data.document_type is not None:
            update_fields.append("document_type = @document_type")
            params.append(bigquery.ScalarQueryParameter("document_type", "STRING", document_data.document_type))
            changes['document_type'] = {'old': existing_doc.document_type, 'new': document_data.document_type}

        if not update_fields:
            # No changes
            return existing_doc

        # Add document_id parameter
        params.append(bigquery.ScalarQueryParameter("document_id", "STRING", document_id))

        # Execute update
        update_sql = f"""
            UPDATE `{self._get_table_id('documents')}`
            SET {', '.join(update_fields)}
            WHERE document_id = @document_id
        """

        try:
            self.bq.execute(update_sql, params)

            # Log audit
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="document_update",
                resource_id=document_id,
                action_detail=json.dumps({'changes': changes}),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            # Get updated document
            return self.get_document_by_id(document_id)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="document_update",
                resource_id=document_id,
                action_detail=f"Failed to update document",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def delete_document(
        self,
        document_id: str,
        deleted_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Delete document from both GCS and BigQuery

        Args:
            document_id: Document ID
            deleted_by: User ID of deleter
            ip_address: IP address
            user_agent: User agent

        Raises:
            ValueError: If document not found
        """
        from google.cloud import bigquery

        # Get document
        document = self.get_document_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            # Delete from GCS first
            self.storage.delete_file(document.file_path)

            # Delete from BigQuery
            delete_sql = f"""
                DELETE FROM `{self._get_table_id('documents')}`
                WHERE document_id = @document_id
            """
            params = [bigquery.ScalarQueryParameter("document_id", "STRING", document_id)]
            self.bq.execute(delete_sql, params)

            # Log audit
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="document_delete",
                resource_id=document_id,
                action_detail=json.dumps({
                    'document_name': document.document_name,
                    'file_path': document.file_path
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="document_delete",
                resource_id=document_id,
                action_detail=f"Failed to delete document",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def get_download_url(
        self,
        document_id: str,
        expiration: int = 3600,
        downloaded_by: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Get signed URL for document download

        Args:
            document_id: Document ID
            expiration: URL expiration in seconds (default 1 hour)
            downloaded_by: User ID of downloader
            ip_address: IP address
            user_agent: User agent

        Returns:
            Signed URL string

        Raises:
            ValueError: If document not found
        """
        # Get document
        document = self.get_document_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Generate signed URL
        signed_url = self.storage.generate_signed_url(document.file_path, expiration=expiration)

        # Log audit (optional - may create too many logs)
        if downloaded_by:
            self._log_audit(
                user_id=downloaded_by,
                user_email="system",
                action_type="document_download",
                resource_id=document_id,
                action_detail=document.document_name,
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        return signed_url
