# New Branch Team - ทีมสาขาใหม่

## Overview

ทีมสาขาใหม่มีหน้าที่จัดการข้อมูลสาขาที่อยู่ระหว่างการเปิดใหม่ ติดตามสถานะการเปิดสาขา และประมาณการวันที่เปิดทำการ เพื่อให้ทีมอื่นๆ สามารถเตรียมความพร้อมได้ตามแผนงาน

**สิทธิ์การเข้าถึง:** ทีมสาขาใหม่ (New Branch Team) และ Admin

---

## จัดการข้อมูลสาขาใหม่

### Overview

จัดการและติดตามสถานะของสาขาที่กำลังอยู่ระหว่างการเปิดใหม่ ตั้งแต่ขั้นตอนการวางแผน ก่อสร้าง จนถึงพร้อมเปิดทำการ รวมถึงการประมาณการวันที่เปิดและติดตามความคืบหน้า

### หน้าจัดการสาขาใหม่ (`/new-branch`)

#### ฟีเจอร์
- **รายการสาขาใหม่ทั้งหมด**: แสดงตารางสาขาที่อยู่ระหว่างการเปิดใหม่
- **ค้นหา/กรอง**:
  - รหัสสาขา
  - ชื่อสาขา
  - สถานะของสาขา
  - จังหวัด
  - Estimate Opening Date (ช่วงวันที่)
- **เพิ่มสาขาใหม่**: สร้างข้อมูลสาขาใหม่ที่กำลังจะเปิด
- **แก้ไขข้อมูล**: อัพเดทสถานะและ Estimate Opening Date
- **ลบข้อมูล**: ลบข้อมูล (soft delete) เมื่อยกเลิกแผนเปิดสาขา
- **ดูประวัติการเปลี่ยนแปลง**: ติดตามการเปลี่ยนแปลงสถานะและวันที่
- **Dashboard สรุป**: แสดงจำนวนสาขาแยกตามสถานะ และสาขาที่จะเปิดในเดือนนี้

#### ข้อมูลที่แสดงในตาราง

| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขา (clickable -> link to details) |
| ชื่อสาขา | ชื่อสาขา |
| จังหวัด | จังหวัดที่ตั้งสาขา |
| สถานะของสาขา | รอเปิด / ก่อสร้าง / เปิดทำการ |
| Estimate Opening Date | วันที่คาดว่าจะเปิดทำการ |
| วันที่เหลือ | นับถอยหลังจนถึงวันเปิดทำการ (เช่น "30 วัน") |
| ผู้รับผิดชอบ | ผู้รับผิดชอบหลักของสาขา |
| Actions | View / Edit / Delete buttons |

### Form: เพิ่ม/แก้ไขข้อมูลสาขาใหม่

**ฟอร์มแบ่งเป็น 3 sections:**

#### 1. ข้อมูลพื้นฐานของสาขา
- **รหัสสาขา** (Text input) - required
  - Format: BR + 3-4 หลัก เช่น "BR001", "BR1234"
  - ต้องไม่ซ้ำกับสาขาที่มีอยู่แล้ว
- **ชื่อสาขา** (Text input) - required
  - เช่น "สาขาสยาม", "สาขาเซ็นทรัล พระราม 9"
- **จังหวัด** (Dropdown - list of provinces) - required
- **อำเภอ/เขต** (Text input) - required
- **ที่อยู่** (Textarea) - optional
  - ที่อยู่โดยละเอียด (ถ้ามี)

#### 2. สถานะและแผนการ
- **สถานะของสาขา** (Dropdown) - required
  - **รอเปิด** - วางแผนเปิดสาขา ยังไม่เริ่มก่อสร้าง
  - **ก่อสร้าง** - อยู่ระหว่างการก่อสร้าง/ปรับปรุงสถานที่
  - **เปิดทำการ** - เปิดทำการแล้ว (พร้อมให้ทีมอื่นเข้ามาจัดการ)
- **Estimate Opening Date** (Date picker) - required
  - วันที่ประมาณการเปิดทำการ
  - ต้องเป็นวันที่ในอนาคต
- **Actual Opening Date** (Date picker) - optional
  - วันที่เปิดทำการจริง (กรอกเมื่อเปิดแล้ว)
  - เมื่อกรอก Actual Opening Date สถานะจะต้องเป็น "เปิดทำการ"

