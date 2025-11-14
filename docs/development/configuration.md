# Configuration Files

## Overview

เอกสารนี้รวบรวม configuration files ทั้งหมดที่จำเป็นสำหรับ Retail Branch Management System พร้อมคำอธิบายและตัวอย่างการใช้งาน

## File Structure

```
retail-branch-demo/
├── .env.example              # Environment variables template
├── .env                      # Environment variables (gitignored)
├── .gitignore                # Git ignore patterns
├── .dockerignore             # Docker ignore patterns
├── config.py                 # Application configuration
├── requirements.txt          # Python dependencies
├── pyproject.toml            # UV package manager config
├── package.json              # Node.js dependencies (Tailwind)
├── tailwind.config.js        # Tailwind CSS configuration
├── Dockerfile                # Container configuration
├── .gitlab-ci.yml            # GitLab CI/CD pipeline
└── scripts/
    ├── setup_local.sh        # Local development setup
    └── run_local.sh          # Run local development server
```

## 1. Environment Variables

### .env.example

```bash
# .env.example
# Copy this file to .env and update with your credentials
# DO NOT commit .env to git!

# ============================================================================
# Google Cloud Platform
# ============================================================================
PROJECT_ID=your-gcp-project-id
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# ============================================================================
# Google OAuth 2.0
# ============================================================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

# Production:
# OAUTH_REDIRECT_URI=https://your-domain.run.app/auth/callback

# ============================================================================
# Session Management
# ============================================================================
SESSION_SECRET=your-random-secret-key-min-32-characters-long
SESSION_MAX_AGE=86400  # 24 hours in seconds

# ============================================================================
# Email Service (SendGrid)
# ============================================================================
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@retailbranch.com
FROM_NAME=Retail Branch System
ENABLE_EMAIL_NOTIFICATIONS=true

# ============================================================================
# Application Settings
# ============================================================================
ENVIRONMENT=development  # development, staging, production
APP_NAME=Retail Branch Management System
APP_VERSION=1.0.0
DEBUG=true

# ============================================================================
# Security Settings
# ============================================================================
ALLOWED_EMAIL_DOMAINS=yourcompany.com,example.com
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100  # requests per window
RATE_LIMIT_WINDOW=60     # seconds

# ============================================================================
# Notification Settings
# ============================================================================
NOTIFICATION_TIMEZONE=Asia/Bangkok

# ============================================================================
# File Upload Settings
# ============================================================================
MAX_FILE_SIZE=10485760  # 10 MB in bytes
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,xlsx

# ============================================================================
# Database Settings
# ============================================================================
BIGQUERY_LOCATION=asia-southeast1

# ============================================================================
# Logging Settings
# ============================================================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Creating .env File

```bash
# Copy example to .env
cp .env.example .env

# Edit with your credentials
nano .env
# or
vim .env
```

**IMPORTANT:**
- **Never commit `.env` to git!**
- Add `.env` to `.gitignore`
- Use Secret Manager for production
- Rotate secrets regularly

## 2. Application Configuration

### app/config.py

```python
# app/config.py

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""

    # ========================================================================
    # Google Cloud Platform
    # ========================================================================
    PROJECT_ID: str = os.getenv("PROJECT_ID", "")
    DATASET_ID: str = os.getenv("DATASET_ID", "retail_branches")
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    BIGQUERY_LOCATION: str = os.getenv("BIGQUERY_LOCATION", "asia-southeast1")

    # ========================================================================
    # Google OAuth 2.0
    # ========================================================================
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    OAUTH_REDIRECT_URI: str = os.getenv(
        "OAUTH_REDIRECT_URI",
        "http://localhost:8000/auth/callback"
    )

    # ========================================================================
    # Session Management
    # ========================================================================
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "")
    SESSION_MAX_AGE: int = int(os.getenv("SESSION_MAX_AGE", "86400"))

    # ========================================================================
    # Email Service
    # ========================================================================
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@retailbranch.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "Retail Branch System")
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true"

    # ========================================================================
    # Application Settings
    # ========================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_NAME: str = os.getenv("APP_NAME", "Retail Branch Management System")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ========================================================================
    # Security Settings
    # ========================================================================
    ALLOWED_EMAIL_DOMAINS: List[str] = os.getenv(
        "ALLOWED_EMAIL_DOMAINS", ""
    ).split(",") if os.getenv("ALLOWED_EMAIL_DOMAINS") else []

    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # ========================================================================
    # Notification Settings
    # ========================================================================
    NOTIFICATION_TIMEZONE: str = os.getenv("NOTIFICATION_TIMEZONE", "Asia/Bangkok")

    # ========================================================================
    # File Upload Settings
    # ========================================================================
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10 MB
    ALLOWED_FILE_TYPES: List[str] = os.getenv(
        "ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png,xlsx"
    ).split(",")

    # ========================================================================
    # Logging Settings
    # ========================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ========================================================================
    # Computed Properties
    # ========================================================================
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    # ========================================================================
    # Validation
    # ========================================================================
    def validate(self):
        """Validate required settings"""
        required_settings = [
            "PROJECT_ID",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "SESSION_SECRET",
        ]

        missing = [s for s in required_settings if not getattr(self, s)]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Validate SESSION_SECRET length
        if len(self.SESSION_SECRET) < 32:
            raise ValueError("SESSION_SECRET must be at least 32 characters long")

