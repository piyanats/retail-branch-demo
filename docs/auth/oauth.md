# Google OAuth 2.0 Authentication

## Overview

ระบบใช้ **Google OAuth 2.0** สำหรับการ login เข้าใช้งานของผู้ใช้ทุกคน โดยผู้ใช้จะต้อง login ด้วย Google Account ก่อนเข้าใช้งานระบบ ซึ่งจะช่วยให้:
- ไม่ต้องสร้างและจัดการ password เอง (ใช้ Google authentication)
- รองรับ Single Sign-On (SSO)
- ปลอดภัยและเชื่อถือได้ (Google's security)
- ตรวจสอบสิทธิ์ผู้ใช้จาก email domain

## Setup OAuth Client

1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
2. เปิด **APIs & Services** > **Credentials**
3. สร้าง **OAuth 2.0 Client ID** (Application type: Web application)
4. ตั้งค่า **Authorized redirect URIs**:
   - Development: `http://localhost:8000/auth/callback`
   - Production: `https://your-domain.run.app/auth/callback`
5. บันทึก **Client ID** และ **Client Secret**

## Environment Variables for OAuth

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-key
```

## User Authentication Flow

1. **ผู้ใช้เข้าหน้า Login**: เข้าที่ `/` หรือ `/login`
2. **กด "Sign in with Google"**: คลิกปุ่ม login
3. **Redirect to Google**: ระบบ redirect ไปยัง Google OAuth consent screen
4. **ผู้ใช้เลือก Google Account**: เลือก account และอนุมัติการเข้าถึงข้อมูล
5. **Google Callback**: Google redirect กลับมาที่ `/auth/callback` พร้อม authorization code
6. **Exchange Token**: Backend แลก authorization code เป็น access token
7. **Get User Info**: ดึงข้อมูลผู้ใช้จาก Google API (email, name, picture)
8. **Verify User**: ตรวจสอบ email กับ BigQuery (table: `users`)
   - ถ้ามี user ในระบบ → อนุญาตให้ login
   - ถ้าไม่มี → แสดง error "Unauthorized user"
9. **Create Session**: สร้าง session cookie สำหรับ user
10. **Update Last Login**: อัพเดท `last_login` timestamp ใน BigQuery
11. **Redirect to Dashboard**: ส่งผู้ใช้ไปหน้าแรกตาม team ของ user

## Session Management

**Session Storage:**
- ใช้ **itsdangerous** สำหรับ signed session cookies
- เก็บข้อมูล: `user_id`, `email`, `name`, `team`, `role`
- Session timeout: 24 ชั่วโมง (configurable)

**Session Cookie Settings:**
- `httponly=True`: ป้องกัน XSS attacks
- `secure=True`: ใช้ HTTPS only (production)
- `samesite='Lax'`: ป้องกัน CSRF attacks

## Protected Routes

**Route Protection:**
- ทุก route (ยกเว้น `/login` และ `/auth/callback`) ต้อง login ก่อน
- Middleware ตรวจสอบ session cookie ทุก request
- ถ้าไม่มี session → redirect to `/login`
- ถ้า session หมดอายุ → redirect to `/login` พร้อม message

**Team-Based Access Control:**
- ตรวจสอบ `team` จาก session
- แสดงเฉพาะเมนูและข้อมูลที่ team มีสิทธิ์เข้าถึง
- ถ้าเข้าถึง route ที่ไม่มีสิทธิ์ → แสดง 403 Forbidden

## Logout

**Logout Flow:**
1. ผู้ใช้คลิก "Logout"
2. ลบ session cookie
3. (Optional) Revoke Google access token
4. Redirect to `/login`

## API Endpoints

### GET `/auth/login`
เริ่มต้น Google OAuth flow

**Description:**
- Redirect ผู้ใช้ไปยัง Google OAuth consent screen
- สร้าง state parameter สำหรับ CSRF protection
- Request scopes: `email`, `profile`

**Response:**
```
HTTP 302 Redirect
Location: https://accounts.google.com/o/oauth2/v2/auth?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=http://localhost:8000/auth/callback&
  response_type=code&
  scope=email profile&
  state=random-state-token&
  access_type=offline
```

### GET `/auth/callback`
รับ OAuth callback จาก Google

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: State parameter for CSRF verification

**Success Response (Redirect):**
```
HTTP 302 Redirect
Location: /dashboard
Set-Cookie: session=signed-session-token; HttpOnly; Secure; SameSite=Lax
```

**Error Response (Unauthorized User):**
```html
HTTP 403 Forbidden

<!DOCTYPE html>
<html>
<head><title>Unauthorized</title></head>
<body>
  <h1>Unauthorized Access</h1>
  <p>Your email is not registered in the system. Please contact the administrator.</p>
  <a href="/auth/login">Try Again</a>
</body>
</html>
```

**Error Response (OAuth Error):**
```html
HTTP 400 Bad Request

<!DOCTYPE html>
<html>
<head><title>Authentication Failed</title></head>
<body>
  <h1>Authentication Failed</h1>
  <p>Unable to authenticate with Google. Please try again.</p>
  <a href="/auth/login">Back to Login</a>
</body>
</html>
```

### POST `/auth/logout`
ออกจากระบบ

**Response:**
```
HTTP 302 Redirect
Location: /login
Set-Cookie: session=; Max-Age=0
```

**JSON Response (if Accept: application/json):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET `/auth/me`
ดึงข้อมูลผู้ใช้ปัจจุบัน (current user)

**Authentication Required:** Yes (session cookie)

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid-123",
    "email": "john@example.com",
    "name": "John Doe",
    "user_level": "editor",
    "teams": [
      {
        "team_name": "legal",
        "role": "editor"
      },
      {
        "team_name": "new_branch",
        "role": "viewer"
      }
    ],
    "permissions": {
      "can_access_admin": false,
      "can_manage_users": false,
      "accessible_teams": ["legal", "new_branch"]
    },
    "last_login": "2024-03-25T14:30:00Z"
  }
}
```

**Error Response (Not Authenticated):**
```json
{
  "success": false,
  "error": "Not authenticated",
  "message": "Please login to continue",
  "code": "AUTHENTICATION_REQUIRED"
}
```

### Session Cookie Format

**Cookie Name:** `session`

**Cookie Attributes:**
- **HttpOnly**: true (ป้องกัน JavaScript access)
- **Secure**: true (HTTPS only in production)
- **SameSite**: Lax (ป้องกัน CSRF)
- **Max-Age**: 86400 (24 hours)
- **Path**: /

**Session Data (encrypted):**
```json
{
  "user_id": "uuid-123",
  "email": "john@example.com",
  "name": "John Doe",
  "user_level": "editor",
  "teams": ["legal", "new_branch"],
  "iat": 1711372800,
  "exp": 1711459200
}
```

## Security Best Practices

### CSRF Protection
- ใช้ `state` parameter ใน OAuth flow
- ตรวจสอบ state token ที่ callback endpoint
- ใช้ SameSite cookie attribute

### Session Security
- Session token ถูก sign ด้วย SECRET_KEY
- ตรวจสอบ signature ทุก request
- Session timeout 24 ชั่วโมง
- ห้าม decode session ใน client-side JavaScript

### Token Handling
- **ห้าม** เก็บ access token ใน cookie หรือ localStorage
- Exchange token ที่ backend เท่านั้น
- (Optional) เก็บ refresh token ใน secure database ถ้าต้องการ offline access

### Error Handling
- **ห้าม** แสดง error details ที่เป็นความลับ
- Log errors ที่ backend สำหรับ debugging
- แสดง generic error message ให้ user

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Users table schema
- [../features/user-management.md](../features/user-management.md) - User management
- [../development/setup.md](../development/setup.md) - OAuth setup in development
