import jwt
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import HTTPException, status

# Load environment variables (like SECRET_KEY) from .env file
load_dotenv()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fetch your secret key and JWT settings from environment
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create and encode a JWT token
def create_access_token(data: dict, roles: list[str], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    to_encode.update({"roles": roles})
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify and decode a JWT access token
def verify_token(token: str) -> Optional[dict]:
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check the expiration time (exp)
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token does not have an expiration date")

        # Compare the expiration time to the current time
        expire_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # If expired, return None or raise an exception
        if expire_time < datetime.now(tz=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

        return payload  # Return the decoded payload if the token is valid

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")