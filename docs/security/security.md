# Security

## Overview

เอกสารนี้อธิบายมาตรการความปลอดภัยที่ใช้ในระบบ Retail Branch Management System ครอบคลุมทั้ง Authentication, Authorization, Data Security, API Security และ Best Practices ต่างๆ

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Security Layers                    │
├─────────────────────────────────────────────────────┤
│ 1. Network Layer (Cloud Armor, VPC)                │
│ 2. Application Layer (HTTPS, CORS, Rate Limiting)  │
│ 3. Authentication Layer (Google OAuth 2.0)         │
│ 4. Authorization Layer (RBAC, Permissions)         │
│ 5. Data Layer (Encryption, Access Control)         │
│ 6. Audit Layer (Logging, Monitoring)              │
└─────────────────────────────────────────────────────┘
```

## 1. Authentication & Authorization

### Google OAuth 2.0 Authentication

**Implementation:**
```python
# services/oauth_service.py

from authlib.integrations.starlette_client import OAuth
import os

oauth = OAuth()

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

async def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token and return user info"""
    try:
        user_info = await oauth.google.parse_id_token(token)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Security Measures:**
- **HTTPS Only**: ใช้ HTTPS เท่านั้นสำหรับ OAuth redirect
- **State Parameter**: ป้องกัน CSRF attacks ใน OAuth flow
- **Token Validation**: ตรวจสอบ token signature และ expiry
- **Email Domain Restriction**: จำกัดเฉพาะ email domains ที่อนุญาต

**Email Domain Whitelist (Optional):**
```python
ALLOWED_EMAIL_DOMAINS = [
    'yourcompany.com',
    'example.com'
]

def verify_email_domain(email: str) -> bool:
    """Verify email domain is allowed"""
    domain = email.split('@')[1]
    return domain in ALLOWED_EMAIL_DOMAINS
```

### Session Management

**Secure Session Cookies:**
```python
# middleware/auth.py

from itsdangerous import URLSafeTimedSerializer
import os

SECRET_KEY = os.getenv('SESSION_SECRET')
serializer = URLSafeTimedSerializer(SECRET_KEY)

def create_session(user_data: dict) -> str:
    """Create signed session token"""
    return serializer.dumps(user_data, salt='session-salt')

def verify_session(token: str, max_age: int = 86400) -> dict:
    """Verify and decode session token"""
    try:
        data = serializer.loads(
            token,
            salt='session-salt',
            max_age=max_age  # 24 hours
        )
        return data
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
```

**Session Cookie Configuration:**
```python
response.set_cookie(
    key="session",
    value=session_token,
    httponly=True,        # ป้องกัน JavaScript access
    secure=True,          # HTTPS only
    samesite='Lax',      # ป้องกัน CSRF
    max_age=86400,       # 24 hours
    path='/',
    domain=None          # Same domain only
)
```

**Session Security Best Practices:**
- **Short Expiry**: Session หมดอายุใน 24 ชั่วโมง
- **Secure Flag**: ใช้เฉพาะกับ HTTPS
- **HttpOnly Flag**: ป้องกัน XSS attacks
- **SameSite**: ป้องกัน CSRF attacks
- **Regenerate Session**: สร้าง session ใหม่หลัง login

### Role-Based Access Control (RBAC)

**Permission Check Middleware:**
```python
# middleware/auth.py

from fastapi import Depends, HTTPException
from typing import List

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from session"""
    session_token = request.cookies.get('session')
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = verify_session(session_token)
    return user_data

