# Quickstart: AI Chatbot for Cruise Search

This guide provides instructions on how to set up and run the AI Chatbot API.

## Prerequisites

-   Python 3.11
-   An existing `chroma_data` directory with cruise information.

## Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables**:
    Create a `.env` file in the root of the project and add any necessary credentials (if any).

## Running the API

1.  **Start the FastAPI server**:
    ```bash
    uvicorn src.api:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## Using the API

You can interact with the API using a tool like `curl` or the automatically generated OpenAPI documentation at `http://127.0.0.1:8000/docs`.

**Example request**:

```bash
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d '{
  "message": "I want to go to the Caribbean next summer"
}'
```
