# Notification System

## Overview

ระบบแจ้งเตือนสำหรับ events ต่างๆ ในระบบ รองรับทั้ง **In-App Notifications** (Toast) และ **Email Notifications** เพื่อแจ้งเตือนผู้ใช้เกี่ยวกับ events สำคัญ

## Notification Types

### 1. In-App Notifications (Toast)

**Use Cases:**
- แสดงผลลัพธ์ของ action ทันที (success, error, warning)
- ไม่ต้อง persist ข้อมูล
- แสดง 3-5 วินาที แล้วหายไป

**Implementation:** JavaScript Toast component (see frontend/javascript.md)

### 2. Email Notifications

**Use Cases:**
- Events สำคัญที่ต้องแจ้งเตือนแม้ไม่ได้ online
- ต้อง persist และ track การส่ง
- สามารถส่งหลายคนพร้อมกัน

## Email Notification Events

### New Branch Team

| Event | Trigger | Recipients | Template |
|-------|---------|------------|----------|
| **Branch Opening Soon** | 30 days before estimate opening date | New Branch Team Managers | `branch_opening_30days.html` |
| **Branch Opening This Week** | 7 days before estimate opening date | New Branch Team + Legal + SRD + SCM | `branch_opening_7days.html` |
| **Branch Opened** | Actual opening date is set | All teams | `branch_opened.html` |
| **Branch Opening Overdue** | Estimate date passed but not opened | New Branch Team Managers | `branch_overdue.html` |

### Legal Team

| Event | Trigger | Recipients | Template |
|-------|---------|------------|----------|
| **ภ.พ.09 Expiring Soon** | 60 days before expiry | Legal Team | `ppp09_expiring_60days.html` |
| **ภ.พ.09 Expiring This Month** | 30 days before expiry | Legal Team Managers | `ppp09_expiring_30days.html` |
| **ภ.พ.09 Expired** | Day after expiry date | Legal Team Managers | `ppp09_expired.html` |
| **ภ.พ.20 Tax Filing Reminder** | 10 days before filing deadline | Legal Team | `ppp20_filing_reminder.html` |

### SCM Team

| Event | Trigger | Recipients | Template |
|-------|---------|------------|----------|
| **DC Change Scheduled** | When DC change is scheduled | SCM Team Managers | `dc_change_scheduled.html` |
| **DC Change Tomorrow** | 1 day before effective date | SCM Team + Branch Managers | `dc_change_tomorrow.html` |
| **DC Change Completed** | Auto-change completed | SCM Team | `dc_change_completed.html` |

### Admin

| Event | Trigger | Recipients | Template |
|-------|---------|------------|----------|
| **New User Added** | User created | Admins | `user_created.html` |
| **Permission Changed** | User permissions updated | Admins + Affected User | `permission_changed.html` |
| **Failed Login Attempts** | 5 failed logins in 15 minutes | Admins | `security_alert.html` |

## Email Service Implementation

### Using SendGrid (Recommended)

