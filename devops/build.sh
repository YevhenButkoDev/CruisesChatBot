#!/bin/bash

# Build Docker image
docker build -f Dockerfile -t cruise-ai-agent-api ..

echo "Docker image 'cruise-ai-agent-api' built successfully"
