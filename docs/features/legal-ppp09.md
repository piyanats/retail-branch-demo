# Legal ภ.พ.09 Management

## Overview

ภ.พ.09 (ภาษีที่ดินและสิ่งปลูกสร้าง ภ.พ.๐๙) คือ แบบแจ้งการประเมินภาษีที่ดินและสิ่งปลูกสร้าง ซึ่งเป็นเอกสารสำคัญทางกฎหมายสำหรับการดำเนินธุรกิจค้าปลีก ทีมกฎหมายจะมีหน้าที่ในการจัดการข้อมูล ภ.พ.09 ของแต่ละสาขา พร้อมทั้งเก็บเอกสาร PDF ต้นฉบับ

## Legal ภ.พ.09 Management Page (`/legal/ppp09`)

**สิทธิ์การเข้าถึง:** ทีมกฎหมาย (Legal Team) และ Admin

### ฟีเจอร์
- **รายการ ภ.พ.09 ทั้งหมด**: แสดงตารางข้อมูล ภ.พ.09 ของทุกสาขา
- **ค้นหา**: ค้นหาด้วย รหัสสาขา, เลขที่ ภ.พ.09, ชื่อเจ้าของ, ที่อยู่
- **กรอง**: กรองตาม จังหวัด, สถานะการชำระภาษี, วันหมดอายุ
- **เพิ่ม ภ.พ.09 ใหม่**: สร้างข้อมูล ภ.พ.09 ใหม่พร้อม upload PDF
- **แก้ไข ภ.พ.09**: แก้ไขข้อมูลและอัพเดท PDF
- **ลบ ภ.พ.09**: ลบข้อมูล (soft delete)
- **ดาวน์โหลด PDF**: ดาวน์โหลดเอกสาร ภ.พ.09 ต้นฉบับ
- **แจ้งเตือนหมดอายุ**: แจ้งเตือน ภ.พ.09 ที่ใกล้หมดอายุ (เช่น 30, 60, 90 วันก่อนหมดอายุ)

## Form: เพิ่ม/แก้ไข ภ.พ.09

**ฟอร์มแบ่งเป็น 4 sections:**

### 1. ข้อมูลทั่วไป
- รหัสสาขา (Dropdown/Autocomplete)
- เลขที่ ภ.พ.09 (Text input)
- ชื่อเจ้าของ/ผู้เสียภาษี (Text input)
- วันที่ออกเอกสาร (Date picker)
- วันหมดอายุ (Date picker)

### 2. ที่อยู่ตาม ภ.พ.09 (แยกตาม field)
- บ้านเลขที่ (Text input)
- หมู่ที่ (Text input)
- ตรอก (Text input - optional)
- ซอย (Text input - optional)
- ถนน (Text input - optional)
- ตำบล/แขวง (Text input)
- อำเภอ/เขต (Text input)
- จังหวัด (Dropdown - list of provinces)
- รหัสไปรษณีย์ (Text input - 5 digits)

**หมายเหตุ:** ที่อยู่ต้องแยกเป็น fields เพื่อให้ค้นหาและจัดการได้ง่าย

### 3. ข้อมูลเนื้อที่และภาษี
- เนื้อที่ดิน:
  - ไร่ (Number input)
  - งาน (Number input)
  - ตารางวา (Number input)
- พื้นที่สิ่งปลูกสร้าง (ตร.ม.) (Number input)
- จำนวนเงินภาษีต่อปี (บาท) (Number input)
- สถานะการชำระ (Dropdown: paid, unpaid, overdue)

### 4. เอกสาร PDF และหมายเหตุ
- อัพโหลด PDF ภ.พ.09 (File upload - accept PDF only, max 10MB)
  - แสดง preview/thumbnail ถ้ามี PDF อยู่แล้ว
  - ปุ่ม "Replace PDF" สำหรับเปลี่ยน PDF ใหม่
  - ปุ่ม "Download PDF" สำหรับดาวน์โหลด
  - ปุ่ม "Delete PDF" สำหรับลบ PDF
- หมายเหตุ (Textarea - optional)

## API Endpoints

- **GET /api/legal/ppp09** - ดึงรายการ ภ.พ.09 ทั้งหมด
- **GET /api/legal/ppp09/{ppp09_id}** - ดึงข้อมูล ภ.พ.09 รายการเดียว
- **POST /api/legal/ppp09** - สร้าง ภ.พ.09 ใหม่
- **PUT /api/legal/ppp09/{ppp09_id}** - แก้ไขข้อมูล ภ.พ.09
- **DELETE /api/legal/ppp09/{ppp09_id}** - ลบ ภ.พ.09 (soft delete)
- **POST /api/legal/ppp09/{ppp09_id}/upload-pdf** - อัพโหลด PDF
- **GET /api/legal/ppp09/{ppp09_id}/download-pdf** - ดาวน์โหลด PDF
- **DELETE /api/legal/ppp09/{ppp09_id}/delete-pdf** - ลบ PDF

## Business Logic

### การตรวจสอบหมดอายุ
- Cron job หรือ Cloud Scheduler ทำงานทุกวัน
- ตรวจสอบ ภ.พ.09 ที่จะหมดอายุใน 30, 60, 90 วัน
- ส่ง email notification ไปยังทีมกฎหมาย

### การตรวจสอบการชำระภาษี
- แสดง badge/alert สำหรับ ภ.พ.09 ที่ยังไม่ชำระภาษี (unpaid)
- แสดง badge/alert แดงสำหรับ ภ.พ.09 ที่ค้างชำระ (overdue)

### PDF Storage
- เก็บ PDF ไว้ใน GCS bucket: `gs://{bucket}/legal/ppp09/{branch_id}_{ppp09_number}_{year}.pdf`
- ตั้งชื่อไฟล์ให้มีความหมายและไม่ซ้ำกัน
- เก็บ metadata (file_size, upload_time, uploader) ใน BigQuery

## Status Badges

- **Paid**: เขียว (Success Green)
- **Unpaid**: ส้ม (Warning Orange)
- **Overdue**: แดง (Error Red)

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - legal_ppp09 table schema
- [audit-logs.md](audit-logs.md) - Audit logging for ภ.พ.09 operations