async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Require admin level"""
    if current_user.get('user_level') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_team_access(team: str, min_role: str = 'viewer'):
    """Decorator to require team access"""
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

**Usage in Routes:**
```python
@router.get("/api/legal/ppp09")
async def get_ppp09_list(
    current_user: dict = Depends(require_team_access('legal', 'viewer'))
):
    """Legal team members can view ภ.พ.09"""
    pass

@router.post("/api/legal/ppp09")
async def create_ppp09(
    current_user: dict = Depends(require_team_access('legal', 'editor'))
):
    """Only editors and managers can create ภ.พ.09"""
    pass

@router.delete("/api/legal/ppp09/{ppp09_id}")
async def delete_ppp09(
    ppp09_id: str,
    current_user: dict = Depends(require_team_access('legal', 'manager'))
):
    """Only managers can delete ภ.พ.09"""
    pass
```

## 2. API Security

### CORS Configuration

**Secure CORS Setup:**
```python
# main.py

from fastapi.middleware.cors import CORSMiddleware

# Production: Specific origins only
ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]

# Development: Localhost
if os.getenv('ENVIRONMENT') == 'development':
    ALLOWED_ORIGINS.append("http://localhost:8000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Allow cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600  # Cache preflight requests
)
```

**CORS Best Practices:**
- **Never use `*`** สำหรับ production
- **Specific Origins**: ระบุ origins ที่อนุญาตชัดเจน
- **Allow Credentials**: เปิดเฉพาะเมื่อจำเป็น
- **Limited Methods**: อนุญาตเฉพาะ methods ที่ใช้

### CSRF Protection

**CSRF Token Implementation:**
```python
# middleware/csrf.py

from fastapi import Request, HTTPException
import secrets

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)

async def verify_csrf_token(request: Request):
    """Verify CSRF token for state-changing requests"""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token_from_header = request.headers.get('X-CSRF-Token')
        token_from_session = request.state.csrf_token

        if not token_from_header or token_from_header != token_from_session:
            raise HTTPException(status_code=403, detail="CSRF token missing or invalid")
```

**Frontend CSRF Token:**
```javascript
// Get CSRF token from meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

// Include in all API requests
const API = {
  async post(endpoint, data) {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
      },
      body: JSON.stringify(data),
      credentials: 'same-origin'
    });
    return response.json();
  }
};
```

**Template with CSRF Token:**
```html
<!-- base.html -->
<head>
  <meta name="csrf-token" content="{{ csrf_token }}">
</head>
```

### Rate Limiting

**Rate Limit Middleware:**
```python
# middleware/rate_limit.py

from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, requests: int = 100, window: int = 60):
        """
        Args:
            requests: Max requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients = defaultdict(list)

    async def check_rate_limit(self, request: Request):
        """Check if client exceeded rate limit"""
        client_ip = request.client.host
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)

        # Clean old requests
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip]
            if req_time > window_start
        ]

        # Check limit
        if len(self.clients[client_ip]) >= self.requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

        # Add current request
        self.clients[client_ip].append(now)

# Initialize rate limiter
rate_limiter = RateLimiter(requests=100, window=60)  # 100 req/min

# Apply to routes
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response
```

**Different Rate Limits per Endpoint:**
```python
# Stricter limits for sensitive endpoints
auth_rate_limiter = RateLimiter(requests=10, window=60)  # 10 login attempts/min
upload_rate_limiter = RateLimiter(requests=20, window=60)  # 20 uploads/min

@router.post("/auth/login")
async def login(request: Request):
    await auth_rate_limiter.check_rate_limit(request)
    # Login logic
    pass
```

### Input Validation

**Pydantic Models for Validation:**
```python
# models/validation.py

from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    name: constr(min_length=2, max_length=100)
    user_level: constr(regex='^(admin|manager|editor|viewer)$')

    @validator('name')
    def sanitize_name(cls, v):
        """Remove potentially dangerous characters"""
        # Allow only alphanumeric, spaces, Thai characters
        pattern = r'^[a-zA-Z0-9ก-๙\s\-\.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid characters in name')
        return v

class BranchCreate(BaseModel):
    branch_id: constr(regex='^BR[0-9]{3,6}$')  # BR001, BR000123
    branch_name: constr(min_length=2, max_length=200)
    phone: Optional[constr(regex='^[0-9\-\+\(\)\s]{8,20}$')]
    postal_code: constr(regex='^\d{5}$')  # 5 digits

    @validator('branch_id')
    def validate_branch_id(cls, v):
        # Additional validation logic
        return v.upper()
