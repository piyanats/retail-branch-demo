# Design & UI/UX Guidelines

## Design Principles

### 1. Simplicity & Minimalism (ความเรียบง่าย)
- เน้นเนื้อหาที่สำคัญ ตัดสิ่งที่ไม่จำเป็นออก
- ใช้ white space อย่างเหมาะสม เพื่อให้ดูโปร่ง ไม่อัดแน่น
- หลีกเลี่ยงการใช้ decorations หรือ effects ที่มากเกินไป
- "Less is More" - ทำน้อยแต่ได้มาก

### 2. Modern & Clean Design (ดีไซน์ทันสมัย)
- ใช้ flat design หรือ subtle shadows (ไม่ใช้ skeuomorphism)
- มุมโค้งมน (rounded corners) สำหรับ cards และ buttons
- Consistent spacing และ alignment ทุกหน้า
- ใช้ modern icons (line icons หรือ outline style)

### 3. User-Centric (เน้นผู้ใช้)
- Navigation ชัดเจน รู้ว่าตัวเองอยู่ที่ไหนในระบบ
- Call-to-action (CTA) buttons เด่นชัด และวางตำแหน่งที่เหมาะสม
- Feedback ทันที เมื่อผู้ใช้ทำ action (loading, success, error states)
- Error messages ที่เข้าใจง่าย พร้อมแนะนำวิธีแก้ไข

### 4. Accessibility (การเข้าถึง)
- สีที่มี contrast ดี อ่านง่าย (WCAG AA standard)
- Font size อ่านง่าย (ไม่เล็กเกินไป)
- รองรับ keyboard navigation
- ใช้ semantic HTML elements

## Color Palette

### Primary Colors
- **Primary Blue**: `#3B82F6` - สำหรับ primary buttons, links, highlights
- **Success Green**: `#10B981` - แสดงสถานะสำเร็จ, confirmations
- **Warning Orange**: `#F59E0B` - แสดงการแจ้งเตือน, warnings
- **Error Red**: `#EF4444` - แสดง errors, destructive actions

### Neutral Colors
- **Gray Scale**: `#111827` (dark) → `#F9FAFB` (light)
- ใช้สำหรับ text, borders, backgrounds
- Gray-900 สำหรับ headings, Gray-700 สำหรับ body text

### Usage
- Background: White (`#FFFFFF`) หรือ Light Gray (`#F9FAFB`)
- ใช้สีประจำทีม (team colors) เป็น accents เมื่อเหมาะสม
- Hover states: ใช้สีเข้มขึ้น 10-20%

## Typography

