# SRD Team - ทีม SRD (Store Research & Development)

## Overview

ทีม SRD มีหน้าที่จัดการข้อมูล Layout และรูปแบบของสาขาแต่ละสาขา โดยมีเมนูหลักคือ **ข้อมูล Layout สาขา** สำหรับจัดเก็บข้อมูลเกี่ยวกับรูปแบบร้าน, ประเภทสินค้า, และการปรับปรุงสาขา

**สิทธิ์การเข้าถึง:** ทีม SRD และ Admin

---

## ข้อมูล Layout สาขา

### Overview

จัดการข้อมูล Layout และคุณสมบัติของสาขาแต่ละสาขา รวมถึงรูปแบบร้าน (Format), ประเภทสินค้า (Assortment), การปรับปรุงร้าน (Renovate), และการอนุญาตพิเศษต่างๆ

### หน้าจัดการ Layout สาขา (`/srd/layout`)

#### ฟีเจอร์
- **รายการ Layout สาขาทั้งหมด**: แสดงตารางข้อมูล Layout ของทุกสาขา
- **ค้นหา/กรอง**:
  - รหัสสาขา
  - ชื่อสาขา
  - Assortment Type
  - Format
  - ALC Flag
  - Halan Flag
  - จังหวัด
- **เพิ่มข้อมูลใหม่**: สร้างข้อมูล Layout สำหรับสาขาใหม่
- **แก้ไขข้อมูล**: แก้ไขข้อมูล Layout ของสาขา
- **ลบข้อมูล**: ลบข้อมูล (soft delete)
- **ประวัติการเปลี่ยนแปลง**: ดูประวัติการแก้ไข Layout ของแต่ละสาขา

#### ข้อมูลที่แสดงในตาราง

| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขา (clickable -> link to branch details) |
| ชื่อสาขา | ชื่อสาขา |
| Assortment Type | ประเภทการจัดสินค้า (มาตรฐาน / เมือง) |
| Format | รูปแบบร้าน (Supermarket / Mall / โรงโป๊ะ) |
| วันที่ Renovate ล่าสุด | วันที่ปรับปรุงร้านครั้งล่าสุด |
| ALC Flag | ขายแอลกอฮอล์ (ใช่ / ไม่ใช่) |
| Halan Flag | สถานะ Halan (ใช่ / ไม่ใช่) |
| จังหวัด | จังหวัดที่ตั้งสาขา |
| Actions | View / Edit / Delete buttons |

### Form: เพิ่ม/แก้ไข Layout สาขา

**ฟอร์มแบ่งเป็น 3 sections:**

#### 1. ข้อมูลสาขา
- **รหัสสาขา** (Dropdown/Autocomplete) - required
- **ชื่อสาขา** (Auto-fill จากรหัสสาขา) - read-only
- **จังหวัด** (Auto-fill จากข้อมูลสาขา) - read-only

#### 2. ข้อมูล Layout และรูปแบบ
- **Assortment Type** (Dropdown) - required
  - มาตรฐาน
  - เมือง
- **Format** (Dropdown) - required
  - Supermarket
  - Mall
  - โรงโป๊ะ
- **วันที่ Renovate ล่าสุด** (Date picker) - optional
  - วันที่ทำการปรับปรุงร้านครั้งล่าสุด
  - ถ้ายังไม่เคย renovate ไม่ต้องกรอก

#### 3. Flags และสิทธิ์พิเศษ
- **ALC Flag** (Toggle/Checkbox) - required
  - ใช่ = สาขานี้สามารถขายแอลกอฮอล์ได้
  - ไม่ใช่ = ไม่สามารถขายแอลกอฮอล์
- **Halan Flag** (Toggle/Checkbox) - required
  - ใช่ = มีสถานะ Halan
  - ไม่ใช่ = ไม่มีสถานะ Halan

#### 4. หมายเหตุ
- **หมายเหตุ** (Textarea) - optional
  - ระบุรายละเอียดเพิ่มเติม เช่น "Renovate ครั้งที่ 3 - เพิ่มโซนอาหารสด"

### Validation Rules

- **รหัสสาขา**: required, ต้องมีในระบบ (ตาราง branches)
- **Assortment Type**: required, ต้องเลือก มาตรฐาน หรือ เมือง
- **Format**: required, ต้องเลือก Supermarket, Mall, หรือ โรงโป๊ะ
- **วันที่ Renovate**: optional, ถ้ากรอกต้องไม่เกินวันนี้
- **ALC Flag**: required, ต้องเลือก ใช่ หรือ ไม่ใช่
- **Halan Flag**: required, ต้องเลือก ใช่ หรือ ไม่ใช่

### UI Components

#### Assortment Type Badges
- **มาตรฐาน**: น้ำเงิน (Primary Blue) - `#3B82F6`
- **เมือง**: เขียว (Success Green) - `#10B981`

#### Format Badges
- **Supermarket**: น้ำเงิน (Primary Blue) - `#3B82F6`
- **Mall**: ม่วง (Purple) - `#8B5CF6`
- **โรงโป๊ะ**: ส้ม (Warning Orange) - `#F59E0B`

#### Flag Indicators
- **ALC Flag (ใช่)**: เขียว (Success Green) - แสดง "ขายแอลกอฮอล์ได้"
- **ALC Flag (ไม่ใช่)**: เทา (Gray) - แสดง "ไม่ขายแอลกอฮอล์"
- **Halan Flag (ใช่)**: เขียว (Success Green) - แสดง "Halan"
- **Halan Flag (ไม่ใช่)**: เทา (Gray) - แสดง "-"

