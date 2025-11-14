# Retail Branch Management System - Documentation

## Project Overview

ระบบบริหารจัดการข้อมูลสาขาของร้านสะดวกซื้อ (Retail Branch Management System) เป็น Web Application ที่ออกแบบมาเพื่อให้หลายทีมงานสามารถจัดการข้อมูลสาขาได้อย่างมีประสิทธิภาพ โดยแต่ละทีมจะเห็นเฉพาะเมนูและข้อมูลที่เกี่ยวข้องกับทีมของตนเองเท่านั้น

## Core Features

- **User Authentication (Google OAuth 2.0)**: ระบบ login เข้าใช้งานผ่าน Google Account โดยผู้ใช้ทุกคนต้อง login ก่อนเข้าใช้งานระบบ
- **User Management & Permissions**: จัดการผู้ใช้และกำหนดสิทธิ์การเข้าถึงเมนูต่างๆ โดย user 1 คนสามารถเข้าถึงได้มากกว่า 1 เมนู
- **CRUD Operations**: สามารถเพิ่ม แก้ไข และลบข้อมูลสาขาได้
- **Multi-Team Access**: รองรับการเข้าใช้งานของหลายทีม โดยแต่ละทีมมีสิทธิ์และเห็นเมนูเฉพาะของตนเอง
- **Branch Data Management**: จัดการข้อมูลสาขา เช่น รหัสสาขา, ชื่อสาขา, ที่อยู่
- **Document Management**: จัดเก็บและจัดการเอกสารที่เกี่ยวข้องกับแต่ละสาขา
- **Responsive Design**: รองรับการใช้งานบนทุกอุปกรณ์ (Desktop, Tablet, Mobile)

## Team Roles & Permissions

| ทีม | หน้าที่ | ข้อมูลที่เข้าถึง |
|-----|---------|-----------------|
| **ทีมสาขาใหม่** | จัดการข้อมูลการเปิดสาขาใหม่ | ข้อมูลสาขาที่กำลังเปิดใหม่, สถานะการเปิดสาขา, timeline |
| **ทีมกฎหมาย** | จัดการเอกสารทางกฎหมายและข้อมูล ภ.พ.09 | เอกสารสัญญา, ใบอนุญาต, ภ.พ.09 (แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง), เอกสารกฎหมายของแต่ละสาขา |
| **ทีม SRD** | จัดการเอกสาร layout | แปลนผัง, layout ร้าน, floor plan ของแต่ละสาขา |
| **ทีม SCM** | จัดการข้อมูล DC | ข้อมูล Distribution Center ที่รับผิดชอบแต่ละสาขา |

**หมายเหตุ:**
- ผู้ใช้ 1 คนสามารถเป็นสมาชิกของหลายทีมได้ (Multi-Team Membership)
- Admin สามารถกำหนดสิทธิ์ให้ user เข้าถึงเมนูต่างๆ ได้ผ่านหน้า User Management

## User Levels

| Level | สิทธิ์ | คำอธิบาย |
|-------|-------|---------|
| **Admin** | จัดการระบบทั้งหมด | จัดการ users, permissions, ทุก teams, ทุกข้อมูล |
| **Manager** | จัดการทีมของตัวเอง | จัดการข้อมูลและ users ในทีมที่ตัวเองรับผิดชอบ |
| **Editor** | แก้ไขข้อมูล | สามารถเพิ่ม แก้ไข ข้อมูลในทีมที่มีสิทธิ์ |
| **Viewer** | ดูข้อมูลอย่างเดียว | ดูข้อมูลในทีมที่มีสิทธิ์ ไม่สามารถแก้ไขได้ |

## Documentation Structure

เอกสารถูกแบ่งออกตามหน้าที่การทำงาน:

### Architecture & Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System Architecture & Tech Stack
- **[DATABASE.md](DATABASE.md)** - Database Schema (BigQuery)
- **[DESIGN.md](DESIGN.md)** - Design & UI/UX Guidelines

### Features
- **[features/user-management.md](features/user-management.md)** - User Management & Permissions
- **[features/audit-logs.md](features/audit-logs.md)** - Audit Logs & Activity Tracking
- **[features/legal-ppp09.md](features/legal-ppp09.md)** - Legal ภ.พ.09 Management

### Development
- **[development/setup.md](development/setup.md)** - Local Development Setup
- **[development/guidelines.md](development/guidelines.md)** - Development Guidelines & Code Style

### Deployment
- **[deployment/docker.md](deployment/docker.md)** - Docker Setup
- **[deployment/cicd.md](deployment/cicd.md)** - CI/CD Pipeline (GitLab CI)
- **[deployment/cloud-run.md](deployment/cloud-run.md)** - Google Cloud Run Deployment

### Authentication & Frontend
- **[auth/oauth.md](auth/oauth.md)** - Google OAuth 2.0 Authentication
- **[frontend/tailwind.md](frontend/tailwind.md)** - Tailwind CSS Setup

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (สำหรับ Tailwind CSS)
- UV Package Manager
- Google Cloud Project with BigQuery & GCS

### Setup

```bash
# Setup environment
chmod +x scripts/*.sh
./scripts/setup_local.sh

# Run development server
./scripts/run_local.sh
```

ดูรายละเอียดเพิ่มเติมใน [development/setup.md](development/setup.md)

## Tech Stack Summary

**Backend:**
- Python 3.12 + FastAPI
- Google OAuth 2.0
- BigQuery (Database)
- Google Cloud Storage (Files)
- Uvicorn (ASGI server)
- UV (Package manager)

**Frontend:**
- HTML5/CSS3
- Vanilla JavaScript
- Tailwind CSS

**Infrastructure:**
- Google Cloud Run
- Docker
- GitLab CI/CD

## Design Philosophy

- **Minimalist & Clean**: ดีไซน์เรียบง่าย ไม่วุ่นวาย เน้นเนื้อหาที่สำคัญ
- **Modern UI**: ใช้ design patterns ที่ทันสมัยและเป็นมาตรฐานของอุตสาหกรรม
- **User-Centric**: ออกแบบโดยคำนึงถึงผู้ใช้งานเป็นหลัก ใช้งานง่าย เข้าใจง่าย
- **Responsive First**: รองรับทุกอุปกรณ์ (Mobile, Tablet, Desktop)

## Next Steps

1. อ่าน [ARCHITECTURE.md](ARCHITECTURE.md) เพื่อเข้าใจ system architecture
2. ศึกษา [DATABASE.md](DATABASE.md) สำหรับ database schema
3. ตั้งค่า development environment ตาม [development/setup.md](development/setup.md)
4. ทำความเข้าใจ [auth/oauth.md](auth/oauth.md) สำหรับ OAuth flow
5. เริ่มพัฒนาตาม [development/guidelines.md](development/guidelines.md)

## Notes

- **ผู้ใช้ทุกคนต้อง login ผ่าน Google OAuth 2.0 ก่อนเข้าใช้งาน**
- ระบบนี้เน้นความเรียบง่ายและประสิทธิภาพ
- แต่ละทีมมี view และ permissions แยกกัน
- Session-based authentication พร้อม secure cookies
- Code ต้องอ่านง่าย maintain ง่าย