# Initialize settings
settings = Settings()

# Validate settings on startup (production only)
if settings.is_production:
    settings.validate()
```

**Usage in Application:**

```python
# app/main.py

from app.config import settings

# Use settings throughout the app
print(f"Running in {settings.ENVIRONMENT} mode")
print(f"Project ID: {settings.PROJECT_ID}")

if settings.is_production:
    # Production-specific logic
    pass
```

## 3. Python Dependencies

### requirements.txt

```txt
# requirements.txt
# Python dependencies for Retail Branch Management System

# ============================================================================
# Web Framework
# ============================================================================
fastapi==0.121.1                # Modern async web framework
uvicorn[standard]==0.38.0       # ASGI server for production
python-multipart==0.0.9         # For file uploads

# ============================================================================
# Template Engine
# ============================================================================
jinja2==3.1.6                   # Template engine for HTML

# ============================================================================
# Authentication
# ============================================================================
authlib==1.6.5                  # OAuth client library
itsdangerous==2.2.0             # Secure session management
httpx==0.27.0                   # HTTP client for OAuth (required by authlib)

# ============================================================================
# Google Cloud Platform
# ============================================================================
google-cloud-bigquery==3.38.0   # BigQuery client
google-cloud-storage==3.5.0     # GCS client
google-cloud-secret-manager==2.22.0  # Secret Manager

# ============================================================================
# Email Service
# ============================================================================
sendgrid==6.13.0                # SendGrid email service

# ============================================================================
# Data Validation
# ============================================================================
pydantic==2.10.7                # Data validation with type hints
email-validator==2.2.0          # Email validation

# ============================================================================
# Utilities
# ============================================================================
python-dotenv==1.2.1            # Environment variables from .env
python-magic==0.4.27            # File type detection (MIME)

# ============================================================================
# Security
# ============================================================================
bleach==6.2.0                   # HTML sanitization

# ============================================================================
# Testing
# ============================================================================
pytest==9.0.1                   # Testing framework
pytest-asyncio==0.25.2          # Async tests

# ============================================================================
# Development Tools
# ============================================================================
black==25.1.0                   # Code formatter
flake8==7.1.1                   # Code linter
mypy==1.15.0                    # Static type checker
```

**Install Dependencies:**

```bash
# Using UV (recommended)
uv pip install -r requirements.txt

# Using pip
pip install -r requirements.txt
```

### pyproject.toml

```toml
# pyproject.toml
# UV Package Manager Configuration

[project]
name = "retail-branch-demo"
version = "1.0.0"
description = "Retail Branch Management System"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
readme = "README.md"
requires-python = ">=3.12"

dependencies = [
    "fastapi==0.121.1",
    "uvicorn[standard]==0.38.0",
    "jinja2==3.1.6",
    "authlib==1.6.5",
    "itsdangerous==2.2.0",
    "google-cloud-bigquery==3.38.0",
    "google-cloud-storage==3.5.0",
    "google-cloud-secret-manager==2.22.0",
    "sendgrid==6.13.0",
    "pydantic==2.10.7",
    "email-validator==2.2.0",
    "python-dotenv==1.2.1",
    "python-magic==0.4.27",
    "bleach==6.2.0",
    "python-multipart==0.0.9",
    "httpx==0.27.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest==9.0.1",
    "pytest-asyncio==0.25.2",
    "black==25.1.0",
    "flake8==7.1.1",
    "mypy==1.15.0",
]

