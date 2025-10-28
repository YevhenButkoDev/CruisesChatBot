#!/bin/bash

# Configuration
PROJECT_ID="cruises-api-yevhen-dev"
SERVICE_NAME="cruise-ai-agent"
REGION="europe-central2"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
SERVICE_ACCOUNT="cruise-ai-agent@$PROJECT_ID.iam.gserviceaccount.com"

# Build and push Docker image
echo "Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME ..

echo "Configuring Docker for GCR..."
gcloud auth configure-docker

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
  --set-env-vars "CHROMA_DATA_DIR=/tmp/chroma_data,FIRESTORE_PROJECT_ID=$PROJECT_ID,JWT_ALGORITHM=HS256,ALLOWED_ORIGINS=https://uat.center.cruises,GCS_BUCKET_NAME=cruise_bucket,DB_HOST=uat-db-do-user-2290310-0.d.db.ondigitalocean.com,DB_PORT=25060,DB_NAME=db_cruise,DB_USER=llm_user" \
  --set-secrets "JWT_SECRET=jwt-secret:latest,OPENAI_API_KEY=openai-api-key:latest,DB_PASSWORD=db-password:latest" \
  --project $PROJECT_ID

echo "Deployment complete!"