```

**SQL Injection Prevention:**
```python
# ✅ GOOD: Use parameterized queries
def get_branch_by_id(branch_id: str):
    query = """
        SELECT * FROM retail_branches.branches
        WHERE branch_id = @branch_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("branch_id", "STRING", branch_id)
        ]
    )
    results = client.query(query, job_config=job_config)
    return results

# ❌ BAD: Never use string concatenation
def get_branch_by_id_unsafe(branch_id: str):
    query = f"SELECT * FROM branches WHERE branch_id = '{branch_id}'"
    # Vulnerable to SQL injection!
```

**XSS Prevention:**
```python
# Template auto-escaping (Jinja2)
# {{ variable }} is automatically escaped

# For raw HTML (use carefully!)
# {{ variable|safe }}

# Python-side sanitization
import bleach

def sanitize_html(html: str) -> str:
    """Remove dangerous HTML/JavaScript"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    allowed_attrs = {'a': ['href', 'title']}

    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
```

## 3. Data Security

### Encryption at Rest

**BigQuery Encryption:**
- Default: Google-managed encryption keys
- Optional: Customer-managed encryption keys (CMEK)

**GCS Bucket Encryption:**
```bash
# Enable encryption for GCS bucket
gsutil encryption set \
  -k projects/PROJECT_ID/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY \
  gs://bucket-name
```

### Encryption in Transit

**Force HTTPS:**
```python
# middleware/https.py

from fastapi import Request
from fastapi.responses import RedirectResponse

@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    """Redirect HTTP to HTTPS"""
    if request.url.scheme == "http" and not request.url.hostname == "localhost":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)

    response = await call_next(request)
    return response
```

**Security Headers:**
```python
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)

    # Security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response
```

### Sensitive Data Handling

**Environment Variables (Never commit to Git):**
```bash
# .env file (add to .gitignore)
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
SESSION_SECRET=xxx
SENDGRID_API_KEY=xxx
```

**Google Secret Manager (Production):**
```python
# services/secrets_service.py

