# SCM Team - ทีม SCM (Supply Chain Management)

## Overview

ทีม SCM มีหน้าที่จัดการข้อมูล Distribution Center (DC) ของแต่ละสาขา โดยมีเมนูหลักคือ **จัดการข้อมูล DC ของสาขา** สำหรับดูและเปลี่ยนแปลง DC ที่รับผิดชอบแต่ละสาขา พร้อมกำหนดวันที่มีผลล่วงหน้า

**สิทธิ์การเข้าถึง:** ทีม SCM และ Admin

---

## จัดการข้อมูล DC ของสาขา

### Overview

จัดการข้อมูล Distribution Center (DC) ที่รับผิดชอบแต่ละสาขา รวมถึงการเปลี่ยน DC และกำหนดวันที่มีผลล่วงหน้า เพื่อให้ระบบ Supply Chain สามารถวางแผนการจัดส่งสินค้าได้อย่างมีประสิทธิภาพ

### หน้าจัดการ DC ของสาขา (`/scm/dc`)

#### ฟีเจอร์
- **รายการ DC ของสาขาทั้งหมด**: แสดงตาราง DC ปัจจุบันและอนาคตของทุกสาขา
- **ค้นหา/กรอง**:
  - รหัสสาขา
  - ชื่อสาขา
  - จังหวัด
  - อำเภอ
  - DC (DC1, DC2, DC4)
  - วันที่มีผล
- **แสดง DC ปัจจุบัน**: แสดง DC ที่กำลังรับผิดชอบสาขาในปัจจุบัน
- **เปลี่ยน DC**: เปลี่ยน DC ไปยัง DC อื่น (DC1, DC2, DC4)
- **กำหนดวันที่มีผล**: ตั้งวันที่มีผลล่วงหน้าสำหรับการเปลี่ยน DC
- **ดูประวัติการเปลี่ยน DC**: แสดงประวัติการเปลี่ยน DC ของแต่ละสาขา
- **แจ้งเตือน DC ที่จะเปลี่ยน**: แสดงรายการสาขาที่จะเปลี่ยน DC ในอนาคต

#### ข้อมูลที่แสดงในตาราง

| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขา (clickable -> link to branch details) |
| ชื่อสาขา | ชื่อสาขา |
| จังหวัด | จังหวัดที่ตั้งสาขา |
| อำเภอ | อำเภอที่ตั้งสาขา |
| DC ปัจจุบัน | DC ที่รับผิดชอบในปัจจุบัน (DC1/DC2/DC4) |
| DC อนาคต | DC ที่จะเปลี่ยนไป (ถ้ามีกำหนดการ) |
| วันที่มีผล | วันที่จะเปลี่ยน DC (ถ้ามีกำหนดการ) |
| สถานะ | Active / Scheduled (มีกำหนดการเปลี่ยน) |
| Actions | View / Change DC / Cancel Schedule buttons |

### Form: เปลี่ยน DC

**ฟอร์มแบ่งเป็น 3 sections:**

#### 1. ข้อมูลสาขา
- **รหัสสาขา** (Dropdown/Autocomplete) - required
- **ชื่อสาขา** (Auto-fill จากรหัสสาขา) - read-only
- **จังหวัด** (Auto-fill จากข้อมูลสาขา) - read-only
- **อำเภอ** (Auto-fill จากข้อมูลสาขา) - read-only

#### 2. ข้อมูล DC
- **DC ปัจจุบัน** (Display field) - read-only
  - แสดง DC ที่รับผิดชอบในปัจจุบัน
  - Badge สี: DC1 (Blue), DC2 (Green), DC4 (Orange)
- **DC ใหม่** (Dropdown) - required
  - เลือก DC ที่ต้องการเปลี่ยนไป
  - Options: DC1, DC2, DC4
  - ต้องไม่เหมือนกับ DC ปัจจุบัน
- **วันที่มีผล** (Date picker) - required
  - เลือกวันที่ต้องการให้มีผล
  - ต้องเป็นวันที่ในอนาคต (ไม่สามารถเลือกวันนี้หรือย้อนหลังได้)
  - แนะนำ: กำหนดล่วงหน้าอย่างน้อย 7 วัน

#### 3. เหตุผลและหมายเหตุ
- **เหตุผลในการเปลี่ยน DC** (Textarea) - required
  - ระบุเหตุผลในการเปลี่ยน DC เช่น:
    - "ปรับโครงสร้าง Supply Chain ภาคกลาง"
    - "เพิ่มประสิทธิภาพการจัดส่ง"
    - "DC เดิมเต็มกำลังการผลิต"
- **หมายเหตุ** (Textarea) - optional
  - หมายเหตุเพิ่มเติม

### Validation Rules

