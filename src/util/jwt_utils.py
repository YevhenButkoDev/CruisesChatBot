import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def create_jwt_token(user_id: str = "test_user", expires_in_hours: int = 24) -> str:
    """
    Create a valid JWT token.
    
    :param user_id: User identifier
    :param expires_in_hours: Token expiration time in hours
    :return: JWT token string
    """
    secret = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, secret, algorithm=algorithm)

if __name__ == "__main__":
    token = create_jwt_token(user_id="cruise_client", expires_in_hours=24*365)
    print(f"JWT Token: {token}")
