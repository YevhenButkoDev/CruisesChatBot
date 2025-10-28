# Credentials Setup for Google Cloud Run Deployment

## Required Credentials

### 1. Google Cloud Service Account Key

**Create Service Account:**
```bash
# Create service account
gcloud iam service-accounts create cruise-ai-agent \
    --description="Service account for Cruise AI Agent" \
    --display-name="Cruise AI Agent"

# Grant necessary permissions
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
    --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com
    
gcloud projects add-iam-policy-binding cruises-api-yevhen-dev \
  --member="serviceAccount:cruise-ai-agent@cruises-api-yevhen-dev.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Add to Docker:**
```dockerfile
# Add to Dockerfile
COPY service-account-key.json /app/service-account-key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json
```

### 2. MongoDB Atlas (for Agent Checkpoints)

**Setup:**
1. Create MongoDB Atlas cluster
2. Create database user
3. Get connection string

**Update .env:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=cruise_agent_checkpoints
```

### 3. Environment Variables to Set

**Required for Cloud Run:**
```bash
# In devops/.env
JWT_SECRET=your-256-bit-secret-key
OPENAI_API_KEY=sk-proj-your-openai-key
GCS_BUCKET_NAME=your-chroma-data-bucket
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_HOST=your-postgres-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
```

## Setup Steps

### 1. Google Cloud Setup
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create GCS bucket
gsutil mb gs://your-chroma-data-bucket

# Upload ChromaDB data
gsutil -m cp -r src/chroma_data gs://your-chroma-data-bucket/
```

### 2. Update Dockerfile
```dockerfile
# Add service account key
COPY service-account-key.json /app/service-account-key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json
```

### 3. Update Deployment Script
```bash
# In devops/deploy-cloudrun.sh
PROJECT_ID="your-gcp-project-id"
GCS_BUCKET="your-chroma-data-bucket"
```

## Security Notes

1. **Never commit service account keys to git**
2. **Use Cloud Run environment variables for secrets**
3. **Rotate keys regularly**
4. **Use least privilege IAM roles**

## Alternative: Use Cloud Run Service Account

Instead of service account key file, you can use Cloud Run's default service account:

```bash
# Grant permissions to Cloud Run service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

Then remove `GOOGLE_APPLICATION_CREDENTIALS` from environment variables.
