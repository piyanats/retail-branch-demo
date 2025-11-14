# Implementation Roadmap

## Overview

เอกสารนี้อธิบายลำดับขั้นตอนการพัฒนา Retail Branch Management System แบบ step-by-step พร้อมรายละเอียดไฟล์ที่ต้องสร้างในแต่ละ phase

**Total Estimated Time:** 6-8 สัปดาห์ (1.5-2 เดือน)

**Team Size:** 2-3 developers

---

## Phase 0: Project Setup (1-2 วัน)

### 0.1 Create Project Structure

**สร้าง directories ตาม architecture:**

```bash
mkdir -p retail-branch-demo/{app,static,scripts,tests,docs}
mkdir -p app/{models,services,routes,middleware,templates}
mkdir -p app/templates/{admin,teams,emails,components}
mkdir -p static/{css,js}
mkdir -p static/js/{utils,components}
mkdir -p tests/{unit,integration}
```

**Files to create:**
```
retail-branch-demo/
├── app/
│   ├── __init__.py              # Empty file
│   ├── models/
│   │   └── __init__.py          # Empty file
│   ├── services/
│   │   └── __init__.py          # Empty file
│   ├── routes/
│   │   └── __init__.py          # Empty file
│   ├── middleware/
│   │   └── __init__.py          # Empty file
│   └── templates/
│       └── (empty for now)
├── static/
│   ├── css/
│   │   └── input.css            # Tailwind input
│   └── js/
│       └── (empty for now)
├── scripts/
│   └── (will create later)
├── tests/
│   ├── __init__.py              # Empty file
│   └── conftest.py              # Pytest configuration
└── docs/
    └── (already created)
```

**Create empty `__init__.py` files:**
```bash
touch app/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/routes/__init__.py
touch app/middleware/__init__.py
touch tests/__init__.py
```

### 0.2 Setup Configuration Files

**Files to create (in order):**

1. **`.gitignore`** - Copy from `docs/development/configuration.md`
2. **`.dockerignore`** - Copy from `docs/development/configuration.md`
3. **`.env.example`** - Copy from `docs/development/configuration.md`
4. **`requirements.txt`** - Copy from `docs/development/configuration.md`
5. **`pyproject.toml`** - Copy from `docs/development/configuration.md`
6. **`package.json`** - Copy from `docs/development/configuration.md`
7. **`tailwind.config.js`** - Copy from `docs/development/configuration.md`
8. **`static/css/input.css`** - Copy from `docs/development/configuration.md`
9. **`Dockerfile`** - Copy from `docs/development/configuration.md`
10. **`.gitlab-ci.yml`** - Copy from `docs/deployment/cicd.md`

### 0.3 Install Dependencies

**Create setup script:**

**`scripts/setup_local.sh`** - Copy from `docs/development/configuration.md`

**Run setup:**
```bash
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

**Update `.env` file:**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

**Verify installation:**
```bash
source .venv/bin/activate
python --version  # Should be 3.12+
uv --version      # Should show UV version
npm --version     # Should show npm version
```

### 0.4 Setup Google Cloud Platform

**Prerequisites:**
- Google Cloud Project created
- Billing enabled
- APIs enabled: BigQuery, Cloud Storage, Secret Manager

**Create BigQuery dataset and tables:**

**`scripts/setup_bigquery.py`**
```python
#!/usr/bin/env python3
"""Setup BigQuery dataset and tables"""

from google.cloud import bigquery
import os

PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = 'retail_branches'
LOCATION = 'asia-southeast1'

client = bigquery.Client(project=PROJECT_ID)

# Create dataset
dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
dataset = bigquery.Dataset(dataset_id)
dataset.location = LOCATION

try:
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"✅ Created dataset {dataset_id}")
except Exception as e:
    print(f"❌ Error creating dataset: {e}")

# Create tables (copy SQL from docs/DATABASE.md)
tables_sql = {
    'branches': """
        CREATE TABLE IF NOT EXISTS retail_branches.branches (
          branch_id STRING NOT NULL,
          branch_name STRING NOT NULL,
          address STRING,
          province STRING,
          district STRING,
          postal_code STRING,
          phone STRING,
          status STRING,
          dc_code STRING,
          opening_date DATE,
          created_at TIMESTAMP,
          updated_at TIMESTAMP,
          created_by STRING,
          updated_by STRING
        );
    """,
    # ... (add all other tables from DATABASE.md)
}