[tool.black]
line-length = 100
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"
```

## 4. Frontend Configuration

### package.json

```json
{
  "name": "retail-branch-demo",
  "version": "1.0.0",
  "description": "Retail Branch Management System - Frontend",
  "scripts": {
    "dev": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch",
    "build": "npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify",
    "lint": "eslint static/js/**/*.js"
  },
  "keywords": [
    "retail",
    "branch",
    "management"
  ],
  "author": "Your Name",
  "license": "MIT",
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.55.0"
  }
}
```

**Install Node.js Dependencies:**

```bash
npm install
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
    extend: {
      colors: {
        // Custom brand colors
        'brand-blue': '#3B82F6',
        'brand-green': '#10B981',
        'brand-orange': '#F59E0B',
        'brand-red': '#EF4444',
        'brand-purple': '#8B5CF6',
      },
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),  // Optional: Better form styles
  ],
}
```

### static/css/input.css

```css
/* static/css/input.css */

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom CSS */

@layer components {
  /* Buttons */
  .btn {
    @apply px-4 py-2 rounded-md font-medium transition-colors duration-200;
  }

  .btn-primary {
    @apply btn bg-blue-600 text-white hover:bg-blue-700;
  }

  .btn-secondary {
    @apply btn bg-gray-200 text-gray-800 hover:bg-gray-300;
  }

  .btn-danger {
    @apply btn bg-red-600 text-white hover:bg-red-700;
  }

  /* Cards */
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }

  /* Form inputs */
  .form-input {
    @apply mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500;
  }

  /* Table */
  .table {
    @apply min-w-full divide-y divide-gray-200;
  }

  .table thead {
    @apply bg-gray-50;
  }

  .table th {
    @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
  }

  .table td {
    @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
  }

  .table tbody tr:hover {
    @apply bg-gray-50;
  }
}

@layer utilities {
  /* Custom utilities */
  .text-balance {
    text-wrap: balance;
  }
}
```

## 5. Docker Configuration

### Dockerfile

```dockerfile
# Dockerfile
# Multi-stage build for optimal image size

# ============================================================================
# Stage 1: Build stage
# ============================================================================
FROM python:3.12-slim AS builder

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

# ============================================================================
# Stage 2: Runtime stage
# ============================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app
COPY ./static ./static

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
```

### .dockerignore

```
# .dockerignore
# Files to exclude from Docker build context

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.eggs
.pytest_cache
.mypy_cache
.coverage
htmlcov/

# Virtual environments
env/
venv/
.venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore
.gitattributes

# Documentation
*.md
docs/

# Tests
tests/
test_*.py

# CI/CD
.gitlab-ci.yml
.github/

# Environment variables
.env
.env.*
!.env.example

# Node.js
node_modules/
npm-debug.log

# Tailwind
static/css/input.css

# Misc
.DS_Store
*.log
tmp/
temp/
```

## 6. Git Configuration

### .gitignore

```
# .gitignore
# Files to exclude from Git version control

# ============================================================================
# Python
# ============================================================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# ============================================================================
# Virtual Environments
# ============================================================================
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# ============================================================================
# IDEs
# ============================================================================
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# ============================================================================
# Testing
# ============================================================================
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/

# ============================================================================
# Environment Variables & Secrets
# ============================================================================
.env
.env.local
.env.*.local
*.key
*.pem
*.json
!.env.example

# ============================================================================
# Google Cloud
# ============================================================================
service-account-*.json
gcp-*.json

# ============================================================================
# Logs
# ============================================================================
*.log
logs/
pip-log.txt

# ============================================================================
# Node.js (for Tailwind CSS)
# ============================================================================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# ============================================================================
# Tailwind CSS
# ============================================================================
static/css/output.css

# ============================================================================
# macOS
# ============================================================================
.DS_Store
.AppleDouble
.LSOverride

# ============================================================================
# Windows
# ============================================================================
Thumbs.db
ehthumbs.db
Desktop.ini

# ============================================================================
# Temporary files
# ============================================================================
*.tmp
*.temp
tmp/
temp/

# ============================================================================
# Database backups
# ============================================================================
*.sql
*.sqlite
*.db
```

## 7. CI/CD Configuration

### .gitlab-ci.yml

Complete GitLab CI/CD pipeline configuration (see [cicd.md](../deployment/cicd.md) for full details):

```yaml
# .gitlab-ci.yml
# GitLab CI/CD Pipeline for Retail Branch Management System