```python
# services/email_service.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from jinja2 import Environment, FileSystemLoader

class EmailService:
    """Email service using SendGrid"""

    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.client = SendGridAPIClient(self.api_key)
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@retailbranch.com')
        self.from_name = os.getenv('FROM_NAME', 'Retail Branch System')

        # Jinja2 template engine
        self.template_env = Environment(
            loader=FileSystemLoader('app/templates/emails')
        )

    def send_email(
        self,
        to_emails: list,
        subject: str,
        template_name: str,
        context: dict
    ) -> bool:
        """
        Send email using template

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            template_name: Template file name
            context: Template context variables

        Returns:
            bool: True if sent successfully
        """
        try:
            # Render template
            template = self.template_env.get_template(template_name)
            html_content = template.render(**context)

            # Create message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=[To(email) for email in to_emails],
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            # Send
            response = self.client.send(message)

            # Log
            self._log_email_sent(to_emails, subject, response.status_code)

            return response.status_code in [200, 201, 202]

        except Exception as e:
            self._log_email_error(to_emails, subject, str(e))
            return False

    def send_branch_opening_alert(
        self,
        branch_id: str,
        branch_name: str,
        estimate_opening_date: str,
        days_remaining: int
    ):
        """Send branch opening alert"""

        # Get recipients (New Branch Team Managers)
        recipients = self._get_team_managers('new_branch')

        template = 'branch_opening_30days.html' if days_remaining == 30 else 'branch_opening_7days.html'

        return self.send_email(
            to_emails=recipients,
            subject=f"Branch Opening Alert: {branch_name} - {days_remaining} days",
            template_name=template,
            context={
                'branch_id': branch_id,
                'branch_name': branch_name,
                'estimate_opening_date': estimate_opening_date,
                'days_remaining': days_remaining
            }
        )

    def send_ppp09_expiring_alert(
        self,
        ppp09_id: str,
        branch_id: str,
        branch_name: str,
        expiry_date: str,
        days_remaining: int
    ):
        """Send ภ.พ.09 expiring alert"""

        recipients = self._get_team_managers('legal')

        template = 'ppp09_expiring_60days.html' if days_remaining == 60 else 'ppp09_expiring_30days.html'

        return self.send_email(
            to_emails=recipients,
            subject=f"ภ.พ.09 Expiring Soon: {branch_name} - {days_remaining} days",
            template_name=template,
            context={
                'ppp09_id': ppp09_id,
                'branch_id': branch_id,
                'branch_name': branch_name,
                'expiry_date': expiry_date,
                'days_remaining': days_remaining
            }
        )

    def send_dc_change_notification(
        self,
        branch_id: str,
        branch_name: str,
        current_dc: str,
        new_dc: str,
        effective_date: str,
        reason: str
    ):
        """Send DC change notification"""

        recipients = self._get_team_managers('scm')

        return self.send_email(
            to_emails=recipients,
            subject=f"DC Change Scheduled: {branch_name}",
            template_name='dc_change_scheduled.html',
            context={
                'branch_id': branch_id,
                'branch_name': branch_name,
                'current_dc': current_dc,
                'new_dc': new_dc,
                'effective_date': effective_date,
                'reason': reason
            }
        )

    def _get_team_managers(self, team_name: str) -> list:
        """Get email addresses of team managers"""
        # Query BigQuery for users with manager role in team
        query = f"""
            SELECT u.email
            FROM retail_branches.users u
            JOIN retail_branches.user_teams ut ON u.user_id = ut.user_id
            WHERE ut.team_name = '{team_name}'
              AND (ut.role = 'manager' OR u.user_level = 'admin')
              AND u.is_active = true
        """
        # Execute query and return emails
        # Implementation here

    def _log_email_sent(self, recipients, subject, status_code):
        """Log successful email"""
        print(f"Email sent: {subject} to {recipients} - Status: {status_code}")
        # Log to BigQuery or logging service

    def _log_email_error(self, recipients, subject, error):
        """Log email error"""
        print(f"Email failed: {subject} to {recipients} - Error: {error}")
        # Log to BigQuery or error tracking service
```

## Email Templates

### Template Structure

```
app/templates/emails/
├── base_email.html           # Base template
├── branch_opening_30days.html
├── branch_opening_7days.html
├── branch_opened.html
├── branch_overdue.html
├── ppp09_expiring_60days.html
├── ppp09_expiring_30days.html
├── ppp09_expired.html
├── ppp20_filing_reminder.html
├── dc_change_scheduled.html
├── dc_change_tomorrow.html
├── dc_change_completed.html
├── user_created.html
└── permission_changed.html
```

### Base Email Template

```html
<!-- app/templates/emails/base_email.html -->
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Retail Branch Management System{% endblock %}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: #3B82F6;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            background: #f9fafb;
            padding: 30px;
            border: 1px solid #e5e7eb;
        }
        .footer {
            background: #f3f4f6;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-radius: 0 0 8px 8px;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #3B82F6;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px 0;
        }
        .alert {
            padding: 15px;
            border-left: 4px solid #F59E0B;
            background: #FEF3C7;
            margin: 20px 0;
        }
        .info-box {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Retail Branch Management System</h1>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        <p>This is an automated message from Retail Branch Management System</p>
        <p>Please do not reply to this email</p>
    </div>
</body>
</html>
```

### Example: Branch Opening Alert

