# Deploy Widget to Google Cloud Run

## Prerequisites
- Google Cloud SDK installed
- Docker installed
- Google Cloud project with billing enabled
- Cloud Run API enabled

## Steps

### 1. Local Testing
```bash
# Install dependencies
npm install

# Set environment variables for widget build
export API_URL=http://localhost:3000/api/chat

# Build widget first
npm run build

# Set backend environment variables
export API_URL=https://your-ai-api.com/ask
export TOKEN="Bearer your-jwt-token"

# Start backend app
npm start
```

### 2. Create Dockerfile
```dockerfile
FROM node:18-alpine
WORKDIR /app

# Build arguments
ARG API_URL=https://your-app.run.app/api/chat

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set environment variable for build
ENV API_URL=$API_URL

# Build widget
RUN npm run build

# Expose port
EXPOSE 8080

# Start backend app
CMD ["npm", "start"]
```

### 3. Build and Push Container
```bash
# Set project ID
export PROJECT_ID=your-project-id

# Build image with API URL
docker build -t gcr.io/$PROJECT_ID/widget \
  --build-arg API_URL=https://your-app.run.app/api/chat .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/widget
```

### 4. Deploy to Cloud Run
```bash
gcloud run deploy widget \
  --image gcr.io/$PROJECT_ID/widget \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### 5. Environment Variables (if needed)
```bash
gcloud run deploy widget \
  --image gcr.io/$PROJECT_ID/widget \
  --set-env-vars "NODE_ENV=production,API_URL=https://your-ai-api.com/ask,TOKEN=Bearer your-jwt-token"
```

### 6. Custom Domain (optional)
```bash
gcloud run domain-mappings create \
  --service widget \
  --domain your-domain.com
```

## Configuration Options
- `--memory`: Set memory limit (default: 512Mi)
- `--cpu`: Set CPU allocation (default: 1)
- `--max-instances`: Set max scaling instances
- `--concurrency`: Set max concurrent requests per instance

## Verify Deployment
```bash
gcloud run services describe widget --region us-central1
```
