# User Management & Permissions

## Overview

ระบบมีหน้าจัดการผู้ใช้และสิทธิ์สำหรับ Admin ในการควบคุมการเข้าถึงของผู้ใช้แต่ละคน โดยผู้ใช้ 1 คนสามารถเข้าถึงได้มากกว่า 1 ทีม/เมนู

## User Management Page (`/admin/users`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

### ฟีเจอร์
- **รายการผู้ใช้ทั้งหมด**: แสดงตารางผู้ใช้พร้อม email, name, user level, status
- **ค้นหาผู้ใช้**: ค้นหาด้วย email หรือ name
- **กรองผู้ใช้**: กรองตาม user level (admin, manager, editor, viewer) หรือ status (active/inactive)
- **เพิ่มผู้ใช้ใหม่**: เพิ่ม user ใหม่ (กรอก email, name, เลือก user level)
- **แก้ไขผู้ใช้**: แก้ไข name, user level, status
- **ลบผู้ใช้**: ปิดการใช้งาน (soft delete โดยตั้ง is_active = false)

### UI Components
- ตาราง users พร้อม pagination
- ปุ่ม "Add User" (primary button, มุมขวาบน)
- Search box และ filter dropdowns
- Actions column: Edit, Deactivate/Activate buttons
- Modal สำหรับเพิ่ม/แก้ไข user

### ข้อมูลที่แสดง

| Column | Description |
|--------|-------------|
| Email | อีเมลผู้ใช้ |
| Name | ชื่อผู้ใช้ |
| User Level | admin / manager / editor / viewer |
| Teams | จำนวนทีมที่สังกัด (clickable เพื่อดู details) |
| Status | Active / Inactive |
| Last Login | เข้าสู่ระบบล่าสุด |
| Actions | Edit / Deactivate buttons |

## User Permissions Page (`/admin/permissions`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

### ฟีเจอร์
- **เลือกผู้ใช้**: Dropdown หรือ autocomplete สำหรับเลือก user
- **แสดงทีมปัจจุบัน**: แสดง teams ที่ user มีสิทธิ์เข้าถึง
- **เพิ่มสิทธิ์เข้าทีม**: เลือกทีมและ role (viewer/editor/manager) แล้วเพิ่ม
- **แก้ไขสิทธิ์**: เปลี่ยน role ในแต่ละทีม
- **ลบสิทธิ์**: ลบสิทธิ์ออกจากทีม

### Workflow
1. Admin เลือก user จาก dropdown
2. ระบบแสดงทีมและ role ที่ user มีสิทธิ์
3. Admin สามารถ:
   - เพิ่มสิทธิ์ใหม่ (เลือกทีม + role)
   - แก้ไข role ในทีมที่มีอยู่
   - ลบสิทธิ์ออกจากทีม
4. บันทึกการเปลี่ยนแปลงลง BigQuery

## Permission Logic

**การตรวจสอบสิทธิ์:**
1. ตรวจสอบ `user_level` จาก `users` table
   - ถ้าเป็น `admin` → อนุญาตให้เข้าถึงทุกอย่าง
2. ตรวจสอบ `user_teams` table
   - ดึง teams ที่ user มีสิทธิ์
   - ตรวจสอบ role ในแต่ละทีม
3. แสดงเฉพาะเมนูที่ user มีสิทธิ์

### User Level Permissions

| User Level | Permissions |
|-----------|-------------|
| **Admin** | - เข้าถึงทุก teams และทุกเมนู<br>- จัดการ users<br>- กำหนดสิทธิ์<br>- ดู/แก้ไข/ลบข้อมูลทั้งหมด |
| **Manager** | - เข้าถึง teams ที่มีสิทธิ์<br>- จัดการข้อมูลในทีมของตัวเอง<br>- ไม่สามารถจัดการ users ได้ |
| **Editor** | - เข้าถึง teams ที่มีสิทธิ์<br>- เพิ่ม/แก้ไขข้อมูล<br>- ไม่สามารถลบข้อมูล |
| **Viewer** | - เข้าถึง teams ที่มีสิทธิ์<br>- ดูข้อมูลอย่างเดียว<br>- ไม่สามารถแก้ไขหรือลบ |

## Navigation for Admin

Admin จะเห็นเมนูเพิ่มเติม:
- **Users**: จัดการผู้ใช้
- **Permissions**: กำหนดสิทธิ์ผู้ใช้
- **All Teams**: เข้าถึงทุกทีม (New Branch, Legal, SRD, SCM)

## API Endpoints

### User Management APIs

#### GET `/api/admin/users`
ดึงรายการผู้ใช้ทั้งหมด

