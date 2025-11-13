# Retail Branch Management System

## Project Overview

ระบบบริหารจัดการข้อมูลสาขาของร้านสะดวกซื้อ (Retail Branch Management System) เป็น Web Application ที่ออกแบบมาเพื่อให้หลายทีมงานสามารถจัดการข้อมูลสาขาได้อย่างมีประสิทธิภาพ โดยแต่ละทีมจะเห็นเฉพาะเมนูและข้อมูลที่เกี่ยวข้องกับทีมของตนเองเท่านั้น

## Features & Requirements

### Core Features
- **User Authentication (Google OAuth 2.0)**: ระบบ login เข้าใช้งานผ่าน Google Account โดยผู้ใช้ทุกคนต้อง login ก่อนเข้าใช้งานระบบ
- **CRUD Operations**: สามารถเพิ่ม แก้ไข และลบข้อมูลสาขาได้
- **Multi-Team Access**: รองรับการเข้าใช้งานของหลายทีม โดยแต่ละทีมมีสิทธิ์และเห็นเมนูเฉพาะของตนเอง
- **Branch Data Management**: จัดการข้อมูลสาขา เช่น รหัสสาขา, ชื่อสาขา, ที่อยู่
- **Document Management**: จัดเก็บและจัดการเอกสารที่เกี่ยวข้องกับแต่ละสาขา
- **Responsive Design**: รองรับการใช้งานบนทุกอุปกรณ์ (Desktop, Tablet, Mobile)

### Team Roles & Permissions

| ทีม | หน้าที่ | ข้อมูลที่เข้าถึง |
|-----|---------|-----------------|
| **ทีมสาขาใหม่** | จัดการข้อมูลการเปิดสาขาใหม่ | ข้อมูลสาขาที่กำลังเปิดใหม่, สถานะการเปิดสาขา, timeline |
| **ทีมกฎหมาย** | จัดการเอกสารทางกฎหมาย | เอกสารสัญญา, ใบอนุญาต, เอกสารกฎหมายของแต่ละสาขา |
| **ทีม SRD** | จัดการเอกสาร layout | แปลนผัง, layout ร้าน, floor plan ของแต่ละสาขา |
| **ทีม SCM** | จัดการข้อมูล DC | ข้อมูล Distribution Center ที่รับผิดชอบแต่ละสาขา |

## Tech Stack

### Backend
- **Python 3.12**: ภาษาหลักในการพัฒนา
- **Framework**: FastAPI - modern, fast, async web framework
- **Authentication**: Google OAuth 2.0 สำหรับ login
- **BigQuery**: Database หลักสำหรับเก็บข้อมูลสาขา
- **Google Cloud Storage (GCS)**: เก็บไฟล์เอกสาร
- **Uvicorn**: ASGI server สำหรับ production
- **UV**: Package manager สำหรับจัดการ Python dependencies

### Frontend
- **HTML5/CSS3**: โครงสร้างและการออกแบบ
- **Vanilla JavaScript**: เพิ่มความเป็น dynamic
- **Tailwind CSS**: Utility-first CSS framework สำหรับ responsive design

### Infrastructure
- **Google Cloud Run**: สำหรับ deployment
- **Service Account**: สำหรับ authentication กับ GCP services
- **Docker**: Container สำหรับการ deploy (ใช้ UV package manager)
- **GitLab CI/CD**: Automated deployment pipeline

## Architecture

### System Architecture
```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Cloud Run      │
│  (Web App)      │
└────┬───────┬────┘
     │       │
     │       └──────────┐
     ▼                  ▼
┌──────────┐    ┌──────────────┐
│ BigQuery │    │     GCS      │
│ (Data)   │    │  (Files)     │
└──────────┘    └──────────────┘
```

