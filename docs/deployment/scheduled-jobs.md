# Scheduled Jobs

## Overview

ระบบใช้ **Google Cloud Scheduler** ในการจัดการ scheduled jobs ที่ต้องทำงานเป็นประจำ เช่น การตรวจสอบวันหมดอายุเอกสาร, การเปลี่ยน DC อัตโนมัติ, การส่งแจ้งเตือน เป็นต้น

## Architecture

```
┌──────────────────┐
│ Cloud Scheduler  │ → Trigger at scheduled time
└────────┬─────────┘
         │ HTTP POST
         ▼
┌──────────────────┐
│   Cloud Run      │ → Execute job handler
│   (Web App)      │
└────────┬─────────┘
         │
         ├──────────→ BigQuery (query data)
         ├──────────→ Send Notifications (email)
         └──────────→ Update Records (auto-change)
```

## Scheduled Jobs List

| Job Name | Schedule | Description | Teams Affected |
|----------|----------|-------------|----------------|
| **dc-auto-change** | Daily at 00:00 | ทำการเปลี่ยน DC อัตโนมัติสำหรับ scheduled changes | SCM |
| **branch-opening-alerts** | Daily at 08:00 | ตรวจสอบและส่งแจ้งเตือนสาขาที่ใกล้เปิด (30, 7 วัน) | New Branch, Legal, SRD, SCM |
| **ppp09-expiry-alerts** | Daily at 08:00 | ตรวจสอบและส่งแจ้งเตือน ภ.พ.09 ที่ใกล้หมดอายุ (60, 30 วัน) หรือหมดอายุแล้ว | Legal |
| **ppp20-tax-reminders** | Daily at 08:00 | ส่ง reminder สำหรับการยื่นภาษี ภ.พ.20 (10 วันก่อนถึงกำหนด) | Legal |
| **overdue-branch-check** | Daily at 09:00 | ตรวจสอบสาขาที่เลยวันเปิดแล้วแต่ยังไม่เปิด | New Branch |
| **cleanup-old-sessions** | Daily at 02:00 | ลบ session cookies ที่หมดอายุ | System |
| **data-backup** | Daily at 03:00 | Backup ข้อมูลสำคัญจาก BigQuery ไป GCS | System |

## Timezone Configuration

**ทุก scheduled jobs ใช้ timezone:**
```
Asia/Bangkok (UTC+7)
```

**ตัวอย่าง:**
- `Daily at 00:00` = เที่ยงคืนตามเวลาประเทศไทย
- `Daily at 08:00` = 8:00 น. ตามเวลาประเทศไทย

## Job Implementations

### 1. DC Auto-Change Job

**Schedule:** Daily at 00:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/dc-auto-change`

**Description:**
ตรวจสอบ `dc_changes` table และทำการเปลี่ยน DC อัตโนมัติสำหรับ records ที่มี `effective_date = today` และ `status = 'scheduled'`

**Logic:**
```python
# routes/job_routes.py

from datetime import date, datetime
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/api/jobs", tags=["Scheduled Jobs"])