#### 3. ผู้รับผิดชอบและหมายเหตุ
- **ผู้รับผิดชอบ** (Text input) - optional
  - ชื่อผู้รับผิดชอบหลักของโครงการเปิดสาขานี้
- **เบอร์โทรติดต่อ** (Text input) - optional
  - Format: 0X-XXXX-XXXX หรือ 0XX-XXX-XXXX
- **หมายเหตุ** (Textarea) - optional
  - รายละเอียดเพิ่มเติม เช่น "รอ ภ.พ.09", "ติดปัญหาการขออนุญาต"

### Validation Rules

- **รหัสสาขา**: required, unique, format BR + 3-4 หลัก
- **ชื่อสาขา**: required, อย่างน้อย 3 ตัวอักษร
- **จังหวัด**: required
- **อำเภอ/เขต**: required
- **สถานะของสาขา**: required (รอเปิด, ก่อสร้าง, เปิดทำการ)
- **Estimate Opening Date**: required, ต้องเป็นวันที่ในอนาคต (เมื่อสร้างใหม่)
- **Actual Opening Date**:
  - optional
  - ถ้ากรอก ต้อง >= Estimate Opening Date
  - ถ้ากรอก สถานะต้องเป็น "เปิดทำการ"
- **เบอร์โทรติดต่อ**: ถ้ากรอก ต้องเป็นรูปแบบที่ถูกต้อง

### UI Components

#### Status Badges
- **รอเปิด**: ส้ม (Warning Orange) - `#F59E0B` - "🕐 รอเปิด"
- **ก่อสร้าง**: น้ำเงิน (Primary Blue) - `#3B82F6` - "🏗️ ก่อสร้าง"
- **เปิดทำการ**: เขียว (Success Green) - `#10B981` - "✅ เปิดทำการ"

#### Days Remaining Indicator
- **มากกว่า 60 วัน**: เทา (Gray) - "เหลือ 90 วัน"
- **30-60 วัน**: ส้ม (Orange) - "เหลือ 45 วัน"
- **น้อยกว่า 30 วัน**: แดง (Red) - "เหลือ 15 วัน"
- **เลยกำหนด**: แดงเข้ม (Dark Red) - "เลยกำหนด 5 วัน"

#### Dashboard Summary Cards

```
┌────────────────────────────────────────────────────┐
│  📊 Dashboard - สาขาใหม่                           │
├────────────┬────────────┬────────────┬────────────┤
│ 🕐 รอเปิด  │ 🏗️ ก่อสร้าง│ ✅ เปิดแล้ว │ 📅 เปิดเดือนนี้│
│    12      │     8      │     3      │     5      │
└────────────┴────────────┴────────────┴────────────┘
```

### API Endpoints

```
GET    /api/new-branch                          # ดึงรายการสาขาใหม่ทั้งหมด (รองรับ pagination, search, filter)
GET    /api/new-branch/{branch_id}              # ดึงข้อมูลสาขาใหม่รายการเดียว
POST   /api/new-branch                          # สร้างข้อมูลสาขาใหม่
PUT    /api/new-branch/{branch_id}              # แก้ไขข้อมูลสาขาใหม่
DELETE /api/new-branch/{branch_id}              # ลบข้อมูล (soft delete)

# Status & History
PATCH  /api/new-branch/{branch_id}/status       # อัพเดทเฉพาะสถานะ
GET    /api/new-branch/{branch_id}/history      # ดึงประวัติการเปลี่ยนแปลง
GET    /api/new-branch/dashboard                # ดึงข้อมูลสรุปสำหรับ dashboard

# Upcoming Openings
GET    /api/new-branch/upcoming                 # สาขาที่จะเปิดใน 30 วันข้างหน้า
GET    /api/new-branch/overdue                  # สาขาที่เลยกำหนดเปิด
```

### Business Logic

#### การเปลี่ยนสถานะอัตโนมัติ
- เมื่อ Actual Opening Date ถูกกรอก → อัพเดทสถานะเป็น "เปิดทำการ" อัตโนมัติ
- เมื่อสถานะเป็น "เปิดทำการ" → แจ้งเตือนทีมอื่นๆ (Legal, SRD, SCM) ให้เข้ามาจัดการข้อมูล

