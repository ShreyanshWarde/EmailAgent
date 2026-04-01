"""
Authentication module for Email AI Agent
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import HTTPException, status
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    email: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class User(BaseModel):
    email: str
    disabled: Optional[bool] = None

# Simple user store (in production, use a database)
# This just checks if Gmail credentials exist
def get_user(email: str) -> Optional[User]:
    """
    Get user by email - simple check if Gmail token exists
    """
    if os.path.exists('token.pickle'):
        return User(email=email, disabled=False)
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user - for demo, accepts any user with valid Gmail token
    In production, implement proper authentication
    """
    user = get_user(email)
    if user and not user.disabled:
        return user
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email, user_id=payload.get("user_id"))
    except JWTError:
        return None

def check_gmail_auth() -> bool:
    """
    Check if Gmail is already authenticated
    Returns True if valid token exists
    """
    if os.path.exists('token.pickle'):
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                if creds and creds.valid:
                    return True
        except:
            return False
    return False

def initiate_gmail_auth():
    """
    Initiate Gmail OAuth flow
    Returns auth URL for frontend redirect
    
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
              'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send']
    CREDENTIALS_PATH = r'C:\AI_AGENT_PROJECTS\EmailAgent\venv\credentials.json'
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES,
        redirect_uri='http://localhost:8000/api/auth/callback'
    )
    
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return auth_url

def complete_gmail_auth(code: str):
    """
    Complete Gmail OAuth flow with authorization code
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
              'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send']
    
    CREDENTIALS_PATH = r'C:\AI_AGENT_PROJECTS\EmailAgent\venv\credentials.json'
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES,
        redirect_uri='http://localhost:8000/api/auth/callback'
    )
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # Save credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    return True