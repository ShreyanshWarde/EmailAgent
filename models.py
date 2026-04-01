"""
Pydantic models for data validation - ensures our data is clean and correct
"""
from pydantic import BaseModel, EmailStr, validator # type: ignore
from typing import Optional, List
from datetime import datetime

class EmailContent(BaseModel):
    """Model for email content validation"""
    subject: str
    from_email: EmailStr
    body: str
    received_date: Optional[datetime] = None
    
    @validator('body')
    def body_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Email body cannot be empty')
        return v.strip()

class DraftResponse(BaseModel):
    """Model for AI-generated responses"""
    should_reply: bool
    reason: str
    reply_subject: str
    reply_body: str
    tone: str = "professional"  # professional, friendly, formal, casual
    
    @validator('reply_subject')
    def subject_length(cls, v):
        if len(v) > 150:
            raise ValueError('Subject too long')
        return v
    
    @validator('reply_body')
    def body_length(cls, v):
        if len(v) > 5000:
            raise ValueError('Response too long')
        return v

class EmailThread(BaseModel):
    """Model for email conversation thread"""
    thread_id: str
    emails: List[EmailContent]
    summary: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

'''What this does: This class handles all Gmail interactions. It:

Authenticates with Google

Fetches unread emails

Sends emails

Marks emails as read'''