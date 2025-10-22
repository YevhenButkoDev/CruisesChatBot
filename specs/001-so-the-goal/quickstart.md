# Quickstart

**Date**: 2025-10-12

## Prerequisites

-   Python 3.11
-   PostgreSQL database
-   Environment variables set for database connection

## Installation

1.  Clone the repository.
2.  Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Running the application

1.  **Run the data extraction and vector DB creation process:**
    ```bash
    python src/api.py
    ```
2.  **Run the API:**
    ```bash
    uvicorn src.api.main:app --reload
    ```

## API Usage

-   **Endpoint:** `/query`
-   **Method:** `POST`
-   **Request Body:**
    ```json
    {
        "query": "text"
    }
    ```
-   **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"query": "cruises in the Mediterranean"}' http://127.0.0.1:8000/query
    ```
