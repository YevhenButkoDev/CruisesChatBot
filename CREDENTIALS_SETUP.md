# Credentials Setup for Cruise AI Agent

## Required Services & APIs

### 1. Google Cloud APIs
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
```

### 2. Service Account Setup
```bash
# Create service account (if not exists)
gcloud iam service-accounts create cruise-ai-agent \
    --description="Service account for Cruise AI Agent" \
    --display-name="Cruise AI Agent" \
    --project=cruises-api-yevhen-dev

# Grant Firestore permissions (for AI agent checkpointing)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Grant Cloud Storage permissions (for ChromaDB data sync)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Grant Secret Manager permissions (for accessing secrets in Cloud Run)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Artifact Registry permissions (for pushing Docker images)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Grant Service Account User permissions (for Cloud Run deployment)
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create service account key for local development
gcloud iam service-accounts keys create devops/secret/service-account-key.json \
    --iam-account=cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com
```

## Environment Variables

### Local Development (.env)
```bash
# Authentication
JWT_SECRET=cruise-secret
JWT_ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=http://localhost:8000

# Google Cloud
GCS_BUCKET_NAME=cruise_bucket
GOOGLE_APPLICATION_CREDENTIALS=/Users/ybutko/Documents/Projects/cruise-info-vector-db-creator/devops/secret/service-account-key.json
FIRESTORE_PROJECT_ID=cruises-api-yevhen-dev

# ChromaDB
CHROMA_DATA_DIR=/tmp/chroma_data

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-key

# Database
DB_HOST=uat-db-do-user-2290310-0.d.db.ondigitalocean.com
DB_PORT=25060
DB_NAME=db_cruise
DB_USER=llm_user
DB_PASSWORD=your-db-password
```

### Cloud Run Secrets (Production)
```bash
# Create secrets in Google Secret Manager
echo "cruise-secret" | gcloud secrets create jwt-secret --data-file=- --project=cruises-api-yevhen-dev
echo "your-openai-key" | gcloud secrets create openai-api-key --data-file=- --project=cruises-api-yevhen-dev
echo "your-db-password" | gcloud secrets create db-password --data-file=- --project=cruises-api-yevhen-dev
```

## Setup Steps

### 1. Google Cloud Storage Setup
```bash
# Create GCS bucket for ChromaDB data
gsutil mb gs://cruise_bucket

# Upload ChromaDB data
gsutil -m cp -r src/chroma_data gs://cruise_bucket/
```

### 2. Local Development
```bash
# Run with Docker Compose
cd devops
docker-compose up -d
```

### 3. Cloud Run Deployment
```bash
# Deploy to Cloud Run
cd devops
./deploy-cloudrun.sh
```

## Security Best Practices

1. **Service Account Keys**: Only for local development, never commit to git
2. **Production Secrets**: Use Google Secret Manager for sensitive data
3. **CORS**: Configure appropriate origins for your frontend
4. **IAM**: Use least privilege principle for service account permissions
5. **Key Rotation**: Regularly rotate service account keys and API keys

## Architecture Overview

- **Firestore**: AI agent conversation checkpointing
- **Cloud Storage**: ChromaDB vector database data sync
- **Secret Manager**: Secure storage of API keys and passwords
- **Cloud Run**: Serverless container deployment with service account authentication