**Query Parameters:**
- `page` (optional): หมายเลขหน้า (default: 1)
- `limit` (optional): จำนวนรายการต่อหน้า (default: 20, max: 100)
- `search` (optional): ค้นหาจาก email หรือ name
- `user_level` (optional): กรองตาม user level (admin, manager, editor, viewer)
- `status` (optional): กรองตาม status (active, inactive)
- `sort` (optional): เรียงลำดับ (created_at, last_login, email) ใช้ - สำหรับ descending

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "uuid-123",
      "email": "john@example.com",
      "name": "John Doe",
      "user_level": "editor",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-03-20T14:25:00Z",
      "teams_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

#### GET `/api/admin/users/{user_id}`
ดึงข้อมูลผู้ใช้รายเดียว

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-123",
    "email": "john@example.com",
    "name": "John Doe",
    "user_level": "editor",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-02-10T09:15:00Z",
    "last_login": "2024-03-20T14:25:00Z",
    "teams": [
      {
        "user_team_id": "uuid-456",
        "team_name": "legal",
        "role": "editor",
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "user_team_id": "uuid-789",
        "team_name": "new_branch",
        "role": "viewer",
        "created_at": "2024-01-20T11:00:00Z"
      }
    ]
  }
}
```

#### POST `/api/admin/users`
สร้างผู้ใช้ใหม่

**Request Body:**
```json
{
  "email": "jane@example.com",
  "name": "Jane Smith",
  "user_level": "editor"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": "uuid-new",
    "email": "jane@example.com",
    "name": "Jane Smith",
    "user_level": "editor",
    "is_active": true,
    "created_at": "2024-03-25T10:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "email": ["Email already exists"],
    "user_level": ["Must be one of: admin, manager, editor, viewer"]
  },
  "code": "VALIDATION_ERROR"
}
```

#### PUT `/api/admin/users/{user_id}`
แก้ไขข้อมูลผู้ใช้

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "user_level": "manager",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "user_id": "uuid-123",
    "email": "john@example.com",
    "name": "John Doe Updated",
    "user_level": "manager",
    "is_active": true,
    "updated_at": "2024-03-25T11:30:00Z"
  }
}
```

#### DELETE `/api/admin/users/{user_id}`
ปิดการใช้งานผู้ใช้ (soft delete)

**Response:**
```json
{
  "success": true,
  "message": "User deactivated successfully",
  "data": {
    "user_id": "uuid-123",
    "is_active": false
  }
}
```

### Permission Management APIs

#### GET `/api/admin/permissions/{user_id}`
ดึงสิทธิ์ทั้งหมดของผู้ใช้

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-123",
    "email": "john@example.com",
    "name": "John Doe",
    "permissions": [
      {
        "user_team_id": "uuid-456",
        "team_name": "legal",
        "role": "editor",
        "created_at": "2024-01-15T10:30:00Z",
        "created_by": "admin@example.com"
      },
      {
        "user_team_id": "uuid-789",
        "team_name": "new_branch",
        "role": "viewer",
        "created_at": "2024-01-20T11:00:00Z",
        "created_by": "admin@example.com"
      }
    ]
  }
}
```

#### POST `/api/admin/permissions`
เพิ่มสิทธิ์ให้ผู้ใช้เข้าทีม

**Request Body:**
```json
{
  "user_id": "uuid-123",
  "team_name": "srd",
  "role": "manager"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permission added successfully",
  "data": {
    "user_team_id": "uuid-new",
    "user_id": "uuid-123",
    "team_name": "srd",
    "role": "manager",
    "created_at": "2024-03-25T12:00:00Z",
    "created_by": "admin@example.com"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Permission already exists",
  "message": "User already has access to this team",
  "code": "DUPLICATE_PERMISSION"
}
```

#### PUT `/api/admin/permissions/{user_team_id}`
แก้ไข role ของผู้ใช้ในทีม

**Request Body:**
```json
{
  "role": "editor"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permission updated successfully",
  "data": {
    "user_team_id": "uuid-456",
    "user_id": "uuid-123",
    "team_name": "legal",
    "role": "editor",
    "updated_at": "2024-03-25T13:00:00Z"
  }
}
```

#### DELETE `/api/admin/permissions/{user_team_id}`
ลบสิทธิ์ผู้ใช้ออกจากทีม

**Response:**
```json
{
  "success": true,
  "message": "Permission removed successfully"
}
```

### Authentication Required
**ทุก API endpoint ต้องมี authentication และเฉพาะ Admin เท่านั้นที่เข้าถึงได้**

**Error Response (Unauthorized):**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Admin access required",
  "code": "UNAUTHORIZED"
}
```

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema for users and user_teams tables
- [audit-logs.md](audit-logs.md) - Audit logging for user management actions
