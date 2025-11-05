#!/bin/bash

# Build Docker image
docker build -f DockerfileApi -t cruise-ai-agent-api ..

echo "Docker image 'cruise-ai-agent-api' built successfully"
