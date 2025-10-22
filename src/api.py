from fastapi import FastAPI
from pydantic import BaseModel
from src.vector_db.query import query_chroma_db
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()


class Query(BaseModel):
    query: str


class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"


# Chat bot instances will be created per session


@app.post("/query")
def query(query: Query):
    """Queries the vector database and returns the most relevant cruise information."""
    results = query_chroma_db(query.query)
    
    # The results from chromadb are a bit complex, we need to parse them
    # to match the openapi.yaml format.
    
    if not results or not results.get("ids"):
        return []

    parsed_results = []
    for i, doc_id in enumerate(results["ids"][0]):
        parsed_results.append({
            "cruise_id": doc_id,
            "cruise_info": results["documents"][0][i],
            "meta": results["metadatas"][0][i],
            "score": results["distances"][0][i]
        })

    return parsed_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
