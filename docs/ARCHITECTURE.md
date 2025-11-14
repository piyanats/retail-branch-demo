# System Architecture

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

## System Architecture

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

## Application Structure

```
retail-branch-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration settings
│   ├── models/                 # Data models with type hints
│   │   ├── __init__.py
│   │   ├── branch.py
│   │   ├── document.py
│   │   ├── user.py             # User model
│   │   └── legal_ppp09.py      # Legal PPP09 (ภ.พ.09) model
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── bigquery_service.py
│   │   ├── storage_service.py
│   │   ├── oauth_service.py    # Google OAuth service
│   │   └── user_service.py     # User management service
│   ├── routes/                 # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # OAuth routes
│   │   ├── branch_routes.py
│   │   ├── document_routes.py
│   │   ├── admin_routes.py     # Admin routes (user management)
│   │   └── legal_ppp09_routes.py # Legal ภ.พ.09 routes
│   ├── middleware/             # Authentication & Authorization
│   │   ├── __init__.py
│   │   └── auth.py
│   └── templates/              # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html          # OAuth login page
│       ├── admin/              # Admin pages
│       │   ├── users.html      # User management page
│       │   └── permissions.html # User permissions management
│       └── teams/
│           ├── new_branch.html
│           ├── legal.html
│           ├── legal_ppp09.html # Legal ภ.พ.09 management page
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

## Component Layers

### 1. Presentation Layer (Templates)
- HTML templates with Jinja2
- Tailwind CSS for styling
- Vanilla JavaScript for interactivity
- Responsive design for all devices

### 2. API Layer (Routes)
- FastAPI routes
- RESTful API endpoints
- Request validation
- Response formatting

### 3. Business Logic Layer (Services)
- BigQuery service (database operations)
- Storage service (GCS file operations)
- OAuth service (authentication)
- User service (user management)

### 4. Data Layer (Models)
- Pydantic models with type hints
- Data validation
- Serialization/Deserialization

### 5. Middleware Layer
- Authentication middleware
- Authorization middleware
- Error handling
- Logging

## Minimal Dependencies

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

## Design Principles

- **Keep It Simple**: เน้นความเรียบง่าย ใช้ library น้อยที่สุด
- **Modern & Fast**: ใช้ FastAPI สำหรับ async performance
- **Serverless First**: Deploy บน Cloud Run (serverless, auto-scaling)
- **Type Safety**: ใช้ type hints ทุก function และ method
- **Testable**: Code ต้อง testable และ maintainable

## Security Considerations

- ใช้ Service Account แทนการใช้ API keys
- Validate input ทุกครั้งก่อนส่งไป BigQuery
- ตรวจสอบสิทธิ์การเข้าถึงตาม team
- ไม่เก็บ credentials ใน code หรือ git
- ใช้ environment variables สำหรับ sensitive data
- Session-based authentication พร้อม secure cookies
- HTTPS only (production)

## Related Documentation

- [DATABASE.md](DATABASE.md) - Database schema details
- [deployment/docker.md](deployment/docker.md) - Docker setup
- [deployment/cloud-run.md](deployment/cloud-run.md) - Cloud Run deployment
- [auth/oauth.md](auth/oauth.md) - OAuth authentication flow