#### Notification/Alert
- **30 วันก่อนเปิด**: ส่ง notification ให้ทีมสาขาใหม่และทีมที่เกี่ยวข้อง
- **7 วันก่อนเปิด**: ส่ง reminder พร้อมตรวจสอบความพร้อม
- **วันเปิดทำการ**: ส่ง notification ให้ทุกทีมเพื่อเริ่มดำเนินการ
- **เลยกำหนดเปิด**: แสดง warning ในระบบ

#### Status Transition Rules
```
รอเปิด → ก่อสร้าง → เปิดทำการ
   ↓         ↓           ↓
  [อนุญาตย้อนกลับได้]  [ไม่อนุญาตย้อนกลับ]
```

#### Filter & Search Logic
- **สถานะ**: กรองตาม รอเปิด, ก่อสร้าง, เปิดทำการ
- **จังหวัด**: Dropdown selection
- **Estimate Opening Date**: Date range picker
- **วันที่เหลือ**: กรองตาม < 30 วัน, 30-60 วัน, > 60 วัน, เลยกำหนด
- **ค้นหา**: รหัสสาขา, ชื่อสาขา (partial match)

---

## UI/UX Guidelines

### Navigation

**New Branch Team Navbar:**
```
[Logo] | Dashboard | สาขาใหม่ | Reports | [User Avatar ▼]
```

### Color Coding

**ทีมสาขาใหม่ Accent Color:** Blue `#3B82F6` (Growth, New beginnings)

ใช้ accent color ใน:
- Page headers
- Active menu items
- Primary buttons
- Team badges
- "ก่อสร้าง" status badge

### Responsive Design

- **Desktop**: แสดงตารางแบบเต็ม พร้อม dashboard cards และ filters
- **Tablet**: ตารางแบบ scroll horizontal, dashboard cards แบบ 2 columns
- **Mobile**: แสดงแบบ card list, dashboard cards แบบ vertical stack

### Form Layout (2-column responsive grid)

```
┌──────────────────────────────────────────┐
│ รหัสสาขา           │ ชื่อสาขา            │
├──────────────────────────────────────────┤
│ จังหวัด            │ อำเภอ/เขต          │
├──────────────────────────────────────────┤
│ ที่อยู่                                  │
├──────────────────────────────────────────┤
│ สถานะของสาขา      │ Estimate Opening    │
├──────────────────────────────────────────┤
│ Actual Opening (optional)                │
├──────────────────────────────────────────┤
│ ผู้รับผิดชอบ       │ เบอร์โทรติดต่อ      │
├──────────────────────────────────────────┤
│ หมายเหตุ                                 │
└──────────────────────────────────────────┘
```

### Upcoming Openings Panel

แสดงรายการสาขาที่จะเปิดใน 30 วันข้างหน้า:

```
┌─────────────────────────────────────────┐
│ 📅 สาขาที่จะเปิดใน 30 วันข้างหน้า       │
├─────────────────────────────────────────┤
│ 🏗️ BR001 - สาขาสยาม                    │
│    เปิด: 15 ก.พ. 2567 | เหลือ 10 วัน   │
├─────────────────────────────────────────┤
│ 🏗️ BR005 - สาขาบางนา                   │
│    เปิด: 25 ก.พ. 2567 | เหลือ 20 วัน   │
└─────────────────────────────────────────┘
```

---

## Audit Logs

**Actions ที่บันทึก:**

- `new_branch_create` - สร้างข้อมูลสาขาใหม่
- `new_branch_update` - แก้ไขข้อมูลสาขาใหม่
- `new_branch_delete` - ลบข้อมูลสาขาใหม่
- `new_branch_status_change` - เปลี่ยนสถานะสาขา (event พิเศษ)
- `new_branch_opened` - เปิดทำการแล้ว (event พิเศษเมื่อกรอก Actual Opening Date)

**ตัวอย่าง action_detail:**

```json
// new_branch_status_change
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "status_change": {
    "old_status": "รอเปิด",
    "new_status": "ก่อสร้าง"
  },
  "estimate_opening_date": "2024-03-15",
  "days_until_opening": 45
}

// new_branch_opened
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "estimate_opening_date": "2024-03-15",
  "actual_opening_date": "2024-03-12",
  "days_difference": -3,
  "note": "เปิดก่อนกำหนด 3 วัน"
}
```

