# API Standards & Conventions

## Overview

เอกสารนี้กำหนด standards และ conventions สำหรับการออกแบบ REST API ของระบบ Retail Branch Management System เพื่อให้การใช้งาน API มีความสม่ำเสมอและคาดเดาได้

## Base URL

**Development:**
```
http://localhost:8000
```

**Production:**
```
https://retail-branch-demo-xxxxxxxxxx-as.a.run.app
```

## API Versioning

ไม่ใช้ API versioning ใน path (/v1, /v2) เพื่อความเรียบง่าย
- หาก API เปลี่ยนแปลง ให้รักษา backward compatibility
- ถ้าจำเป็นต้อง breaking change ให้สร้าง endpoint ใหม่แทน

## Authentication

**ทุก API endpoint (ยกเว้น `/auth/login` และ `/auth/callback`) ต้องมี authentication**

**Authentication Method:** Session-based (Cookie)
- Cookie name: `session`
- Cookie attributes: HttpOnly, Secure (production), SameSite=Lax
- Session timeout: 24 hours

**Unauthenticated Response:**
```json
{
  "success": false,
  "error": "Not authenticated",
  "message": "Please login to continue",
  "code": "AUTHENTICATION_REQUIRED"
}
```
HTTP Status: `401 Unauthorized`

## Authorization

**ตรวจสอบ permissions ตาม user level และ team membership**

**Unauthorized Access Response:**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "You do not have permission to access this resource",
  "code": "UNAUTHORIZED"
}
```
HTTP Status: `403 Forbidden`

## Request Format

### HTTP Methods

| Method | Usage | Idempotent |
|--------|-------|------------|
| GET | ดึงข้อมูล | Yes |
| POST | สร้างข้อมูลใหม่ | No |
| PUT | แก้ไขข้อมูลทั้งหมด | Yes |
| PATCH | แก้ไขข้อมูลบางส่วน | Yes |
| DELETE | ลบข้อมูล | Yes |

### Content Type

**Request Headers:**
```
Content-Type: application/json
Accept: application/json
```

**Request Body (JSON):**
```json
{
  "field1": "value1",
  "field2": 123,
  "field3": true
}
```

### Multipart Form Data (File Upload)

**Request Headers:**
```
Content-Type: multipart/form-data
```

**Form Fields:**
```
------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="branch_id"

BR001
------WebKitFormBoundary--
```

## Response Format

### Success Response

**Structure:**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // ... response data
  }
}
```

**Examples:**

**Single Resource:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-123",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**List of Resources:**
```json
{
  "success": true,
  "data": [
    { "id": "1", "name": "Item 1" },
    { "id": "2", "name": "Item 2" }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

**Create/Update Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": "uuid-new",
    "email": "jane@example.com"
  }
}
```

**Delete Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### Error Response

**Standard Error Format:**
```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    // Optional: detailed error information
  }
}
```

**Validation Error:**
```json
{
  "success": false,
  "error": "Validation failed",
  "message": "The request data is invalid",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": ["Email already exists"],
    "name": ["Name is required"],
    "user_level": ["Must be one of: admin, manager, editor, viewer"]
  }
}
```

**Not Found Error:**
```json
{
  "success": false,
  "error": "Resource not found",
  "message": "The requested user was not found",
  "code": "NOT_FOUND"
}
```

**Server Error:**
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please try again later.",
  "code": "INTERNAL_ERROR"
}
```

### HTTP Status Codes

| Status Code | Meaning | Usage |
|------------|---------|-------|
| **200 OK** | Success | GET, PUT, PATCH, DELETE successful |
| **201 Created** | Resource created | POST successful |
| **204 No Content** | Success without body | DELETE successful (alternative) |
| **400 Bad Request** | Invalid request | Validation errors, malformed JSON |
| **401 Unauthorized** | Not authenticated | Missing or invalid session |
| **403 Forbidden** | Not authorized | Insufficient permissions |
| **404 Not Found** | Resource not found | Resource doesn't exist |
| **409 Conflict** | Resource conflict | Duplicate entry, concurrent update |
| **422 Unprocessable Entity** | Validation failed | Semantic validation errors |
| **429 Too Many Requests** | Rate limit exceeded | Too many API calls |
| **500 Internal Server Error** | Server error | Unexpected server errors |
| **503 Service Unavailable** | Service down | Maintenance, database down |

## Pagination

**ใช้ offset-based pagination**

### Query Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | หมายเลขหน้า (เริ่มจาก 1) |
| `limit` | integer | 20 | 100 | จำนวนรายการต่อหน้า |

### Example Request

```
GET /api/admin/users?page=2&limit=50
```

### Pagination Response

```json
{
  "success": true,
  "data": [ /* ... */ ],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 145,
    "total_pages": 3,
    "has_next": true,
    "has_prev": true
  }
}
```

**Pagination Fields:**
- `page`: หมายเลขหน้าปัจจุบัน
- `limit`: จำนวนรายการต่อหน้า
- `total`: จำนวนรายการทั้งหมด
- `total_pages`: จำนวนหน้าทั้งหมด
- `has_next`: มีหน้าถัดไปหรือไม่ (optional)
- `has_prev`: มีหน้าก่อนหน้าหรือไม่ (optional)

### Default Page Sizes

| Endpoint Type | Default | Max |
|--------------|---------|-----|
| General List APIs | 20 | 100 |
| Audit Logs | 50 | 100 |
| Search Results | 20 | 50 |
| Dropdown Options | 100 | 500 |

## Filtering

**ใช้ query parameters สำหรับการกรอง**

### Simple Filters

**Exact Match:**
```
GET /api/admin/users?status=active&user_level=editor
```

**Multiple Values (OR):**
```
GET /api/admin/users?user_level=editor,manager
```
หมายถึง: `user_level = 'editor' OR user_level = 'manager'`

### Date Range Filters

**Date Range:**
```
GET /api/admin/audit-logs?date_from=2024-01-01&date_to=2024-03-31
```

**Date Format:** `YYYY-MM-DD`

### Common Filter Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | กรองตามสถานะ | `active`, `inactive` |
| `user_level` | string | กรองตามระดับผู้ใช้ | `admin`, `editor` |
| `team_name` | string | กรองตามทีม | `legal`, `srd` |
| `branch_status` | string | กรองตามสถานะสาขา | `รอเปิด`, `เปิดทำการ` |
| `province` | string | กรองตามจังหวัด | `กรุงเทพมหานคร` |
| `date_from` | date | กรองตั้งแต่วันที่ | `2024-01-01` |
| `date_to` | date | กรองถึงวันที่ | `2024-12-31` |

## Sorting

**ใช้ `sort` query parameter**

### Syntax

**Ascending (เรียงจากน้อยไปมาก):**
```
GET /api/admin/users?sort=created_at
```

**Descending (เรียงจากมากไปน้อย):**
```
GET /api/admin/users?sort=-created_at
```

**Multiple Fields:**
```
GET /api/admin/users?sort=-created_at,email
```
หมายถึง: เรียงตาม `created_at` descending แล้วเรียงตาม `email` ascending

### Common Sort Fields

| Resource | Sort Fields |
|----------|-------------|
| Users | `created_at`, `last_login`, `email`, `name` |
| Audit Logs | `created_at`, `user_email`, `action_type` |
| Branches | `created_at`, `branch_id`, `branch_name`, `province` |
| PPP09 | `created_at`, `branch_id`, `registration_date` |

### Default Sorting

**ถ้าไม่ระบุ `sort` parameter:**
- ส่วนใหญ่เรียงตาม `created_at` descending (ล่าสุดก่อน)
- Audit Logs: `created_at` descending
- User Lists: `created_at` descending

## Searching

**ใช้ `search` query parameter**

### Full-Text Search

```
GET /api/admin/users?search=john
```

**ค้นหาใน fields:**
- Users: `email`, `name`
- Audit Logs: `user_email`, `resource_id`, `action_detail`
- Branches: `branch_id`, `branch_name`, `address`
- PPP09: `branch_id`, `ppp09_number`, `address`

### Search Behavior

- **Case-insensitive** (ไม่สนใจตัวพิมพ์เล็ก/ใหญ่)
- **Partial match** (ค้นหาบางส่วนของคำ)
- **Multiple fields** (ค้นหาหลาย fields พร้อมกัน)

**Example:**
```
GET /api/admin/users?search=john
```
จะค้นหา users ที่มี "john" ใน `email` หรือ `name`

### Combining Search with Filters

```
GET /api/admin/users?search=john&user_level=editor&status=active&sort=-created_at
```

## File Upload

### Upload Endpoint Pattern

```
POST /api/{team}/{resource}/{id}/upload
```

**Example:**
```
POST /api/legal/ppp09/{ppp09_id}/upload-documents
```

### Upload Request

**Headers:**
```
Content-Type: multipart/form-data
```

**Form Data:**
```
file: [binary]
document_type: "ppp09"
reference_id: "PPP09-001"
```

### Upload Response

```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "document_id": "uuid-doc-123",
    "file_name": "ppp09_document.pdf",
    "file_size": 2048576,
    "mime_type": "application/pdf",
    "file_path": "gs://bucket/legal/ppp09/BR001_ppp09_2024.pdf",
    "uploaded_at": "2024-03-25T15:00:00Z"
  }
}
```

### Upload Limits

| File Type | Max Size | Allowed Extensions |
|-----------|----------|-------------------|
| PDF | 10 MB | `.pdf` |
| Images | 5 MB | `.jpg`, `.jpeg`, `.png` |
| Excel | 10 MB | `.xls`, `.xlsx` |

### Upload Error Response

```json
{
  "success": false,
  "error": "File validation failed",
  "message": "The uploaded file is too large",
  "code": "FILE_TOO_LARGE",
  "details": {
    "file_size": 12582912,
    "max_size": 10485760
  }
}
```

## File Download

### Download Endpoint Pattern

```
GET /api/{team}/{resource}/{id}/download
```

**Example:**
```
GET /api/legal/ppp09/{ppp09_id}/download-document/{document_id}
```

### Download Response

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="ppp09_BR001.pdf"
Content-Length: 2048576
```

**Body:** Binary file data

## Rate Limiting

**Default Rate Limits:**
- **General APIs**: 100 requests/minute per user
- **Search/Filter APIs**: 60 requests/minute per user
- **Export/Download APIs**: 10 requests/minute per user
- **Upload APIs**: 20 requests/minute per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711372800
```

**Rate Limit Error:**
```json
{
  "success": false,
  "error": "Too many requests",
  "message": "Rate limit exceeded. Please try again later.",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": 100,
    "reset_at": "2024-03-25T16:00:00Z"
  }
}
```
HTTP Status: `429 Too Many Requests`

## CORS Headers

**Development:**
```
Access-Control-Allow-Origin: http://localhost:8000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Production:**
```
Access-Control-Allow-Origin: https://your-domain.run.app
Access-Control-Allow-Credentials: true
```

## Timestamps

**Format:** ISO 8601 with UTC timezone

```json
{
  "created_at": "2024-03-25T10:30:00Z",
  "updated_at": "2024-03-25T14:45:30Z"
}
```

**Timezone:** Always use UTC (Z suffix)

## Field Naming Conventions

**Use `snake_case` สำหรับ JSON keys:**
```json
{
  "user_id": "uuid-123",
  "email_address": "john@example.com",
  "created_at": "2024-03-25T10:30:00Z",
  "is_active": true
}
```

**ห้ามใช้:**
- ❌ `camelCase`
- ❌ `PascalCase`
- ❌ `kebab-case`

## Boolean Values

**ใช้ `true` และ `false` (lowercase)**

```json
{
  "is_active": true,
  "alc_flag": false,
  "halan_flag": true
}
```

## Null Values

**ใช้ `null` สำหรับ empty/missing values**

```json
{
  "phone_number": null,
  "remarks": null,
  "actual_opening_date": null
}
```

**ห้าม omit fields** - ส่ง `null` แทน

## Related Documentation

- [../features/user-management.md](../features/user-management.md) - User Management APIs
- [../features/audit-logs.md](../features/audit-logs.md) - Audit Logs APIs
- [../auth/oauth.md](../auth/oauth.md) - Authentication APIs
- [../features/legal-ppp09.md](../features/legal-ppp09.md) - Legal Team APIs
- [../features/new-branch.md](../features/new-branch.md) - New Branch Team APIs
- [../features/srd-layout.md](../features/srd-layout.md) - SRD Team APIs
- [../features/scm-dc.md](../features/scm-dc.md) - SCM Team APIs