stages:
  - build
  - deploy-dev
  - deploy-prod

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_NAME: gcr.io/${GCP_PROJECT_ID}/retail-branch-demo

# ============================================================================
# Build Stage: Build and push Docker image
# ============================================================================
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
    # Build Docker image
    - docker build -t ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} .
    - docker tag ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} ${IMAGE_NAME}:latest

    # Push to Container Registry
    - docker push ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}
    - docker push ${IMAGE_NAME}:latest
  only:
    - main
    - tags

# ============================================================================
# Deploy to Development
# ============================================================================
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
        --memory 512Mi \
        --cpu 1 \
        --timeout 60 \
        --max-instances 10 \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_DEV},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_DEV},ENVIRONMENT=development" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest,SENDGRID_API_KEY=sendgrid_api_key:latest"
  when: manual
  only:
    - main
  environment:
    name: development
    url: https://retail-branch-demo-dev-xxxxxxxxxx-as.a.run.app

# ============================================================================
# Deploy to Production
# ============================================================================
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
        --memory 1Gi \
        --cpu 2 \
        --timeout 120 \
        --min-instances 1 \
        --max-instances 50 \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_PROD},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_PROD},ENVIRONMENT=production" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest,SENDGRID_API_KEY=sendgrid_api_key:latest"
  when: manual
  only:
    - tags
  environment:
    name: production
    url: https://retail-branch-demo-xxxxxxxxxx-as.a.run.app
```

## 8. Development Scripts

### scripts/setup_local.sh

```bash
#!/bin/bash
# scripts/setup_local.sh
# Local development environment setup

set -e  # Exit on error

echo "========================================="
echo "Retail Branch Demo - Local Setup"
echo "========================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
uv pip install -r requirements.txt

# Install Node.js dependencies
if command -v npm &> /dev/null; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Warning: npm not found. Skipping Node.js dependencies."
    echo "Install Node.js to build Tailwind CSS."
fi

# Build Tailwind CSS
if [ -f "package.json" ]; then
    echo "Building Tailwind CSS..."
    npm run build
fi

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your credentials!"
fi

echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your credentials"
echo "2. Run './scripts/run_local.sh' to start the server"
echo ""
```

### scripts/run_local.sh

```bash
#!/bin/bash
# scripts/run_local.sh
# Run local development server

set -e  # Exit on error

echo "========================================="
echo "Starting Retail Branch Demo"
echo "========================================="

# Activate virtual environment
source .venv/bin/activate

# Run Tailwind CSS in watch mode (background)
if [ -f "package.json" ]; then
    echo "Starting Tailwind CSS watcher..."
    npm run dev &
    TAILWIND_PID=$!
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ ! -z "$TAILWIND_PID" ]; then
        kill $TAILWIND_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Run FastAPI development server
echo "Starting FastAPI development server..."
echo "Server running at: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Make scripts executable:**

```bash
chmod +x scripts/*.sh
```

## 9. Configuration Best Practices

### 1. Environment-Specific Configuration

**Use different .env files:**
```bash
.env.development
.env.staging
.env.production
```

**Load based on ENVIRONMENT:**
```python
env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"
load_dotenv(env_file)
```

### 2. Secret Management

**Development:** Use `.env` file

**Production:** Use Google Secret Manager

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create secret-name --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding secret-name \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Validation

**Validate configuration on startup:**
```python
# In main.py
from app.config import settings

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        settings.validate()
        print(f"✅ Configuration validated successfully")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Project ID: {settings.PROJECT_ID}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        raise
```

### 4. Configuration Documentation

**Document all environment variables:**
- Variable name
- Description
- Type
- Default value
- Required/Optional
- Example value

### 5. Version Control

**Never commit:**
- `.env` files
- Service account keys (`*.json`)
- API keys
- Passwords/secrets

**Always commit:**
- `.env.example`
- Configuration templates
- Documentation

## 10. Testing Configuration

### pytest.ini

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Coverage
addopts =
    --verbose
    --cov=app
    --cov-report=html
    --cov-report=term-missing

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

## Related Documentation

- [cicd.md](../deployment/cicd.md) - Complete CI/CD pipeline
- [security.md](../security/security.md) - Security best practices
- [api-standards.md](./api-standards.md) - API conventions
- [file-upload.md](./file-upload.md) - File upload configuration