for table_name, sql in tables_sql.items():
    try:
        client.query(sql).result()
        print(f"✅ Created table {table_name}")
    except Exception as e:
        print(f"❌ Error creating table {table_name}: {e}")
```

**Run BigQuery setup:**
```bash
python scripts/setup_bigquery.py
```

**Create GCS bucket:**
```bash
gsutil mb -p ${PROJECT_ID} -l asia-southeast1 gs://retail-branch-documents
gsutil defacl set private gs://retail-branch-documents
gsutil versioning set on gs://retail-branch-documents
```

**Setup Google OAuth 2.0:**
1. Go to Google Cloud Console > APIs & Services > Credentials
2. Create OAuth 2.0 Client ID
3. Add redirect URIs: `http://localhost:8000/auth/callback`
4. Copy Client ID and Client Secret to `.env`

**Checkpoint:** ✅ All dependencies installed, GCP configured, credentials ready

---

## Phase 1: Core Infrastructure (2-3 วัน)

### 1.1 Configuration Module

**Create `app/config.py`:**
- Copy complete code from `docs/development/configuration.md`
- Includes Settings class with all environment variables

**Test configuration:**
```bash
python -c "from app.config import settings; print(settings.PROJECT_ID)"
```

### 1.2 BigQuery Service

**Create `app/services/bigquery_service.py`:**

```python
"""BigQuery service for database operations"""

from google.cloud import bigquery
from typing import List, Dict, Any, Optional
from app.config import settings

class BigQueryService:
    """Service for BigQuery operations"""

    def __init__(self):
        self.client = bigquery.Client(project=settings.PROJECT_ID)
        self.dataset_id = settings.DATASET_ID

    def query(self, sql: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dicts"""
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = params

        query_job = self.client.query(sql, job_config=job_config)
        results = query_job.result()

        return [dict(row) for row in results]

    def insert_rows(self, table_id: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into table"""
        full_table_id = f"{settings.PROJECT_ID}.{self.dataset_id}.{table_id}"
        table = self.client.get_table(full_table_id)
        errors = self.client.insert_rows_json(table, rows)

        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")

    def execute(self, sql: str) -> None:
        """Execute SQL without returning results"""
        query_job = self.client.query(sql)
        query_job.result()  # Wait for completion

# Global instance
bigquery_service = BigQueryService()
```

**Test BigQuery service:**

**Create `tests/unit/test_bigquery_service.py`:**
```python
import pytest
from app.services.bigquery_service import bigquery_service

def test_query_users():
    """Test querying users table"""
    results = bigquery_service.query("SELECT COUNT(*) as count FROM retail_branches.users")
    assert len(results) > 0
    assert 'count' in results[0]
```

### 1.3 Storage Service

**Create `app/services/storage_service.py`:**

```python
"""Google Cloud Storage service for file operations"""

from google.cloud import storage
from datetime import timedelta
from typing import BinaryIO
from app.config import settings
import os

class StorageService:
    """Service for GCS operations"""

    def __init__(self):
        self.client = storage.Client(project=settings.PROJECT_ID)
        self.bucket_name = settings.GCS_BUCKET
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(
        self,
        file: BinaryIO,
        folder: str,
        filename: str,
        content_type: str
    ) -> dict:
        """Upload file to GCS"""
        blob_path = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_path)

        blob.upload_from_file(file, content_type=content_type)

        return {
            'file_path': f"gs://{self.bucket_name}/{blob_path}",
            'blob_name': blob_path,
            'size': blob.size,
            'content_type': blob.content_type
        }

    def generate_signed_url(
        self,
        blob_name: str,
        expiration: int = 3600
    ) -> str:
        """Generate signed URL for download"""
        blob = self.bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration),
            method="GET"
        )

        return url

    def delete_file(self, blob_name: str) -> None:
        """Delete file from GCS"""
        blob = self.bucket.blob(blob_name)
        blob.delete()

# Global instance
storage_service = StorageService()
```

### 1.4 Base Templates