### Font Family
- **System Fonts**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial`
- ใช้ system fonts เพื่อ performance ดีและความคุ้นเคย

### Font Sizes
- **Heading 1**: `2.25rem` (36px) - หน้าหลัก, page titles
- **Heading 2**: `1.875rem` (30px) - section titles
- **Heading 3**: `1.5rem` (24px) - subsections
- **Body**: `1rem` (16px) - paragraph text
- **Small**: `0.875rem` (14px) - captions, labels
- **Tiny**: `0.75rem` (12px) - helper text (ใช้น้อย)

### Font Weight
- Regular (400): Body text
- Medium (500): Emphasized text
- Semibold (600): Subheadings
- Bold (700): Headings, important text

### Line Height
- Headings: `1.2` (tight)
- Body text: `1.5` (comfortable reading)
- Small text: `1.4`

## Layout & Spacing

### Container Width
- **Max Width**: `1280px` (desktop)
- **Padding**: `1rem` (mobile), `2rem` (tablet), `4rem` (desktop)
- Centered layout สำหรับ main content

### Spacing Scale (Tailwind)
- `4px` (space-1): Tight spacing
- `8px` (space-2): Small gaps
- `16px` (space-4): Default spacing
- `24px` (space-6): Medium spacing
- `32px` (space-8): Large spacing
- `48px` (space-12): Section spacing
- `64px` (space-16): Page sections

### Grid System
- 12-column grid สำหรับ layout
- Responsive breakpoints:
  - Mobile: `< 640px`
  - Tablet: `640px - 1024px`
  - Desktop: `> 1024px`

## UI Components

### Buttons
- **Primary Button**: Blue background, white text, rounded corners
- **Secondary Button**: White background, gray border, gray text
- **Danger Button**: Red background, white text (สำหรับ delete actions)
- Padding: `0.5rem 1rem` (small), `0.75rem 1.5rem` (default)
- Hover: Darker shade + subtle shadow
- Disabled: Gray, low opacity, no pointer

### Cards
- White background
- Subtle shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Rounded corners: `0.5rem` (8px)
- Padding: `1.5rem` (24px)
- Hover: Lift up (translate + stronger shadow)

### Forms
- Input height: `2.5rem` (40px)
- Border: `1px solid gray-300`
- Focus: Blue border + subtle shadow
- Labels: Above inputs, bold, Gray-700
- Validation: Red border สำหรับ errors พร้อม helper text

### Tables
- Striped rows (zebra pattern) สำหรับอ่านง่าย
- Hover: Light gray background
- Headers: Bold, Gray-900, bottom border
- Padding: `0.75rem 1rem`
- Responsive: Scroll horizontal บน mobile

### Navigation
- Top navbar: Fixed position, white background, shadow
- Active state: Blue underline หรือ background
- Logo/Brand: ซ้ายสุด
- User menu: ขวาสุด พร้อม avatar
- Mobile: Hamburger menu

## User Experience (UX) Guidelines

### 1. Feedback & Response
- **Loading States**: แสดง spinner หรือ skeleton screens
- **Success Messages**: Toast notification (เขียว) แสดง 3-5 วินาที
- **Error Messages**: Modal หรือ inline (แดง) พร้อมคำแนะนำ
- **Confirmation**: Modal สำหรับ destructive actions (delete)

### 2. Navigation & Flow
- **Breadcrumbs**: แสดงตำแหน่งปัจจุบันในระบบ
- **Back Buttons**: ให้กลับไปหน้าก่อนหน้าได้
- **Clear CTAs**: ปุ่มหลักเด่นชัด, ปุ่มรองเบาลง
- **Search**: Accessible, auto-suggest ถ้าเป็นไปได้

### 3. Performance
- **Fast Load**: หน้าเว็บโหลดเร็ว (< 3 seconds)
- **Lazy Loading**: โหลดรูปภาพและ components ตามต้องการ
- **Pagination**: แบ่งหน้าสำหรับ data มาก (20-50 items/page)
- **Caching**: Cache ข้อมูลที่ไม่เปลี่ยนบ่อย

### 4. Mobile Experience
- **Touch Friendly**: Buttons ขนาดอย่างน้อย `44x44px`
- **Thumb Zone**: ปุ่มสำคัญอยู่ในตำแหน่งที่จับได้ง่าย
- **Reduced Motion**: ลด animations บน mobile
- **Offline Ready**: แสดง error ชัดเจนเมื่อไม่มี connection

### 5. Consistency
- ใช้ components เดียวกันทั้งระบบ
- สี, spacing, typography ต้อง consistent
- เมนูและ navigation เหมือนกันทุกหน้า
- Patterns ที่คุ้นเคย (e.g., search icon คือ magnifying glass)

## Team-Specific UI Elements

แต่ละทีมจะมี accent color ของตัวเอง:
- **ทีมสาขาใหม่**: Blue (`#3B82F6`) - Growth, New beginnings
- **ทีมกฎหมาย**: Purple (`#8B5CF6`) - Authority, Professional
- **ทีม SRD**: Orange (`#F97316`) - Creative, Design
- **ทีม SCM**: Green (`#10B981`) - Efficiency, Logistics

ใช้ accent color ใน:
- Page headers
- Section highlights
- Team badges/tags
- Icons

## Related Documentation

- [frontend/tailwind.md](frontend/tailwind.md) - Tailwind CSS setup and configuration