### API Endpoints

```
GET    /api/srd/layout                    # ดึงรายการ Layout ทั้งหมด (รองรับ pagination, search, filter)
GET    /api/srd/layout/{branch_id}        # ดึงข้อมูล Layout ของสาขา
POST   /api/srd/layout                    # สร้างข้อมูล Layout ใหม่
PUT    /api/srd/layout/{branch_id}        # แก้ไขข้อมูล Layout
DELETE /api/srd/layout/{branch_id}        # ลบข้อมูล Layout (soft delete)

# History
GET    /api/srd/layout/{branch_id}/history # ดึงประวัติการเปลี่ยนแปลง Layout
```

### Business Logic

#### การบันทึกประวัติ
- ทุกครั้งที่มีการแก้ไขข้อมูล Layout จะบันทึกประวัติลงใน audit logs
- แสดงประวัติการเปลี่ยนแปลง: วันที่, ผู้แก้ไข, ฟิลด์ที่เปลี่ยน, ค่าเก่า/ค่าใหม่

#### Renovate Tracking
- ถ้ามีการอัพเดท "วันที่ Renovate ล่าสุด" ให้บันทึกเป็น event พิเศษใน audit logs
- แสดงจำนวนวันนับจากวันที่ Renovate ล่าสุด (เช่น "Renovate ล่าสุด 365 วันที่แล้ว")

#### Filter Logic
- **Assortment Type**: กรองตาม มาตรฐาน หรือ เมือง
- **Format**: กรองตาม Supermarket, Mall, โรงโป๊ะ
- **ALC Flag**: กรองสาขาที่ขาย/ไม่ขายแอลกอฮอล์
- **Halan Flag**: กรองสาขาที่มี/ไม่มี Halan Flag
- **วันที่ Renovate**: กรองช่วงวันที่ (เช่น Renovate ใน 6 เดือนที่ผ่านมา)

---

## UI/UX Guidelines

### Navigation

**SRD Team Navbar:**
```
[Logo] | Dashboard | Layout สาขา | [User Avatar ▼]
```

### Color Coding

**ทีม SRD Accent Color:** Orange `#F97316` (Creative, Design)

ใช้ accent color ใน:
- Page headers
- Active menu items
- Primary buttons
- Team badges

### Responsive Design

- **Desktop**: แสดงตารางแบบเต็ม พร้อม filters
- **Tablet**: ตารางแบบ scroll horizontal, filters แบบ collapsible
- **Mobile**: แสดงแบบ card list, filters แบบ modal/bottom sheet

### Form Layout (2-column responsive grid)

```
┌──────────────────────────────────────────┐
│ รหัสสาขา           │ ชื่อสาขา (read-only)│
├──────────────────────────────────────────┤
│ Assortment Type    │ Format             │
├──────────────────────────────────────────┤
│ วันที่ Renovate ล่าสุด                   │
├──────────────────────────────────────────┤
│ ALC Flag           │ Halan Flag         │
├──────────────────────────────────────────┤
│ หมายเหตุ                                 │
└──────────────────────────────────────────┘
```

---

## Audit Logs

**Actions ที่บันทึก:**

- `srd_layout_create` - สร้างข้อมูล Layout ใหม่
- `srd_layout_update` - แก้ไขข้อมูล Layout
- `srd_layout_delete` - ลบข้อมูล Layout
- `srd_layout_renovate` - อัพเดทวันที่ Renovate (event พิเศษ)

**ตัวอย่าง action_detail:**

```json
// srd_layout_update
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "changes": {
    "format": {
      "old": "Supermarket",
      "new": "Mall"
    },
    "alc_flag": {
      "old": false,
      "new": true
    }
  }
}

// srd_layout_renovate
{
  "branch_id": "BR001",
  "branch_name": "สาขาสยาม",
  "renovate_date": "2024-02-15",
  "previous_renovate_date": "2023-01-10",
  "days_since_last_renovate": 401
}
```

---

## Database Schema

### Table: `srd_layout`

```sql
CREATE TABLE retail_branches.srd_layout (
  layout_id STRING NOT NULL,               -- รหัส Layout (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)

  -- ข้อมูล Layout
  assortment_type STRING NOT NULL,         -- ประเภทการจัดสินค้า (มาตรฐาน, เมือง)
  format STRING NOT NULL,                  -- รูปแบบร้าน (Supermarket, Mall, โรงโป๊ะ)
  last_renovate_date DATE,                 -- วันที่ Renovate ล่าสุด

  -- Flags
  alc_flag BOOLEAN NOT NULL,               -- ขายแอลกอฮอล์ได้หรือไม่
  halan_flag BOOLEAN NOT NULL,             -- มี Halan Flag หรือไม่

  -- หมายเหตุ
  remarks STRING,                          -- หมายเหตุเพิ่มเติม

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

### Indexes and Partitioning

```sql
-- Partition by created_at (daily)
-- Cluster by branch_id, assortment_type, format
CREATE TABLE retail_branches.srd_layout
PARTITION BY DATE(created_at)
CLUSTER BY branch_id, assortment_type, format
AS SELECT * FROM retail_branches.srd_layout;
```

---

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema details
- [audit-logs.md](audit-logs.md) - Audit logging for SRD operations
- [../DESIGN.md](../DESIGN.md) - UI/UX design guidelines
