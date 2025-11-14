# Database Schema (BigQuery)

## Dataset: `retail_branches`

### Table: `branches`

ตารางเก็บข้อมูลสาขาทั้งหมด

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

### Table: `documents`

ตารางเก็บข้อมูลเอกสารที่เกี่ยวข้องกับสาขา

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

### Table: `users`

ตารางเก็บข้อมูลผู้ใช้งานระบบ

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

### Table: `user_teams`

ตารางเก็บความสัมพันธ์ระหว่าง user กับ team (Multi-team membership)

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

### Table: `legal_ppp09`

ตารางเก็บข้อมูล ภ.พ.09 (แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง) สำหรับการจดทะเบียนที่อยู่สาขาตามสรรพากร

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

ตารางเก็บข้อมูล ภ.พ.20 (แบบแสดงรายการภาษีมูลค่าเพิ่ม)

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

### Table: `legal_documents`

ตารางเก็บเอกสารสำหรับ ภ.พ.09 และ ภ.พ.20 (รองรับหลายไฟล์)

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

### Table: `audit_logs`

ตารางเก็บบันทึก activity ทั้งหมดของ user

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

## Database Notes

- **User 1 คนสามารถมีหลาย records ใน `user_teams`** (multi-team membership)
- **`users.user_level`** กำหนดสิทธิ์ระดับระบบ (admin สามารถทำทุกอย่าง)
- **`user_teams.role`** กำหนดสิทธิ์ในแต่ละทีม (viewer, editor, manager)
- **Admin** สามารถจัดการ users และ permissions ผ่านหน้า Admin
- **`audit_logs`** เก็บบันทึก activity ทั้งหมดของ user รวมถึง admin
- **`legal_ppp09`** เก็บข้อมูลการจดทะเบียนที่อยู่สาขา (ภ.พ.09) สำหรับทีมกฎหมาย
- **`legal_ppp20`** เก็บข้อมูลเอกสาร ภ.พ.20 (แบบแสดงรายการภาษีมูลค่าเพิ่ม) สำหรับทีมกฎหมาย
- **`legal_documents`** เก็บเอกสารไฟล์สำหรับทั้ง ภ.พ.09 และ ภ.พ.20 (รองรับหลายไฟล์ต่อรายการ)
- **`legal_ppp09.branch_id`** และ **`legal_ppp20.branch_id`** เชื่อมโยงกับ `branches.branch_id`
- **`legal_documents.reference_id`** เชื่อมโยงกับ `ppp09_id` หรือ `ppp20_id` ตาม `document_type`
- **ที่อยู่ใน `legal_ppp09`** แยกเป็น fields เพื่อให้ค้นหาและจัดการได้ง่าย
- **`legal_ppp09.ppp09_number`** เป็น unique per branch (เลขที่ตามสรรพากร)
- **สถานะของสาขา** ใน `legal_ppp09`: ยังไม่จดสรรพากร, เปิดให้บริการ, รอเปิดทำการ

## Performance Optimization

### Partitioning
- **`audit_logs`** - Partition โดย `created_at` (รายวัน)
- **`legal_ppp09`** - Partition โดย `DATE(created_at)` (รายวัน)
- **`legal_ppp20`** - Partition โดย `DATE(created_at)` (รายวัน)
- **`legal_documents`** - Partition โดย `DATE(uploaded_at)` (รายวัน)

### Clustering
- **`audit_logs`** - Cluster โดย `user_id` และ `action_type`
- **`legal_ppp09`** - Cluster โดย `branch_id` และ `branch_status`
- **`legal_ppp20`** - Cluster โดย `branch_id` และ `tax_period`
- **`legal_documents`** - Cluster โดย `document_type` และ `branch_id`

### Indexing Recommendations
- เนื่องจาก BigQuery ไม่มี traditional indexes แต่ใช้ partitioning และ clustering แทน
- ควร query โดยใช้ partition fields และ clustered columns เพื่อ performance ที่ดี

## Data Retention Policy

- **audit_logs**: เก็บทั้งหมดใน BigQuery (ไม่มีการลบ)
- สามารถ archive logs เก่ากว่า 1 ปี ไปยัง GCS (ถ้าต้องการประหยัดค่าใช้จ่าย)

## Related Documentation

- [features/user-management.md](features/user-management.md) - User & permissions management
- [features/audit-logs.md](features/audit-logs.md) - Audit logs details
- [features/legal-ppp09.md](features/legal-ppp09.md) - Legal ภ.พ.09 management