### Application Structure
```
retail-branch-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration settings
│   ├── models/                 # Data models with type hints
│   │   ├── __init__.py
│   │   ├── branch.py
│   │   └── document.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── bigquery_service.py
│   │   ├── storage_service.py
│   │   └── oauth_service.py    # Google OAuth service
│   ├── routes/                 # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # OAuth routes
│   │   ├── branch_routes.py
│   │   └── document_routes.py
│   ├── middleware/             # Authentication & Authorization
│   │   ├── __init__.py
│   │   └── auth.py
│   └── templates/              # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html          # OAuth login page
│       └── teams/
│           ├── new_branch.html
│           ├── legal.html
│           ├── srd.html
│           └── scm.html
├── static/
│   ├── css/
│   │   ├── input.css            # Tailwind input
│   │   └── output.css           # Tailwind compiled output
│   └── js/
│       └── app.js
├── scripts/
│   ├── setup_local.sh          # Setup local environment with UV
│   └── run_local.sh            # Run local development server
├── tests/
│   ├── __init__.py
│   └── test_services.py
├── Dockerfile
├── .gitlab-ci.yml              # GitLab CI/CD pipeline
├── requirements.txt
├── pyproject.toml              # UV configuration
├── package.json                # Node.js for Tailwind CSS
├── tailwind.config.js          # Tailwind configuration
├── .env.example
├── .dockerignore
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Database Schema (BigQuery)

### Dataset: `retail_branches`

#### Table: `branches`
```sql
CREATE TABLE retail_branches.branches (
  branch_id STRING NOT NULL,           -- รหัสสาขา
  branch_name STRING NOT NULL,         -- ชื่อสาขา
  address STRING,                      -- ที่อยู่
  province STRING,                     -- จังหวัด
  district STRING,                     -- เขต/อำเภอ
  postal_code STRING,                  -- รหัสไปรษณีย์
  phone STRING,                        -- เบอร์โทรศัพท์
  status STRING,                       -- สถานะ (active, opening, closed)
  dc_code STRING,                      -- รหัส Distribution Center
  opening_date DATE,                   -- วันที่เปิดสาขา
  created_at TIMESTAMP,                -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                -- วันที่แก้ไขล่าสุด
  created_by STRING,                   -- ผู้สร้าง
  updated_by STRING                    -- ผู้แก้ไข
);
```

#### Table: `documents`
```sql
CREATE TABLE retail_branches.documents (
  document_id STRING NOT NULL,         -- รหัสเอกสาร
  branch_id STRING NOT NULL,           -- รหัสสาขาที่เกี่ยวข้อง
  document_type STRING NOT NULL,       -- ประเภทเอกสาร (legal, layout, etc.)
  document_name STRING NOT NULL,       -- ชื่อเอกสาร
  file_path STRING NOT NULL,           -- path ใน GCS
  file_size INT64,                     -- ขนาดไฟล์ (bytes)
  mime_type STRING,                    -- ประเภทไฟล์
  team STRING NOT NULL,                -- ทีมที่รับผิดชอบ
  uploaded_at TIMESTAMP,               -- วันที่อัพโหลด
  uploaded_by STRING                   -- ผู้อัพโหลด
);
```

#### Table: `users`
```sql
CREATE TABLE retail_branches.users (
  user_id STRING NOT NULL,             -- รหัสผู้ใช้
  email STRING NOT NULL,               -- อีเมล
  name STRING NOT NULL,                -- ชื่อ
  team STRING NOT NULL,                -- ทีมที่สังกัด
  role STRING NOT NULL,                -- บทบาท (viewer, editor, admin)
  is_active BOOLEAN,                   -- สถานะการใช้งาน
  created_at TIMESTAMP,                -- วันที่สร้าง
  last_login TIMESTAMP                 -- เข้าสู่ระบบล่าสุด
);
```

## User Authentication (Google OAuth 2.0)

ระบบใช้ **Google OAuth 2.0** สำหรับการ login เข้าใช้งานของผู้ใช้ทุกคน โดยผู้ใช้จะต้อง login ด้วย Google Account ก่อนเข้าใช้งานระบบ ซึ่งจะช่วยให้:
- ไม่ต้องสร้างและจัดการ password เอง (ใช้ Google authentication)
- รองรับ Single Sign-On (SSO)
- ปลอดภัยและเชื่อถือได้ (Google's security)
- ตรวจสอบสิทธิ์ผู้ใช้จาก email domain

### Login Page Design

หน้า Login (`/login`) เป็นหน้าแรกที่ผู้ใช้เข้าถึงเมื่อยังไม่ได้ login:

**หน้า Login จะประกอบด้วย:**
- Logo และชื่อระบบ "Retail Branch Management System"
- คำอธิบายสั้นๆ เกี่ยวกับระบบ
- ปุ่ม "Sign in with Google" พร้อม Google logo
- Footer พร้อม copyright information
- Responsive design สำหรับทุกอุปกรณ์

**UI/UX:**
- ใช้ Tailwind CSS เพื่อ clean และ modern design
- Centered layout พร้อม card/container สำหรับ login form
- Loading state เมื่อกำลัง redirect ไป Google
- Error message หากการ login ล้มเหลว

### Setup OAuth Client
1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
2. เปิด **APIs & Services** > **Credentials**
3. สร้าง **OAuth 2.0 Client ID** (Application type: Web application)
4. ตั้งค่า **Authorized redirect URIs**:
   - Development: `http://localhost:8000/auth/callback`
   - Production: `https://your-domain.run.app/auth/callback`
