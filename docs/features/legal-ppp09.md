# Legal Team - ทีมกฎหมาย

## Overview

ทีมกฎหมายมีหน้าที่จัดการเอกสารทางกฎหมายที่สำคัญสำหรับการเปิดและดำเนินการสาขา โดยระบบแบ่งออกเป็น 2 เมนูหลัก:

1. **จดทะเบียนที่อยู่สาขา (ภ.พ.09)** - จัดการข้อมูลการจดทะเบียนที่อยู่ของสาขาตามสรรพากร
2. **จัดการเอกสาร ภ.พ.20** - จัดการเอกสารแบบแสดงรายการภาษีมูลค่าเพิ่ม (ภ.พ.20)

**สิทธิ์การเข้าถึง:** ทีมกฎหมาย (Legal Team) และ Admin

---

## 1. จดทะเบียนที่อยู่สาขา (ภ.พ.09)

### Overview

ภ.พ.09 คือ แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง ซึ่งเป็นเอกสารสำคัญทางกฎหมายสำหรับการจดทะเบียนที่อยู่สาขาตามสรรพากร ทีมกฎหมายจะมีหน้าที่ในการจัดการข้อมูล ภ.พ.09 ของแต่ละสาขา พร้อมทั้งเก็บเอกสารต้นฉบับ

### หน้าจัดการ ภ.พ.09 (`/legal/ppp09`)

#### ฟีเจอร์
- **รายการ ภ.พ.09 ทั้งหมด**: แสดงตารางข้อมูลการจดทะเบียนของทุกสาขา
- **ค้นหา/กรอง**:
  - รหัสสาขา
  - ชื่อสาขา
  - เลขที่ตามสรรพากร (ภ.พ.09)
  - สถานะของสาขา
- **เพิ่มข้อมูลใหม่**: สร้างข้อมูลการจดทะเบียน ภ.พ.09 ใหม่พร้อม upload documents
- **แก้ไขข้อมูล**: แก้ไขข้อมูลและอัพเดท documents
- **ลบข้อมูล**: ลบข้อมูล (soft delete)
- **จัดการเอกสาร**: upload/download/delete documents (รองรับหลายไฟล์)

#### ข้อมูลที่แสดงในตาราง

| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขา (clickable -> link to branch details) |
| ชื่อสาขา | ชื่อสาขา |
| เลขที่ตามสรรพากร | เลขที่ ภ.พ.09 |
| ที่อยู่ตามสรรพากร | ที่อยู่ตาม ภ.พ.09 (แสดงแบบย่อ) |
| หมายเลขโทรศัพท์ | เบอร์โทรศัพท์ติดต่อ |
| วันที่จดทะเบียน | วันที่จดทะเบียนกับสรรพากร |
| สถานะของสาขา | ยังไม่จดสรรพากร / เปิดให้บริการ / รอเปิดทำการ |
| เอกสาร | จำนวนไฟล์ที่อัพโหลด + ไอคอน download |
| Actions | View / Edit / Delete buttons |

### Form: เพิ่ม/แก้ไข ภ.พ.09

**ฟอร์มแบ่งเป็น 4 sections:**

#### 1. ข้อมูลทั่วไป
- **รหัสสาขา** (Dropdown/Autocomplete) - required
- **ชื่อสาขา** (Auto-fill จากรหัสสาขา) - read-only
- **เลขที่ตามสรรพากร (ภ.พ.09)** (Text input) - required
- **วันที่จดทะเบียน** (Date picker) - required
- **สถานะของสาขา** (Dropdown) - required
  - ยังไม่จดสรรพากร
  - เปิดให้บริการ
  - รอเปิดทำการ

#### 2. ที่อยู่ตาม ภ.พ.09 (แยกตาม field)
- **บ้านเลขที่** (Text input) - required
- **หมู่ที่** (Text input) - optional
- **ตรอก** (Text input) - optional
- **ซอย** (Text input) - optional
- **ถนน** (Text input) - optional
- **ตำบล/แขวง** (Text input) - required
- **อำเภอ/เขต** (Text input) - required
- **จังหวัด** (Dropdown - list of provinces) - required
- **รหัสไปรษณีย์** (Text input - 5 digits) - required

