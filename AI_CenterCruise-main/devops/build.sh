#!/bin/bash

# Set variables
IMAGE_NAME="cruise-widget"

# Build Docker image
docker build -f Dockerfile -t $IMAGE_NAME ..

echo "✅ Docker image built: $IMAGE_NAME"
