# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY ../requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ../src ./src

# Copy ChromaDB data directly into the image
COPY ../src/chroma_data ./chroma_data

# Expose port FastAPI will run on
EXPOSE 8000

# Environment variables for Cloud Run
ENV CHROMA_DATA_DIR=/app/chroma_data
ENV PORT=8000

# Add to Dockerfile
COPY ./secret/service-account-key.json /app/service-account-key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json

# Command to run FastAPI using Uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]