**หมายเหตุ:** ที่อยู่ต้องแยกเป็น fields เพื่อให้ค้นหาและจัดการได้ง่าย

#### 3. ข้อมูลติดต่อ
- **หมายเลขโทรศัพท์** (Text input) - required
  - Format: 0X-XXXX-XXXX หรือ 0XX-XXX-XXXX
  - Validation: เฉพาะตัวเลขและเครื่องหมาย -

#### 4. เอกสารแนบและหมายเหตุ
- **Upload Documents** (Multiple file upload)
  - รองรับไฟล์: PDF, JPG, PNG
  - ขนาดไฟล์สูงสุด: 10MB ต่อไฟล์
  - สามารถ upload ได้หลายไฟล์
  - แสดงรายการไฟล์ที่ upload แล้ว พร้อมปุ่ม:
    - Preview/Download
    - Delete (ลบแต่ละไฟล์)
- **หมายเหตุ** (Textarea) - optional

### UI Layout: Address Fields (2-column responsive grid)

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

### Status Badges

- **ยังไม่จดสรรพากร**: ส้ม (Warning Orange) - `#F59E0B`
- **เปิดให้บริการ**: เขียว (Success Green) - `#10B981`
- **รอเปิดทำการ**: น้ำเงิน (Primary Blue) - `#3B82F6`

### Validation Rules

- **รหัสสาขา**: required, ต้องมีในระบบ (ตาราง branches)
- **เลขที่ตามสรรพากร**: required, unique per branch
- **วันที่จดทะเบียน**: required, ต้องไม่เกินวันนี้
- **ที่อยู่**: บ้านเลขที่, ตำบล/แขวง, อำเภอ/เขต, จังหวัด, รหัสไปรษณีย์ = required
- **รหัสไปรษณีย์**: ต้องเป็นตัวเลข 5 หลัก
- **หมายเลขโทรศัพท์**: required, ต้องเป็นรูปแบบที่ถูกต้อง
- **สถานะของสาขา**: required
- **Documents**: ถ้า upload ต้องเป็นไฟล์ PDF, JPG, PNG เท่านั้น, ขนาดไม่เกิน 10MB ต่อไฟล์

### API Endpoints - ภ.พ.09

```
GET    /api/legal/ppp09                           # ดึงรายการทั้งหมด (รองรับ pagination, search, filter)
GET    /api/legal/ppp09/{ppp09_id}                # ดึงข้อมูลรายการเดียว
POST   /api/legal/ppp09                           # สร้างข้อมูลใหม่
PUT    /api/legal/ppp09/{ppp09_id}                # แก้ไขข้อมูล
DELETE /api/legal/ppp09/{ppp09_id}                # ลบข้อมูล (soft delete)

# Document Management
POST   /api/legal/ppp09/{ppp09_id}/upload         # อัพโหลดเอกสาร (หลายไฟล์)
GET    /api/legal/ppp09/{ppp09_id}/documents      # ดึงรายการเอกสารทั้งหมด
GET    /api/legal/ppp09/documents/{document_id}   # ดาวน์โหลดเอกสาร
DELETE /api/legal/ppp09/documents/{document_id}   # ลบเอกสาร
```

### Document Storage - ภ.พ.09

**GCS Bucket Path:**
```
gs://{bucket}/legal/ppp09/{branch_id}/{ppp09_id}/{filename}
```

**Naming Convention:**
```
{branch_id}_ppp09_{timestamp}_{original_filename}
```

**Metadata ใน BigQuery:**
- document_id
- ppp09_id (FK)
- branch_id (FK)
- file_name
- file_path (GCS path)
- file_size (bytes)
- mime_type
- uploaded_at (timestamp)
- uploaded_by (user email)

---

## 2. จัดการเอกสาร ภ.พ.20

### Overview

ภ.พ.20 คือ แบบแสดงรายการภาษีมูลค่าเพิ่ม (VAT) ซึ่งเป็นเอกสารสำคัญทางบัญชีและกฎหมายสำหรับการดำเนินธุรกิจ ทีมกฎหมายจะมีหน้าที่ในการจัดเก็บและจัดการเอกสาร ภ.พ.20 ของแต่ละสาขา

