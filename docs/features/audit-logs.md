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

## API Endpoints

### GET `/api/admin/audit-logs`
ดึงรายการ audit logs

**Query Parameters:**
- `page` (optional): หมายเลขหน้า (default: 1)
- `limit` (optional): จำนวนรายการต่อหน้า (default: 50, max: 100)
- `user_id` (optional): กรองตามผู้ใช้
- `user_email` (optional): กรองตามอีเมลผู้ใช้
- `action_type` (optional): กรองตาม action (login, create, update, delete, etc.)
- `resource_type` (optional): กรองตาม resource (branch, document, user, permission, ppp09, ppp20, srd_layout, scm_dc, new_branch)
- `resource_id` (optional): กรองตาม resource ID เฉพาะ
- `status` (optional): กรองตาม status (success, failed)
- `date_from` (optional): กรองตั้งแต่วันที่ (format: YYYY-MM-DD)
- `date_to` (optional): กรองถึงวันที่ (format: YYYY-MM-DD)
- `search` (optional): ค้นหาจาก email, resource_id, action_detail
- `sort` (optional): เรียงลำดับ (created_at, user_email, action_type) ใช้ - สำหรับ descending (default: -created_at)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "log_id": "uuid-log-123",
      "user_id": "uuid-user-456",
      "user_email": "john@example.com",
      "action_type": "ppp09_update",
      "resource_type": "ppp09",
      "resource_id": "PPP09-001",
      "action_detail": {
        "ppp09_id": "PPP09-001",
        "branch_id": "BR001",
        "changes": {
          "branch_status": {
            "old": "ยังไม่จดสรรพากร",
            "new": "เปิดให้บริการ"
          }
        }
      },
      "ip_address": "203.154.123.45",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
      "status": "success",
      "error_message": null,
      "created_at": "2024-03-25T14:30:15Z"
    },
    {
      "log_id": "uuid-log-124",
      "user_id": "uuid-user-789",
      "user_email": "admin@example.com",
      "action_type": "permission_add",
      "resource_type": "permission",
      "resource_id": "uuid-perm-999",
      "action_detail": {
        "target_user_id": "uuid-user-456",
        "target_user_email": "john@example.com",
        "team_name": "legal",
        "role": "editor"
      },
      "ip_address": "203.154.123.50",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
      "status": "success",
      "error_message": null,
      "created_at": "2024-03-25T10:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1523,
    "total_pages": 31
  }
}
```

### GET `/api/admin/audit-logs/{log_id}`
ดึงรายละเอียด audit log เฉพาะรายการ

**Response:**
```json
{
  "success": true,
  "data": {
    "log_id": "uuid-log-123",
    "user_id": "uuid-user-456",
    "user_email": "john@example.com",
    "user_name": "John Doe",
    "action_type": "new_branch_status_change",
    "resource_type": "new_branch",
    "resource_id": "BR005",
    "action_detail": {
      "branch_id": "BR005",
      "branch_name": "สาขาสยาม",
      "status_change": {
        "from": "ก่อสร้าง",
        "to": "เปิดทำการ"
      },
      "actual_opening_date": "2024-03-25"
    },
    "ip_address": "203.154.123.45",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "status": "success",
    "error_message": null,
    "created_at": "2024-03-25T14:30:15Z"
  }
}
```

### GET `/api/admin/audit-logs/export`
Export audit logs เป็น CSV

**Query Parameters:** (เหมือนกับ GET `/api/admin/audit-logs`)

**Response:** CSV file download
```
Content-Type: text/csv
Content-Disposition: attachment; filename="audit_logs_2024-03-25.csv"

log_id,timestamp,user_email,action_type,resource_type,resource_id,status,ip_address
uuid-log-123,2024-03-25T14:30:15Z,john@example.com,ppp09_update,ppp09,PPP09-001,success,203.154.123.45
...
```

### GET `/api/admin/audit-logs/stats`
สรุปสถิติ audit logs

**Query Parameters:**
- `date_from` (optional): วันที่เริ่มต้น
- `date_to` (optional): วันที่สิ้นสุด

**Response:**
```json
{
  "success": true,
  "data": {
    "total_logs": 1523,
    "date_range": {
      "from": "2024-03-01",
      "to": "2024-03-25"
    },
    "by_action_type": {
      "login": 345,
      "ppp09_update": 123,
      "new_branch_create": 45,
      "permission_add": 23,
      "document_upload": 234
    },
    "by_resource_type": {
      "ppp09": 156,
      "ppp20": 89,
      "new_branch": 67,
      "srd_layout": 45,
      "scm_dc": 34
    },
    "by_user": [
      {
        "user_email": "admin@example.com",
        "count": 456
      },
      {
        "user_email": "john@example.com",
        "count": 234
      }
    ],
    "by_status": {
      "success": 1500,
      "failed": 23
    }
  }
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

### API Rate Limiting
- **Default**: 100 requests per minute per user
- **Export endpoint**: 5 requests per minute per user

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Audit logs table schema
- [user-management.md](user-management.md) - User management actions that generate audit logs
