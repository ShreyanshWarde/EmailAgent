"""
FastAPI Email AI Agent Backend
"""
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, Dict, Any
import uvicorn
from dotenv import load_dotenv

from api.routes import router as api_router
from api.auth import verify_token, create_access_token, Token, TokenData
import nest_asyncio
nest_asyncio.apply()
# Load environment variables
load_dotenv()

app = FastAPI(
    title="Email AI Agent API",
    description="Backend API for Email AI Agent with Gmail integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Include API routes
app.include_router(api_router, prefix="/api")

# Security dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user from token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    return token_data

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Email AI Agent API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "login": "/api/login",
            "process_emails": "/api/process",
            "send_test": "/api/send-test",
            "status": "/api/status"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "email-ai-agent"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )