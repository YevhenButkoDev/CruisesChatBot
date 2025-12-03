#!/bin/bash

# Set variables
IMAGE_NAME="cruise-widget"
API_URL=${API_URL:-"https://cruise-ai-agent-620626195243.europe-central2.run.app/ask"}
TOKEN=${TOKEN}

# Run Docker container
docker run -p 3000:3000 \
  -e API_URL="$API_URL" \
  -e TOKEN="$TOKEN" \
  -d \
  $IMAGE_NAME

echo "🚀 Container started on http://localhost:3000"