```html
<!-- app/templates/emails/branch_opening_30days.html -->
{% extends "emails/base_email.html" %}

{% block title %}Branch Opening Alert - {{ branch_name }}{% endblock %}

{% block content %}
<h2>🏪 Branch Opening Alert</h2>

<div class="alert">
    <strong>⏰ Reminder:</strong> Branch opening in {{ days_remaining }} days
</div>

<div class="info-box">
    <p><strong>Branch ID:</strong> {{ branch_id }}</p>
    <p><strong>Branch Name:</strong> {{ branch_name }}</p>
    <p><strong>Estimated Opening Date:</strong> {{ estimate_opening_date }}</p>
    <p><strong>Days Remaining:</strong> {{ days_remaining }} days</p>
</div>

<p>Please ensure all preparations are complete before the opening date.</p>

<h3>Required Actions:</h3>
<ul>
    <li>✅ Complete legal documents (ภ.พ.09, ภ.พ.20)</li>
    <li>✅ Finalize store layout (SRD Team)</li>
    <li>✅ Confirm DC assignment (SCM Team)</li>
    <li>✅ Staff recruitment and training</li>
</ul>

<a href="https://retailbranch.com/new-branch/{{ branch_id }}" class="button">
    View Branch Details
</a>

<p>If you have any questions, please contact the New Branch Team.</p>
{% endblock %}
```

## Notification Preferences (Future Enhancement)

### User Notification Settings

```python
# Future: Allow users to configure notification preferences

class NotificationPreferences:
    """User notification preferences"""

    preferences = {
        'email_notifications': True,
        'branch_opening_alerts': True,
        'ppp09_expiry_alerts': True,
        'dc_change_alerts': True,
        'frequency': 'immediate',  # immediate, daily_digest, weekly_digest
    }
```

## Environment Variables

```bash
# Email service configuration
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@retailbranch.com
FROM_NAME=Retail Branch System

# Email notification settings
ENABLE_EMAIL_NOTIFICATIONS=true
NOTIFICATION_TIMEZONE=Asia/Bangkok
```

## Testing Email Templates

### Development Email Testing

```python
# Use Mailtrap or similar service for development
SENDGRID_API_KEY=<mailtrap-api-key>
FROM_EMAIL=test@example.com

# Or disable emails in development
ENABLE_EMAIL_NOTIFICATIONS=false
```

### Email Preview Route (Development Only)

```python
# routes/dev_routes.py

@router.get("/dev/email-preview/{template_name}")
async def preview_email_template(template_name: str):
    """Preview email template in browser (dev only)"""

    if os.getenv('ENVIRONMENT') != 'development':
        raise HTTPException(status_code=404)

    email_service = EmailService()
    template = email_service.template_env.get_template(f"{template_name}.html")

    # Sample context
    context = {
        'branch_id': 'BR001',
        'branch_name': 'สาขาสยาม',
        'estimate_opening_date': '2024-04-30',
        'days_remaining': 30
    }

    html = template.render(**context)
    return HTMLResponse(content=html)
```

## Monitoring & Logging

### Email Delivery Tracking

```python
# Track email delivery status
def track_email_delivery(
    email_id: str,
    recipient: str,
    status: str,
    sent_at: datetime
):
    """Log email delivery to BigQuery"""

    log_data = {
        'email_id': email_id,
        'recipient': recipient,
        'status': status,  # sent, delivered, bounced, failed
        'sent_at': sent_at,
        'delivered_at': datetime.now() if status == 'delivered' else None
    }

    # Insert to BigQuery email_logs table
```

### Failed Email Retry

```python
# Retry failed emails
def retry_failed_emails():
    """Retry emails that failed to send"""

    # Query failed emails from last 24 hours
    # Retry with exponential backoff
    # Max 3 retries
```

## Rate Limiting

**SendGrid Free Tier:**
- 100 emails/day
- Consider upgrading for production

**Email Batching:**
- Group notifications sent to same recipients
- Send daily digest instead of individual emails

## Security Considerations

1. **Email Spoofing Prevention**: Use SPF, DKIM, DMARC records
2. **Sensitive Information**: Don't include passwords or secrets in emails
3. **Unsubscribe Link**: Provide opt-out option (required by law)
4. **Rate Limiting**: Prevent email bombing
5. **Template Injection**: Sanitize all user input in templates

## Alternative: Using Google Cloud Email API

```python
# Alternative implementation using Google Cloud Email
from google.cloud import gmail_v1

# Implementation for Gmail API
# Suitable if already using GCP infrastructure
```

## Related Documentation

- [scheduled-jobs.md](../deployment/scheduled-jobs.md) - Scheduled notification jobs
- [../frontend/javascript.md](../frontend/javascript.md) - Toast notifications
- [../DATABASE.md](../DATABASE.md) - Email logs table (future)
- [../development/api-standards.md](../development/api-standards.md) - API conventions
