#!/bin/bash

# Set variables
IMAGE_NAME="cruise-ai-agent-api"
DOCKER_REPO="butkoevgenii/cruise-client"
TAG="latest"

# Build the image
echo "Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME ..

# Tag for Docker Hub
echo "Tagging image for Docker Hub..."
docker tag $IMAGE_NAME:latest $DOCKER_REPO:$TAG

# Login to Docker Hub (will prompt for password)
echo "Logging in to Docker Hub..."
docker login

# Push to Docker Hub
echo "Pushing image to Docker Hub..."
docker push $DOCKER_REPO:$TAG
