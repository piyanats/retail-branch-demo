# CI/CD Pipeline (GitLab CI)

## .gitlab-ci.yml

```yaml
stages:
  - build
  - deploy-dev
  - deploy-prod

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_NAME: gcr.io/${GCP_PROJECT_ID}/retail-branch-demo

# Build Docker image
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

## Deployment Workflow

1. **Development**: Push to `main` branch → Build → Manual deploy to DEV
2. **Production**: Create tag (e.g., `v1.0.0`) → Build → Manual deploy to PROD

```bash
# Deploy to production
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## Related Documentation

- [docker.md](docker.md) - Docker setup
- [cloud-run.md](cloud-run.md) - Cloud Run deployment