**Create `app/templates/base.html`:**

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>{% block title %}{{ settings.APP_NAME }}{% endblock %}</title>

    <!-- Tailwind CSS -->
    <link rel="stylesheet" href="{{ url_for('static', path='/css/output.css') }}">

    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    {% block body %}{% endblock %}

    <!-- JavaScript -->
    <script src="{{ url_for('static', path='/js/utils/api.js') }}"></script>
    <script src="{{ url_for('static', path='/js/utils/toast.js') }}"></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Create `app/templates/login.html`:**

```html
{% extends "base.html" %}

{% block title %}Login - {{ settings.APP_NAME }}{% endblock %}

{% block body %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">
                Retail Branch Management System
            </h2>
            <p class="mt-2 text-center text-sm text-gray-600">
                ระบบบริหารจัดการข้อมูลสาขาของร้านสะดวกซื้อ
            </p>
        </div>

        <div class="mt-8 space-y-6">
            <a href="/auth/login"
               class="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <!-- Google logo SVG -->
                </svg>
                Sign in with Google
            </a>
        </div>
    </div>
</div>
{% endblock %}
```

### 1.5 Main Application

**Create `app/main.py`:**

```python
"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
```

**Create `scripts/run_local.sh`:**
- Copy from `docs/development/configuration.md`

**Test application:**
```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

**Visit:** `http://localhost:8000/health`

**Checkpoint:** ✅ Core services working, templates rendering, Tailwind CSS compiled

---

## Phase 2: Authentication (2-3 วัน)

### 2.1 OAuth Service

**Create `app/services/oauth_service.py`:**

```python
"""Google OAuth 2.0 service"""

from authlib.integrations.starlette_client import OAuth
from app.config import settings

oauth = OAuth()

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

async def get_oauth_client():
    """Get OAuth client instance"""
    return oauth.google
```

### 2.2 Session Management

**Create `app/middleware/session.py`:**

```python
"""Session management middleware"""

from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, HTTPException
from app.config import settings

serializer = URLSafeTimedSerializer(settings.SESSION_SECRET)

def create_session(user_data: dict) -> str:
    """Create signed session token"""
    return serializer.dumps(user_data, salt='session-salt')

def verify_session(token: str) -> dict:
    """Verify and decode session token"""
    try:
        data = serializer.loads(
            token,
            salt='session-salt',
            max_age=settings.SESSION_MAX_AGE
        )
        return data
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

def get_session_user(request: Request) -> dict:
    """Get user from session cookie"""
    session_token = request.cookies.get('session')
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return verify_session(session_token)
```

### 2.3 Authentication Middleware

**Create `app/middleware/auth.py`:**

```python
"""Authentication and authorization middleware"""

from fastapi import Depends, HTTPException, Request
from app.middleware.session import get_session_user
from typing import List

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user"""
    return get_session_user(request)

async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Require admin level"""
    if current_user.get('user_level') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_team_access(team: str, min_role: str = 'viewer'):
    """Require access to specific team"""
    async def dependency(current_user: dict = Depends(get_current_user)):
        # Admin has access to everything
        if current_user.get('user_level') == 'admin':
            return current_user

        # Check team membership
        user_teams = current_user.get('teams', [])
        team_data = next((t for t in user_teams if t['team_name'] == team), None)

        if not team_data:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Not a member of {team} team"
            )

        # Check role level
        role_hierarchy = ['viewer', 'editor', 'manager']
        user_role_level = role_hierarchy.index(team_data['role'])
        required_role_level = role_hierarchy.index(min_role)

        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: {min_role} role required"
            )

        return current_user

    return dependency
```

### 2.4 Authentication Routes

**Create `app/routes/auth_routes.py`:**

