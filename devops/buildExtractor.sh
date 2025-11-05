#!/bin/bash

# Build Docker image
docker build -f DockerfileExtractor -t cruise-ai-agent-extractor ..

echo "Docker image 'cruise-ai-agent-extractor' built successfully"