- **รหัสสาขา**: required, ต้องมีในระบบ (ตาราง branches)
- **DC ใหม่**: required, ต้องไม่เหมือนกับ DC ปัจจุบัน, ต้องเป็น DC1, DC2, หรือ DC4
- **วันที่มีผล**: required, ต้องเป็นวันที่ในอนาคต (มากกว่าวันนี้)
- **เหตุผลในการเปลี่ยน DC**: required, อย่างน้อย 10 ตัวอักษร
- **ไม่สามารถมีกำหนดการเปลี่ยน DC ซ้อนทับกัน**: ถ้าสาขามีกำหนดการเปลี่ยน DC อยู่แล้ว ต้อง cancel กำหนดการเดิมก่อน

### UI Components

#### DC Badges
- **DC1**: น้ำเงิน (Primary Blue) - `#3B82F6`
- **DC2**: เขียว (Success Green) - `#10B981`
- **DC4**: ส้ม (Warning Orange) - `#F59E0B`

#### Status Badges
- **Active**: เขียว (Success Green) - DC ปัจจุบันที่ใช้งานอยู่
- **Scheduled**: ส้ม (Warning Orange) - มีกำหนดการเปลี่ยน DC ในอนาคต
- **Pending**: น้ำเงิน (Primary Blue) - รอวันที่มีผล (ใช้เมื่อใกล้ถึงวันที่มีผล เช่น 3 วันก่อน)

#### Alert/Warning
- **การเปลี่ยน DC ที่ใกล้จะมีผล (7 วันก่อน)**: แสดง warning badge สีส้ม
- **การเปลี่ยน DC ที่ใกล้จะมีผล (3 วันก่อน)**: แสดง alert badge สีแดง

### API Endpoints

```
GET    /api/scm/dc                         # ดึงรายการ DC ของสาขาทั้งหมด (รองรับ pagination, search, filter)
GET    /api/scm/dc/{branch_id}             # ดึงข้อมูล DC ของสาขา (current + scheduled)
POST   /api/scm/dc/change                  # เปลี่ยน DC (สร้างกำหนดการใหม่)
PUT    /api/scm/dc/schedule/{schedule_id}  # แก้ไขกำหนดการเปลี่ยน DC
DELETE /api/scm/dc/schedule/{schedule_id}  # ยกเลิกกำหนดการเปลี่ยน DC

# History & Scheduled Changes
GET    /api/scm/dc/{branch_id}/history     # ดึงประวัติการเปลี่ยน DC
GET    /api/scm/dc/scheduled                # ดึงรายการสาขาที่มีกำหนดการเปลี่ยน DC
GET    /api/scm/dc/upcoming                 # ดึงรายการเปลี่ยน DC ที่จะมีผลใน 7 วันข้างหน้า
```

### Business Logic

#### การเปลี่ยน DC อัตโนมัติ
- ระบบจะมี Cron Job หรือ Cloud Scheduler ทำงานทุกวันเวลา 00:00
- ตรวจสอบ `scm_dc_schedule` table หา records ที่ `effective_date = วันนี้` และ `status = 'scheduled'`
- อัพเดท `scm_dc_assignment.current_dc` เป็น DC ใหม่
- อัพเดท `scm_dc_schedule.status` เป็น `'completed'`
- บันทึก audit log สำหรับการเปลี่ยน DC

#### การแจ้งเตือน
- **7 วันก่อนวันที่มีผล**: ส่ง notification ไปยังทีม SCM และสาขาที่เกี่ยวข้อง
- **3 วันก่อนวันที่มีผล**: ส่ง alert notification พร้อม confirmation
- **1 วันก่อนวันที่มีผล**: ส่ง final reminder

#### Filter Logic
- **รหัสสาขา**: ค้นหาแบบ exact match หรือ partial match
- **ชื่อสาขา**: ค้นหาแบบ partial match
- **จังหวัด/อำเภอ**: Dropdown selection
- **DC**: กรองตาม DC1, DC2, DC4 (ทั้ง current และ scheduled)
- **วันที่มีผล**: กรองช่วงวันที่ (date range)
- **สถานะ**: กรองตาม Active, Scheduled

#### ประวัติการเปลี่ยน DC
- แสดงประวัติ 12 เดือนล่าสุด (หรือทั้งหมด)
- แสดง: วันที่เปลี่ยน, DC เดิม, DC ใหม่, เหตุผล, ผู้ทำรายการ
- สามารถ export เป็น CSV หรือ Excel

---

## UI/UX Guidelines

### Navigation

**SCM Team Navbar:**
```
[Logo] | Dashboard | DC Management | Reports | [User Avatar ▼]
```

### Color Coding

**ทีม SCM Accent Color:** Green `#10B981` (Efficiency, Logistics)

ใช้ accent color ใน:
- Page headers
- Active menu items
- Primary buttons
- Team badges

### Responsive Design

- **Desktop**: แสดงตารางแบบเต็ม พร้อม filters และ upcoming changes panel
- **Tablet**: ตารางแบบ scroll horizontal, filters แบบ collapsible
- **Mobile**: แสดงแบบ card list, filters แบบ modal/bottom sheet

### Form Layout (2-column responsive grid)