### หน้าจัดการ ภ.พ.20 (`/legal/ppp20`)

#### ฟีเจอร์
- **รายการ ภ.พ.20 ทั้งหมด**: แสดงตารางข้อมูล ภ.พ.20 ของทุกสาขา
- **ค้นหา/กรอง**:
  - รหัสสาขา
  - ชื่อสาขา
  - เลขที่ตามสรรพากร
- **เพิ่มข้อมูลใหม่**: สร้างข้อมูล ภ.พ.20 ใหม่พร้อม upload documents
- **แก้ไขข้อมูล**: แก้ไขข้อมูลและอัพเดท documents
- **ลบข้อมูล**: ลบข้อมูล (soft delete)
- **จัดการเอกสาร**: upload/download/delete documents (รองรับหลายไฟล์)

#### ข้อมูลที่แสดงในตาราง

| Column | Description |
|--------|-------------|
| รหัสสาขา | รหัสสาขา (clickable -> link to branch details) |
| ชื่อสาขา | ชื่อสาขา |
| เลขที่ตามสรรพากร | เลขที่ผู้เสียภาษี |
| งวดภาษี | เดือน/ปี ของการยื่น ภ.พ.20 |
| วันที่ยื่น | วันที่ยื่นเอกสาร ภ.พ.20 |
| จำนวนเอกสาร | จำนวนไฟล์ที่อัพโหลด + ไอคอน download |
| หมายเหตุ | หมายเหตุเพิ่มเติม (แสดงแบบย่อ) |
| Actions | View / Edit / Delete buttons |

### Form: เพิ่ม/แก้ไข ภ.พ.20

**ฟอร์มแบ่งเป็น 3 sections:**

#### 1. ข้อมูลสาขา
- **รหัสสาขา** (Dropdown/Autocomplete) - required
- **ชื่อสาขา** (Auto-fill จากรหัสสาขา) - read-only
- **เลขที่ตามสรรพากร** (Auto-fill จาก ภ.พ.09 ถ้ามี หรือ กรอกเอง) - required

#### 2. ข้อมูลภาษี
- **งวดภาษี** (Month/Year picker) - required
  - เลือกเดือนและปี เช่น "มกราคม 2567"
- **วันที่ยื่น** (Date picker) - required
  - วันที่ยื่นเอกสาร ภ.พ.20

#### 3. เอกสารแนบและหมายเหตุ
- **Upload Documents ภ.พ.20** (Multiple file upload)
  - รองรับไฟล์: PDF, JPG, PNG, Excel (XLS, XLSX)
  - ขนาดไฟล์สูงสุด: 10MB ต่อไฟล์
  - สามารถ upload ได้หลายไฟล์
  - แสดงรายการไฟล์ที่ upload แล้ว พร้อมปุ่ม:
    - Preview/Download
    - Delete (ลบแต่ละไฟล์)
- **หมายเหตุ** (Textarea) - optional
  - ระบุรายละเอียดเพิ่มเติม เช่น "ภ.พ.20 งวดภาษีมกราคม 2567 - แก้ไขครั้งที่ 2"

### Validation Rules

- **รหัสสาขา**: required, ต้องมีในระบบ
- **เลขที่ตามสรรพากร**: required
- **งวดภาษี**: required, ต้องเป็นรูปแบบ Month/Year
- **วันที่ยื่น**: required, ต้องไม่เกินวันนี้
- **Documents**: ต้อง upload อย่างน้อย 1 ไฟล์, ไฟล์ต้องเป็น PDF, JPG, PNG, XLS, XLSX เท่านั้น, ขนาดไม่เกิน 10MB ต่อไฟล์

### API Endpoints - ภ.พ.20

```
GET    /api/legal/ppp20                           # ดึงรายการทั้งหมด (รองรับ pagination, search, filter)
GET    /api/legal/ppp20/{ppp20_id}                # ดึงข้อมูลรายการเดียว
POST   /api/legal/ppp20                           # สร้างข้อมูลใหม่
PUT    /api/legal/ppp20/{ppp20_id}                # แก้ไขข้อมูล
DELETE /api/legal/ppp20/{ppp20_id}                # ลบข้อมูล (soft delete)

# Document Management
POST   /api/legal/ppp20/{ppp20_id}/upload         # อัพโหลดเอกสาร (หลายไฟล์)
GET    /api/legal/ppp20/{ppp20_id}/documents      # ดึงรายการเอกสารทั้งหมด
GET    /api/legal/ppp20/documents/{document_id}   # ดาวน์โหลดเอกสาร
DELETE /api/legal/ppp20/documents/{document_id}   # ลบเอกสาร
```

