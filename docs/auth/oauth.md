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

## Related Documentation

- [../DATABASE.md](../DATABASE.md) - Users table schema
- [../features/user-management.md](../features/user-management.md) - User management
- [../development/setup.md](../development/setup.md) - OAuth setup in development
