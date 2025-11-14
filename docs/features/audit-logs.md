# Audit Logs & Activity Tracking

## Overview

ระบบมีการบันทึก activity ทั้งหมดของผู้ใช้ (รวมถึง Admin) เพื่อติดตามว่า **ใคร ทำอะไร เมื่อไหร่** โดยเก็บไว้ใน `audit_logs` table

## Audit Logs Page (`/admin/audit-logs`)

**สิทธิ์การเข้าถึง:** เฉพาะ Admin เท่านั้น

### ฟีเจอร์
- **ดูบันทึก activity ทั้งหมด**: แสดงตาราง audit logs พร้อม filter และ search
- **กรองตามผู้ใช้**: เลือกดู activity ของ user คนใดคนหนึ่ง
- **กรองตาม action type**: login, create, update, delete, permission_change
- **กรองตาม resource**: branch, document, user, permission, ppp09, ppp20, srd_layout, scm_dc, new_branch
- **กรองตามช่วงเวลา**: เลือกช่วงวันที่
- **ค้นหา**: ค้นหาจาก email, resource_id, action_detail
- **Export**: Export logs เป็น CSV สำหรับการวิเคราะห์

### ข้อมูลที่แสดง

| Column | Description |
|--------|-------------|
| Timestamp | วันเวลาที่เกิด event |
| User | ชื่อและอีเมลผู้ใช้ |
| Action | ประเภท action (login, create, update, delete) |
| Resource | ทรัพยากรที่เกี่ยวข้อง (branch, document, user) |
| Details | รายละเอียด action (expandable) |
| IP Address | IP address ของผู้ใช้ |
| Status | Success / Failed |

## Actions ที่บันทึก

### Authentication Actions
- `login` - ผู้ใช้ login เข้าระบบ
- `logout` - ผู้ใช้ logout ออกจากระบบ
- `login_failed` - ความพยายาม login ที่ล้มเหลว

### Branch Actions
- `branch_create` - สร้างข้อมูลสาขาใหม่
- `branch_update` - แก้ไขข้อมูลสาขา
- `branch_delete` - ลบข้อมูลสาขา

### Document Actions
- `document_upload` - อัพโหลดเอกสาร
- `document_download` - ดาวน์โหลดเอกสาร
- `document_delete` - ลบเอกสาร

### User Management Actions
- `user_create` - สร้าง user ใหม่
- `user_update` - แก้ไขข้อมูล user
- `user_deactivate` - ปิดการใช้งาน user
- `user_activate` - เปิดการใช้งาน user

### Permission Management Actions
- `permission_add` - เพิ่มสิทธิ์ให้ user เข้าทีม
- `permission_update` - แก้ไข role ของ user ในทีม
- `permission_remove` - ลบสิทธิ์ user ออกจากทีม

### Legal Team - ภ.พ.09 Management Actions
- `ppp09_create` - สร้างข้อมูล ภ.พ.09 ใหม่
- `ppp09_update` - แก้ไขข้อมูล ภ.พ.09
- `ppp09_delete` - ลบข้อมูล ภ.พ.09
- `ppp09_document_upload` - อัพโหลดเอกสาร ภ.พ.09
- `ppp09_document_download` - ดาวน์โหลดเอกสาร ภ.พ.09
- `ppp09_document_delete` - ลบเอกสาร ภ.พ.09

### Legal Team - ภ.พ.20 Management Actions
- `ppp20_create` - สร้างข้อมูล ภ.พ.20 ใหม่
- `ppp20_update` - แก้ไขข้อมูล ภ.พ.20
- `ppp20_delete` - ลบข้อมูล ภ.พ.20
- `ppp20_document_upload` - อัพโหลดเอกสาร ภ.พ.20
- `ppp20_document_download` - ดาวน์โหลดเอกสาร ภ.พ.20
- `ppp20_document_delete` - ลบเอกสาร ภ.พ.20

### SRD Team - Layout Management Actions
- `srd_layout_create` - สร้างข้อมูล Layout ใหม่
- `srd_layout_update` - แก้ไขข้อมูล Layout
- `srd_layout_delete` - ลบข้อมูล Layout
- `srd_layout_renovate` - อัพเดทวันที่ Renovate (event พิเศษ)

### SCM Team - DC Management Actions
- `scm_dc_change_scheduled` - กำหนดการเปลี่ยน DC
- `scm_dc_change_completed` - เปลี่ยน DC สำเร็จ (auto)
- `scm_dc_schedule_updated` - แก้ไขกำหนดการเปลี่ยน DC
- `scm_dc_schedule_cancelled` - ยกเลิกกำหนดการเปลี่ยน DC

### New Branch Team - Branch Tracking Actions
- `new_branch_create` - สร้างข้อมูลสาขาใหม่
- `new_branch_update` - แก้ไขข้อมูลสาขาใหม่
- `new_branch_delete` - ลบข้อมูลสาขาใหม่
- `new_branch_status_change` - เปลี่ยนสถานะสาขา (รอเปิด → ก่อสร้าง → เปิดทำการ)
- `new_branch_opened` - บันทึกวันเปิดสาขาจริง (Actual Opening Date)

## Audit Log Retention

**นโยบายการเก็บข้อมูล:**
- เก็บ audit logs ทั้งหมดใน BigQuery (ไม่มีการลบ)
- Partition โดย created_at (รายวัน) เพื่อประสิทธิภาพในการ query
- Clustering โดย user_id และ action_type
- สามารถ archive logs เก่ากว่า 1 ปี ไปยัง GCS (ถ้าต้องการประหยัดค่าใช้จ่าย)

## Security & Privacy

**การรักษาความปลอดภัย:**
- ห้าม edit หรือ delete audit logs
- Append-only (เพิ่มได้อย่างเดียว)
- เฉพาะ Admin เท่านั้นที่ดู audit logs ได้
- ไม่เก็บข้อมูล sensitive (เช่น password, tokens) ใน action_detail
- Encrypt sensitive fields ถ้าจำเป็น

## Usage Examples

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

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Audit logs table schema
- [user-management.md](user-management.md) - User management actions that generate audit logs
