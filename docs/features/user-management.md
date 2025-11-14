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

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema for users and user_teams tables
- [audit-logs.md](audit-logs.md) - Audit logging for user management actions
