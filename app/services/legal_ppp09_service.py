"""Legal PPP09 (ภ.พ.09) management service

This service handles all PPP09 (ภาษีที่ดินและสิ่งปลูกสร้าง) operations including:
- PPP09 CRUD operations
- PDF upload/download/delete
- Expiry checking and alerts
- Payment status management
"""

from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime, timedelta, date
import uuid
import math
import json

from app.services.bigquery_service import BigQueryService
from app.services.storage_service import StorageService
from app.models.legal_ppp09 import (
    PPP09Create,
    PPP09Update,
    PPP09Response,
    PPP09Filter,
    is_expiring_soon,
    is_expired
)
from app.models.user import PaginatedResponse
from app.config import settings


class LegalPPP09Service:
    """Service for Legal PPP09 management operations"""

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
            'resource_type': 'ppp09',
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
    # PPP09 CRUD Operations
    # ========================================================================

    def get_ppp09_list(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[PPP09Filter] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of PPP09 records with optional filtering

        Args:
            page: Page number (starts from 1)
            limit: Items per page (max 100)
            filters: Optional filters

        Returns:
            PaginatedResponse with PPP09 data
        """
        from google.cloud import bigquery

        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            if filters.branch_id:
                where_clauses.append("branch_id = @branch_id")
                params.append(bigquery.ScalarQueryParameter("branch_id", "STRING", filters.branch_id))

            if filters.province:
                where_clauses.append("address_province = @province")
                params.append(bigquery.ScalarQueryParameter("province", "STRING", filters.province))

            if filters.payment_status:
                where_clauses.append("payment_status = @payment_status")
                params.append(bigquery.ScalarQueryParameter("payment_status", "STRING", filters.payment_status))

            if filters.expiring_soon:
                # PPP09 expiring within 90 days
                today = date.today()
                expiry_threshold = today + timedelta(days=90)
                where_clauses.append("expiry_date BETWEEN @today AND @threshold")
                params.append(bigquery.ScalarQueryParameter("today", "DATE", today))
                params.append(bigquery.ScalarQueryParameter("threshold", "DATE", expiry_threshold))

            if filters.search:
                where_clauses.append(
                    "(LOWER(ppp09_number) LIKE @search OR LOWER(owner_name) LIKE @search)"
                )
                params.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{filters.search.lower()}%"))

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM `{self._get_table_id('legal_ppp09')}`
            {where_sql}
        """
        count_result = self.bq.query(count_sql, params)
        total = count_result[0]['total'] if count_result else 0

        # Calculate pagination
        total_pages = math.ceil(total / limit)
        offset = (page - 1) * limit

        # Get sort column and order
        sort_column = filters.sort if filters and filters.sort else "created_at"
        sort_order = filters.order.upper() if filters and filters.order else "DESC"

        # Validate sort column
        valid_sort_columns = ['ppp09_number', 'issue_date', 'expiry_date', 'owner_name', 'annual_tax_amount', 'payment_status', 'created_at']
        if sort_column not in valid_sort_columns:
            sort_column = 'created_at'

        # Get PPP09 records
        ppp09_sql = f"""
            SELECT
                ppp09_id,
                branch_id,
                ppp09_number,
                CAST(issue_date AS STRING) as issue_date,
                CAST(expiry_date AS STRING) as expiry_date,
                owner_name,
                address_number,
                address_moo,
                address_trok,
                address_soi,
                address_road,
                address_tambon,
                address_amphoe,
                address_province,
                address_postal_code,
                land_area_rai,
                land_area_ngan,
                land_area_wa,
                building_area_sqm,
                annual_tax_amount,
                payment_status,
                pdf_file_path,
                pdf_file_size,
                CAST(pdf_uploaded_at AS STRING) as pdf_uploaded_at,
                pdf_uploaded_by,
                remarks,
                CAST(created_at AS STRING) as created_at,
                CAST(updated_at AS STRING) as updated_at,
                created_by,
                updated_by
            FROM `{self._get_table_id('legal_ppp09')}`
            {where_sql}
            ORDER BY {sort_column} {sort_order}
            LIMIT @limit OFFSET @offset
        """

        # Add pagination parameters
        params.extend([
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset)
        ])

        ppp09_records = self.bq.query(ppp09_sql, params)

        return PaginatedResponse(
            data=ppp09_records,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    def get_ppp09_by_id(self, ppp09_id: str) -> Optional[PPP09Response]:
        """
        Get PPP09 record by ID

        Args:
            ppp09_id: PPP09 ID

        Returns:
            PPP09Response or None if not found
        """
        from google.cloud import bigquery

        sql = f"""
            SELECT
                ppp09_id,
                branch_id,
                ppp09_number,
                CAST(issue_date AS STRING) as issue_date,
                CAST(expiry_date AS STRING) as expiry_date,
                owner_name,
                address_number,
                address_moo,
                address_trok,
                address_soi,
                address_road,
                address_tambon,
                address_amphoe,
                address_province,
                address_postal_code,
                land_area_rai,
                land_area_ngan,
                land_area_wa,
                building_area_sqm,
                annual_tax_amount,
                payment_status,
                pdf_file_path,
                pdf_file_size,
                CAST(pdf_uploaded_at AS STRING) as pdf_uploaded_at,
                pdf_uploaded_by,
                remarks,
                CAST(created_at AS STRING) as created_at,
                CAST(updated_at AS STRING) as updated_at,
                created_by,
                updated_by
            FROM `{self._get_table_id('legal_ppp09')}`
            WHERE ppp09_id = @ppp09_id
        """

        params = [bigquery.ScalarQueryParameter("ppp09_id", "STRING", ppp09_id)]
        ppp09_records = self.bq.query(sql, params)

        if not ppp09_records:
            return None

        return PPP09Response(**ppp09_records[0])

    def create_ppp09(
        self,
        ppp09_data: PPP09Create,
        created_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> PPP09Response:
        """
        Create new PPP09 record

        Args:
            ppp09_data: PPP09 creation data
            created_by: User ID of creator
            ip_address: IP address
            user_agent: User agent

        Returns:
            PPP09Response
        """
        ppp09_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        ppp09_dict = {
            'ppp09_id': ppp09_id,
            'branch_id': ppp09_data.branch_id,
            'ppp09_number': ppp09_data.ppp09_number,
            'issue_date': ppp09_data.issue_date.isoformat() if ppp09_data.issue_date else None,
            'expiry_date': ppp09_data.expiry_date.isoformat() if ppp09_data.expiry_date else None,
            'owner_name': ppp09_data.owner_name,
            'address_number': ppp09_data.address_number,
            'address_moo': ppp09_data.address_moo,
            'address_trok': ppp09_data.address_trok,
            'address_soi': ppp09_data.address_soi,
            'address_road': ppp09_data.address_road,
            'address_tambon': ppp09_data.address_tambon,
            'address_amphoe': ppp09_data.address_amphoe,
            'address_province': ppp09_data.address_province,
            'address_postal_code': ppp09_data.address_postal_code,
            'land_area_rai': ppp09_data.land_area_rai,
            'land_area_ngan': ppp09_data.land_area_ngan,
            'land_area_wa': ppp09_data.land_area_wa,
            'building_area_sqm': ppp09_data.building_area_sqm,
            'annual_tax_amount': ppp09_data.annual_tax_amount,
            'payment_status': ppp09_data.payment_status,
            'pdf_file_path': None,
            'pdf_file_size': None,
            'pdf_uploaded_at': None,
            'pdf_uploaded_by': None,
            'remarks': ppp09_data.remarks,
            'created_at': now,
            'updated_at': now,
            'created_by': created_by,
            'updated_by': created_by
        }

        try:
            self.bq.insert_rows(self._get_table_id('legal_ppp09'), [ppp09_dict])

            # Log audit
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="ppp09_create",
                resource_id=ppp09_id,
                action_detail=json.dumps({
                    'branch_id': ppp09_data.branch_id,
                    'ppp09_number': ppp09_data.ppp09_number
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return PPP09Response(**ppp09_dict)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="ppp09_create",
                resource_id=ppp09_id,
                action_detail=f"Failed to create PPP09",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def update_ppp09(
        self,
        ppp09_id: str,
        ppp09_data: PPP09Update,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> PPP09Response:
        """
        Update PPP09 record

        Args:
            ppp09_id: PPP09 ID
            ppp09_data: PPP09 update data
            updated_by: User ID of updater
            ip_address: IP address
            user_agent: User agent

        Returns:
            PPP09Response

        Raises:
            ValueError: If PPP09 not found
        """
        from google.cloud import bigquery

        # Check if PPP09 exists
        existing_ppp09 = self.get_ppp09_by_id(ppp09_id)
        if not existing_ppp09:
            raise ValueError(f"PPP09 {ppp09_id} not found")

        # Build update SET clause (only non-None fields)
        update_fields = []
        params = []
        changes = {}

        # Helper to add field if not None
        def add_field(field_name: str, value: Any, bq_type: str):
            if value is not None:
                update_fields.append(f"{field_name} = @{field_name}")
                # Handle date objects
                if isinstance(value, date):
                    params.append(bigquery.ScalarQueryParameter(field_name, bq_type, value))
                else:
                    params.append(bigquery.ScalarQueryParameter(field_name, bq_type, value))
                changes[field_name] = {'old': getattr(existing_ppp09, field_name), 'new': value}

        # Add all possible fields
        add_field('ppp09_number', ppp09_data.ppp09_number, 'STRING')
        add_field('issue_date', ppp09_data.issue_date, 'DATE')
        add_field('expiry_date', ppp09_data.expiry_date, 'DATE')
        add_field('owner_name', ppp09_data.owner_name, 'STRING')
        add_field('address_number', ppp09_data.address_number, 'STRING')
        add_field('address_moo', ppp09_data.address_moo, 'STRING')
        add_field('address_trok', ppp09_data.address_trok, 'STRING')
        add_field('address_soi', ppp09_data.address_soi, 'STRING')
        add_field('address_road', ppp09_data.address_road, 'STRING')
        add_field('address_tambon', ppp09_data.address_tambon, 'STRING')
        add_field('address_amphoe', ppp09_data.address_amphoe, 'STRING')
        add_field('address_province', ppp09_data.address_province, 'STRING')
        add_field('address_postal_code', ppp09_data.address_postal_code, 'STRING')
        add_field('land_area_rai', ppp09_data.land_area_rai, 'FLOAT64')
        add_field('land_area_ngan', ppp09_data.land_area_ngan, 'FLOAT64')
        add_field('land_area_wa', ppp09_data.land_area_wa, 'FLOAT64')
        add_field('building_area_sqm', ppp09_data.building_area_sqm, 'FLOAT64')
        add_field('annual_tax_amount', ppp09_data.annual_tax_amount, 'FLOAT64')
        add_field('payment_status', ppp09_data.payment_status, 'STRING')
        add_field('remarks', ppp09_data.remarks, 'STRING')

        if not update_fields:
            # No changes
            return existing_ppp09

        # Add updated_at and updated_by
        now = datetime.now().isoformat()
        update_fields.append("updated_at = @updated_at")
        params.append(bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", now))
        update_fields.append("updated_by = @updated_by")
        params.append(bigquery.ScalarQueryParameter("updated_by", "STRING", updated_by))

        # Add ppp09_id parameter
        params.append(bigquery.ScalarQueryParameter("ppp09_id", "STRING", ppp09_id))

        # Execute update
        update_sql = f"""
            UPDATE `{self._get_table_id('legal_ppp09')}`
            SET {', '.join(update_fields)}
            WHERE ppp09_id = @ppp09_id
        """

        try:
            self.bq.execute(update_sql, params)

            # Log audit
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="ppp09_update",
                resource_id=ppp09_id,
                action_detail=json.dumps({'changes': changes}),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            # Get updated PPP09
            return self.get_ppp09_by_id(ppp09_id)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="ppp09_update",
                resource_id=ppp09_id,
                action_detail=f"Failed to update PPP09",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def delete_ppp09(
        self,
        ppp09_id: str,
        deleted_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Delete PPP09 record (including PDF if exists)

        Args:
            ppp09_id: PPP09 ID
            deleted_by: User ID of deleter
            ip_address: IP address
            user_agent: User agent

        Raises:
            ValueError: If PPP09 not found
        """
        from google.cloud import bigquery

        # Get PPP09
        ppp09 = self.get_ppp09_by_id(ppp09_id)
        if not ppp09:
            raise ValueError(f"PPP09 {ppp09_id} not found")

        try:
            # Delete PDF from GCS if exists
            if ppp09.pdf_file_path:
                self.storage.delete_file(ppp09.pdf_file_path)

            # Delete from BigQuery
            delete_sql = f"""
                DELETE FROM `{self._get_table_id('legal_ppp09')}`
                WHERE ppp09_id = @ppp09_id
            """
            params = [bigquery.ScalarQueryParameter("ppp09_id", "STRING", ppp09_id)]
            self.bq.execute(delete_sql, params)

            # Log audit
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="ppp09_delete",
                resource_id=ppp09_id,
                action_detail=json.dumps({
                    'branch_id': ppp09.branch_id,
                    'ppp09_number': ppp09.ppp09_number
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
                action_type="ppp09_delete",
                resource_id=ppp09_id,
                action_detail=f"Failed to delete PPP09",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    # ========================================================================
    # PDF Operations
    # ========================================================================

    def upload_ppp09_pdf(
        self,
        ppp09_id: str,
        file: BinaryIO,
        file_size: int,
        uploaded_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Upload PPP09 PDF file

        Args:
            ppp09_id: PPP09 ID
            file: PDF file binary stream
            file_size: File size in bytes
            uploaded_by: User ID of uploader
            ip_address: IP address
            user_agent: User agent

        Returns:
            File path in GCS

        Raises:
            ValueError: If PPP09 not found or file validation fails
        """
        from google.cloud import bigquery

        # Get PPP09
        ppp09 = self.get_ppp09_by_id(ppp09_id)
        if not ppp09:
            raise ValueError(f"PPP09 {ppp09_id} not found")

        # Validate file size (max 10MB for PDF)
        if file_size > 10 * 1024 * 1024:
            raise ValueError(f"PDF file size exceeds maximum allowed size of 10MB")

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = f"legal/ppp09/{ppp09.branch_id}"
        filename = f"ppp09_{ppp09.branch_id}_{timestamp}.pdf"

        try:
            # Upload to GCS
            upload_result = self.storage.upload_file(
                file=file,
                folder=folder,
                filename=filename,
                content_type='application/pdf'
            )

            file_path = upload_result['blob_name']
            now = datetime.now().isoformat()

            # Update PPP09 with PDF info
            update_sql = f"""
                UPDATE `{self._get_table_id('legal_ppp09')}`
                SET
                    pdf_file_path = @pdf_file_path,
                    pdf_file_size = @pdf_file_size,
                    pdf_uploaded_at = @pdf_uploaded_at,
                    pdf_uploaded_by = @pdf_uploaded_by,
                    updated_at = @updated_at,
                    updated_by = @updated_by
                WHERE ppp09_id = @ppp09_id
            """

            params = [
                bigquery.ScalarQueryParameter("pdf_file_path", "STRING", file_path),
                bigquery.ScalarQueryParameter("pdf_file_size", "INT64", file_size),
                bigquery.ScalarQueryParameter("pdf_uploaded_at", "TIMESTAMP", now),
                bigquery.ScalarQueryParameter("pdf_uploaded_by", "STRING", uploaded_by),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", now),
                bigquery.ScalarQueryParameter("updated_by", "STRING", uploaded_by),
                bigquery.ScalarQueryParameter("ppp09_id", "STRING", ppp09_id)
            ]

            self.bq.execute(update_sql, params)

            # Log audit
            self._log_audit(
                user_id=uploaded_by,
                user_email="system",
                action_type="ppp09_pdf_upload",
                resource_id=ppp09_id,
                action_detail=json.dumps({
                    'file_path': file_path,
                    'file_size': file_size
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return file_path

        except Exception as e:
            # If BigQuery update failed but GCS upload succeeded, try to delete the file
            if 'file_path' in locals():
                try:
                    self.storage.delete_file(file_path)
                except:
                    pass

            # Log audit failure
            self._log_audit(
                user_id=uploaded_by,
                user_email="system",
                action_type="ppp09_pdf_upload",
                resource_id=ppp09_id,
                action_detail=f"Failed to upload PDF",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def get_ppp09_pdf_download_url(
        self,
        ppp09_id: str,
        expiration: int = 3600,
        downloaded_by: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Get signed URL for PPP09 PDF download

        Args:
            ppp09_id: PPP09 ID
            expiration: URL expiration in seconds (default 1 hour)
            downloaded_by: User ID of downloader
            ip_address: IP address
            user_agent: User agent

        Returns:
            Signed URL string

        Raises:
            ValueError: If PPP09 not found or no PDF available
        """
        # Get PPP09
        ppp09 = self.get_ppp09_by_id(ppp09_id)
        if not ppp09:
            raise ValueError(f"PPP09 {ppp09_id} not found")

        if not ppp09.pdf_file_path:
            raise ValueError(f"PPP09 {ppp09_id} has no PDF file")

        # Generate signed URL
        signed_url = self.storage.generate_signed_url(ppp09.pdf_file_path, expiration=expiration)

        # Log audit
        if downloaded_by:
            self._log_audit(
                user_id=downloaded_by,
                user_email="system",
                action_type="ppp09_pdf_download",
                resource_id=ppp09_id,
                action_detail=ppp09.ppp09_number,
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        return signed_url

    def delete_ppp09_pdf(
        self,
        ppp09_id: str,
        deleted_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Delete PPP09 PDF file

        Args:
            ppp09_id: PPP09 ID
            deleted_by: User ID of deleter
            ip_address: IP address
            user_agent: User agent

        Raises:
            ValueError: If PPP09 not found or no PDF available
        """
        from google.cloud import bigquery

        # Get PPP09
        ppp09 = self.get_ppp09_by_id(ppp09_id)
        if not ppp09:
            raise ValueError(f"PPP09 {ppp09_id} not found")

        if not ppp09.pdf_file_path:
            raise ValueError(f"PPP09 {ppp09_id} has no PDF file")

        try:
            # Delete from GCS
            self.storage.delete_file(ppp09.pdf_file_path)

            # Update PPP09 to remove PDF info
            now = datetime.now().isoformat()
            update_sql = f"""
                UPDATE `{self._get_table_id('legal_ppp09')}`
                SET
                    pdf_file_path = NULL,
                    pdf_file_size = NULL,
                    pdf_uploaded_at = NULL,
                    pdf_uploaded_by = NULL,
                    updated_at = @updated_at,
                    updated_by = @updated_by
                WHERE ppp09_id = @ppp09_id
            """

            params = [
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", now),
                bigquery.ScalarQueryParameter("updated_by", "STRING", deleted_by),
                bigquery.ScalarQueryParameter("ppp09_id", "STRING", ppp09_id)
            ]

            self.bq.execute(update_sql, params)

            # Log audit
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="ppp09_pdf_delete",
                resource_id=ppp09_id,
                action_detail=ppp09.pdf_file_path,
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="ppp09_pdf_delete",
                resource_id=ppp09_id,
                action_detail=f"Failed to delete PDF",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise
