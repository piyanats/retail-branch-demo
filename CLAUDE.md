# Retail Branch Management System

## Project Overview

ระบบบริหารจัดการข้อมูลสาขาของร้านสะดวกซื้อ (Retail Branch Management System) เป็น Web Application ที่ออกแบบมาเพื่อให้หลายทีมงานสามารถจัดการข้อมูลสาขาได้อย่างมีประสิทธิภาพ โดยแต่ละทีมจะเห็นเฉพาะเมนูและข้อมูลที่เกี่ยวข้องกับทีมของตนเองเท่านั้น

## Features & Requirements

### Core Features
- **User Authentication (Google OAuth 2.0)**: ระบบ login เข้าใช้งานผ่าน Google Account โดยผู้ใช้ทุกคนต้อง login ก่อนเข้าใช้งานระบบ
- **User Management & Permissions**: จัดการผู้ใช้และกำหนดสิทธิ์การเข้าถึงเมนูต่างๆ โดย user 1 คนสามารถเข้าถึงได้มากกว่า 1 เมนู
- **CRUD Operations**: สามารถเพิ่ม แก้ไข และลบข้อมูลสาขาได้
- **Multi-Team Access**: รองรับการเข้าใช้งานของหลายทีม โดยแต่ละทีมมีสิทธิ์และเห็นเมนูเฉพาะของตนเอง
- **Branch Data Management**: จัดการข้อมูลสาขา เช่น รหัสสาขา, ชื่อสาขา, ที่อยู่
- **Document Management**: จัดเก็บและจัดการเอกสารที่เกี่ยวข้องกับแต่ละสาขา
- **Responsive Design**: รองรับการใช้งานบนทุกอุปกรณ์ (Desktop, Tablet, Mobile)

### Team Roles & Permissions

| ทีม | หน้าที่ | ข้อมูลที่เข้าถึง |
|-----|---------|-----------------|
| **ทีมสาขาใหม่** | จัดการข้อมูลการเปิดสาขาใหม่ | ข้อมูลสาขาที่กำลังเปิดใหม่, สถานะการเปิดสาขา, timeline |
| **ทีมกฎหมาย** | จัดการเอกสารทางกฎหมายและข้อมูล ภ.พ.09 | เอกสารสัญญา, ใบอนุญาต, ภ.พ.09 (แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง), เอกสารกฎหมายของแต่ละสาขา |
| **ทีม SRD** | จัดการเอกสาร layout | แปลนผัง, layout ร้าน, floor plan ของแต่ละสาขา |
| **ทีม SCM** | จัดการข้อมูล DC | ข้อมูล Distribution Center ที่รับผิดชอบแต่ละสาขา |

**หมายเหตุ:**
- ผู้ใช้ 1 คนสามารถเป็นสมาชิกของหลายทีมได้ (Multi-Team Membership)
- Admin สามารถกำหนดสิทธิ์ให้ user เข้าถึงเมนูต่างๆ ได้ผ่านหน้า User Management

### User Levels

| Level | สิทธิ์ | คำอธิบาย |
|-------|-------|---------|
| **Admin** | จัดการระบบทั้งหมด | จัดการ users, permissions, ทุก teams, ทุกข้อมูล |
| **Manager** | จัดการทีมของตัวเอง | จัดการข้อมูลและ users ในทีมที่ตัวเองรับผิดชอบ |
| **Editor** | แก้ไขข้อมูล | สามารถเพิ่ม แก้ไข ข้อมูลในทีมที่มีสิทธิ์ |
| **Viewer** | ดูข้อมูลอย่างเดียว | ดูข้อมูลในทีมที่มีสิทธิ์ ไม่สามารถแก้ไขได้ |

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

### Design Philosophy
- **Minimalist & Clean**: ดีไซน์เรียบง่าย ไม่วุ่นวาย เน้นเนื้อหาที่สำคัญ
- **Modern UI**: ใช้ design patterns ที่ทันสมัยและเป็นมาตรฐานของอุตสาหกรรม
- **User-Centric**: ออกแบบโดยคำนึงถึงผู้ใช้งานเป็นหลัก ใช้งานง่าย เข้าใจง่าย
- **Responsive First**: รองรับทุกอุปกรณ์ (Mobile, Tablet, Desktop)

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
  user_id STRING NOT NULL,             -- รหัสผู้ใช้ (UUID)
  email STRING NOT NULL,               -- อีเมล (unique)
  name STRING NOT NULL,                -- ชื่อผู้ใช้
  user_level STRING NOT NULL,          -- ระดับผู้ใช้ (admin, manager, editor, viewer)
  is_active BOOLEAN,                   -- สถานะการใช้งาน
  created_at TIMESTAMP,                -- วันที่สร้าง
  updated_at TIMESTAMP,                -- วันที่แก้ไข
  last_login TIMESTAMP                 -- เข้าสู่ระบบล่าสุด
);
```

#### Table: `user_teams`
```sql
CREATE TABLE retail_branches.user_teams (
  user_team_id STRING NOT NULL,       -- รหัสความสัมพันธ์ (UUID)
  user_id STRING NOT NULL,             -- รหัสผู้ใช้
  team_name STRING NOT NULL,           -- ชื่อทีม (new_branch, legal, srd, scm)
  role STRING NOT NULL,                -- บทบาทในทีม (viewer, editor, manager)
  created_at TIMESTAMP,                -- วันที่เพิ่ม
  created_by STRING                    -- ผู้ที่เพิ่มสิทธิ์
);
```

#### Table: `legal_ppp09`
```sql
CREATE TABLE retail_branches.legal_ppp09 (
  ppp09_id STRING NOT NULL,                -- รหัส ภ.พ.09 (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)
  ppp09_number STRING,                     -- เลขที่ ภ.พ.09
  issue_date DATE,                         -- วันที่ออกเอกสาร
  expiry_date DATE,                        -- วันหมดอายุ
  owner_name STRING,                       -- ชื่อเจ้าของ/ผู้เสียภาษี

  -- ที่อยู่ตาม ภ.พ.09 (แยกตาม field)
  address_number STRING,                   -- บ้านเลขที่
  address_moo STRING,                      -- หมู่ที่
  address_trok STRING,                     -- ตรอก
  address_soi STRING,                      -- ซอย
  address_road STRING,                     -- ถนน
  address_tambon STRING,                   -- ตำบล/แขวง
  address_amphoe STRING,                   -- อำเภอ/เขต
  address_province STRING,                 -- จังหวัด
  address_postal_code STRING,              -- รหัสไปรษณีย์

  -- ข้อมูลเพิ่มเติม
  land_area_rai FLOAT64,                   -- เนื้อที่ดิน (ไร่)
  land_area_ngan FLOAT64,                  -- เนื้อที่ดิน (งาน)
  land_area_wa FLOAT64,                    -- เนื้อที่ดิน (ตารางวา)
  building_area_sqm FLOAT64,              -- พื้นที่สิ่งปลูกสร้าง (ตร.ม.)
  annual_tax_amount FLOAT64,              -- จำนวนเงินภาษีต่อปี (บาท)
  payment_status STRING,                   -- สถานะการชำระ (paid, unpaid, overdue)

  -- เอกสาร PDF
  pdf_file_path STRING,                    -- path ใน GCS สำหรับ PDF ภ.พ.09
  pdf_file_size INT64,                     -- ขนาดไฟล์ PDF (bytes)
  pdf_uploaded_at TIMESTAMP,               -- วันที่อัพโหลด PDF
  pdf_uploaded_by STRING,                  -- ผู้อัพโหลด PDF

  -- หมายเหตุ
  remarks STRING,                          -- หมายเหตุเพิ่มเติม

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

#### Table: `audit_logs`
```sql
CREATE TABLE retail_branches.audit_logs (
  log_id STRING NOT NULL,                  -- รหัสบันทึก (UUID)
  user_id STRING NOT NULL,                 -- ผู้ใช้ที่ทำ action
  user_email STRING NOT NULL,              -- อีเมลผู้ใช้
  action_type STRING NOT NULL,             -- ประเภท action (login, create, update, delete, etc.)
  resource_type STRING,                    -- ประเภททรัพยากร (branch, document, user, permission, ppp09)
  resource_id STRING,                      -- รหัสทรัพยากรที่เกี่ยวข้อง
  action_detail STRING,                    -- รายละเอียด action (JSON format)
  ip_address STRING,                       -- IP address ของผู้ใช้
  user_agent STRING,                       -- Browser/Client ที่ใช้
  status STRING,                           -- สถานะ (success, failed)
  error_message STRING,                    -- ข้อความ error (ถ้ามี)
  created_at TIMESTAMP NOT NULL            -- เวลาที่เกิด event
);
```

**หมายเหตุ Database Schema:**
- User 1 คนสามารถมีหลาย records ใน `user_teams` (multi-team membership)
- `users.user_level` กำหนดสิทธิ์ระดับระบบ (admin สามารถทำทุกอย่าง)
- `user_teams.role` กำหนดสิทธิ์ในแต่ละทีม (viewer, editor, manager)
- Admin สามารถจัดการ users และ permissions ผ่านหน้า Admin
- `audit_logs` เก็บบันทึก activity ทั้งหมดของ user รวมถึง admin
- `legal_ppp09` เก็บข้อมูล ภ.พ.09 (แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง) สำหรับทีมกฎหมาย
- `legal_ppp09.branch_id` เชื่อมโยงกับ `branches.branch_id` (1 สาขา สามารถมีได้ 1 ภ.พ.09 หรือมากกว่า ขึ้นอยู่กับการต่ออายุ)
- ที่อยู่ใน `legal_ppp09` แยกเป็น fields เพื่อให้ค้นหาและจัดการได้ง่าย

## Design & UI/UX Guidelines

### Design Principles

**1. Simplicity & Minimalism (ความเรียบง่าย)**
- เน้นเนื้อหาที่สำคัญ ตัดสิ่งที่ไม่จำเป็นออก
- ใช้ white space อย่างเหมาะสม เพื่อให้ดูโปร่ง ไม่อัดแน่น
- หลีกเลี่ยงการใช้ decorations หรือ effects ที่มากเกินไป
- "Less is More" - ทำน้อยแต่ได้มาก

**2. Modern & Clean Design (ดีไซน์ทันสมัย)**
- ใช้ flat design หรือ subtle shadows (ไม่ใช้ skeuomorphism)
- มุมโค้งมน (rounded corners) สำหรับ cards และ buttons
- Consistent spacing และ alignment ทุกหน้า
- ใช้ modern icons (line icons หรือ outline style)

**3. User-Centric (เน้นผู้ใช้)**
- Navigation ชัดเจน รู้ว่าตัวเองอยู่ที่ไหนในระบบ
- Call-to-action (CTA) buttons เด่นชัด และวางตำแหน่งที่เหมาะสม
- Feedback ทันที เมื่อผู้ใช้ทำ action (loading, success, error states)
- Error messages ที่เข้าใจง่าย พร้อมแนะนำวิธีแก้ไข

**4. Accessibility (การเข้าถึง)**
- สีที่มี contrast ดี อ่านง่าย (WCAG AA standard)
- Font size อ่านง่าย (ไม่เล็กเกินไป)
- รองรับ keyboard navigation
- ใช้ semantic HTML elements

### Color Palette

**Primary Colors:**
- **Primary Blue**: `#3B82F6` - สำหรับ primary buttons, links, highlights
- **Success Green**: `#10B981` - แสดงสถานะสำเร็จ, confirmations
- **Warning Orange**: `#F59E0B` - แสดงการแจ้งเตือน, warnings
- **Error Red**: `#EF4444` - แสดง errors, destructive actions

**Neutral Colors:**
- **Gray Scale**: `#111827` (dark) → `#F9FAFB` (light)
- ใช้สำหรับ text, borders, backgrounds
- Gray-900 สำหรับ headings, Gray-700 สำหรับ body text

**Usage:**
- Background: White (`#FFFFFF`) หรือ Light Gray (`#F9FAFB`)
- ใช้สีประจำทีม (team colors) เป็น accents เมื่อเหมาะสม
- Hover states: ใช้สีเข้มขึ้น 10-20%

### Typography

**Font Family:**
- **System Fonts**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial`
- ใช้ system fonts เพื่อ performance ดีและความคุ้นเคย

**Font Sizes:**
- **Heading 1**: `2.25rem` (36px) - หน้าหลัก, page titles
- **Heading 2**: `1.875rem` (30px) - section titles
- **Heading 3**: `1.5rem` (24px) - subsections
- **Body**: `1rem` (16px) - paragraph text
- **Small**: `0.875rem` (14px) - captions, labels
- **Tiny**: `0.75rem` (12px) - helper text (ใช้น้อย)

**Font Weight:**
- Regular (400): Body text
- Medium (500): Emphasized text
- Semibold (600): Subheadings
- Bold (700): Headings, important text

**Line Height:**
- Headings: `1.2` (tight)
- Body text: `1.5` (comfortable reading)
- Small text: `1.4`

### Layout & Spacing

**Container Width:**
- **Max Width**: `1280px` (desktop)
- **Padding**: `1rem` (mobile), `2rem` (tablet), `4rem` (desktop)
- Centered layout สำหรับ main content

**Spacing Scale (Tailwind):**
- `4px` (space-1): Tight spacing
- `8px` (space-2): Small gaps
- `16px` (space-4): Default spacing
- `24px` (space-6): Medium spacing
- `32px` (space-8): Large spacing
- `48px` (space-12): Section spacing
- `64px` (space-16): Page sections

**Grid System:**
- 12-column grid สำหรับ layout
- Responsive breakpoints:
  - Mobile: `< 640px`
  - Tablet: `640px - 1024px`
  - Desktop: `> 1024px`

### UI Components

**Buttons:**
- **Primary Button**: Blue background, white text, rounded corners
- **Secondary Button**: White background, gray border, gray text
- **Danger Button**: Red background, white text (สำหรับ delete actions)
- Padding: `0.5rem 1rem` (small), `0.75rem 1.5rem` (default)
- Hover: Darker shade + subtle shadow
- Disabled: Gray, low opacity, no pointer

**Cards:**
- White background
- Subtle shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Rounded corners: `0.5rem` (8px)
- Padding: `1.5rem` (24px)
- Hover: Lift up (translate + stronger shadow)

**Forms:**
- Input height: `2.5rem` (40px)
- Border: `1px solid gray-300`
- Focus: Blue border + subtle shadow
- Labels: Above inputs, bold, Gray-700
- Validation: Red border สำหรับ errors พร้อม helper text

**Tables:**
- Striped rows (zebra pattern) สำหรับอ่านง่าย
- Hover: Light gray background
- Headers: Bold, Gray-900, bottom border
- Padding: `0.75rem 1rem`
- Responsive: Scroll horizontal บน mobile

**Navigation:**
- Top navbar: Fixed position, white background, shadow
- Active state: Blue underline หรือ background
- Logo/Brand: ซ้ายสุด
- User menu: ขวาสุด พร้อม avatar
- Mobile: Hamburger menu

### User Experience (UX) Guidelines

**1. Feedback & Response**
- **Loading States**: แสดง spinner หรือ skeleton screens
- **Success Messages**: Toast notification (เขียว) แสดง 3-5 วินาที
- **Error Messages**: Modal หรือ inline (แดง) พร้อมคำแนะนำ
- **Confirmation**: Modal สำหรับ destructive actions (delete)

**2. Navigation & Flow**
- **Breadcrumbs**: แสดงตำแหน่งปัจจุบันในระบบ
- **Back Buttons**: ให้กลับไปหน้าก่อนหน้าได้
- **Clear CTAs**: ปุ่มหลักเด่นชัด, ปุ่มรองเบาลง
- **Search**: Accessible, auto-suggest ถ้าเป็นไปได้

**3. Performance**
- **Fast Load**: หน้าเว็บโหลดเร็ว (< 3 seconds)
- **Lazy Loading**: โหลดรูปภาพและ components ตามต้องการ
- **Pagination**: แบ่งหน้าสำหรับ data มาก (20-50 items/page)
- **Caching**: Cache ข้อมูลที่ไม่เปลี่ยนบ่อย

**4. Mobile Experience**
- **Touch Friendly**: Buttons ขนาดอย่างน้อย `44x44px`
- **Thumb Zone**: ปุ่มสำคัญอยู่ในตำแหน่งที่จับได้ง่าย
- **Reduced Motion**: ลด animations บน mobile
- **Offline Ready**: แสดง error ชัดเจนเมื่อไม่มี connection

**5. Consistency**
- ใช้ components เดียวกันทั้งระบบ
- สี, spacing, typography ต้อง consistent
- เมนูและ navigation เหมือนกันทุกหน้า
- Patterns ที่คุ้นเคย (e.g., search icon คือ magnifying glass)

### Team-Specific UI Elements

แต่ละทีมจะมี accent color ของตัวเอง:
- **ทีมสาขาใหม่**: Blue (`#3B82F6`) - Growth, New beginnings
- **ทีมกฎหมาย**: Purple (`#8B5CF6`) - Authority, Professional
- **ทีม SRD**: Orange (`#F97316`) - Creative, Design
- **ทีม SCM**: Green (`#10B981`) - Efficiency, Logistics

ใช้ accent color ใน:
- Page headers
- Section highlights
- Team badges/tags
- Icons

## User Management & Permissions

### Overview

ระบบมีหน้าจัดการผู้ใช้และสิทธิ์สำหรับ Admin ในการควบคุมการเข้าถึงของผู้ใช้แต่ละคน โดยผู้ใช้ 1 คนสามารถเข้าถึงได้มากกว่า 1 ทีม/เมนู

### User Management Page (`/admin/users`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

**ฟีเจอร์:**
- **รายการผู้ใช้ทั้งหมด**: แสดงตารางผู้ใช้พร้อม email, name, user level, status
- **ค้นหาผู้ใช้**: ค้นหาด้วย email หรือ name
- **กรองผู้ใช้**: กรองตาม user level (admin, manager, editor, viewer) หรือ status (active/inactive)
- **เพิ่มผู้ใช้ใหม่**: เพิ่ม user ใหม่ (กรอก email, name, เลือก user level)
- **แก้ไขผู้ใช้**: แก้ไข name, user level, status
- **ลบผู้ใช้**: ปิดการใช้งาน (soft delete โดยตั้ง is_active = false)

**UI Components:**
- ตาราง users พร้อม pagination
- ปุ่ม "Add User" (primary button, มุมขวาบน)
- Search box และ filter dropdowns
- Actions column: Edit, Deactivate/Activate buttons
- Modal สำหรับเพิ่ม/แก้ไข user

**ข้อมูลที่แสดง:**
| Column | Description |
|--------|-------------|
| Email | อีเมลผู้ใช้ |
| Name | ชื่อผู้ใช้ |
| User Level | admin / manager / editor / viewer |
| Teams | จำนวนทีมที่สังกัด (clickable เพื่อดู details) |
| Status | Active / Inactive |
| Last Login | เข้าสู่ระบบล่าสุด |
| Actions | Edit / Deactivate buttons |

### User Permissions Page (`/admin/permissions`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

**ฟีเจอร์:**
- **เลือกผู้ใช้**: Dropdown หรือ autocomplete สำหรับเลือก user
- **แสดงทีมปัจจุบัน**: แสดง teams ที่ user มีสิทธิ์เข้าถึง
- **เพิ่มสิทธิ์เข้าทีม**: เลือกทีมและ role (viewer/editor/manager) แล้วเพิ่ม
- **แก้ไขสิทธิ์**: เปลี่ยน role ในแต่ละทีม
- **ลบสิทธิ์**: ลบสิทธิ์ออกจากทีม

**UI Layout:**

```
┌──────────────────────────────────────────┐
│  User Permissions Management             │
├──────────────────────────────────────────┤
│  Select User: [Dropdown/Autocomplete]    │
├──────────────────────────────────────────┤
│  Current Permissions:                     │
│  ┌────────────────────────────────────┐  │
│  │ Team        │ Role    │ Actions   │  │
│  ├────────────────────────────────────┤  │
│  │ New Branch  │ Editor  │ [Edit][X] │  │
│  │ Legal       │ Viewer  │ [Edit][X] │  │
│  │ SRD         │ Manager │ [Edit][X] │  │
│  └────────────────────────────────────┘  │
├──────────────────────────────────────────┤
│  Add New Permission:                      │
│  Team: [Dropdown]   Role: [Dropdown]     │
│  [Add Permission Button]                  │
└──────────────────────────────────────────┘
```

**Workflow:**
1. Admin เลือก user จาก dropdown
2. ระบบแสดงทีมและ role ที่ user มีสิทธิ์
3. Admin สามารถ:
   - เพิ่มสิทธิ์ใหม่ (เลือกทีม + role)
   - แก้ไข role ในทีมที่มีอยู่
   - ลบสิทธิ์ออกจากทีม
4. บันทึกการเปลี่ยนแปลงลง BigQuery

### Permission Logic

**การตรวจสอบสิทธิ์:**
1. ตรวจสอบ `user_level` จาก `users` table
   - ถ้าเป็น `admin` → อนุญาตให้เข้าถึงทุกอย่าง
2. ตรวจสอบ `user_teams` table
   - ดึง teams ที่ user มีสิทธิ์
   - ตรวจสอบ role ในแต่ละทีม
3. แสดงเฉพาะเมนูที่ user มีสิทธิ์

**ตัวอย่าง:**
```
User: john@example.com
user_level: editor

user_teams:
- team_name: new_branch, role: editor
- team_name: legal, role: viewer

→ john สามารถ:
  - เข้าเมนู New Branch (แก้ไขได้)
  - เข้าเมนู Legal (ดูอย่างเดียว)
  - ไม่เห็นเมนู SRD และ SCM
```

### User Level Permissions

| User Level | Permissions |
|-----------|-------------|
| **Admin** | - เข้าถึงทุก teams และทุกเมนู<br>- จัดการ users<br>- กำหนดสิทธิ์<br>- ดู/แก้ไข/ลบข้อมูลทั้งหมด |
| **Manager** | - เข้าถึง teams ที่มีสิทธิ์<br>- จัดการข้อมูลในทีมของตัวเอง<br>- ไม่สามารถจัดการ users ได้ |
| **Editor** | - เข้าถึง teams ที่มีสิทธิ์<br>- เพิ่ม/แก้ไขข้อมูล<br>- ไม่สามารถลบข้อมูล |
| **Viewer** | - เข้าถึง teams ที่มีสิทธิ์<br>- ดูข้อมูลอย่างเดียว<br>- ไม่สามารถแก้ไขหรือลบ |

### Navigation for Admin

Admin จะเห็นเมนูเพิ่มเติม:
- **Users**: จัดการผู้ใช้
- **Permissions**: กำหนดสิทธิ์ผู้ใช้
- **All Teams**: เข้าถึงทุกทีม (New Branch, Legal, SRD, SCM)

**Admin Navbar Example:**
```
[Logo] | Dashboard | Users | Permissions | Audit Logs | Teams ▼ | [User Avatar ▼]
                                                         |
                                                         ├── New Branch
                                                         ├── Legal
                                                         ├── SRD
                                                         └── SCM
```

## Audit Logs & Activity Tracking

### Overview

ระบบมีการบันทึก activity ทั้งหมดของผู้ใช้ (รวมถึง Admin) เพื่อติดตามว่า **ใคร ทำอะไร เมื่อไหร่** โดยเก็บไว้ใน `audit_logs` table

### Audit Logs Page (`/admin/audit-logs`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

**ฟีเจอร์:**
- **ดูบันทึก activity ทั้งหมด**: แสดงตาราง audit logs พร้อม filter และ search
- **กรองตามผู้ใช้**: เลือกดู activity ของ user คนใดคนหนึ่ง
- **กรองตาม action type**: login, create, update, delete, permission_change
- **กรองตาม resource**: branch, document, user, permission
- **กรองตามช่วงเวลา**: เลือกช่วงวันที่
- **ค้นหา**: ค้นหาจาก email, resource_id, action_detail
- **Export**: Export logs เป็น CSV สำหรับการวิเคราะห์

**UI Components:**
- ตาราง audit logs พร้อม pagination
- Filter panel (user, action type, resource, date range)
- Search box
- ปุ่ม "Export to CSV"
- Timeline view (optional) สำหรับดู activity แบบ chronological

**ข้อมูลที่แสดง:**
| Column | Description |
|--------|-------------|
| Timestamp | วันเวลาที่เกิด event |
| User | ชื่อและอีเมลผู้ใช้ |
| Action | ประเภท action (login, create, update, delete) |
| Resource | ทรัพยากรที่เกี่ยวข้อง (branch, document, user) |
| Details | รายละเอียด action (expandable) |
| IP Address | IP address ของผู้ใช้ |
| Status | Success / Failed |

### Actions ที่บันทึก

**Authentication Actions:**
- `login` - ผู้ใช้ login เข้าระบบ
- `logout` - ผู้ใช้ logout ออกจากระบบ
- `login_failed` - ความพยายาม login ที่ล้มเหลว

**Branch Actions:**
- `branch_create` - สร้างข้อมูลสาขาใหม่
- `branch_update` - แก้ไขข้อมูลสาขา
- `branch_delete` - ลบข้อมูลสาขา
- `branch_view` - ดูข้อมูลสาขา (optional - ถ้าต้องการความละเอียดสูง)

**Document Actions:**
- `document_upload` - อัพโหลดเอกสาร
- `document_download` - ดาวน์โหลดเอกสาร
- `document_delete` - ลบเอกสาร
- `document_update` - แก้ไขข้อมูลเอกสาร

**User Management Actions:**
- `user_create` - สร้าง user ใหม่
- `user_update` - แก้ไขข้อมูล user (name, level, status)
- `user_deactivate` - ปิดการใช้งาน user
- `user_activate` - เปิดการใช้งาน user

**Permission Management Actions:**
- `permission_add` - เพิ่มสิทธิ์ให้ user เข้าทีม
- `permission_update` - แก้ไข role ของ user ในทีม
- `permission_remove` - ลบสิทธิ์ user ออกจากทีม

**Legal ภ.พ.09 Management Actions:**
- `ppp09_create` - สร้างข้อมูล ภ.พ.09 ใหม่
- `ppp09_update` - แก้ไขข้อมูล ภ.พ.09
- `ppp09_delete` - ลบข้อมูล ภ.พ.09
- `ppp09_pdf_upload` - อัพโหลด PDF เอกสาร ภ.พ.09
- `ppp09_pdf_download` - ดาวน์โหลด PDF เอกสาร ภ.พ.09
- `ppp09_pdf_delete` - ลบ PDF เอกสาร ภ.พ.09

### Action Detail Format (JSON)

**ตัวอย่าง action_detail สำหรับแต่ละ action:**

```json
// branch_update
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "changes": {
    "phone": {
      "old": "02-123-4567",
      "new": "02-987-6543"
    },
    "status": {
      "old": "opening",
      "new": "active"
    }
  }
}

// permission_add
{
  "target_user_id": "user-456",
  "target_user_email": "john@example.com",
  "team_name": "legal",
  "role": "editor"
}

// document_upload
{
  "document_id": "DOC001",
  "document_name": "สัญญาเช่า-สาขา001.pdf",
  "file_size": 2048576,
  "branch_id": "BR001",
  "team": "legal"
}

// ppp09_update
{
  "ppp09_id": "PPP09-001",
  "branch_id": "BR001",
  "ppp09_number": "12345/2567",
  "changes": {
    "payment_status": {
      "old": "unpaid",
      "new": "paid"
    },
    "annual_tax_amount": {
      "old": 15000.00,
      "new": 16500.00
    }
  }
}

// ppp09_pdf_upload
{
  "ppp09_id": "PPP09-001",
  "branch_id": "BR001",
  "pdf_file_name": "ภพ09-สาขาสยาม-2567.pdf",
  "file_size": 3145728,
  "file_path": "gs://bucket/legal/ppp09/BR001_ppp09_2567.pdf"
}
```

### Audit Log Retention

**นโยบายการเก็บข้อมูล:**
- เก็บ audit logs ทั้งหมดใน BigQuery (ไม่มีการลบ)
- Partition โดย created_at (รายวัน) เพื่อประสิทธิภาพในการ query
- Clustering โดย user_id และ action_type
- สามารถ archive logs เก่ากว่า 1 ปี ไปยัง GCS (ถ้าต้องการประหยัดค่าใช้จ่าย)

### Security & Privacy

**การรักษาความปลอดภัย:**
- ห้าม edit หรือ delete audit logs
- Append-only (เพิ่มได้อย่างเดียว)
- เฉพาะ Admin เท่านั้นที่ดู audit logs ได้
- ไม่เก็บข้อมูล sensitive (เช่น password, tokens) ใน action_detail
- Encrypt sensitive fields ถ้าจำเป็น

**ตัวอย่างการใช้งาน:**
```
Admin ต้องการตรวจสอบว่า:
1. ใครแก้ไขข้อมูลสาขา BR001 เมื่อวานนี้?
   → กรองด้วย resource_id = "BR001", action = "branch_update", date = yesterday

2. User john@example.com ทำอะไรบ้างในเดือนนี้?
   → กรองด้วย user_email = "john@example.com", date range = this month

3. มีใครพยายาม login ไม่สำเร็จบ่อยๆ หรือไม่?
   → กรองด้วย action = "login_failed", สังเกต pattern

4. ใครเป็นคนเพิ่มสิทธิ์ให้ user นี้?
   → กรองด้วย action = "permission_add", target_user_id
```

## Legal ภ.พ.09 Management (สำหรับทีมกฎหมาย)

### Overview

ภ.พ.09 (ภาษีที่ดินและสิ่งปลูกสร้าง ภ.พ.๐๙) คือ แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง ซึ่งเป็นเอกสารสำคัญทางกฎหมายสำหรับการดำเนินธุรกิจค้าปลีก ทีมกฎหมายจะมีหน้าที่ในการจัดการข้อมูล ภ.พ.09 ของแต่ละสาขา พร้อมทั้งเก็บเอกสาร PDF ต้นฉบับ

### Legal ภ.พ.09 Management Page (`/legal/ppp09`)

**สิทธิ์การเข้าถึง:** ทีมกฎหมาย (Legal Team) และ Admin

**ฟีเจอร์:**
- **รายการ ภ.พ.09 ทั้งหมด**: แสดงตารางข้อมูล ภ.พ.09 ของทุกสาขา
- **ค้นหา**: ค้นหาด้วย รหัสสาขา, เลขที่ ภ.พ.09, ชื่อเจ้าของ, ที่อยู่
- **กรอง**: กรองตาม จังหวัด, สถานะการชำระภาษี, วันหมดอายุ
- **เพิ่ม ภ.พ.09 ใหม่**: สร้างข้อมูล ภ.พ.09 ใหม่พร้อม upload PDF
- **แก้ไข ภ.พ.09**: แก้ไขข้อมูลและอัพเดท PDF
- **ลบ ภ.พ.09**: ลบข้อมูล (soft delete)
- **ดาวน์โหลด PDF**: ดาวน์โหลดเอกสาร ภ.พ.09 ต้นฉบับ
- **แจ้งเตือนหมดอายุ**: แจ้งเตือน ภ.พ.09 ที่ใกล้หมดอายุ (เช่น 30, 60, 90 วันก่อนหมดอายุ)

**UI Components:**
- ตาราง ภ.พ.09 พร้อม pagination
- ปุ่ม "เพิ่ม ภ.พ.09 ใหม่" (primary button, มุมขวาบน)
- Search box และ filter dropdowns
- Actions column: View, Edit, Delete, Download PDF buttons
- Modal สำหรับเพิ่ม/แก้ไข ภ.พ.09
- Alert/Badge สำหรับ ภ.พ.09 ที่ใกล้หมดอายุ หรือค้างชำระภาษี

**ข้อมูลที่แสดงในตาราง:**
| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขาที่เกี่ยวข้อง (clickable -> link to branch details) |
| ชื่อสาขา | ชื่อสาขา |
| เลขที่ ภ.พ.09 | เลขที่เอกสาร ภ.พ.09 |
| ชื่อเจ้าของ | ชื่อผู้เสียภาษี |
| ที่อยู่ | ที่อยู่ (แสดงแบบย่อ) |
| วันที่ออก | วันที่ออกเอกสาร |
| วันหมดอายุ | วันหมดอายุ (แสดง badge ถ้าใกล้หมดอายุ) |
| ภาษีต่อปี | จำนวนเงินภาษีต่อปี (บาท) |
| สถานะชำระ | paid / unpaid / overdue |
| PDF | ไอคอน download (ถ้ามี PDF) |
| Actions | View / Edit / Delete buttons |

### Form: เพิ่ม/แก้ไข ภ.พ.09

**ฟอร์มแบ่งเป็น 4 sections:**

**1. ข้อมูลทั่วไป**
- รหัสสาขา (Dropdown/Autocomplete)
- เลขที่ ภ.พ.09 (Text input)
- ชื่อเจ้าของ/ผู้เสียภาษี (Text input)
- วันที่ออกเอกสาร (Date picker)
- วันหมดอายุ (Date picker)

**2. ที่อยู่ตาม ภ.พ.09 (แยกตาม field)**
- บ้านเลขที่ (Text input)
- หมู่ที่ (Text input)
- ตรอก (Text input - optional)
- ซอย (Text input - optional)
- ถนน (Text input - optional)
- ตำบล/แขวง (Text input)
- อำเภอ/เขต (Text input)
- จังหวัด (Dropdown - list of provinces)
- รหัสไปรษณีย์ (Text input - 5 digits)

**หมายเหตุ:** ที่อยู่ต้องแยกเป็น fields เพื่อให้ค้นหาและจัดการได้ง่าย

**3. ข้อมูลเนื้อที่และภาษี**
- เนื้อที่ดิน:
  - ไร่ (Number input)
  - งาน (Number input)
  - ตารางวา (Number input)
- พื้นที่สิ่งปลูกสร้าง (ตร.ม.) (Number input)
- จำนวนเงินภาษีต่อปี (บาท) (Number input)
- สถานะการชำระ (Dropdown: paid, unpaid, overdue)

**4. เอกสาร PDF และหมายเหตุ**
- อัพโหลด PDF ภ.พ.09 (File upload - accept PDF only, max 10MB)
  - แสดง preview/thumbnail ถ้ามี PDF อยู่แล้ว
  - ปุ่ม "Replace PDF" สำหรับเปลี่ยน PDF ใหม่
  - ปุ่ม "Download PDF" สำหรับดาวน์โหลด
  - ปุ่ม "Delete PDF" สำหรับลบ PDF
- หมายเหตุ (Textarea - optional)

**Validation:**
- รหัสสาขา: required, ต้องมีในระบบ
- เลขที่ ภ.พ.09: required
- ชื่อเจ้าของ: required
- วันที่ออกเอกสาร: required, ต้องไม่เกินวันนี้
- วันหมดอายุ: ต้องมากกว่าวันที่ออกเอกสาร
- ที่อยู่: บ้านเลขที่, ตำบล/แขวง, อำเภอ/เขต, จังหวัด, รหัสไปรษณีย์ = required
- รหัสไปรษณีย์: ต้องเป็นตัวเลข 5 หัก
- PDF: ถ้า upload ต้องเป็นไฟล์ PDF เท่านั้น, ขนาดไม่เกิน 10MB

**Buttons:**
- "บันทึก" (Primary button)
- "ยกเลิก" (Secondary button)

### UI/UX Considerations

**Address Fields Layout (2-column responsive grid):**
```
┌──────────────────────────────────────────┐
│ บ้านเลขที่         │ หมู่ที่             │
├──────────────────────────────────────────┤
│ ตรอก               │ ซอย                │
├──────────────────────────────────────────┤
│ ถนน                                      │
├──────────────────────────────────────────┤
│ ตำบล/แขวง         │ อำเภอ/เขต          │
├──────────────────────────────────────────┤
│ จังหวัด            │ รหัสไปรษณีย์        │
└──────────────────────────────────────────┘
```

**Land Area Fields Layout (3-column):**
```
┌──────────────────────────────────────────┐
│ เนื้อที่ดิน                               │
│ ไร่      │ งาน      │ ตารางวา           │
└──────────────────────────────────────────┘
```

**Status Badges:**
- **Paid**: เขียว (Success Green)
- **Unpaid**: ส้ม (Warning Orange)
- **Overdue**: แดง (Error Red)

**Expiry Alert:**
- ภ.พ.09 ที่หมดอายุภายใน 30 วัน → แสดง Warning badge สีส้ม
- ภ.พ.09 ที่หมดอายุแล้ว → แสดง Error badge สีแดง

**PDF Upload:**
- Drag & drop zone สำหรับ upload PDF
- Progress bar ระหว่าง upload
- Success message เมื่อ upload สำเร็จ
- Error message ถ้า upload ล้มเหลว

### API Endpoints

**GET /api/legal/ppp09**
- ดึงรายการ ภ.พ.09 ทั้งหมด
- รองรับ pagination, search, filter
- Response: List of PPP09 objects

**GET /api/legal/ppp09/{ppp09_id}**
- ดึงข้อมูล ภ.พ.09 รายการเดียว
- Response: PPP09 object

**POST /api/legal/ppp09**
- สร้าง ภ.พ.09 ใหม่
- Request body: PPP09 data (JSON)
- Response: Created PPP09 object

**PUT /api/legal/ppp09/{ppp09_id}**
- แก้ไขข้อมูล ภ.พ.09
- Request body: PPP09 data (JSON)
- Response: Updated PPP09 object

**DELETE /api/legal/ppp09/{ppp09_id}**
- ลบ ภ.พ.09 (soft delete)
- Response: Success message

**POST /api/legal/ppp09/{ppp09_id}/upload-pdf**
- อัพโหลด PDF เอกสาร ภ.พ.09
- Request: Multipart form-data with PDF file
- Response: File path and metadata

**GET /api/legal/ppp09/{ppp09_id}/download-pdf**
- ดาวน์โหลด PDF เอกสาร ภ.พ.09
- Response: PDF file (binary)

**DELETE /api/legal/ppp09/{ppp09_id}/delete-pdf**
- ลบ PDF เอกสาร ภ.พ.09
- Response: Success message

### Business Logic

**การตรวจสอบหมดอายุ:**
- Cron job หรือ Cloud Scheduler ทำงานทุกวัน
- ตรวจสอบ ภ.พ.09 ที่จะหมดอายุใน 30, 60, 90 วัน
- ส่ง email notification ไปยังทีมกฎหมาย

**การตรวจสอบการชำระภาษี:**
- แสดง badge/alert สำหรับ ภ.พ.09 ที่ยังไม่ชำระภาษี (unpaid)
- แสดง badge/alert แดงสำหรับ ภ.พ.09 ที่ค้างชำระ (overdue)

**PDF Storage:**
- เก็บ PDF ไว้ใน GCS bucket: `gs://{bucket}/legal/ppp09/{branch_id}_{ppp09_number}_{year}.pdf`
- ตั้งชื่อไฟล์ให้มีความหมายและไม่ซ้ำกัน
- เก็บ metadata (file_size, upload_time, uploader) ใน BigQuery

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
