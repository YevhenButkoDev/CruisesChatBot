#!/bin/bash

# Configuration
PROJECT_ID="cruises-api-yevhen-dev"
SERVICE_NAME="cruise-ai-agent"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
SERVICE_ACCOUNT="cruise-service-account@$PROJECT_ID.iam.gserviceaccount.com"

# Build and push Docker image
echo "Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME ..

echo "Pushing to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --service-account $SERVICE_ACCOUNT \
  --set-env-vars "CHROMA_DATA_DIR=/app/chroma_data,FIRESTORE_PROJECT_ID=$PROJECT_ID" \
  --project $PROJECT_ID

echo "Deployment complete!"