```python
"""Authentication routes"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from app.services.oauth_service import oauth
from app.middleware.session import create_session
from app.services.bigquery_service import bigquery_service
from app.main import templates

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
async def login(request: Request):
    """Initiate OAuth login"""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request):
    """OAuth callback handler"""
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        email = user_info.get('email')
        name = user_info.get('name')

        # Check if user exists in database
        query = f"""
            SELECT
                u.user_id,
                u.email,
                u.name,
                u.user_level,
                u.is_active,
                ARRAY_AGG(
                    STRUCT(
                        ut.team_name,
                        ut.role
                    )
                ) as teams
            FROM retail_branches.users u
            LEFT JOIN retail_branches.user_teams ut ON u.user_id = ut.user_id
            WHERE u.email = '{email}'
              AND u.is_active = true
            GROUP BY u.user_id, u.email, u.name, u.user_level, u.is_active
        """

        results = bigquery_service.query(query)

        if not results:
            # User not authorized
            return templates.TemplateResponse(
                "unauthorized.html",
                {"request": request, "email": email}
            )

        user = results[0]

        # Update last login
        bigquery_service.execute(f"""
            UPDATE retail_branches.users
            SET last_login = CURRENT_TIMESTAMP()
            WHERE user_id = '{user['user_id']}'
        """)

        # Create session
        session_data = {
            'user_id': user['user_id'],
            'email': user['email'],
            'name': user['name'],
            'user_level': user['user_level'],
            'teams': user['teams']
        }

        session_token = create_session(session_data)

        # Set cookie and redirect to dashboard
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(
            key="session",
            value=session_token,
            httponly=True,
            secure=not settings.is_development,
            samesite='lax',
            max_age=settings.SESSION_MAX_AGE
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/login")
    response.delete_cookie("session")
    return response

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user
```

### 2.5 Update Main App

**Update `app/main.py`:**

```python
# Add after app creation
from app.routes import auth_routes

# Include routers
app.include_router(auth_routes.router)

# Root redirect to login
@app.get("/")
async def root():
    return RedirectResponse(url="/login")
```

**Checkpoint:** ✅ OAuth login working, session management functional, protected routes

---

## Phase 3: User Management (3-4 วัน)

### 3.1 User Models

**Create `app/models/user.py`:**

```python
"""User data models"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    user_level: str  # admin, manager, editor, viewer

class UserUpdate(BaseModel):
    name: Optional[str] = None
    user_level: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    user_level: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    teams: List[dict]

class UserTeamCreate(BaseModel):
    user_id: str
    team_name: str  # new_branch, legal, srd, scm
    role: str  # viewer, editor, manager
```

### 3.2 User Service

**Create `app/services/user_service.py`:**

```python
"""User management service"""

from app.services.bigquery_service import bigquery_service
from app.models.user import UserCreate, UserUpdate
from typing import List, Dict, Optional
import uuid
from datetime import datetime

class UserService:
    """Service for user management operations"""

    def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        user_level: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict:
        """Get paginated list of users"""

        # Build WHERE clause
        conditions = []
        if search:
            conditions.append(f"(u.email LIKE '%{search}%' OR u.name LIKE '%{search}%')")
        if user_level:
            conditions.append(f"u.user_level = '{user_level}'")
        if status:
            is_active = status == 'active'
            conditions.append(f"u.is_active = {is_active}")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM retail_branches.users u
            {where_clause}
        """
        total = bigquery_service.query(count_query)[0]['total']

        # Get paginated data
        offset = (page - 1) * limit
        query = f"""
            SELECT
                u.user_id,
                u.email,
                u.name,
                u.user_level,
                u.is_active,
                u.created_at,
                u.last_login,
                COUNT(ut.user_team_id) as team_count
            FROM retail_branches.users u
            LEFT JOIN retail_branches.user_teams ut ON u.user_id = ut.user_id
            {where_clause}
            GROUP BY u.user_id, u.email, u.name, u.user_level, u.is_active, u.created_at, u.last_login
            ORDER BY u.created_at DESC
            LIMIT {limit}
            OFFSET {offset}
        """

        users = bigquery_service.query(query)

        return {
            'users': users,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }

    def create_user(self, user_data: UserCreate, created_by: str) -> Dict:
        """Create new user"""
        user_id = str(uuid.uuid4())

        row = {
            'user_id': user_id,
            'email': user_data.email,
            'name': user_data.name,
            'user_level': user_data.user_level,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        bigquery_service.insert_rows('users', [row])

        return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: str) -> Dict:
        """Get user by ID with teams"""
        query = f"""
            SELECT
                u.user_id,
                u.email,
                u.name,
                u.user_level,
                u.is_active,
                u.created_at,
                u.last_login,
                ARRAY_AGG(
                    STRUCT(
                        ut.user_team_id,
                        ut.team_name,
                        ut.role,
                        ut.created_at
                    )
                ) as teams
            FROM retail_branches.users u
            LEFT JOIN retail_branches.user_teams ut ON u.user_id = ut.user_id
            WHERE u.user_id = '{user_id}'
            GROUP BY u.user_id, u.email, u.name, u.user_level, u.is_active, u.created_at, u.last_login
        """

        results = bigquery_service.query(query)
        return results[0] if results else None

    # ... (add more methods: update_user, deactivate_user, etc.)

# Global instance
user_service = UserService()
```