from google.cloud import secretmanager

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """Get secret from Google Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv('PROJECT_ID')

    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")

# Usage
GOOGLE_CLIENT_SECRET = get_secret("oauth_client_secret")
SENDGRID_API_KEY = get_secret("sendgrid_api_key")
```

**Secrets in Cloud Run:**
```yaml
# In .gitlab-ci.yml deploy stage
gcloud run deploy retail-branch-demo \
  --set-secrets "GOOGLE_CLIENT_SECRET=oauth_client_secret:latest" \
  --set-secrets "SENDGRID_API_KEY=sendgrid_api_key:latest" \
  --set-secrets "SESSION_SECRET=session_secret:latest"
```

**Data Masking in Logs:**
```python
import re

def mask_sensitive_data(text: str) -> str:
    """Mask sensitive data in logs"""
    # Mask email
    text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                  r'\1***@\2', text)

    # Mask phone numbers
    text = re.sub(r'\d{3}-\d{3}-\d{4}', '***-***-****', text)

    # Mask credit card (if any)
    text = re.sub(r'\d{4}-\d{4}-\d{4}-\d{4}', '****-****-****-****', text)

    return text

# Usage in logging
print(mask_sensitive_data(f"User email: {user_email}"))
```

## 4. File Upload Security

### File Validation

**Comprehensive File Validation:**
```python
# services/file_validation.py

import magic
from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = {
    'application/pdf': ['.pdf'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""

    # Check file size
    contents = await file.read()
    file_size = len(contents)
    await file.seek(0)  # Reset file pointer

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if not any(file_ext in exts for exts in ALLOWED_MIME_TYPES.values()):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {file_ext}"
        )

    # Check MIME type (magic number)
    mime = magic.from_buffer(contents, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type detected: {mime}"
        )

    # Verify extension matches MIME type
    if file_ext not in ALLOWED_MIME_TYPES[mime]:
        raise HTTPException(
            status_code=400,
            detail="File extension does not match file content"
        )

    return True

async def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext

    return filename
```

### Virus Scanning (Optional)

**ClamAV Integration:**
```python
# services/virus_scan.py

import clamd

def scan_file_for_virus(file_path: str) -> bool:
    """Scan file for viruses using ClamAV"""
    try:
        cd = clamd.ClamdUnixSocket()
        result = cd.scan(file_path)

        if result[file_path][0] == 'FOUND':
            return False  # Virus found
        return True  # Clean

    except Exception as e:
        # Log error
        print(f"Virus scan failed: {str(e)}")
        # Fail closed - reject file if scan fails
        return False
```

### Secure File Storage

**GCS Bucket Configuration:**
```bash
# Create bucket with restricted access
gsutil mb -p ${PROJECT_ID} -l asia-southeast1 gs://retail-branch-documents

# Set bucket-level IAM
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin \
  gs://retail-branch-documents

# Disable public access
gsutil iam ch allUsers:objectViewer gs://retail-branch-documents
gsutil defacl set private gs://retail-branch-documents

# Enable versioning (for recovery)
gsutil versioning set on gs://retail-branch-documents

# Set lifecycle (delete files older than 7 years)
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 2555}
      }
    ]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://retail-branch-documents
```

**Signed URLs for Download:**
```python
def generate_download_url(file_path: str, expiration: int = 3600) -> str:
    """Generate time-limited signed URL"""
    blob = storage_client.bucket(bucket_name).blob(file_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(seconds=expiration),
        method="GET"
    )

    return url

# Usage
@router.get("/api/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Check permissions
    document = get_document_by_id(document_id)
    if not user_has_access(current_user, document):
        raise HTTPException(status_code=403, detail="Access denied")

    # Generate signed URL (valid for 1 hour)
    download_url = generate_download_url(document['file_path'], expiration=3600)

    return {"download_url": download_url}
```

## 5. Audit & Compliance

### Comprehensive Audit Logging

**Log All Security Events:**
```python
# services/audit_service.py

from datetime import datetime
import json

def log_security_event(
    event_type: str,
    user_id: str,
    user_email: str,
    details: dict,
    request: Request,
    status: str = "success"
):
    """Log security-related events"""

    log_data = {
        'log_id': str(uuid.uuid4()),
        'event_type': event_type,  # login, logout, permission_change, etc.
        'user_id': user_id,
        'user_email': user_email,
        'details': json.dumps(details),
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'status': status,
        'timestamp': datetime.now().isoformat()
    }

    # Insert to BigQuery audit_logs table
    bigquery_service.insert_rows(
        table_id="retail_branches.audit_logs",
        rows=[log_data]
    )

# Usage
@router.post("/auth/login")
async def login(request: Request):
    # ... login logic ...

    log_security_event(
        event_type="login",
        user_id=user['user_id'],
        user_email=user['email'],
        details={'method': 'google_oauth'},
        request=request,
        status="success"
    )
```

**Failed Login Attempts:**
```python
@router.post("/auth/login")
async def login(request: Request):
    try:
        # Login logic
        pass
    except Exception as e:
        # Log failed attempt
        log_security_event(
            event_type="login_failed",
            user_id="unknown",
            user_email=request_data.get('email', 'unknown'),
            details={'error': str(e)},
            request=request,
            status="failed"
        )

        # Check for brute force
        recent_failures = get_recent_failed_logins(
            ip=request.client.host,
            minutes=15
        )

        if len(recent_failures) >= 5:
            # Alert admins
            send_security_alert(
                alert_type="brute_force_attempt",
                ip=request.client.host,
                failures=len(recent_failures)
            )

            # Block IP temporarily
            block_ip(request.client.host, duration=3600)
```

### Data Retention Policies

**Audit Log Retention:**
```sql
-- Partition audit_logs by date
CREATE TABLE retail_branches.audit_logs (
  log_id STRING NOT NULL,
  event_type STRING NOT NULL,
  user_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  ...
)
PARTITION BY DATE(timestamp)
OPTIONS(
  partition_expiration_days=2555  -- 7 years
);
```

**Data Deletion Compliance:**
```python
# GDPR/PDPA: User data deletion
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR/PDPA compliance)"""

    # Delete user record
    bigquery_service.execute(f"""
        DELETE FROM retail_branches.users
        WHERE user_id = '{user_id}'
    """)

    # Delete user permissions
    bigquery_service.execute(f"""
        DELETE FROM retail_branches.user_teams
        WHERE user_id = '{user_id}'
    """)

    # Anonymize audit logs (keep for compliance)
    bigquery_service.execute(f"""
        UPDATE retail_branches.audit_logs
        SET user_email = 'deleted@example.com',
            ip_address = '0.0.0.0',
            user_agent = 'deleted'
        WHERE user_id = '{user_id}'
    """)
