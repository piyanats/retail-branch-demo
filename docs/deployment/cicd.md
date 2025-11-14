# CI/CD Pipeline (GitLab CI)

## Overview

CI/CD Pipeline ประกอบด้วย 3 stages:
1. **Build**: Build Docker image และ push ไปยัง Google Container Registry
2. **Deploy to DEV**: Deploy ไปยัง Development environment (manual trigger)
3. **Deploy to PROD**: Deploy ไปยัง Production environment (manual trigger on tags only)

## Complete .gitlab-ci.yml

```yaml
stages:
  - build
  - deploy-dev
  - deploy-prod

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_NAME: gcr.io/${GCP_PROJECT_ID}/retail-branch-demo

# ============================================
# Build Stage
# ============================================
build:
  stage: build
  image: google/cloud-sdk:alpine
  services:
    - docker:dind
  before_script:
    - echo $GCP_SERVICE_KEY | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud auth configure-docker
  script:
    - docker build -t ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} .
    - docker tag ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} ${IMAGE_NAME}:latest
    - docker push ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA}
    - docker push ${IMAGE_NAME}:latest
  only:
    - main
    - tags

# ============================================
# Deploy to Development
# ============================================
deploy-dev:
  stage: deploy-dev
  image: google/cloud-sdk:alpine
  before_script:
    - echo $GCP_SERVICE_KEY_DEV | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID_DEV
  script:
    - |
      gcloud run deploy retail-branch-demo \
        --image ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} \
        --platform managed \
        --region asia-southeast1 \
        --allow-unauthenticated \
        --service-account ${SERVICE_ACCOUNT_DEV} \
        --max-instances 10 \
        --memory 512Mi \
        --cpu 1 \
        --timeout 300 \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_DEV},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_DEV},ENVIRONMENT=development" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest"
    - echo "Deployment URL:"
    - gcloud run services describe retail-branch-demo --platform managed --region asia-southeast1 --format 'value(status.url)'
  when: manual
  only:
    - main
  environment:
    name: development
    url: https://retail-branch-demo-dev-xxxxxxxxxx-as.a.run.app

# ============================================
# Deploy to Production
# ============================================
deploy-prod:
  stage: deploy-prod
  image: google/cloud-sdk:alpine
  before_script:
    - echo $GCP_SERVICE_KEY_PROD | base64 -d > ${HOME}/gcp-key.json
    - gcloud auth activate-service-account --key-file ${HOME}/gcp-key.json
    - gcloud config set project $GCP_PROJECT_ID_PROD
  script:
    - |
      gcloud run deploy retail-branch-demo \
        --image ${IMAGE_NAME}:${CI_COMMIT_SHORT_SHA} \
        --platform managed \
        --region asia-southeast1 \
        --allow-unauthenticated \
        --service-account ${SERVICE_ACCOUNT_PROD} \
        --max-instances 50 \
        --min-instances 1 \
        --memory 1Gi \
        --cpu 2 \
        --timeout 300 \
        --set-env-vars "PROJECT_ID=${GCP_PROJECT_ID_PROD},DATASET_ID=retail_branches,GCS_BUCKET=${GCS_BUCKET_PROD},ENVIRONMENT=production" \
        --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest,SESSION_SECRET=session_secret:latest"
    - echo "Production Deployment URL:"
    - gcloud run services describe retail-branch-demo --platform managed --region asia-southeast1 --format 'value(status.url)'
  when: manual
  only:
    - tags
  environment:
    name: production
    url: https://retail-branch-demo-xxxxxxxxxx-as.a.run.app
```

## GitLab CI/CD Variables

ตั้งค่า variables ใน GitLab Project Settings > CI/CD > Variables:

**General:**
- `GCP_PROJECT_ID`: Google Cloud Project ID
- `GCP_SERVICE_KEY`: Service Account Key (base64 encoded)

**Development:**
- `GCP_PROJECT_ID_DEV`: GCP Project ID สำหรับ dev
- `GCP_SERVICE_KEY_DEV`: Service Account Key (base64) สำหรับ dev
- `SERVICE_ACCOUNT_DEV`: Service Account email สำหรับ Cloud Run dev
- `GCS_BUCKET_DEV`: GCS Bucket สำหรับ dev

**Production:**
- `GCP_PROJECT_ID_PROD`: GCP Project ID สำหรับ prod
- `GCP_SERVICE_KEY_PROD`: Service Account Key (base64) สำหรับ prod
- `SERVICE_ACCOUNT_PROD`: Service Account email สำหรับ Cloud Run prod
- `GCS_BUCKET_PROD`: GCS Bucket สำหรับ prod

## Cloud Run Configuration

### Development Environment

| Setting | Value |
|---------|-------|
| Region | asia-southeast1 |
| Memory | 512Mi |
| CPU | 1 vCPU |
| Max Instances | 10 |
| Min Instances | 0 (scale to zero) |
| Timeout | 300s (5 minutes) |
| Concurrency | 80 requests |

### Production Environment

| Setting | Value |
|---------|-------|
| Region | asia-southeast1 |
| Memory | 1Gi |
| CPU | 2 vCPU |
| Max Instances | 50 |
| Min Instances | 1 (always running) |
| Timeout | 300s (5 minutes) |
| Concurrency | 80 requests |

## Secrets Management

**Secrets จัดเก็บใน Google Secret Manager**

### Required Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `oauth_client_id` | Google OAuth Client ID | `xxx.apps.googleusercontent.com` |
| `oauth_client_secret` | Google OAuth Client Secret | `GOCSPX-xxx` |
| `session_secret` | Session encryption key | Random 32+ characters |

### Creating Secrets

```bash
# Create secret in Google Secret Manager
echo -n "your-secret-value" | \
  gcloud secrets create oauth_client_id \
    --data-file=- \
    --replication-policy="automatic"

# Add secret version
echo -n "new-secret-value" | \
  gcloud secrets versions add oauth_client_id \
    --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding oauth_client_id \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Updating Secrets

1. Add new secret version (ข้างบนเป็น `:latest`)
2. Cloud Run จะใช้ version ใหม่ใน deployment ถัดไป
3. ไม่ต้อง rebuild Docker image

## Deployment Workflow

### Development Deployment

**Trigger:** Push to `main` branch

```bash
git checkout main
git add .
git commit -m "Feature: Add new functionality"
git push origin main
```

**Pipeline Steps:**
1. GitLab CI ทำการ build Docker image
2. Push image ไปยัง GCR พร้อม tag `${CI_COMMIT_SHORT_SHA}` และ `latest`
3. Manual trigger: คลิก "Deploy to DEV" ใน GitLab CI/CD
4. Cloud Run deploy image ไปยัง DEV environment
5. ตรวจสอบ deployment ที่ DEV URL

### Production Deployment

**Trigger:** Create and push git tag

```bash
# Create tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
git push origin v1.0.0

# หรือ push tag ที่มีอยู่แล้ว
git push origin --tags
```

**Pipeline Steps:**
1. GitLab CI ทำการ build Docker image จาก tag
2. Push image ไปยัง GCR พร้อม tag `${CI_COMMIT_SHORT_SHA}` และ `latest`
3. Manual trigger: คลิก "Deploy to PROD" ใน GitLab CI/CD
4. Cloud Run deploy image ไปยัง PROD environment
5. ตรวจสอบ deployment ที่ PROD URL
6. Monitor logs และ metrics

**Tag Naming Convention:**
- Format: `vMAJOR.MINOR.PATCH`
- Example: `v1.0.0`, `v1.2.3`, `v2.0.0`
- Semantic Versioning: [semver.org](https://semver.org/)

## Rollback Procedure

### Option 1: Deploy Previous Revision (Fastest)

```bash
# List revisions
gcloud run revisions list \
  --service retail-branch-demo \
  --region asia-southeast1

# Rollback to specific revision
gcloud run services update-traffic retail-branch-demo \
  --region asia-southeast1 \
  --to-revisions REVISION_NAME=100
```

**Time:** ~1-2 minutes

### Option 2: Deploy Previous Image Tag

```bash
# Find previous image
gcloud container images list-tags gcr.io/${GCP_PROJECT_ID}/retail-branch-demo

# Deploy specific image
gcloud run deploy retail-branch-demo \
  --image gcr.io/${GCP_PROJECT_ID}/retail-branch-demo:PREVIOUS_COMMIT_SHA \
  --region asia-southeast1 \
  --platform managed
```

**Time:** ~3-5 minutes

### Option 3: Revert Git Commit & Redeploy

```bash
# Find commit to revert
git log --oneline

# Create revert commit
git revert COMMIT_SHA

# Push and trigger pipeline
git push origin main