### 3.3 Admin Routes

**Create `app/routes/admin_routes.py`:**

```python
"""Admin routes for user and permission management"""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.middleware.auth import get_current_admin_user
from app.services.user_service import user_service
from app.models.user import UserCreate, UserUpdate
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    user_level: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """Get paginated list of users"""
    return user_service.get_users(page, limit, search, user_level, status)

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new user"""
    return user_service.create_user(user_data, current_user['user_id'])

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Get user by ID"""
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ... (add more endpoints: update, delete, permissions)
```

### 3.4 Admin Templates

**Create `app/templates/admin/users.html`:**

```html
{% extends "app_layout.html" %}

{% block title %}User Management - Admin{% endblock %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">User Management</h1>
        <button onclick="openCreateUserModal()" class="btn-primary">
            Add User
        </button>
    </div>

    <!-- Search and filters -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input type="text" id="search" placeholder="Search by email or name" class="form-input">
            <select id="user-level-filter" class="form-input">
                <option value="">All Levels</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="editor">Editor</option>
                <option value="viewer">Viewer</option>
            </select>
            <select id="status-filter" class="form-input">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
            </select>
        </div>
    </div>

    <!-- Users table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="table" id="users-table">
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Level</th>
                    <th>Teams</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="users-table-body">
                <!-- Populated by JavaScript -->
            </tbody>
        </table>
    </div>

    <!-- Pagination -->
    <div id="pagination" class="mt-4"></div>
</div>

<!-- Create User Modal -->
<div id="create-user-modal" class="hidden">
    <!-- Modal content -->
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', path='/js/admin/users.js') }}"></script>
{% endblock %}
```

### 3.5 Frontend JavaScript

**Create `static/js/admin/users.js`:**

```javascript
// User management JavaScript
let currentPage = 1;
const limit = 20;

async function loadUsers() {
    const search = document.getElementById('search').value;
    const userLevel = document.getElementById('user-level-filter').value;
    const status = document.getElementById('status-filter').value;

    const params = {
        page: currentPage,
        limit: limit
    };

    if (search) params.search = search;
    if (userLevel) params.user_level = userLevel;
    if (status) params.status = status;

    try {
        const response = await API.get('/api/admin/users', params);
        renderUsersTable(response.users);
        renderPagination(response.total_pages, response.page);
    } catch (error) {
        Toast.show('Failed to load users: ' + error.message, 'error');
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.email}</td>
            <td>${user.name}</td>
            <td><span class="badge">${user.user_level}</span></td>
            <td>${user.team_count} teams</td>
            <td>
                <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                    ${user.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${user.last_login ? formatDate(user.last_login) : 'Never'}</td>
            <td>
                <button onclick="editUser('${user.user_id}')" class="btn-sm">Edit</button>
                <button onclick="managePermissions('${user.user_id}')" class="btn-sm">Permissions</button>
            </td>
        </tr>
    `).join('');
}

// Load users on page load
document.addEventListener('DOMContentLoaded', loadUsers);