### Document Storage - ภ.พ.20

**GCS Bucket Path:**
```
gs://{bucket}/legal/ppp20/{branch_id}/{ppp20_id}/{filename}
```

**Naming Convention:**
```
{branch_id}_ppp20_{period}_{timestamp}_{original_filename}
```
ตัวอย่าง: `BR001_ppp20_202401_20240215_143022_vat_report.pdf`

**Metadata ใน BigQuery:**
- document_id
- ppp20_id (FK)
- branch_id (FK)
- file_name
- file_path (GCS path)
- file_size (bytes)
- mime_type
- uploaded_at (timestamp)
- uploaded_by (user email)

---

## Database Schema

### Table: `legal_ppp09`

```sql
CREATE TABLE retail_branches.legal_ppp09 (
  ppp09_id STRING NOT NULL,                -- รหัส ภ.พ.09 (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)
  ppp09_number STRING NOT NULL,            -- เลขที่ตามสรรพากร (ภ.พ.09)
  registration_date DATE,                  -- วันที่จดทะเบียน

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

  -- ข้อมูลติดต่อ
  phone_number STRING,                     -- หมายเลขโทรศัพท์

  -- สถานะ
  branch_status STRING,                    -- สถานะของสาขา (ยังไม่จดสรรพากร, เปิดให้บริการ, รอเปิดทำการ)

  -- หมายเหตุ
  remarks STRING,                          -- หมายเหตุเพิ่มเติม

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

### Table: `legal_ppp20`

```sql
CREATE TABLE retail_branches.legal_ppp20 (
  ppp20_id STRING NOT NULL,                -- รหัส ภ.พ.20 (UUID)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)
  tax_id STRING NOT NULL,                  -- เลขที่ตามสรรพากร
  tax_period STRING NOT NULL,              -- งวดภาษี (format: "YYYY-MM" เช่น "2024-01")
  filing_date DATE,                        -- วันที่ยื่น

  -- หมายเหตุ
  remarks STRING,                          -- หมายเหตุเพิ่มเติม

  -- Metadata
  created_at TIMESTAMP,                    -- วันที่สร้างข้อมูล
  updated_at TIMESTAMP,                    -- วันที่แก้ไขล่าสุด
  created_by STRING,                       -- ผู้สร้าง
  updated_by STRING                        -- ผู้แก้ไข
);
```

### Table: `legal_documents` (ใช้ร่วมกันสำหรับทั้ง ภ.พ.09 และ ภ.พ.20)

```sql
CREATE TABLE retail_branches.legal_documents (
  document_id STRING NOT NULL,             -- รหัสเอกสาร (UUID)
  document_type STRING NOT NULL,           -- ประเภทเอกสาร (ppp09, ppp20)
  reference_id STRING NOT NULL,            -- รหัสอ้างอิง (ppp09_id หรือ ppp20_id)
  branch_id STRING NOT NULL,               -- รหัสสาขา (FK -> branches.branch_id)

  -- ข้อมูลไฟล์
  file_name STRING NOT NULL,               -- ชื่อไฟล์ต้นฉบับ
  file_path STRING NOT NULL,               -- path ใน GCS
  file_size INT64,                         -- ขนาดไฟล์ (bytes)
  mime_type STRING,                        -- ประเภทไฟล์ (application/pdf, image/jpeg, etc.)

  -- Metadata
  uploaded_at TIMESTAMP,                   -- วันที่อัพโหลด
  uploaded_by STRING                       -- ผู้อัพโหลด (user email)
);
```

### Indexes and Partitioning

```sql
-- Partition by created_at (daily) for legal_ppp09
-- Cluster by branch_id, branch_status
CREATE TABLE retail_branches.legal_ppp09
PARTITION BY DATE(created_at)
CLUSTER BY branch_id, branch_status
AS SELECT * FROM retail_branches.legal_ppp09;