# Manual deploy via GitLab CI
```

**Time:** ~5-10 minutes (includes build)

### Emergency Rollback Script

```bash
#!/bin/bash
# rollback.sh

SERVICE_NAME="retail-branch-demo"
REGION="asia-southeast1"

echo "Fetching current revisions..."
REVISIONS=$(gcloud run revisions list \
  --service $SERVICE_NAME \
  --region $REGION \
  --format="value(metadata.name)" \
  --limit=5)

echo "Available revisions:"
echo "$REVISIONS" | nl

read -p "Enter revision number to rollback to: " REV_NUM
REVISION=$(echo "$REVISIONS" | sed -n "${REV_NUM}p")

echo "Rolling back to: $REVISION"
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-revisions $REVISION=100

echo "Rollback complete!"
```

## Monitoring & Logging

### Cloud Run Logs

```bash
# View logs
gcloud run services logs read retail-branch-demo \
  --region asia-southeast1 \
  --limit 100

# Follow logs (tail)
gcloud run services logs tail retail-branch-demo \
  --region asia-southeast1

# Filter logs
gcloud run services logs read retail-branch-demo \
  --region asia-southeast1 \
  --filter='severity>=ERROR'
```

### Deployment Status

```bash
# Check service status
gcloud run services describe retail-branch-demo \
  --region asia-southeast1

# Check revision status
gcloud run revisions describe REVISION_NAME \
  --region asia-southeast1

# Check traffic split
gcloud run services describe retail-branch-demo \
  --region asia-southeast1 \
  --format='value(status.traffic)'
```

### Health Check

**Endpoint:** `GET /health` or `GET /`

```bash
# Check if service is healthy
curl https://retail-branch-demo-xxx.run.app/health

# Expected response
{"status":"healthy","timestamp":"2024-03-25T10:30:00Z"}
```

## Troubleshooting

### Deployment Failed

**Error: Permission denied**
```
ERROR: (gcloud.run.deploy) Permission denied
```

**Solution:**
- ตรวจสอบ Service Account มี roles: `roles/run.admin`, `roles/iam.serviceAccountUser`
- ตรวจสอบ Secret Manager IAM permissions

**Error: Image not found**
```
ERROR: Image 'gcr.io/project/image:tag' not found
```

**Solution:**
- ตรวจสอบว่า build stage สำเร็จ
- ตรวจสอบ IMAGE_NAME ใน .gitlab-ci.yml
- ตรวจสอบ GCR permissions

### Service Not Starting

**Check logs:**
```bash
gcloud run services logs read retail-branch-demo \
  --region asia-southeast1 \
  --limit 50
```

**Common Issues:**
1. **Missing environment variables** - ตรวจสอบ `--set-env-vars`
2. **Secret not accessible** - ตรวจสอบ Secret Manager IAM
3. **Port mismatch** - Cloud Run expects port 8080 (default)
4. **Out of memory** - เพิ่ม memory limit

### High Latency

**Solutions:**
1. เพิ่ม min-instances (reduce cold starts)
2. เพิ่ม CPU/memory
3. Check database query performance
4. Enable caching

## CI/CD Best Practices

### 1. Always Test in DEV First
- Deploy to DEV ก่อนเสมอ
- ทดสอบ functionality ครบถ้วน
- ตรวจสอบ logs ไม่มี errors

### 2. Use Semantic Versioning
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### 3. Write Clear Commit Messages
```bash
# Good
git commit -m "feat: Add PPP09 document upload feature"
git commit -m "fix: Fix pagination bug in user list"
git commit -m "docs: Update API documentation"

# Bad
git commit -m "update"
git commit -m "fix bug"
```

### 4. Tag Release Commits
```bash
git tag -a v1.2.0 -m "Release v1.2.0

New features:
- PPP09 document upload
- Audit log export

Bug fixes:
- Fix user pagination
- Fix session timeout"
```

### 5. Keep Secrets Secure
- **Never** commit secrets to git
- Use Secret Manager
- Rotate secrets regularly
- Use different secrets for DEV/PROD

### 6. Monitor Deployments
- Check logs after deployment
- Monitor error rates
- Set up alerts for critical errors
- Have rollback plan ready

## Related Documentation

- [docker.md](docker.md) - Docker setup
- [cloud-run.md](cloud-run.md) - Cloud Run deployment
- [../development/setup.md](../development/setup.md) - Local development
