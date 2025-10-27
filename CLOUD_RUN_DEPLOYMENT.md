# Google Cloud Run Deployment Guide

## Overview

This guide explains how to deploy your Cruise AI Agent to Google Cloud Run with persistent ChromaDB storage using Google Cloud Storage.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Request  │───▶│  Cloud Run API   │───▶│ ChromaDB Local  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        ▲
                                ▼                        │
                       ┌──────────────────┐             │
                       │   MongoDB Atlas  │             │
                       │   (Checkpoints)  │             │
                       └──────────────────┘             │
                                                         │
                       ┌──────────────────┐             │
                       │ Google Cloud     │─────────────┘
                       │ Storage Bucket   │ (Sync on startup)
                       │ (ChromaDB Data)  │
                       └──────────────────┘
```

## How It Works

### 1. **Startup Process**
- Cloud Run container starts
- `sync_chroma_data_from_gcs()` downloads ChromaDB data from GCS bucket to `/app/chroma_data`
- FastAPI server starts and serves requests

### 2. **Runtime**
- API requests use local ChromaDB data for fast queries
- JWT authentication protects endpoints
- CORS allows requests from whitelisted origins
- Agent conversations stored in MongoDB checkpoints

### 3. **Data Flow**
```
GCS Bucket → Container Local Storage → ChromaDB → Vector Search → AI Agent → Response
```

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **GCS Bucket** for ChromaDB data storage
3. **MongoDB Atlas** cluster for agent checkpoints
4. **Docker** installed locally
5. **gcloud CLI** configured

## Setup Steps

### 1. Create GCS Bucket
```bash
gsutil mb gs://cruise_bucket
```

### 2. Upload ChromaDB Data
```bash
# Upload your existing ChromaDB data
gsutil -m cp -r src/chroma_data gs://cruise_bucket
```

### 3. Configure Environment
Update `devops/deploy-cloudrun.sh`:
```bash
PROJECT_ID="your-gcp-project-id"
GCS_BUCKET="your-chroma-data-bucket"
```

### 4. Deploy
```bash
cd devops
./deploy-cloudrun.sh
```

## Environment Variables

The deployment sets these environment variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `GCS_BUCKET_NAME` | your-bucket-name | GCS bucket for ChromaDB data |
| `CHROMA_DATA_DIR` | `/app/chroma_data` | Local ChromaDB storage path |
| `JWT_SECRET` | your-secret-key | JWT token signing key |
| `MONGODB_URI` | mongodb://... | MongoDB connection for checkpoints |
| `OPENAI_API_KEY` | sk-... | OpenAI API access |

## API Usage

### Authentication
All endpoints require JWT token:
```bash
curl -X POST "https://your-service-url/ask" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"question": "Find cruises to Barcelona", "chat_id": "user123"}'
```

### Generate JWT Token
```python
from src.util.jwt_utils import create_jwt_token
token = create_jwt_token("user123", expires_in_hours=24)
```

## Storage Strategy

### Why This Approach?

1. **Fast Access**: Local storage for runtime queries
2. **Persistence**: GCS ensures data survives container restarts
3. **Scalability**: Multiple instances can share the same data
4. **Cost-Effective**: Only pay for storage and compute when used

### Data Sync Process

```python
# On container startup
sync_chroma_data_from_gcs()  # Downloads from GCS to local

# Runtime
query_chroma_db(query)  # Uses local data for fast queries
```

## Monitoring

### Cloud Run Metrics
- Request count and latency
- Memory and CPU usage
- Error rates

### Logs
```bash
gcloud logs read --service=cruise-ai-agent --limit=50
```

## Scaling

Cloud Run automatically scales based on:
- **Requests**: 0 to 1000 concurrent requests per instance
- **Memory**: 2Gi allocated per instance
- **CPU**: 1 vCPU per instance

## Cost Optimization

1. **Cold Starts**: First request may be slower due to GCS sync
2. **Minimum Instances**: Set to 0 for cost savings
3. **Request Timeout**: 60 seconds default
4. **Memory**: Adjust based on ChromaDB size

## Troubleshooting

### Common Issues

1. **GCS Access Denied**
   - Ensure Cloud Run service account has Storage Object Viewer role

2. **ChromaDB Not Found**
   - Check GCS bucket exists and contains `chroma_data/` folder

3. **Memory Issues**
   - Increase memory allocation in deployment script

4. **Cold Start Timeout**
   - Increase request timeout or use minimum instances

### Debug Commands
```bash
# Check service status
gcloud run services describe cruise-ai-agent --region=us-central1

# View logs
gcloud logs tail --service=cruise-ai-agent

# Test locally
docker run -p 8000:8000 -e GCS_BUCKET_NAME=your-bucket gcr.io/project/cruise-ai-agent
```

## Security

- **JWT Authentication**: All endpoints protected
- **CORS**: Whitelisted origins only
- **Environment Variables**: Secrets managed via Cloud Run
- **IAM**: Least privilege access to GCS

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domain
3. Implement health checks
4. Add CI/CD pipeline
5. Set up staging environment
