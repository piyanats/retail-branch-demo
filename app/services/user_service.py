"""User management service

This service handles all user and user team operations including:
- User CRUD operations
- Team membership management
- User authentication lookups
- Audit logging
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import math

from app.services.bigquery_service import BigQueryService
from app.models.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserTeamCreate,
    UserTeamUpdate,
    UserTeamResponse,
    PaginatedResponse,
    UserFilter
)
from app.config import settings


class UserService:
    """Service for user management operations"""

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
            # Don't fail the main operation if audit logging fails
            print(f"Warning: Failed to log audit: {e}")

    # ========================================================================
    # User CRUD Operations
    # ========================================================================

    def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[UserFilter] = None
    ) -> PaginatedResponse:
        """
        Get paginated list of users with optional filtering

        Args:
            page: Page number (starts from 1)
            limit: Items per page (max 100)
            filters: Optional filters (search, user_level, status, sort, order)

        Returns:
            PaginatedResponse with users data
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        if filters:
            if filters.search:
                where_clauses.append("(LOWER(email) LIKE @search OR LOWER(name) LIKE @search)")
                params.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{filters.search.lower()}%"))

            if filters.user_level:
                where_clauses.append("user_level = @user_level")
                params.append(bigquery.ScalarQueryParameter("user_level", "STRING", filters.user_level))

            if filters.status:
                is_active = filters.status == "active"
                where_clauses.append("is_active = @is_active")
                params.append(bigquery.ScalarQueryParameter("is_active", "BOOL", is_active))

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM `{self._get_table_id('users')}`
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
        valid_sort_columns = ['email', 'name', 'user_level', 'created_at', 'updated_at', 'last_login']
        if sort_column not in valid_sort_columns:
            sort_column = 'created_at'

        # Get users with team count
        users_sql = f"""
            SELECT
                u.user_id,
                u.email,
                u.name,
                u.user_level,
                u.is_active,
                u.created_at,
                u.updated_at,
                u.last_login,
                COUNT(ut.user_team_id) as team_count
            FROM `{self._get_table_id('users')}` u
            LEFT JOIN `{self._get_table_id('user_teams')}` ut ON u.user_id = ut.user_id
            {where_sql}
            GROUP BY u.user_id, u.email, u.name, u.user_level, u.is_active, u.created_at, u.updated_at, u.last_login
            ORDER BY u.{sort_column} {sort_order}
            LIMIT @limit OFFSET @offset
        """

        # Add pagination parameters
        params.extend([
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset)
        ])

        users = self.bq.query(users_sql, params)

        return PaginatedResponse(
            data=users,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserDetailResponse]:
        """
        Get user by ID with team details

        Args:
            user_id: User ID

        Returns:
            UserDetailResponse or None if not found
        """
        # Get user data
        user_sql = f"""
            SELECT
                user_id,
                email,
                name,
                user_level,
                is_active,
                created_at,
                updated_at,
                last_login
            FROM `{self._get_table_id('users')}`
            WHERE user_id = @user_id
        """

        from google.cloud import bigquery
        params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        users = self.bq.query(user_sql, params)

        if not users:
            return None

        user_data = users[0]

        # Get user teams
        teams = self.get_user_teams(user_id)

        return UserDetailResponse(
            user_id=user_data['user_id'],
            email=user_data['email'],
            name=user_data['name'],
            user_level=user_data['user_level'],
            is_active=user_data['is_active'],
            created_at=user_data.get('created_at'),
            updated_at=user_data.get('updated_at'),
            last_login=user_data.get('last_login'),
            team_count=len(teams),
            teams=teams
        )

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address

        Args:
            email: User email

        Returns:
            User dict or None if not found
        """
        sql = f"""
            SELECT
                user_id,
                email,
                name,
                user_level,
                is_active,
                created_at,
                updated_at,
                last_login
            FROM `{self._get_table_id('users')}`
            WHERE LOWER(email) = LOWER(@email)
        """

        from google.cloud import bigquery
        params = [bigquery.ScalarQueryParameter("email", "STRING", email)]
        users = self.bq.query(sql, params)

        return users[0] if users else None

    def create_user(
        self,
        user_data: UserCreate,
        created_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserResponse:
        """
        Create new user

        Args:
            user_data: User creation data
            created_by: User ID of creator
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            UserResponse with created user data

        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError(f"User with email {user_data.email} already exists")

        # Create user
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        user_dict = {
            'user_id': user_id,
            'email': user_data.email,
            'name': user_data.name,
            'user_level': user_data.user_level,
            'is_active': True,
            'created_at': now,
            'updated_at': now,
            'last_login': None
        }

        try:
            self.bq.insert_rows(self._get_table_id('users'), [user_dict])

            # Log audit
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="user_create",
                resource_type="user",
                resource_id=user_id,
                action_detail=f"Created user {user_data.email}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return UserResponse(**user_dict, team_count=0)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="user_create",
                resource_type="user",
                resource_id=user_id,
                action_detail=f"Failed to create user {user_data.email}",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def update_user(
        self,
        user_id: str,
        user_data: UserUpdate,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserResponse:
        """
        Update user information

        Args:
            user_id: User ID to update
            user_data: User update data
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            UserResponse with updated user data

        Raises:
            ValueError: If user not found
        """
        # Check if user exists
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError(f"User {user_id} not found")

        # Build update SET clause
        update_fields = []
        params = []
        changes = {}

        from google.cloud import bigquery

        if user_data.name is not None:
            update_fields.append("name = @name")
            params.append(bigquery.ScalarQueryParameter("name", "STRING", user_data.name))
            changes['name'] = {'old': existing_user.name, 'new': user_data.name}

        if user_data.user_level is not None:
            update_fields.append("user_level = @user_level")
            params.append(bigquery.ScalarQueryParameter("user_level", "STRING", user_data.user_level))
            changes['user_level'] = {'old': existing_user.user_level, 'new': user_data.user_level}

        if user_data.is_active is not None:
            update_fields.append("is_active = @is_active")
            params.append(bigquery.ScalarQueryParameter("is_active", "BOOL", user_data.is_active))
            changes['is_active'] = {'old': existing_user.is_active, 'new': user_data.is_active}

        if not update_fields:
            # No changes
            return UserResponse(
                user_id=existing_user.user_id,
                email=existing_user.email,
                name=existing_user.name,
                user_level=existing_user.user_level,
                is_active=existing_user.is_active,
                created_at=existing_user.created_at,
                updated_at=existing_user.updated_at,
                last_login=existing_user.last_login,
                team_count=existing_user.team_count
            )

        # Add updated_at
        now = datetime.now().isoformat()
        update_fields.append("updated_at = @updated_at")
        params.append(bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", now))

        # Add user_id parameter
        params.append(bigquery.ScalarQueryParameter("user_id", "STRING", user_id))

        # Execute update
        update_sql = f"""
            UPDATE `{self._get_table_id('users')}`
            SET {', '.join(update_fields)}
            WHERE user_id = @user_id
        """

        try:
            self.bq.execute(update_sql, params)

            # Log audit
            import json
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="user_update",
                resource_type="user",
                resource_id=user_id,
                action_detail=json.dumps({'changes': changes}),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            # Get updated user
            updated_user = self.get_user_by_id(user_id)
            return UserResponse(
                user_id=updated_user.user_id,
                email=updated_user.email,
                name=updated_user.name,
                user_level=updated_user.user_level,
                is_active=updated_user.is_active,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at,
                last_login=updated_user.last_login,
                team_count=updated_user.team_count
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="user_update",
                resource_type="user",
                resource_id=user_id,
                action_detail=f"Failed to update user",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def deactivate_user(
        self,
        user_id: str,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Deactivate user (soft delete)

        Args:
            user_id: User ID to deactivate
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Raises:
            ValueError: If user not found
        """
        update_data = UserUpdate(is_active=False)
        self.update_user(user_id, update_data, updated_by, ip_address, user_agent)

        # Log specific deactivate action
        self._log_audit(
            user_id=updated_by,
            user_email="system",
            action_type="user_deactivate",
            resource_type="user",
            resource_id=user_id,
            action_detail=f"Deactivated user {user_id}",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )

    def activate_user(
        self,
        user_id: str,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Activate user

        Args:
            user_id: User ID to activate
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Raises:
            ValueError: If user not found
        """
        update_data = UserUpdate(is_active=True)
        self.update_user(user_id, update_data, updated_by, ip_address, user_agent)

        # Log specific activate action
        self._log_audit(
            user_id=updated_by,
            user_email="system",
            action_type="user_activate",
            resource_type="user",
            resource_id=user_id,
            action_detail=f"Activated user {user_id}",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )

    def update_last_login(self, user_id: str) -> None:
        """
        Update user's last login timestamp

        Args:
            user_id: User ID
        """
        from google.cloud import bigquery

        now = datetime.now().isoformat()
        update_sql = f"""
            UPDATE `{self._get_table_id('users')}`
            SET last_login = @last_login
            WHERE user_id = @user_id
        """

        params = [
            bigquery.ScalarQueryParameter("last_login", "TIMESTAMP", now),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]

        self.bq.execute(update_sql, params)

    # ========================================================================
    # User Team Operations
    # ========================================================================

    def get_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all teams for a user

        Args:
            user_id: User ID

        Returns:
            List of team dicts
        """
        sql = f"""
            SELECT
                user_team_id,
                user_id,
                team_name,
                role,
                created_at,
                created_by
            FROM `{self._get_table_id('user_teams')}`
            WHERE user_id = @user_id
            ORDER BY created_at DESC
        """

        from google.cloud import bigquery
        params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]

        return self.bq.query(sql, params)

    def add_user_to_team(
        self,
        user_team_data: UserTeamCreate,
        created_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserTeamResponse:
        """
        Add user to team with role

        Args:
            user_team_data: User team creation data
            created_by: User ID of creator
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            UserTeamResponse

        Raises:
            ValueError: If user already in team
        """
        # Check if user exists
        user = self.get_user_by_id(user_team_data.user_id)
        if not user:
            raise ValueError(f"User {user_team_data.user_id} not found")

        # Check if user already in team
        existing_teams = self.get_user_teams(user_team_data.user_id)
        for team in existing_teams:
            if team['team_name'] == user_team_data.team_name:
                raise ValueError(f"User already in team {user_team_data.team_name}")

        # Create user team
        user_team_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        user_team_dict = {
            'user_team_id': user_team_id,
            'user_id': user_team_data.user_id,
            'team_name': user_team_data.team_name,
            'role': user_team_data.role,
            'created_at': now,
            'created_by': created_by
        }

        try:
            self.bq.insert_rows(self._get_table_id('user_teams'), [user_team_dict])

            # Log audit
            import json
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="permission_add",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=json.dumps({
                    'target_user_id': user_team_data.user_id,
                    'target_user_email': user.email,
                    'team_name': user_team_data.team_name,
                    'role': user_team_data.role
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            return UserTeamResponse(**user_team_dict)

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=created_by,
                user_email="system",
                action_type="permission_add",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=f"Failed to add user to team",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def update_user_team_role(
        self,
        user_team_id: str,
        role_data: UserTeamUpdate,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserTeamResponse:
        """
        Update user's role in team

        Args:
            user_team_id: User team ID
            role_data: Role update data
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Returns:
            UserTeamResponse

        Raises:
            ValueError: If user team not found
        """
        from google.cloud import bigquery

        # Get existing user team
        sql = f"""
            SELECT user_team_id, user_id, team_name, role, created_at, created_by
            FROM `{self._get_table_id('user_teams')}`
            WHERE user_team_id = @user_team_id
        """
        params = [bigquery.ScalarQueryParameter("user_team_id", "STRING", user_team_id)]
        results = self.bq.query(sql, params)

        if not results:
            raise ValueError(f"User team {user_team_id} not found")

        existing = results[0]

        # Update role
        update_sql = f"""
            UPDATE `{self._get_table_id('user_teams')}`
            SET role = @role
            WHERE user_team_id = @user_team_id
        """

        params = [
            bigquery.ScalarQueryParameter("role", "STRING", role_data.role),
            bigquery.ScalarQueryParameter("user_team_id", "STRING", user_team_id)
        ]

        try:
            self.bq.execute(update_sql, params)

            # Log audit
            import json
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="permission_update",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=json.dumps({
                    'user_id': existing['user_id'],
                    'team_name': existing['team_name'],
                    'old_role': existing['role'],
                    'new_role': role_data.role
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

            # Return updated data
            return UserTeamResponse(
                user_team_id=user_team_id,
                user_id=existing['user_id'],
                team_name=existing['team_name'],
                role=role_data.role,
                created_at=existing['created_at'],
                created_by=existing['created_by']
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="permission_update",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=f"Failed to update user team role",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise

    def remove_user_from_team(
        self,
        user_team_id: str,
        updated_by: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Remove user from team

        Args:
            user_team_id: User team ID
            updated_by: User ID of updater
            ip_address: IP address of request
            user_agent: User agent of request

        Raises:
            ValueError: If user team not found
        """
        from google.cloud import bigquery

        # Get existing user team for audit log
        sql = f"""
            SELECT user_team_id, user_id, team_name, role
            FROM `{self._get_table_id('user_teams')}`
            WHERE user_team_id = @user_team_id
        """
        params = [bigquery.ScalarQueryParameter("user_team_id", "STRING", user_team_id)]
        results = self.bq.query(sql, params)

        if not results:
            raise ValueError(f"User team {user_team_id} not found")

        existing = results[0]

        # Delete user team
        delete_sql = f"""
            DELETE FROM `{self._get_table_id('user_teams')}`
            WHERE user_team_id = @user_team_id
        """

        try:
            self.bq.execute(delete_sql, params)

            # Log audit
            import json
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="permission_remove",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=json.dumps({
                    'user_id': existing['user_id'],
                    'team_name': existing['team_name'],
                    'role': existing['role']
                }),
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )

        except Exception as e:
            # Log audit failure
            self._log_audit(
                user_id=updated_by,
                user_email="system",
                action_type="permission_remove",
                resource_type="permission",
                resource_id=user_team_id,
                action_detail=f"Failed to remove user from team",
                ip_address=ip_address,
                user_agent=user_agent,
                status="failed",
                error_message=str(e)
            )
            raise
