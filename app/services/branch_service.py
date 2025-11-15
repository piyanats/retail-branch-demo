"""Branch management service

This service handles all branch operations including:
- Branch CRUD operations
- Branch search and filtering
- Branch statistics
- Audit logging
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid
import math
import json

from app.services.bigquery_service import BigQueryService
from app.models.branch import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    BranchDetailResponse,
    BranchFilter,
    BranchStats
)
from app.models.user import PaginatedResponse
from app.config import settings


class BranchService:
    """Service for branch management operations"""

    def __init__(self):
        self.bq = BigQueryService()
        self.dataset_id = settings.DATASET_ID

    def _get_table_id(self, table_name: str) -> str:
        """Get full table ID"""
        return f"{settings.PROJECT_ID}.{self.dataset_id}.{table_name}"

    def _log_audit(
        self,
        user_id: str,
        user_email: str,
        action_type: str,
        resource_type: str,
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
            'resource_type': resource_type,
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
    # Branch CRUD Operations
    # ========================================================================

    def get_branches(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[BranchFilter] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of branches with optional filtering

        Args:
            page: Page number (starts from 1)
            limit: Items per page (max 100)
            filters: Optional filters (search, province, district, status, dc_code, sort, order)

        Returns:
            PaginatedResponse with branches data
        """
        from google.cloud import bigquery

        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            if filters.search:
                where_clauses.append(
                    "(LOWER(branch_id) LIKE @search OR LOWER(branch_name) LIKE @search OR LOWER(address) LIKE @search)"
                )
                params.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{filters.search.lower()}%"))

            if filters.province:
                where_clauses.append("province = @province")
                params.append(bigquery.ScalarQueryParameter("province", "STRING", filters.province))

            if filters.district:
                where_clauses.append("district = @district")
                params.append(bigquery.ScalarQueryParameter("district", "STRING", filters.district))

            if filters.status:
                where_clauses.append("status = @status")
                params.append(bigquery.ScalarQueryParameter("status", "STRING", filters.status))

            if filters.dc_code:
                where_clauses.append("dc_code = @dc_code")
                params.append(bigquery.ScalarQueryParameter("dc_code", "STRING", filters.dc_code))

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM `{self._get_table_id('branches')}`
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

        # Validate sort column to prevent SQL injection
        valid_sort_columns = ['branch_id', 'branch_name', 'province', 'district', 'status', 'dc_code', 'opening_date', 'created_at', 'updated_at']
        if sort_column not in valid_sort_columns:
            sort_column = 'created_at'

        # Get branches
        branches_sql = f"""
            SELECT
                branch_id,
                branch_name,
                address,
                province,
                district,
                postal_code,
                phone,
                status,
                dc_code,
                CAST(opening_date AS STRING) as opening_date,
                CAST(created_at AS STRING) as created_at,
                CAST(updated_at AS STRING) as updated_at,
                created_by,
                updated_by
            FROM `{self._get_table_id('branches')}`
            {where_sql}
            ORDER BY {sort_column} {sort_order}
            LIMIT @limit OFFSET @offset
        """

        # Add pagination parameters
        params.extend([
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset)
        ])

        branches = self.bq.query(branches_sql, params)

        return PaginatedResponse(
            data=branches,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    def get_branch_by_id(self, branch_id: str) -> Optional[BranchDetailResponse]:
        """
        Get branch by ID with additional details

        Args:
            branch_id: Branch ID

        Returns:
            BranchDetailResponse or None if not found
        """
        from google.cloud import bigquery

        # Get branch data
        branch_sql = f"""
            SELECT
                branch_id,
                branch_name,
                address,
                province,
                district,
                postal_code,
                phone,
                status,
                dc_code,
                CAST(opening_date AS STRING) as opening_date,
                CAST(created_at AS STRING) as created_at,
                CAST(updated_at AS STRING) as updated_at,
                created_by,
                updated_by
            FROM `{self._get_table_id('branches')}`
            WHERE branch_id = @branch_id
        """

        params = [bigquery.ScalarQueryParameter("branch_id", "STRING", branch_id)]
        branches = self.bq.query(branch_sql, params)

        if not branches:
            return None

        branch_data = branches[0]

        # Get document count
        doc_count_sql = f"""
            SELECT COUNT(*) as count
            FROM `{self._get_table_id('documents')}`
            WHERE branch_id = @branch_id
        """
        doc_count_result = self.bq.query(doc_count_sql, params)
        document_count = doc_count_result[0]['count'] if doc_count_result else 0

        # Check if branch has PPP09
        ppp09_sql = f"""
            SELECT COUNT(*) as count
            FROM `{self._get_table_id('legal_ppp09')}`
            WHERE branch_id = @branch_id
        """
        ppp09_result = self.bq.query(ppp09_sql, params)
        has_ppp09 = ppp09_result[0]['count'] > 0 if ppp09_result else False

        return BranchDetailResponse(
            **branch_data,
            document_count=document_count,
            has_ppp09=has_ppp09
        )

    def create_branch(
        self,
        branch_data: BranchCreate,
        created_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> BranchResponse:
        """
        Create new branch

        Args:
            branch_data: Branch creation data
            created_by: User ID of creator
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            BranchResponse with created branch data

        Raises:
            ValueError: If branch already exists
        """
        # Check if branch already exists
        existing_branch = self.get_branch_by_id(branch_data.branch_id)
        if existing_branch:
            raise ValueError(f"Branch {branch_data.branch_id} already exists")

        # Create branch
        now = datetime.now().isoformat()

        branch_dict = {
            'branch_id': branch_data.branch_id,
            'branch_name': branch_data.branch_name,
            'address': branch_data.address,
            'province': branch_data.province,
            'district': branch_data.district,
            'postal_code': branch_data.postal_code,
            'phone': branch_data.phone,
            'status': branch_data.status,
            'dc_code': branch_data.dc_code,
            'opening_date': branch_data.opening_date.isoformat() if branch_data.opening_date else None,
            'created_at': now,
            'updated_at': now,
            'created_by': created_by,
            'updated_by': created_by
        }

        try:
            self.bq.insert_rows(self._get_table_id('branches'), [branch_dict])

            # Log audit
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="branch_create",
                resource_type="branch",
                resource_id=branch_data.branch_id,
                action_detail=f"Created branch {branch_data.branch_id} - {branch_data.branch_name}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return BranchResponse(**branch_dict)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="branch_create",
                resource_type="branch",
                resource_id=branch_data.branch_id,
                action_detail=f"Failed to create branch {branch_data.branch_id}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def update_branch(
        self,
        branch_id: str,
        branch_data: BranchUpdate,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> BranchResponse:
        """
        Update branch information

        Args:
            branch_id: Branch ID to update
            branch_data: Branch update data
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            BranchResponse with updated branch data

        Raises:
            ValueError: If branch not found
        """
        from google.cloud import bigquery

        # Check if branch exists
        existing_branch = self.get_branch_by_id(branch_id)
        if not existing_branch:
            raise ValueError(f"Branch {branch_id} not found")

        # Build update SET clause
        update_fields = []
        params = []
        changes = {}

        if branch_data.branch_name is not None:
            update_fields.append("branch_name = @branch_name")
            params.append(bigquery.ScalarQueryParameter("branch_name", "STRING", branch_data.branch_name))
            changes['branch_name'] = {'old': existing_branch.branch_name, 'new': branch_data.branch_name}

        if branch_data.address is not None:
            update_fields.append("address = @address")
            params.append(bigquery.ScalarQueryParameter("address", "STRING", branch_data.address))
            changes['address'] = {'old': existing_branch.address, 'new': branch_data.address}

        if branch_data.province is not None:
            update_fields.append("province = @province")
            params.append(bigquery.ScalarQueryParameter("province", "STRING", branch_data.province))
            changes['province'] = {'old': existing_branch.province, 'new': branch_data.province}

        if branch_data.district is not None:
            update_fields.append("district = @district")
            params.append(bigquery.ScalarQueryParameter("district", "STRING", branch_data.district))
            changes['district'] = {'old': existing_branch.district, 'new': branch_data.district}

        if branch_data.postal_code is not None:
            update_fields.append("postal_code = @postal_code")
            params.append(bigquery.ScalarQueryParameter("postal_code", "STRING", branch_data.postal_code))
            changes['postal_code'] = {'old': existing_branch.postal_code, 'new': branch_data.postal_code}

        if branch_data.phone is not None:
            update_fields.append("phone = @phone")
            params.append(bigquery.ScalarQueryParameter("phone", "STRING", branch_data.phone))
            changes['phone'] = {'old': existing_branch.phone, 'new': branch_data.phone}

        if branch_data.status is not None:
            update_fields.append("status = @status")
            params.append(bigquery.ScalarQueryParameter("status", "STRING", branch_data.status))
            changes['status'] = {'old': existing_branch.status, 'new': branch_data.status}

        if branch_data.dc_code is not None:
            update_fields.append("dc_code = @dc_code")
            params.append(bigquery.ScalarQueryParameter("dc_code", "STRING", branch_data.dc_code))
            changes['dc_code'] = {'old': existing_branch.dc_code, 'new': branch_data.dc_code}

        if branch_data.opening_date is not None:
            update_fields.append("opening_date = @opening_date")
            params.append(bigquery.ScalarQueryParameter("opening_date", "DATE", branch_data.opening_date))
            changes['opening_date'] = {'old': existing_branch.opening_date, 'new': branch_data.opening_date.isoformat()}

        if not update_fields:
            # No changes
            return BranchResponse(
                branch_id=existing_branch.branch_id,
                branch_name=existing_branch.branch_name,
                address=existing_branch.address,
                province=existing_branch.province,
                district=existing_branch.district,
                postal_code=existing_branch.postal_code,
                phone=existing_branch.phone,
                status=existing_branch.status,
                dc_code=existing_branch.dc_code,
                opening_date=existing_branch.opening_date,
                created_at=existing_branch.created_at,
                updated_at=existing_branch.updated_at,
                created_by=existing_branch.created_by,
                updated_by=existing_branch.updated_by
            )

        # Add updated_at and updated_by
        now = datetime.now().isoformat()
        update_fields.append("updated_at = @updated_at")
        params.append(bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", now))
        update_fields.append("updated_by = @updated_by")
        params.append(bigquery.ScalarQueryParameter("updated_by", "STRING", updated_by))

        # Add branch_id parameter
        params.append(bigquery.ScalarQueryParameter("branch_id", "STRING", branch_id))

        # Execute update
        update_sql = f"""
            UPDATE `{self._get_table_id('branches')}`
            SET {', '.join(update_fields)}
            WHERE branch_id = @branch_id
        """

        try:
            self.bq.execute(update_sql, params)

            # Log audit
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="branch_update",
                resource_type="branch",
                resource_id=branch_id,
                action_detail=json.dumps({'changes': changes}),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            # Get updated branch
            updated_branch = self.get_branch_by_id(branch_id)
            return BranchResponse(
                branch_id=updated_branch.branch_id,
                branch_name=updated_branch.branch_name,
                address=updated_branch.address,
                province=updated_branch.province,
                district=updated_branch.district,
                postal_code=updated_branch.postal_code,
                phone=updated_branch.phone,
                status=updated_branch.status,
                dc_code=updated_branch.dc_code,
                opening_date=updated_branch.opening_date,
                created_at=updated_branch.created_at,
                updated_at=updated_branch.updated_at,
                created_by=updated_branch.created_by,
                updated_by=updated_branch.updated_by
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="branch_update",
                resource_type="branch",
                resource_id=branch_id,
                action_detail=f"Failed to update branch",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def delete_branch(
        self,
        branch_id: str,
        deleted_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Delete branch

        Args:
            branch_id: Branch ID to delete
            deleted_by: User ID of deleter
            ip_address: IP address of request
            user_agent: User agent of request

        Raises:
            ValueError: If branch not found
        """
        from google.cloud import bigquery

        # Check if branch exists
        existing_branch = self.get_branch_by_id(branch_id)
        if not existing_branch:
            raise ValueError(f"Branch {branch_id} not found")

        # Delete branch
        delete_sql = f"""
            DELETE FROM `{self._get_table_id('branches')}`
            WHERE branch_id = @branch_id
        """

        params = [bigquery.ScalarQueryParameter("branch_id", "STRING", branch_id)]

        try:
            self.bq.execute(delete_sql, params)

            # Log audit
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="branch_delete",
                resource_type="branch",
                resource_id=branch_id,
                action_detail=f"Deleted branch {branch_id} - {existing_branch.branch_name}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=deleted_by,
                user_email="system",
                action_type="branch_delete",
                resource_type="branch",
                resource_id=branch_id,
                action_detail=f"Failed to delete branch",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    # ========================================================================
    # Branch Statistics
    # ========================================================================

    def get_branch_stats(self) -> BranchStats:
        """
        Get branch statistics

        Returns:
            BranchStats with aggregated data
        """
        # Total branches by status
        status_sql = f"""
            SELECT
                COUNT(*) as total_branches,
                COUNTIF(status = 'active') as active_branches,
                COUNTIF(status = 'opening') as opening_branches,
                COUNTIF(status = 'closed') as closed_branches
            FROM `{self._get_table_id('branches')}`
        """

        status_result = self.bq.query(status_sql)
        stats_data = status_result[0] if status_result else {
            'total_branches': 0,
            'active_branches': 0,
            'opening_branches': 0,
            'closed_branches': 0
        }

        # Branches by province
        province_sql = f"""
            SELECT
                province,
                COUNT(*) as count
            FROM `{self._get_table_id('branches')}`
            WHERE province IS NOT NULL
            GROUP BY province
            ORDER BY count DESC
            LIMIT 20
        """

        provinces = self.bq.query(province_sql)

        # Branches by DC
        dc_sql = f"""
            SELECT
                dc_code,
                COUNT(*) as count
            FROM `{self._get_table_id('branches')}`
            WHERE dc_code IS NOT NULL
            GROUP BY dc_code
            ORDER BY count DESC
        """

        dcs = self.bq.query(dc_sql)

        return BranchStats(
            total_branches=stats_data['total_branches'],
            active_branches=stats_data['active_branches'],
            opening_branches=stats_data['opening_branches'],
            closed_branches=stats_data['closed_branches'],
            branches_by_province=provinces,
            branches_by_dc=dcs
        )