// Search and filter handlers
document.getElementById('search').addEventListener('input', debounce(loadUsers, 500));
document.getElementById('user-level-filter').addEventListener('change', loadUsers);
document.getElementById('status-filter').addEventListener('change', loadUsers);
```

**Checkpoint:** ✅ User management working, admin pages functional, CRUD operations tested

---

## Phase 4: Team Features (1-2 สัปดาห์)

### 4.1 Branch Models

**Create `app/models/branch.py`**

### 4.2 Branch Service

**Create `app/services/branch_service.py`**

### 4.3 New Branch Team Routes

**Create `app/routes/new_branch_routes.py`**

### 4.4 Legal Team Routes (ภ.พ.09, ภ.พ.20)

**Create `app/routes/legal_routes.py`**
**Create `app/routes/legal_ppp09_routes.py`**

### 4.5 SRD Team Routes

**Create `app/routes/srd_routes.py`**

### 4.6 SCM Team Routes

**Create `app/routes/scm_routes.py`**

### 4.7 Document Management

**Create `app/routes/document_routes.py`**

**Checkpoint:** ✅ All team features working, file uploads functional, permissions enforced

---

## Phase 5: Notifications & Scheduled Jobs (2-3 วัน)

### 5.1 Email Service

**Create `app/services/email_service.py`**

### 5.2 Email Templates

**Create `app/templates/emails/base_email.html`**
**Create team-specific email templates**

### 5.3 Scheduled Job Routes

**Create `app/routes/job_routes.py`**

### 5.4 Setup Cloud Scheduler

**Run `scripts/create_schedulers.sh`**

**Checkpoint:** ✅ Emails sending, scheduled jobs running, notifications working

---

## Phase 6: Security & Testing (2-3 วัน)

### 6.1 Security Middleware

**Create `app/middleware/security.py`** (CORS, CSRF, Rate limiting)

### 6.2 Security Headers

**Update `app/main.py`** with security headers

### 6.3 Write Tests

**Create tests for:**
- `tests/unit/test_services.py`
- `tests/unit/test_auth.py`
- `tests/integration/test_api.py`

### 6.4 Security Audit

Run security checks:
```bash
# Check dependencies
uv pip list --outdated

# Run tests
pytest

# Check code quality
flake8 app/
mypy app/
```

**Checkpoint:** ✅ Security implemented, tests passing, code quality good

---

## Phase 7: Deployment (1-2 วัน)

### 7.1 Build Docker Image

```bash
docker build -t retail-branch-demo .
docker run -p 8080:8080 retail-branch-demo
```

### 7.2 Setup Secret Manager

```bash
# Create secrets
echo -n "your-secret" | gcloud secrets create secret-name --data-file=-
```

### 7.3 Deploy to Cloud Run (DEV)

```bash
# Update .gitlab-ci.yml variables
# Push to main branch
# Trigger manual deploy-dev
```

### 7.4 Setup Cloud Scheduler

```bash
./scripts/create_schedulers.sh
```

### 7.5 Deploy to Production

```bash
# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Trigger manual deploy-prod
```

**Checkpoint:** ✅ Application deployed, all services running, production ready

---

## Summary Checklist

### Phase 0: Setup ✅
- [ ] Project structure created
- [ ] Configuration files in place
- [ ] Dependencies installed
- [ ] GCP configured
- [ ] BigQuery tables created
- [ ] GCS bucket created
- [ ] OAuth credentials setup

### Phase 1: Core ✅
- [ ] Configuration module working
- [ ] BigQuery service tested
- [ ] Storage service tested
- [ ] Base templates created
- [ ] Main app running

### Phase 2: Auth ✅
- [ ] OAuth login working
- [ ] Session management functional
- [ ] Protected routes working
- [ ] RBAC middleware tested

### Phase 3: Users ✅
- [ ] User CRUD operations
- [ ] Permission management
- [ ] Admin pages functional
- [ ] User service tested

### Phase 4: Teams ✅
- [ ] New Branch features
- [ ] Legal features (ภ.พ.09, ภ.พ.20)
- [ ] SRD features
- [ ] SCM features
- [ ] Document management
- [ ] File uploads working

### Phase 5: Notifications ✅
- [ ] Email service configured
- [ ] Email templates created
- [ ] Scheduled jobs working
- [ ] Cloud Scheduler setup

### Phase 6: Security ✅
- [ ] Security middleware
- [ ] Security headers
- [ ] Tests passing
- [ ] Security audit done

### Phase 7: Deployment ✅
- [ ] Docker image built
- [ ] Secrets configured
- [ ] DEV deployment successful
- [ ] PROD deployment successful
- [ ] Monitoring configured

---

## Next Steps

พร้อมเริ่ม implementation แล้ว! เริ่มจาก:

```bash
# Clone repository
git clone <repository-url>
cd retail-branch-demo

# Run setup
./scripts/setup_local.sh

# Start development
./scripts/run_local.sh
```

**ต้องการให้เริ่มทำ Phase ไหนก่อนครับ?**
