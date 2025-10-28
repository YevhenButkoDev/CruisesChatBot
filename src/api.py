from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import os
import logging

from src.ai_agent import CruiseAgent
from src.util.cloud_storage import sync_chroma_data_from_gcs
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

app = FastAPI()
security = HTTPBearer()

# Sync data when module is imported (runs in Docker)
sync_chroma_data_from_gcs()

agent = CruiseAgent()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# JWT verification
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        logging.info("validating token")
        logging.info(JWT_SECRET)
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as er:
        logging.info(er)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class Query(BaseModel):
    query: str


class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"


class AgentRequest(BaseModel):
    question: str
    chat_id: str

@app.post("/ask")
async def ask_agent(request: AgentRequest, user: dict = Depends(verify_jwt)):
    """
    Call the Cruise AI agent with a user's question and chat ID.
    """
    try:
        responses = agent.ask(user_message=request.question, thread_id=request.chat_id)
        if not responses:
            raise HTTPException(status_code=404, detail="No response from agent")

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    sync_chroma_data_from_gcs()
    uvicorn.run(app, host="0.0.0.0", port=8000)