```
┌──────────────────────────────────────────┐
│ รหัสสาขา           │ ชื่อสาขา (read-only)│
├──────────────────────────────────────────┤
│ จังหวัด (read-only)│ อำเภอ (read-only)   │
├──────────────────────────────────────────┤
│ DC ปัจจุบัน (read-only)                  │
├──────────────────────────────────────────┤
│ DC ใหม่            │ วันที่มีผล          │
├──────────────────────────────────────────┤
│ เหตุผลในการเปลี่ยน DC                    │
├──────────────────────────────────────────┤
│ หมายเหตุ                                 │
└──────────────────────────────────────────┘
```

### Upcoming Changes Panel

แสดงรายการสาขาที่จะเปลี่ยน DC ใน 7 วันข้างหน้า:

```
┌─────────────────────────────────────────┐
│ Upcoming DC Changes (7 days)            │
├─────────────────────────────────────────┤
│ 🔵 BR001 - สาขาสยาม                     │
│    DC1 → DC2 | มีผล: 15 ก.พ. 2567       │
├─────────────────────────────────────────┤
│ 🟠 BR005 - สาขาบางนา                    │
│    DC2 → DC4 | มีผล: 17 ก.พ. 2567       │
└─────────────────────────────────────────┘
```

---

## Audit Logs

**Actions ที่บันทึก:**

- `scm_dc_change_scheduled` - กำหนดการเปลี่ยน DC
- `scm_dc_change_completed` - เปลี่ยน DC สำเร็จ (auto)
- `scm_dc_schedule_updated` - แก้ไขกำหนดการเปลี่ยน DC
- `scm_dc_schedule_cancelled` - ยกเลิกกำหนดการเปลี่ยน DC

**ตัวอย่าง action_detail:**

```json
// scm_dc_change_scheduled
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "current_dc": "DC1",
  "new_dc": "DC2",
  "effective_date": "2024-02-15",
  "reason": "ปรับโครงสร้าง Supply Chain ภาคกลาง",
  "days_until_effective": 10
}

// scm_dc_change_completed (auto)
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "old_dc": "DC1",
  "new_dc": "DC2",
  "effective_date": "2024-02-15",
  "scheduled_by": "scm_user@company.com",
  "completed_at": "2024-02-15T00:00:05Z",
  "completion_type": "automatic"
}

// scm_dc_schedule_cancelled
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "cancelled_dc_change": {
    "from": "DC1",
    "to": "DC2",
    "scheduled_date": "2024-02-15"
  },
  "cancellation_reason": "เปลี่ยนแผน Supply Chain"
}
```

---

## Database Schema

### Table: `scm_dc_assignment`

ตาราง master สำหรับเก็บ DC ปัจจุบันของแต่ละสาขา

```sql
CREATE TABLE retail_branches.scm_dc_assignment (
  assignment_id STRING NOT NULL,           -- รหัส Assignment (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id) UNIQUE

  -- DC Information
  current_dc STRING NOT NULL,              -- DC ปัจจุบัน (DC1, DC2, DC4)

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

### Table: `scm_dc_schedule`

ตารางเก็บกำหนดการเปลี่ยน DC ในอนาคต

```sql
CREATE TABLE retail_branches.scm_dc_schedule (
  schedule_id STRING NOT NULL,             -- รหัสกำหนดการ (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)

  -- DC Change Information
  from_dc STRING NOT NULL,                 -- DC เดิม (DC1, DC2, DC4)
  to_dc STRING NOT NULL,                   -- DC ใหม่ (DC1, DC2, DC4)
  effective_date DATE NOT NULL,            -- วันที่มีผล

  -- Details
  reason STRING NOT NULL,                  -- เหตุผลในการเปลี่ยน DC
  remarks STRING,                          -- หมายเหตุเพิ่มเติม

  -- Status
  status STRING NOT NULL,                  -- สถานะ (scheduled, completed, cancelled)

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างกำหนดการ
  updated_at TIMESTAMP,                    -- วันที่แก้ไข
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING,                       -- ผู้แก้ไข
  completed_at TIMESTAMP,                  -- วันที่ทำการเปลี่ยนเสร็จ (auto)
  cancelled_at TIMESTAMP,                  -- วันที่ยกเลิก
  cancelled_by STRING                      -- ผู้ยกเลิก
);
```

### Indexes and Partitioning

```sql
-- scm_dc_assignment
-- Cluster by branch_id, current_dc
CREATE TABLE retail_branches.scm_dc_assignment
CLUSTER BY branch_id, current_dc
AS SELECT * FROM retail_branches.scm_dc_assignment;

-- scm_dc_schedule
-- Partition by effective_date (daily)
-- Cluster by branch_id, status, effective_date
CREATE TABLE retail_branches.scm_dc_schedule
PARTITION BY DATE(effective_date)
CLUSTER BY branch_id, status, effective_date
AS SELECT * FROM retail_branches.scm_dc_schedule;
```

---

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema details
- [audit-logs.md](audit-logs.md) - Audit logging for SCM operations
- [../DESIGN.md](../DESIGN.md) - UI/UX design guidelines
