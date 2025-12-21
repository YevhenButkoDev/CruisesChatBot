#!/bin/bash

# Set variables
IMAGE_NAME="cruise-widget"
API_URL=${API_URL}
TOKEN=${TOKEN}

# Run Docker container
docker run -p 3000:3000 \
  -e API_URL="$API_URL" \
  -e TOKEN="$TOKEN" \
  $IMAGE_NAME

echo "🚀 Container started on http://localhost:3000"
