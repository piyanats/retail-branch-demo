# Google Cloud Run Deployment

## Prerequisites

- Google Cloud Project
- Service Account with permissions:
  - BigQuery Data Editor
  - BigQuery Job User
  - Storage Object Admin
- Service Account Key JSON

## Environment Variables

```bash
# Google Cloud Platform
PROJECT_ID=your-gcp-project-id
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-key-min-32-chars
```

## Deployment Steps

1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run with service account
4. Configure environment variables
5. Set up IAM permissions

## Manual Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy retail-branch-demo \
  --image gcr.io/PROJECT_ID/retail-branch-demo:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --service-account SERVICE_ACCOUNT_EMAIL \
  --set-env-vars "PROJECT_ID=PROJECT_ID,DATASET_ID=retail_branches,GCS_BUCKET=BUCKET_NAME" \
  --set-secrets "GOOGLE_CLIENT_ID=oauth_client_id:latest,GOOGLE_CLIENT_SECRET=oauth_client_secret:latest"
```

## Related Documentation

- [docker.md](docker.md) - Docker setup
- [cicd.md](cicd.md) - Automated deployment with GitLab CI/CD
