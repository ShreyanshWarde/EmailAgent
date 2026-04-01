"""
API Routes for Email AI Agent
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
import os
import json
from datetime import timedelta
from datetime import datetime 

from api.auth import (
    create_access_token, 
    verify_token, 
    Token, 
    TokenData,
    check_gmail_auth,
    initiate_gmail_auth,
    complete_gmail_auth,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Import your existing components
from main import EmailAIAgent
from gmail_service import GmailService
from models import DraftResponse

router = APIRouter()

# Store active agents (in production, use Redis or database)
active_agents = {}

# Initialize dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current user from token
    """
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

def get_or_create_agent(user_email: str) -> EmailAIAgent:
    """
    Get or create EmailAIAgent for user
    """
    if user_email not in active_agents:
        # Check if Gmail is authenticated
        if not check_gmail_auth():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail not authenticated. Please authenticate first."
            )
        
        try:
            active_agents[user_email] = EmailAIAgent()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize agent: {str(e)}"
            )
    
    return active_agents[user_email]

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - for demo purposes, accepts any credentials
    In production, implement proper user authentication
    """
    # Check if Gmail is authenticated
    if not check_gmail_auth():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please authenticate with Gmail first",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For demo, accept any user
    # In production, verify credentials against database
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username, "user_id": "demo_user"},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        email=form_data.username,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/register")
async def register_user(
    email: str = Body(...),
    password: str = Body(...),
    confirm_password: str = Body(...)
):
    """
    Register new user (demo - in production, store in database)
    """
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if Gmail is authenticated
    if not check_gmail_auth():
        return {
            "message": "User registered (demo). Please authenticate with Gmail.",
            "email": email,
            "next_step": "gmail_auth_required"
        }
    
    return {
        "message": "User registered successfully",
        "email": email,
        "gmail_authenticated": True
    }

@router.get("/auth/gmail")
async def gmail_auth_initiate():
    """
    Initiate Gmail OAuth authentication
    Returns URL for frontend to redirect to
    """
    try:
        auth_url = initiate_gmail_auth()
        return {
            "auth_url": auth_url,
            "message": "Redirect user to this URL for Gmail authentication"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Gmail auth: {str(e)}"
        )

@router.post("/auth/gmail/callback")
async def gmail_auth_callback(code: str = Body(..., embed=True)):
    """
    Complete Gmail OAuth authentication with authorization code
    """
    try:
        success = complete_gmail_auth(code)
        if success:
            return {
                "message": "Gmail authentication successful",
                "authenticated": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to complete Gmail authentication"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/auth/status")
async def auth_status():
    """
    Check authentication status
    """
    gmail_auth = check_gmail_auth()
    return {
        "gmail_authenticated": gmail_auth,
        "requires_gmail_auth": not gmail_auth,
        "message": "Ready to use" if gmail_auth else "Please authenticate with Gmail first"
    }

@router.post("/process", dependencies=[Depends(get_current_user)])
async def process_emails(
    max_emails: int = Query(5, ge=1, le=50),
    user: TokenData = Depends(get_current_user)
):
    """
    Process unread emails and send replies
    """
    try:
        agent = get_or_create_agent(user.email)
        result = agent.process_emails(max_emails=max_emails)
        
        return {
            "success": True,
            "message": f"Processed emails with AI agent",
            "user": user.email,
            "max_emails": max_emails,
            "details": "Check console/logs for detailed output"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process emails: {str(e)}"
        )

@router.get("/emails/unread", dependencies=[Depends(get_current_user)])
async def get_unread_emails(
    max_results: int = Query(10, ge=1, le=50),
    user: TokenData = Depends(get_current_user)
):
    """
    Get list of unread emails (read only)
    """
    try:
        gmail_service = GmailService()
        emails = gmail_service.get_unread_emails(max_results=max_results)
        
        # Format emails for API response
        formatted_emails = []
        for email in emails:
            formatted_emails.append({
                "id": email['id'],
                "from": email['from'],
                "subject": email['subject'],
                "body_preview": email['body'][:200] + "..." if len(email['body']) > 200 else email['body'],
                "thread_id": email['threadId']
            })
        
        return {
            "count": len(formatted_emails),
            "emails": formatted_emails,
            "user": user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emails: {str(e)}"
        )

@router.post("/send-test", dependencies=[Depends(get_current_user)])
async def send_test_email(
    to: str = Body(..., embed=True),
    subject: str = Body("Test Email", embed=True),
    body: str = Body("This is a test email from AI Agent", embed=True),
    user: TokenData = Depends(get_current_user)
):
    """
    Send a test email
    """
    try:
        gmail_service = GmailService()
        success = gmail_service.send_email(to, subject, body)
        
        if success:
            return {
                "success": True,
                "message": "Test email sent successfully",
                "to": to,
                "subject": subject
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

@router.get("/agent/status", dependencies=[Depends(get_current_user)])
async def agent_status(user: TokenData = Depends(get_current_user)):
    """
    Get AI agent status
    """
    try:
        # Check if OpenAI API key is configured
        openai_key = os.getenv('OPENAI_API_KEY')
        gmail_auth = check_gmail_auth()
        
        agent_initialized = user.email in active_agents
        
        return {
            "user": user.email,
            "openai_configured": bool(openai_key),
            "gmail_authenticated": gmail_auth,
            "agent_initialized": agent_initialized,
            "ready_to_use": bool(openai_key) and gmail_auth,
            "message": "Agent is ready" if bool(openai_key) and gmail_auth else "Configuration required"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )

@router.post("/analyze", dependencies=[Depends(get_current_user)])
async def analyze_email(
    email_text: str = Body(..., embed=True),
    user: TokenData = Depends(get_current_user)
):
    """
    Analyze email content without sending
    """
    try:
        agent = get_or_create_agent(user.email)
        
        # Create a mock email dict for analysis
        mock_email = {
            'from': 'sender@example.com',
            'subject': 'Test Analysis',
            'body': email_text
        }
        
        response = agent._generate_response(mock_email)
        
        return {
            "analysis": response.dict(),
            "user": user.email,
            "should_reply": response.should_reply,
            "reason": response.reason
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze email: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "email-ai-agent",
        "timestamp": datetime.now().isoformat()
    }