@router.post("/dc-auto-change")
async def dc_auto_change_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ทำการเปลี่ยน DC อัตโนมัติสำหรับ scheduled changes ที่ถึงวันนี้

    SECURITY: ควรตรวจสอบ header จาก Cloud Scheduler
    """
    # Verify request is from Cloud Scheduler
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    today = date.today()

    # Query scheduled DC changes for today
    query = f"""
        SELECT
            dc.dc_change_id,
            dc.branch_id,
            dc.current_dc,
            dc.new_dc,
            dc.reason
        FROM retail_branches.dc_changes dc
        WHERE dc.effective_date = '{today}'
          AND dc.status = 'scheduled'
    """

    results = bigquery_service.query(query)

    success_count = 0
    failed_count = 0

    for row in results:
        try:
            # Update branch DC
            update_query = f"""
                UPDATE retail_branches.branches
                SET dc_code = '{row['new_dc']}',
                    updated_at = CURRENT_TIMESTAMP(),
                    updated_by = 'system-auto-change'
                WHERE branch_id = '{row['branch_id']}'
            """
            bigquery_service.execute(update_query)

            # Mark DC change as completed
            complete_query = f"""
                UPDATE retail_branches.dc_changes
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP()
                WHERE dc_change_id = '{row['dc_change_id']}'
            """
            bigquery_service.execute(complete_query)

            # Send notification to SCM team
            email_service.send_dc_change_completed(
                branch_id=row['branch_id'],
                old_dc=row['current_dc'],
                new_dc=row['new_dc']
            )

            success_count += 1

        except Exception as e:
            # Log error
            print(f"Failed to change DC for branch {row['branch_id']}: {str(e)}")

            # Mark as failed
            fail_query = f"""
                UPDATE retail_branches.dc_changes
                SET status = 'failed',
                    error_message = '{str(e)}'
                WHERE dc_change_id = '{row['dc_change_id']}'
            """
            bigquery_service.execute(fail_query)

            failed_count += 1

    return {
        "success": True,
        "message": f"DC auto-change completed",
        "date": today.isoformat(),
        "success_count": success_count,
        "failed_count": failed_count
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http dc-auto-change \
  --schedule="0 0 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/dc-auto-change" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 2. Branch Opening Alerts Job

**Schedule:** Daily at 08:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/branch-opening-alerts`

**Description:**
ตรวจสอบสาขาที่จะเปิดใน 30 วัน และ 7 วัน และส่ง email แจ้งเตือน

**Logic:**
```python
@router.post("/branch-opening-alerts")
async def branch_opening_alerts_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ตรวจสอบและส่งแจ้งเตือนสาขาที่ใกล้เปิด (30, 7 วัน)
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    from datetime import timedelta

    today = date.today()
    date_30_days = today + timedelta(days=30)
    date_7_days = today + timedelta(days=7)

    # Query branches opening in 30 days
    query_30 = f"""
        SELECT
            branch_id,
            branch_name,
            estimate_opening_date
        FROM retail_branches.branches
        WHERE estimate_opening_date = '{date_30_days}'
          AND status = 'opening'
          AND actual_opening_date IS NULL
    """

    results_30 = bigquery_service.query(query_30)

    for row in results_30:
        email_service.send_branch_opening_alert(
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            estimate_opening_date=row['estimate_opening_date'],
            days_remaining=30
        )

    # Query branches opening in 7 days
    query_7 = f"""
        SELECT
            branch_id,
            branch_name,
            estimate_opening_date
        FROM retail_branches.branches
        WHERE estimate_opening_date = '{date_7_days}'
          AND status = 'opening'
          AND actual_opening_date IS NULL
    """

    results_7 = bigquery_service.query(query_7)

    for row in results_7:
        email_service.send_branch_opening_alert(
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            estimate_opening_date=row['estimate_opening_date'],
            days_remaining=7
        )

    return {
        "success": True,
        "message": "Branch opening alerts sent",
        "date": today.isoformat(),
        "alerts_30_days": len(results_30),
        "alerts_7_days": len(results_7)
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http branch-opening-alerts \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/branch-opening-alerts" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 3. ภ.พ.09 Expiry Alerts Job

**Schedule:** Daily at 08:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/ppp09-expiry-alerts`

**Description:**
ตรวจสอบ ภ.พ.09 ที่จะหมดอายุใน 60, 30 วัน หรือหมดอายุแล้ว และส่ง email แจ้งเตือนทีมกฎหมาย

**Logic:**
```python
@router.post("/ppp09-expiry-alerts")
async def ppp09_expiry_alerts_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ตรวจสอบและส่งแจ้งเตือน ภ.พ.09 ที่ใกล้หมดอายุ
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    from datetime import timedelta

    today = date.today()
    date_60_days = today + timedelta(days=60)
    date_30_days = today + timedelta(days=30)

    # Query ภ.พ.09 expiring in 60 days
    query_60 = f"""
        SELECT
            p.ppp09_id,
            p.branch_id,
            b.branch_name,
            p.ppp09_number,
            p.expiry_date
        FROM retail_branches.legal_ppp09 p
        JOIN retail_branches.branches b ON p.branch_id = b.branch_id
        WHERE p.expiry_date = '{date_60_days}'
    """

    results_60 = bigquery_service.query(query_60)

    for row in results_60:
        email_service.send_ppp09_expiring_alert(
            ppp09_id=row['ppp09_id'],
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            expiry_date=row['expiry_date'],
            days_remaining=60
        )

    # Query ภ.พ.09 expiring in 30 days
    query_30 = f"""
        SELECT
            p.ppp09_id,
            p.branch_id,
            b.branch_name,
            p.ppp09_number,
            p.expiry_date
        FROM retail_branches.legal_ppp09 p
        JOIN retail_branches.branches b ON p.branch_id = b.branch_id
        WHERE p.expiry_date = '{date_30_days}'
    """

    results_30 = bigquery_service.query(query_30)

    for row in results_30:
        email_service.send_ppp09_expiring_alert(
            ppp09_id=row['ppp09_id'],
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            expiry_date=row['expiry_date'],
            days_remaining=30
        )

    # Query expired ภ.พ.09 (day after expiry)
    yesterday = today - timedelta(days=1)
    query_expired = f"""
        SELECT
            p.ppp09_id,
            p.branch_id,
            b.branch_name,
            p.ppp09_number,
            p.expiry_date
        FROM retail_branches.legal_ppp09 p
        JOIN retail_branches.branches b ON p.branch_id = b.branch_id
        WHERE p.expiry_date = '{yesterday}'
    """

    results_expired = bigquery_service.query(query_expired)

    for row in results_expired:
        email_service.send_ppp09_expired_alert(
            ppp09_id=row['ppp09_id'],
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            expiry_date=row['expiry_date']
        )

    return {
        "success": True,
        "message": "ภ.พ.09 expiry alerts sent",
        "date": today.isoformat(),
        "alerts_60_days": len(results_60),
        "alerts_30_days": len(results_30),
        "alerts_expired": len(results_expired)
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http ppp09-expiry-alerts \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/ppp09-expiry-alerts" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 4. ภ.พ.20 Tax Filing Reminders Job

**Schedule:** Daily at 08:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/ppp20-tax-reminders`

**Description:**
ส่ง reminder สำหรับการยื่นภาษี ภ.พ.20 ล่วงหน้า 10 วันก่อนถึงกำหนด

**Logic:**
```python
@router.post("/ppp20-tax-reminders")
async def ppp20_tax_reminders_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ส่ง reminder สำหรับการยื่นภาษี ภ.พ.20
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    from datetime import timedelta

    today = date.today()
    date_10_days = today + timedelta(days=10)

    # Query ภ.พ.20 with filing deadline in 10 days
    query = f"""
        SELECT
            p.ppp20_id,
            p.branch_id,
            b.branch_name,
            p.filing_deadline,
            p.tax_year
        FROM retail_branches.legal_ppp20 p
        JOIN retail_branches.branches b ON p.branch_id = b.branch_id
        WHERE p.filing_deadline = '{date_10_days}'
          AND p.filing_status = 'pending'
    """

    results = bigquery_service.query(query)

    for row in results:
        email_service.send_ppp20_filing_reminder(
            ppp20_id=row['ppp20_id'],
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            filing_deadline=row['filing_deadline'],
            tax_year=row['tax_year']
        )

    return {
        "success": True,
        "message": "ภ.พ.20 tax filing reminders sent",
        "date": today.isoformat(),
        "reminders_sent": len(results)
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http ppp20-tax-reminders \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/ppp20-tax-reminders" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 5. Overdue Branch Check Job

**Schedule:** Daily at 09:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/overdue-branch-check`

**Description:**
ตรวจสอบสาขาที่เลย estimate_opening_date แล้วแต่ยังไม่ได้เปิด (actual_opening_date IS NULL)

**Logic:**
```python
@router.post("/overdue-branch-check")
async def overdue_branch_check_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ตรวจสอบสาขาที่เลยวันเปิดแล้วแต่ยังไม่เปิด
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    today = date.today()

    # Query branches that are overdue
    query = f"""
        SELECT
            branch_id,
            branch_name,
            estimate_opening_date,
            DATE_DIFF('{today}', estimate_opening_date, DAY) as days_overdue
        FROM retail_branches.branches
        WHERE estimate_opening_date < '{today}'
          AND actual_opening_date IS NULL
          AND status = 'opening'
    """

    results = bigquery_service.query(query)

    for row in results:
        # Send alert to New Branch Team managers
        email_service.send_branch_overdue_alert(
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            estimate_opening_date=row['estimate_opening_date'],
            days_overdue=row['days_overdue']
        )

    return {
        "success": True,
        "message": "Overdue branch checks completed",
        "date": today.isoformat(),
        "overdue_branches": len(results)
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http overdue-branch-check \
  --schedule="0 9 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/overdue-branch-check" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 6. Cleanup Old Sessions Job

**Schedule:** Daily at 02:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/cleanup-sessions`

**Description:**
ลบ session data ที่หมดอายุแล้ว (> 24 ชั่วโมง)

**Logic:**
```python
@router.post("/cleanup-sessions")
async def cleanup_sessions_job(
    x_cloudscheduler: str = Header(None)
):
    """
    ลบ session cookies ที่หมดอายุ

    Note: ถ้าใช้ signed cookies อย่างเดียว ไม่จำเป็นต้องลบ
    แต่ถ้ามี session store (Redis/Memcache) ก็ควรลบ expired sessions
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Implementation depends on session storage mechanism
    # Example: Clear expired sessions from Redis

    return {
        "success": True,
        "message": "Session cleanup completed"
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http cleanup-sessions \
  --schedule="0 2 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/cleanup-sessions" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

### 7. Data Backup Job

**Schedule:** Daily at 03:00 Asia/Bangkok
**Endpoint:** `POST /api/jobs/data-backup`

**Description:**
Export ข้อมูลสำคัญจาก BigQuery ไปยัง GCS เป็น backup

**Logic:**
```python
@router.post("/data-backup")
async def data_backup_job(
    x_cloudscheduler: str = Header(None)
):
    """
    Backup ข้อมูลสำคัญจาก BigQuery ไป GCS
    """
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    from datetime import datetime

    today = datetime.now().strftime("%Y%m%d")

    # Tables to backup
    tables = [
        "branches",
        "legal_ppp09",
        "legal_ppp20",
        "dc_changes",
        "users",
        "user_teams"
    ]

    backup_count = 0

    for table in tables:
        try:
            # Export table to GCS
            destination_uri = f"gs://retail-branch-backups/daily/{today}/{table}.json"

            bigquery_service.export_table_to_gcs(
                table_id=f"retail_branches.{table}",
                destination_uri=destination_uri,
                format="NEWLINE_DELIMITED_JSON"
            )

            backup_count += 1

        except Exception as e:
            print(f"Failed to backup table {table}: {str(e)}")

    return {
        "success": True,
        "message": "Data backup completed",
        "date": today,
        "tables_backed_up": backup_count
    }
```

**Cloud Scheduler Configuration:**
```bash
gcloud scheduler jobs create http data-backup \
  --schedule="0 3 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="https://your-app.run.app/api/jobs/data-backup" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://your-app.run.app"
```

## Security

### Authentication for Scheduled Jobs

**OIDC Token Authentication (Recommended):**
- Cloud Scheduler ใช้ OIDC token สำหรับ authentication
- Cloud Run ตรวจสอบ token โดยอัตโนมัติ
- ตั้งค่า `--oidc-service-account-email` เมื่อสร้าง scheduler job

**Header Verification:**
```python
@router.post("/api/jobs/{job_name}")
async def scheduled_job(
    x_cloudscheduler: str = Header(None)
):
    # Verify request comes from Cloud Scheduler
    if not x_cloudscheduler:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Execute job logic
    pass
```

**IP Whitelisting (Optional):**
- จำกัดการเข้าถึง `/api/jobs/*` endpoints จาก Cloud Scheduler IPs เท่านั้น
- [Google Cloud Scheduler IP ranges](https://cloud.google.com/scheduler/docs/reference/rest)

## Retry Configuration

**Cloud Scheduler Retry Settings:**
```bash
gcloud scheduler jobs create http job-name \
  --schedule="..." \
  --uri="..." \
  --max-retry-attempts=3 \
  --max-retry-duration=3600s \
  --min-backoff-duration=10s \
  --max-backoff-duration=300s
```

**Retry Parameters:**
- `max-retry-attempts`: จำนวนครั้งที่ retry สูงสุด (default: 0)
- `max-retry-duration`: เวลาที่ใช้ retry ทั้งหมด (default: 0)
- `min-backoff-duration`: เวลา backoff ต่ำสุด (default: 5s)
- `max-backoff-duration`: เวลา backoff สูงสุด (default: 1h)

**Exponential Backoff:**
- Retry ครั้งที่ 1: รอ 10 วินาที
- Retry ครั้งที่ 2: รอ 20 วินาที
- Retry ครั้งที่ 3: รอ 40 วินาที

## Error Handling

**Job Error Handling Pattern:**
```python
@router.post("/api/jobs/{job_name}")
async def scheduled_job(x_cloudscheduler: str = Header(None)):
    try:
        # Execute job logic
        results = execute_job()

        # Log success
        log_job_execution(
            job_name="job-name",
            status="success",
            results=results
        )

        return {
            "success": True,
            "message": "Job completed",
            "results": results
        }

    except Exception as e:
        # Log error
        log_job_execution(
            job_name="job-name",
            status="failed",
            error=str(e)
        )

        # Send alert to admins
        send_job_failure_alert(
            job_name="job-name",
            error=str(e)
        )

        # Return error response (will trigger retry)
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {str(e)}"
        )
```

**Logging Job Execution:**
```python
def log_job_execution(
    job_name: str,
    status: str,
    results: dict = None,
    error: str = None
):
    """Log scheduled job execution to BigQuery"""

    log_data = {
        'job_name': job_name,
        'executed_at': datetime.now().isoformat(),
        'status': status,
        'results': json.dumps(results) if results else None,
        'error_message': error
    }

    bigquery_service.insert_rows(
        table_id="retail_branches.job_execution_logs",
        rows=[log_data]
    )
```

## Monitoring & Alerting

### Cloud Monitoring

**Metrics to Monitor:**
- Job execution success rate
- Job execution duration
- Error count
- Retry count

**Create Alerts:**
```bash
# Alert when job fails 3 times in a row
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Scheduled Job Failures" \
  --condition-display-name="Job failed 3 times" \
  --condition-threshold-value=3 \
  --condition-threshold-duration=600s
```

### Job Execution Logs Table

```sql
CREATE TABLE retail_branches.job_execution_logs (
  log_id STRING NOT NULL,              -- รหัสบันทึก (UUID)
  job_name STRING NOT NULL,            -- ชื่อ job
  executed_at TIMESTAMP NOT NULL,      -- เวลาที่ทำงาน
  status STRING NOT NULL,              -- success, failed
  duration_seconds FLOAT64,            -- เวลาที่ใช้ (วินาที)
  results STRING,                      -- ผลลัพธ์ (JSON)
  error_message STRING,                -- ข้อความ error (ถ้ามี)
  retry_count INT64                    -- จำนวนครั้งที่ retry
);
```

### Job Status Dashboard

สร้างหน้า Admin Dashboard สำหรับดู job execution history:

**GET `/admin/jobs`** - แสดงสถานะ scheduled jobs ทั้งหมด

**Features:**
- รายการ jobs ทั้งหมด
- Last execution time
- Success/Failure status
- Error messages (ถ้ามี)
- Manual trigger button (for admins)

## Manual Job Triggers

**Admin Page สำหรับ Manual Trigger:**
```html
<!-- app/templates/admin/jobs.html -->

<div class="jobs-list">
  <h2>Scheduled Jobs</h2>

  <div class="job-card">
    <h3>DC Auto-Change</h3>
    <p>Schedule: Daily at 00:00</p>
    <p>Last Run: 2024-03-15 00:00:05 (Success)</p>
    <button onclick="triggerJob('dc-auto-change')">Run Now</button>
  </div>

  <div class="job-card">
    <h3>Branch Opening Alerts</h3>
    <p>Schedule: Daily at 08:00</p>
    <p>Last Run: 2024-03-15 08:00:12 (Success)</p>
    <button onclick="triggerJob('branch-opening-alerts')">Run Now</button>
  </div>
</div>

<script>
async function triggerJob(jobName) {
  if (!confirm(`Are you sure you want to run ${jobName}?`)) return;

  try {
    const response = await API.post(`/api/jobs/${jobName}`, {});
    Toast.show(`Job ${jobName} completed successfully`, 'success');
  } catch (error) {
    Toast.show(`Job ${jobName} failed: ${error.message}`, 'error');
  }
}
</script>
```

**API Endpoint for Manual Trigger:**
```python
@router.post("/api/admin/trigger-job/{job_name}")
async def trigger_job_manually(
    job_name: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Manual trigger สำหรับ scheduled jobs (Admin only)
    """
    # Execute job based on job_name
    if job_name == "dc-auto-change":
        result = await dc_auto_change_job(x_cloudscheduler="manual-trigger")
    elif job_name == "branch-opening-alerts":
        result = await branch_opening_alerts_job(x_cloudscheduler="manual-trigger")
    # ... other jobs
    else:
        raise HTTPException(status_code=404, detail="Job not found")

    # Log manual trigger
    log_job_execution(
        job_name=job_name,
        status="success",
        results={"triggered_by": current_user['email'], "trigger_type": "manual"}
    )

    return result
```

## Deployment

### Create All Scheduler Jobs

**Script: `scripts/create_schedulers.sh`**
```bash
#!/bin/bash

PROJECT_ID="your-project-id"
REGION="asia-southeast1"
APP_URL="https://your-app.run.app"
SERVICE_ACCOUNT="scheduler@${PROJECT_ID}.iam.gserviceaccount.com"

# DC Auto-Change (Daily at 00:00)
gcloud scheduler jobs create http dc-auto-change \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 0 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/dc-auto-change" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# Branch Opening Alerts (Daily at 08:00)
gcloud scheduler jobs create http branch-opening-alerts \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/branch-opening-alerts" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# ภ.พ.09 Expiry Alerts (Daily at 08:00)
gcloud scheduler jobs create http ppp09-expiry-alerts \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/ppp09-expiry-alerts" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# ภ.พ.20 Tax Reminders (Daily at 08:00)
gcloud scheduler jobs create http ppp20-tax-reminders \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 8 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/ppp20-tax-reminders" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# Overdue Branch Check (Daily at 09:00)
gcloud scheduler jobs create http overdue-branch-check \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 9 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/overdue-branch-check" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# Cleanup Sessions (Daily at 02:00)
gcloud scheduler jobs create http cleanup-sessions \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 2 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/cleanup-sessions" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

# Data Backup (Daily at 03:00)
gcloud scheduler jobs create http data-backup \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 3 * * *" \
  --time-zone="Asia/Bangkok" \
  --uri="${APP_URL}/api/jobs/data-backup" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --oidc-token-audience="${APP_URL}" \
  --max-retry-attempts=3

echo "All scheduler jobs created successfully!"
```

**Make script executable:**
```bash
chmod +x scripts/create_schedulers.sh
./scripts/create_schedulers.sh
```

### Service Account Permissions

**Service Account ที่ใช้ต้องมี permissions:**
- `roles/run.invoker` - เรียก Cloud Run service
- `roles/cloudscheduler.admin` - จัดการ Cloud Scheduler jobs

```bash
# Grant permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:scheduler@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

## Testing Scheduled Jobs

### Local Testing

**Run job endpoint locally:**
```bash
# Test DC auto-change job
curl -X POST http://localhost:8000/api/jobs/dc-auto-change \
  -H "x-cloudscheduler: test"

# Test branch opening alerts
curl -X POST http://localhost:8000/api/jobs/branch-opening-alerts \
  -H "x-cloudscheduler: test"
```

### Cloud Testing

**Trigger job manually via gcloud:**
```bash
gcloud scheduler jobs run dc-auto-change \
  --project=${PROJECT_ID} \
  --location=asia-southeast1
```

**View job logs:**
```bash
gcloud scheduler jobs describe dc-auto-change \
  --project=${PROJECT_ID} \
  --location=asia-southeast1
```

## Troubleshooting

### Common Issues

**Issue 1: Job not executing**
- ตรวจสอบ Cloud Scheduler job status
- ตรวจสอบ service account permissions
- ตรวจสอบ Cloud Run service URL

**Issue 2: Job fails with 403 Forbidden**
- ตรวจสอบ OIDC token configuration
- ตรวจสอบ service account มี role `run.invoker`

**Issue 3: Job times out**
- เพิ่ม timeout ใน Cloud Run service
- ตรวจสอบ BigQuery query performance
- พิจารณาแบ่ง job เป็น smaller batches

**Issue 4: Duplicate executions**
- ตรวจสอบ idempotency ของ job logic
- ใช้ unique transaction IDs
- ตรวจสอบ retry configuration

## Best Practices

1. **Idempotency**: Jobs ต้อง idempotent (รันหลายครั้งได้ผลเหมือนกัน)
2. **Error Handling**: จัดการ errors อย่างเหมาะสม พร้อม retry logic
3. **Logging**: Log ทุก job execution สำหรับการ debug
4. **Monitoring**: ตั้ง alerts สำหรับ job failures
5. **Timeout**: กำหนด timeout ที่เหมาะสม
6. **Batch Processing**: แบ่ง large datasets เป็น batches
7. **Testing**: ทดสอบ jobs ก่อน deploy to production
8. **Documentation**: เขียนเอกสารชัดเจนสำหรับแต่ละ job

## Related Documentation

- [notifications.md](../features/notifications.md) - Email notification service
- [cicd.md](./cicd.md) - CI/CD pipeline configuration
- [api-standards.md](../development/api-standards.md) - API conventions
- [DATABASE.md](../DATABASE.md) - Database schema