---

## Database Schema

### Table: `new_branch_tracking`

```sql
CREATE TABLE retail_branches.new_branch_tracking (
  tracking_id STRING NOT NULL,             -- รหัส Tracking (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (UNIQUE)
  branch_name STRING NOT NULL,             -- ชื่อสาขา

  -- Location
  province STRING NOT NULL,                -- จังหวัด
  district STRING NOT NULL,                -- อำเภอ/เขต
  address STRING,                          -- ที่อยู่โดยละเอียด

  -- Status & Timeline
  branch_status STRING NOT NULL,           -- สถานะ (รอเปิด, ก่อสร้าง, เปิดทำการ)
  estimate_opening_date DATE NOT NULL,     -- วันที่ประมาณการเปิดทำการ
  actual_opening_date DATE,                -- วันที่เปิดทำการจริง

  -- Contact
  responsible_person STRING,               -- ผู้รับผิดชอบ
  contact_phone STRING,                    -- เบอร์โทรติดต่อ

  -- Notes
  remarks STRING,                          -- หมายเหตุ

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

### Indexes and Partitioning

```sql
-- Partition by estimate_opening_date (monthly)
-- Cluster by branch_status, province
CREATE TABLE retail_branches.new_branch_tracking
PARTITION BY DATE_TRUNC(estimate_opening_date, MONTH)
CLUSTER BY branch_status, province
AS SELECT * FROM retail_branches.new_branch_tracking;
```

### Business Rules

- **branch_id** ต้อง unique (1 สาขาควรมีแค่ 1 record ในระบบ)
- **branch_status** values: "รอเปิด", "ก่อสร้าง", "เปิดทำการ"
- เมื่อ **actual_opening_date** ถูกบันทึก → **branch_status** ต้องเป็น "เปิดทำการ"
- เมื่อสถานะเป็น "เปิดทำการ" → สามารถสร้างข้อมูลใน tables อื่นๆ ได้ (legal_ppp09, srd_layout, scm_dc_assignment)

---

## Integration with Other Teams

### เมื่อสาขาเปิดทำการแล้ว

ระบบจะแจ้งเตือนทีมต่างๆ ให้เข้ามาจัดการข้อมูล:

**Legal Team:**
- จัดการ ภ.พ.09 (จดทะเบียนที่อยู่สาขา)
- จัดการ ภ.พ.20 (เอกสารภาษีมูลค่าเพิ่ม)

**SRD Team:**
- กรอกข้อมูล Layout สาขา (Assortment Type, Format, Flags)

**SCM Team:**
- กำหนด DC ที่รับผิดชอบสาขา

### Workflow

```
ทีมสาขาใหม่: สร้างข้อมูล (รอเปิด) → อัพเดทสถานะ (ก่อสร้าง) → เปิดทำการ
                                                                    ↓
    ┌───────────────────────────────────────────────────────────────┘
    │
    ├─→ Legal Team: จัดการ ภ.พ.09, ภ.พ.20
    ├─→ SRD Team: กรอก Layout ข้อมูล
    └─→ SCM Team: กำหนด DC
```

---

## Reports & Analytics

### รายงานที่ควรมี

1. **สาขาที่จะเปิดในเดือนนี้/เดือนหน้า**
2. **สาขาที่เลยกำหนดเปิด** (overdue)
3. **สาขาที่อยู่ระหว่างก่อสร้าง** + Timeline
4. **สรุปการเปิดสาขาแยกตามจังหวัด**
5. **Actual vs Estimate Opening Date Analysis**

---

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema details
- [audit-logs.md](audit-logs.md) - Audit logging for New Branch operations
- [../DESIGN.md](../DESIGN.md) - UI/UX design guidelines
- [legal-ppp09.md](legal-ppp09.md) - Legal team features (ต่อเนื่องหลังเปิดสาขา)
- [srd-layout.md](srd-layout.md) - SRD team features (ต่อเนื่องหลังเปิดสาขา)
- [scm-dc.md](scm-dc.md) - SCM team features (ต่อเนื่องหลังเปิดสาขา)
