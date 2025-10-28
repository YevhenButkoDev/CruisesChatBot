# GitHub Actions Deployment Guide

## Overview
This guide explains how to set up automated deployment to Google Cloud Run using GitHub Actions.

## Prerequisites
- GitHub repository
- Google Cloud Project: `cruises-api-yevhen-dev`
- Service account with proper permissions

## Setup Steps

### 1. Create Service Account Key for GitHub Actions

```bash
# Create a new service account key for GitHub Actions
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com \
    --project=cruises-api-yevhen-dev
```

### 2. Set up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following **Repository Secret**:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_SA_KEY` | Contents of `github-actions-key.json` | Service account key for authentication |

**To get the key content:**
```bash
cat github-actions-key.json
```
Copy the entire JSON content and paste it as the secret value.

### 3. Verify Service Account Permissions

Your service account should have these roles:
```bash
# Check current permissions
gcloud projects get-iam-policy cruises-api-yevhen-dev \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com"

# Required roles:
# - roles/datastore.user (Firestore)
# - roles/storage.objectViewer (Cloud Storage)
# - roles/secretmanager.secretAccessor (Secret Manager)
# - roles/run.admin (Cloud Run deployment)
# - roles/storage.admin (Container Registry)
```

Add missing permissions if needed:
```bash
# Cloud Run admin (for deployment)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Storage admin (for pushing to Container Registry)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## How It Works

### Workflow Triggers
- **Automatic**: Pushes to `main` branch
- **Manual**: Using "Run workflow" button in GitHub Actions tab

### Build Process
1. Checks out code
2. Sets up Google Cloud CLI with service account
3. Builds Docker image natively on Linux (smaller size)
4. Pushes to Google Container Registry
5. Deploys to Cloud Run with environment variables and secrets

### Image Tagging
- `gcr.io/cruises-api-yevhen-dev/cruise-ai-agent:COMMIT_SHA`
- `gcr.io/cruises-api-yevhen-dev/cruise-ai-agent:latest`

## Configuration

### Environment Variables (set in workflow)
- `CHROMA_DATA_DIR=/tmp/chroma_data`
- `FIRESTORE_PROJECT_ID=cruises-api-yevhen-dev`
- `JWT_ALGORITHM=HS256`
- `ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,https://your-frontend-domain.com`
- `GCS_BUCKET_NAME=cruise_bucket`
- Database connection details

### Secrets (from Google Secret Manager)
- `JWT_SECRET=jwt-secret:latest`
- `OPENAI_API_KEY=openai-api-key:latest`
- `DB_PASSWORD=db-password:latest`

## Deployment

### First Deployment
1. Push code to `main` branch
2. GitHub Actions will automatically build and deploy
3. Check the Actions tab for build progress
4. Service URL will be displayed in the deployment logs

### Subsequent Deployments
- Just push to `main` branch
- Or use "Run workflow" button for manual deployment

## Monitoring

### GitHub Actions
- Go to Actions tab in your repository
- Click on workflow runs to see logs
- Build typically takes 5-10 minutes

### Cloud Run
- Check Google Cloud Console → Cloud Run
- View logs and metrics
- Service URL: `https://cruise-ai-agent-[hash]-ew.a.run.app`

## Troubleshooting

### Common Issues
1. **Permission denied**: Check service account roles
2. **Build fails**: Check Dockerfile and requirements.txt
3. **Deployment fails**: Verify secrets exist in Secret Manager
4. **Service won't start**: Check environment variables and port configuration

### Logs
```bash
# View Cloud Run logs
gcloud logs read --service=cruise-ai-agent --region=europe-central2

# View GitHub Actions logs
# Go to GitHub → Actions → Click on workflow run
```

## Security Notes
- Service account key is stored as GitHub secret (encrypted)
- Production secrets use Google Secret Manager
- Non-sensitive config uses environment variables
- Service runs with non-root user

## Cost Estimation
- **GitHub Actions**: Free (within 2,000 minutes/month)
- **Cloud Run**: Pay per request + CPU/memory usage
- **Container Registry**: Storage costs for Docker images