5. บันทึก **Client ID** และ **Client Secret**

### Environment Variables for OAuth
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-key
```

### User Authentication Flow
1. **ผู้ใช้เข้าหน้า Login**: เข้าที่ `/` หรือ `/login`
2. **กด "Sign in with Google"**: คลิกปุ่ม login
3. **Redirect to Google**: ระบบ redirect ไปยัง Google OAuth consent screen
4. **ผู้ใช้เลือก Google Account**: เลือก account และอนุมัติการเข้าถึงข้อมูล
5. **Google Callback**: Google redirect กลับมาที่ `/auth/callback` พร้อม authorization code
6. **Exchange Token**: Backend แลก authorization code เป็น access token
7. **Get User Info**: ดึงข้อมูลผู้ใช้จาก Google API (email, name, picture)
8. **Verify User**: ตรวจสอบ email กับ BigQuery (table: `users`)
   - ถ้ามี user ในระบบ → อนุญาตให้ login
   - ถ้าไม่มี → แสดง error "Unauthorized user"
9. **Create Session**: สร้าง session cookie สำหรับ user
10. **Update Last Login**: อัพเดท `last_login` timestamp ใน BigQuery
11. **Redirect to Dashboard**: ส่งผู้ใช้ไปหน้าแรกตาม team ของ user

### Session Management

**Session Storage:**
- ใช้ **itsdangerous** สำหรับ signed session cookies
- เก็บข้อมูล: `user_id`, `email`, `name`, `team`, `role`
- Session timeout: 24 ชั่วโมง (configurable)

**Session Cookie Settings:**
- `httponly=True`: ป้องกัน XSS attacks
- `secure=True`: ใช้ HTTPS only (production)
- `samesite='Lax'`: ป้องกัน CSRF attacks

### Protected Routes

**Route Protection:**
- ทุก route (ยกเว้น `/login` และ `/auth/callback`) ต้อง login ก่อน
- Middleware ตรวจสอบ session cookie ทุก request
- ถ้าไม่มี session → redirect to `/login`
- ถ้า session หมดอายุ → redirect to `/login` พร้อม message

**Team-Based Access Control:**
- ตรวจสอบ `team` จาก session
- แสดงเฉพาะเมนูและข้อมูลที่ team มีสิทธิ์เข้าถึง
- ถ้าเข้าถึง route ที่ไม่มีสิทธิ์ → แสดง 403 Forbidden

### Logout

**Logout Flow:**
1. ผู้ใช้คลิก "Logout"
2. ลบ session cookie
3. (Optional) Revoke Google access token
4. Redirect to `/login`

## Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ (สำหรับ Tailwind CSS)
- UV Package Manager

### Install UV Package Manager
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Script (scripts/setup_local.sh)
```bash
#!/bin/bash

# Install UV if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment with UV
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
uv pip install -r requirements.txt

# Install Node.js dependencies for Tailwind CSS
echo "Installing Node.js dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

# Copy .env.example to .env
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your credentials"
fi

echo "Setup complete! Run './scripts/run_local.sh' to start the server"
```

### Run Script (scripts/run_local.sh)
```bash
#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run Tailwind CSS in watch mode (background)
npm run dev &
TAILWIND_PID=$!