-- Partition by created_at (daily) for legal_ppp20
-- Cluster by branch_id, tax_period
CREATE TABLE retail_branches.legal_ppp20
PARTITION BY DATE(created_at)
CLUSTER BY branch_id, tax_period
AS SELECT * FROM retail_branches.legal_ppp20;

-- Partition by uploaded_at (daily) for legal_documents
-- Cluster by document_type, branch_id
CREATE TABLE retail_branches.legal_documents
PARTITION BY DATE(uploaded_at)
CLUSTER BY document_type, branch_id
AS SELECT * FROM retail_branches.legal_documents;
```

---

## Business Logic

### Multiple File Upload

**Upload Flow:**
1. User เลือกหลายไฟล์ (drag & drop หรือ file picker)
2. Validate ทุกไฟล์ (ประเภท, ขนาด)
3. Upload แต่ละไฟล์ไปยัง GCS แบบ parallel
4. บันทึก metadata ลง BigQuery table `legal_documents`
5. แสดงรายการไฟล์ที่ upload สำเร็จ

**UI Components:**
- Drag & drop zone
- File list พร้อม progress bar (ระหว่าง upload)
- Success/Error indicators สำหรับแต่ละไฟล์
- Preview thumbnails (สำหรับรูปภาพ)
- Download และ Delete buttons

### Search & Filter

**ภ.พ.09:**
- ค้นหา: รหัสสาขา, ชื่อสาขา, เลขที่ตามสรรพากร, ที่อยู่, หมายเลขโทรศัพท์
- กรอง: สถานะของสาขา, จังหวัด, วันที่จดทะเบียน (range)

**ภ.พ.20:**
- ค้นหา: รหัสสาขา, ชื่อสาขา, เลขที่ตามสรรพากร
- กรอง: งวดภาษี (เดือน/ปี), วันที่ยื่น (range)

### Auto-fill from ภ.พ.09

เมื่อสร้าง ภ.พ.20:
- ถ้าสาขามีข้อมูล ภ.พ.09 แล้ว → auto-fill "เลขที่ตามสรรพากร" จาก ภ.พ.09
- ถ้าไม่มี → ให้ user กรอกเอง

---

## UI/UX Guidelines

### Navigation

**Legal Team Navbar:**
```
[Logo] | Dashboard | ภ.พ.09 | ภ.พ.20 | [User Avatar ▼]
```

### Color Coding

**ทีมกฎหมาย Accent Color:** Purple `#8B5CF6` (Authority, Professional)

ใช้ accent color ใน:
- Page headers
- Active menu items
- Primary buttons
- Team badges

### Responsive Design

- **Desktop**: แสดงตารางแบบเต็ม พร้อม filters
- **Tablet**: ตารางแบบ scroll horizontal, filters แบบ collapsible
- **Mobile**: แสดงแบบ card list, filters แบบ modal/bottom sheet

---

## Audit Logs

**Actions ที่บันทึก:**

**ภ.พ.09:**
- `ppp09_create` - สร้างข้อมูล ภ.พ.09 ใหม่
- `ppp09_update` - แก้ไขข้อมูล ภ.พ.09
- `ppp09_delete` - ลบข้อมูล ภ.พ.09
- `ppp09_document_upload` - อัพโหลดเอกสาร
- `ppp09_document_download` - ดาวน์โหลดเอกสาร
- `ppp09_document_delete` - ลบเอกสาร

**ภ.พ.20:**
- `ppp20_create` - สร้างข้อมูล ภ.พ.20 ใหม่
- `ppp20_update` - แก้ไขข้อมูล ภ.พ.20
- `ppp20_delete` - ลบข้อมูล ภ.พ.20
- `ppp20_document_upload` - อัพโหลดเอกสาร
- `ppp20_document_download` - ดาวน์โหลดเอกสาร
- `ppp20_document_delete` - ลบเอกสาร

---

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Database schema details
- [audit-logs.md](audit-logs.md) - Audit logging for legal operations
- [../DESIGN.md](../DESIGN.md) - UI/UX design guidelines
