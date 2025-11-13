# Retail Branch Management System

## Project Overview

ระบบบริหารจัดการข้อมูลสาขาของร้านสะดวกซื้อ (Retail Branch Management System) เป็น Web Application ที่ออกแบบมาเพื่อให้หลายทีมงานสามารถจัดการข้อมูลสาขาได้อย่างมีประสิทธิภาพ โดยแต่ละทีมจะเห็นเฉพาะเมนูและข้อมูลที่เกี่ยวข้องกับทีมของตนเองเท่านั้น

## Features & Requirements

### Core Features
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
- **BigQuery**: Database หลักสำหรับเก็บข้อมูลสาขา
- **Google Cloud Storage (GCS)**: เก็บไฟล์เอกสาร
- **Uvicorn**: ASGI server สำหรับ production

### Frontend
- **HTML5/CSS3**: โครงสร้างและการออกแบบ
- **Vanilla JavaScript**: เพิ่มความเป็น dynamic
- **Tailwind CSS**: Utility-first CSS framework สำหรับ responsive design

### Infrastructure
- **Google Cloud Run**: สำหรับ deployment
- **Service Account**: สำหรับ authentication กับ GCP services
- **Docker**: Container สำหรับการ deploy

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
│   │   └── storage_service.py
│   ├── routes/                 # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── branch_routes.py
│   │   └── document_routes.py
│   ├── middleware/             # Authentication & Authorization
│   │   ├── __init__.py
│   │   └── auth.py
│   └── templates/              # HTML templates
│       ├── base.html
│       ├── index.html
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
├── tests/
│   ├── __init__.py
│   └── test_services.py
├── Dockerfile
├── requirements.txt
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
PROJECT_ID=your-gcp-project-id
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
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
google-cloud-bigquery==3.38.0   # BigQuery client
google-cloud-storage==3.5.0     # GCS client
python-dotenv==1.2.1            # Environment variables
pytest==9.0.1                   # Testing framework
```

## Next Steps

1. สร้างโครงสร้างโปรเจกต์ตาม Application Structure
2. ติดตั้ง Python dependencies (requirements.txt)
3. ติดตั้ง Node.js และ setup Tailwind CSS
4. ตั้งค่า BigQuery dataset และสร้าง tables
5. สร้าง GCS bucket สำหรับเก็บเอกสาร
6. พัฒนา backend services (BigQuery, GCS)
7. สร้าง API routes สำหรับ CRUD operations (FastAPI)
8. พัฒนา frontend (HTML templates + Tailwind CSS)
9. ใส่ระบบ authentication และ authorization
10. เขียน tests
11. สร้าง Dockerfile
12. Deploy ไปยัง Cloud Run
13. ทดสอบระบบ

## Notes

- ระบบนี้เน้นความเรียบง่ายและประสิทธิภาพ
- ใช้ FastAPI เป็น web framework (modern, async, fast)
- ใช้ Tailwind CSS สำหรับ responsive UI
- ใช้ BigQuery เป็น database หลัก (serverless, scalable)
- ใช้ GCS สำหรับเก็บไฟล์ขนาดใหญ่
- Deploy บน Cloud Run (serverless, auto-scaling)
- แต่ละทีมมี view และ permissions แยกกัน
- Code ต้องอ่านง่าย maintain ง่าย
- ใช้ library เวอร์ชันล่าสุดจาก PyPI