# Run FastAPI development server
echo "Starting FastAPI development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Cleanup on exit
trap "kill $TAILWIND_PID" EXIT
```

### Quick Start
```bash
# Setup environment
chmod +x scripts/*.sh
./scripts/setup_local.sh

# Run development server
./scripts/run_local.sh
```

## CI/CD Pipeline (GitLab CI)

### .gitlab-ci.yml
```yaml
stages:
  - build
  - deploy-dev
  - deploy-prod

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_NAME: gcr.io/${GCP_PROJECT_ID}/retail-branch-demo

# Build Docker image
build:
  stage: build
  image: google/cloud-sdk:alpine
  services:
    - docker:dind
  before_script:
    - echo $GCP_SERVICE_KEY | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud auth configure-docker
  script:
    - docker build -t ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} .
    - docker tag ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} ${IMAGE_NAME}:latest
    - docker push ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}
    - docker push ${IMAGE_NAME}:latest
  only:
    - main
    - tags

# Deploy to DEV (manual trigger on main branch)
deploy-dev:
  stage: deploy-dev
  image: google/cloud-sdk:alpine
  before_script:
    - echo $GCP_SERVICE_KEY_DEV | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID_DEV
  script:
    - |
      gcloud run deploy retail-branch-demo \
        --image ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} \
        --platform managed \
        --region asia-southeast1 \
        --allow-unauthenticated \
        --service-account ${SERVICE_ACCOUNT_DEV} \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_DEV},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_DEV}" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest"
  when: manual
  only:
    - main
  environment:
    name: development
    url: https://retail-branch-demo-dev-xxxxxxxxxx-as.a.run.app

# Deploy to PROD (manual trigger on tags only)
deploy-prod:
  stage: deploy-prod
  image: google/cloud-sdk:alpine
  before_script:
    - echo $GCP_SERVICE_KEY_PROD | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID_PROD
  script:
    - |
      gcloud run deploy retail-branch-demo \
        --image ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} \
        --platform managed \
        --region asia-southeast1 \
        --allow-unauthenticated \
        --service-account ${SERVICE_ACCOUNT_PROD} \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_PROD},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_PROD}" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest"
  when: manual
  only:
    - tags
  environment:
    name: production
    url: https://retail-branch-demo-xxxxxxxxxx-as.a.run.app
```

### GitLab CI/CD Variables
ตั้งค่า variables ใน GitLab Project Settings > CI/CD > Variables:

**General:**
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCP_SERVICE_KEY`: Service Account Key (base64 encoded) สำหรับ build

**Development:**
- `GCP_PROJECT_ID_DEV`: GCP Project ID สำหรับ dev
- `GCP_SERVICE_KEY_DEV`: Service Account Key (base64) สำหรับ dev
- `SERVICE_ACCOUNT_DEV`: Service Account email สำหรับ Cloud Run dev
- `GCS_BUCKET_DEV`: GCS Bucket สำหรับ dev

**Production:**
- `GCP_PROJECT_ID_PROD`: GCP Project ID สำหรับ prod
- `GCP_SERVICE_KEY_PROD`: Service Account Key (base64) สำหรับ prod
- `SERVICE_ACCOUNT_PROD`: Service Account email สำหรับ Cloud Run prod
- `GCS_BUCKET_PROD`: GCS Bucket สำหรับ prod

### Deployment Workflow
1. **Development**: Push to `main` branch → Build → Manual deploy to DEV
2. **Production**: Create tag (e.g., `v1.0.0`) → Build → Manual deploy to PROD

```bash
# Deploy to production
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Dockerfile with UV Package Manager

### Dockerfile
```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./static ./static

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### .dockerignore
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
*.egg-info/
dist/
build/
*.md
.env
.env.local
node_modules/
static/css/input.css
tests/
```

### pyproject.toml
```toml
[project]
name = "retail-branch-demo"
version = "1.0.0"
description = "Retail Branch Management System"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.121.1",
    "uvicorn==0.38.0",
    "jinja2==3.1.6",
    "authlib==1.6.5",
    "itsdangerous==2.2.0",
    "google-cloud-bigquery==3.38.0",
    "google-cloud-storage==3.5.0",
    "python-dotenv==1.2.1",
    "pytest==9.0.1",
    "httpx==0.27.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []
```

## Deployment (Google Cloud Run)

### Prerequisites
- Google Cloud Project
- Service Account with permissions:
  - BigQuery Data Editor
  - BigQuery Job User
  - Storage Object Admin
- Service Account Key JSON

### Environment Variables
```bash
# Google Cloud Platform
PROJECT_ID=your-gcp-project-id
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-key-min-32-chars
```

### Deployment Steps
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run with service account
4. Configure environment variables
5. Set up IAM permissions

## Development Guidelines

### Code Style
- **PEP 8 Compliance**: ใช้ PEP 8 style guide อย่างเคร่งครัด
- **Type Hints**: ใช้ type hints ทุก function และ method
- **Docstrings**: เขียน docstrings สำหรับ functions และ classes
- **Keep It Simple**: เน้นความเรียบง่าย ใช้ library น้อยที่สุด
- **Readability**: code ต้องอ่านง่าย ตั้งชื่อตัวแปรให้สื่อความหมาย

### Example Code Style
```python
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/branches")
async def get_branches_by_team(
    team: str = Query(..., description="ชื่อทีม (new_branch, legal, srd, scm)"),
    status: Optional[str] = Query(None, description="สถานะสาขา (active, opening, closed)")
) -> List[Dict[str, str]]:
    """
    ดึงข้อมูลสาขาตามทีมที่รับผิดชอบ

    Args:
        team: ชื่อทีม
        status: สถานะสาขา - optional

    Returns:
        List of branch dictionaries
    """
    # Implementation here
    pass
```

### Testing
- เขียน unit tests สำหรับ services
- เขียน integration tests สำหรับ API endpoints
- ใช้ pytest เป็น testing framework

### Security Considerations
- ใช้ Service Account แทนการใช้ API keys
- Validate input ทุกครั้งก่อนส่งไป BigQuery
- ตรวจสอบสิทธิ์การเข้าถึงตาม team
- ไม่เก็บ credentials ใน code หรือ git
- ใช้ environment variables สำหรับ sensitive data

## Frontend Setup (Tailwind CSS)

### package.json
```json
{
  "name": "retail-branch-demo",
  "version": "1.0.0",
  "scripts": {
    "dev": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0"
  }
}
```

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### static/css/input.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Minimal Dependencies (requirements.txt)
```txt
fastapi==0.121.1                # Modern async web framework
uvicorn==0.38.0                 # ASGI server for production
jinja2==3.1.6                   # Template engine
authlib==1.6.5                  # OAuth client library
itsdangerous==2.2.0             # Secure session management
google-cloud-bigquery==3.38.0   # BigQuery client
google-cloud-storage==3.5.0     # GCS client
python-dotenv==1.2.1            # Environment variables
pytest==9.0.1                   # Testing framework
httpx==0.27.0                   # HTTP client for OAuth (required by authlib)
```

## Next Steps

1. สร้างโครงสร้างโปรเจกต์ตาม Application Structure
2. สร้าง local development scripts (setup_local.sh, run_local.sh)
3. ติดตั้ง UV package manager
4. ติดตั้ง Python dependencies ด้วย UV (requirements.txt)
5. ติดตั้ง Node.js และ setup Tailwind CSS
6. ตั้งค่า Google OAuth 2.0 Client ID
7. ตั้งค่า BigQuery dataset และสร้าง tables
8. สร้าง GCS bucket สำหรับเก็บเอกสาร
9. พัฒนา backend services (BigQuery, GCS, OAuth)
10. สร้าง API routes สำหรับ authentication และ CRUD operations (FastAPI)
11. พัฒนา frontend (HTML templates + Tailwind CSS + OAuth login)
12. ใส่ระบบ authorization ตาม team roles
13. เขียน tests
14. สร้าง Dockerfile (with UV package manager)
15. สร้าง .gitlab-ci.yml สำหรับ CI/CD pipeline
16. ตั้งค่า GitLab CI/CD variables
17. Deploy ไปยัง Cloud Run (DEV)
18. ทดสอบระบบบน DEV environment
19. สร้าง tag และ deploy ไปยัง PROD
20. ทดสอบระบบบน PROD environment

## Notes

- ระบบนี้เน้นความเรียบง่ายและประสิทธิภาพ
- **ผู้ใช้ทุกคนต้อง login ผ่าน Google OAuth 2.0 ก่อนเข้าใช้งาน**
- ใช้ FastAPI เป็น web framework (modern, async, fast)
- ใช้ Tailwind CSS สำหรับ responsive UI
- ใช้ Google OAuth 2.0 สำหรับ user authentication และ login
- ใช้ UV package manager สำหรับจัดการ Python dependencies (เร็วกว่า pip)
- ใช้ BigQuery เป็น database หลัก (serverless, scalable)
- ใช้ GCS สำหรับเก็บไฟล์ขนาดใหญ่
- Deploy บน Cloud Run (serverless, auto-scaling)
- ใช้ GitLab CI/CD สำหรับ automated deployment
- แต่ละทีมมี view และ permissions แยกกัน
- Manual deployment trigger สำหรับทั้ง DEV และ PROD
- Session-based authentication พร้อม secure cookies
- Code ต้องอ่านง่าย maintain ง่าย
- ใช้ library เวอร์ชันล่าสุดจาก PyPI