```

## 6. Network Security

### Cloud Armor (DDoS Protection)

**Setup Cloud Armor:**
```bash
# Create security policy
gcloud compute security-policies create retail-branch-policy \
  --description "Security policy for retail branch app"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy retail-branch-policy \
  --expression "true" \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 100 \
  --rate-limit-threshold-interval-sec 60 \
  --ban-duration-sec 600

# Add IP blacklist rule
gcloud compute security-policies rules create 2000 \
  --security-policy retail-branch-policy \
  --expression "origin.ip == '192.0.2.1'" \
  --action "deny-403"

# Attach to load balancer backend
gcloud compute backend-services update retail-branch-backend \
  --security-policy retail-branch-policy
```

### VPC Security

**Service Account Permissions:**
```bash
# Principle of least privilege
# Cloud Run service account should only have necessary permissions

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.objectAdmin"

# Do NOT grant overly broad roles like "roles/editor" or "roles/owner"
```

## 7. Security Best Practices

### 1. Principle of Least Privilege
- ให้สิทธิ์เฉพาะที่จำเป็น
- ใช้ role-based access control
- Review permissions เป็นประจำ

### 2. Defense in Depth
- หลายชั้นของการป้องกัน
- ไม่พึ่งพา security measure เพียงอย่างเดียว

### 3. Secure by Default
- Default settings ต้องปลอดภัย
- Opt-in สำหรับ features ที่มีความเสี่ยง

### 4. Keep Software Updated
- อัพเดท dependencies เป็นประจำ
- Monitor security advisories
- Automated dependency scanning

### 5. Security Testing
- Penetration testing
- Vulnerability scanning
- Code security review

### 6. Incident Response Plan
- มีแผนรับมือเมื่อเกิด security incident
- Contact list สำหรับ emergency
- Backup และ recovery procedures

## 8. Security Checklist

**Before Production:**
- [ ] HTTPS enabled และบังคับใช้
- [ ] OAuth 2.0 configured correctly
- [ ] Session cookies: httponly, secure, samesite
- [ ] CORS configured (no wildcard `*`)
- [ ] CSRF protection enabled
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (template escaping)
- [ ] File upload validation (size, type, content)
- [ ] Secrets in Secret Manager (not in code)
- [ ] Security headers configured
- [ ] Audit logging enabled
- [ ] Error messages don't leak sensitive info
- [ ] Service account least privilege
- [ ] Cloud Armor configured
- [ ] Backup strategy in place
- [ ] Incident response plan documented

## 9. Security Monitoring

### Cloud Monitoring Alerts

**Create Security Alerts:**
```bash
# Alert on multiple failed login attempts
gcloud alpha monitoring policies create \
  --notification-channels=${CHANNEL_ID} \
  --display-name="Failed Login Attempts" \
  --condition-display-name="5+ failed logins in 5 minutes" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s

# Alert on unauthorized access attempts
gcloud alpha monitoring policies create \
  --notification-channels=${CHANNEL_ID} \
  --display-name="403 Forbidden Errors" \
  --condition-display-name="Multiple 403 errors" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s
```

### Log Analysis

**Query Suspicious Activity:**
```sql
-- Failed login attempts by IP
SELECT
  ip_address,
  COUNT(*) as failed_attempts,
  MAX(timestamp) as last_attempt
FROM retail_branches.audit_logs
WHERE event_type = 'login_failed'
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY ip_address
HAVING failed_attempts > 10
ORDER BY failed_attempts DESC;

-- Unusual permission changes
SELECT
  user_email,
  action_type,
  resource_id,
  timestamp
FROM retail_branches.audit_logs
WHERE action_type IN ('permission_add', 'permission_remove', 'user_deactivate')
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY timestamp DESC;
```

## Related Documentation

- [oauth.md](../auth/oauth.md) - OAuth 2.0 implementation
- [user-management.md](../features/user-management.md) - User permissions
- [audit-logs.md](../features/audit-logs.md) - Audit logging
- [file-upload.md](../development/file-upload.md) - File upload security
- [cicd.md](../deployment/cicd.md) - Secure deployment
- [api-standards.md](../development/api-standards.md) - API security standards
