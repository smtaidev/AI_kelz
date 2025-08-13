#!/usr/bin/env python3
"""
Email Schema Definitions
Pydantic models for email generation API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class EmailTone(str, Enum):
    """Available email tones"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    URGENT = "urgent"
    POLITE = "polite"

class EmailType(str, Enum):
    """Available email types"""
    GENERAL = "general"
    COMPLAINT = "complaint"
    REQUEST = "request"
    INQUIRY = "inquiry"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"
    APOLOGY = "apology"
    MEETING_REQUEST = "meeting_request"
    STATUS_UPDATE = "status_update"
    PROPOSAL = "proposal"

class EmailGenerationRequest(BaseModel):
    """Request model for email generation from voice"""
    email_type: EmailType = Field(default=EmailType.GENERAL, description="Type of email to generate")
    tone: EmailTone = Field(default=EmailTone.PROFESSIONAL, description="Tone of the email")
    recipient: Optional[str] = Field(default=None, description="Optional context about the recipient")
    additional_instructions: Optional[str] = Field(default=None, description="Additional instructions for email generation")

class TranscriptionResult(BaseModel):
    """Model for transcription results"""
    original: str = Field(..., description="Original transcription from voice")
    polished: Optional[str] = Field(default=None, description="Polished version of transcription")
    length: int = Field(..., description="Length of original transcription")

class EmailContent(BaseModel):
    """Model for generated email content"""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    full_content: str = Field(..., description="Complete generated email content")
    word_count: int = Field(..., description="Word count of email body")

class EmailGenerationResponse(BaseModel):
    """Response model for email generation"""
    status: str = Field(..., description="Status of the operation (success/error)")
    message: str = Field(..., description="Status message")
    filename: Optional[str] = Field(default=None, description="Original audio filename")
    transcription: Optional[TranscriptionResult] = Field(default=None, description="Transcription results")
    email: Optional[EmailContent] = Field(default=None, description="Generated email content")
    processing_time: Optional[float] = Field(default=None, description="Total processing time in seconds")

class EmailAnalysis(BaseModel):
    """Model for email content analysis"""
    sentiment: Optional[str] = Field(default=None, description="Detected sentiment of the email")
    key_points: Optional[List[str]] = Field(default=None, description="Key points extracted from content")
    urgency_level: Optional[str] = Field(default=None, description="Detected urgency level")
    suggested_improvements: Optional[List[str]] = Field(default=None, description="Suggestions for improvement")

class EmailGenerationResponseWithAnalysis(EmailGenerationResponse):
    """Extended response model with analysis"""
    analysis: Optional[EmailAnalysis] = Field(default=None, description="Email content analysis")

# Request models for different endpoints
class TextToEmailRequest(BaseModel):
    """Request model for generating email from text"""
    text: str = Field(..., description="Text content to convert to email")
    email_type: EmailType = Field(default=EmailType.GENERAL, description="Type of email to generate")
    tone: EmailTone = Field(default=EmailTone.PROFESSIONAL, description="Tone of the email")
    recipient: Optional[str] = Field(default=None, description="Optional context about the recipient")

class EmailImprovementRequest(BaseModel):
    """Request model for improving existing email"""
    subject: str = Field(..., description="Current email subject")
    body: str = Field(..., description="Current email body")
    improvement_type: str = Field(default="general", description="Type of improvement needed")
    target_tone: EmailTone = Field(default=EmailTone.PROFESSIONAL, description="Target tone for improvement")

# Error response models
class EmailError(BaseModel):
    """Error response model"""
    status: str = Field(default="error", description="Error status")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")

# Health check models
class EmailServiceHealth(BaseModel):
    """Health check response for email service"""
    service: str = Field(default="email_generation", description="Service name")
    status: str = Field(..., description="Service status")
    openai_available: bool = Field(..., description="OpenAI API availability")
    transcription_available: bool = Field(..., description="Transcription service availability")
    timestamp: str = Field(..., description="Health check timestamp")

# Statistics models
class EmailStats(BaseModel):
    """Email generation statistics"""
    total_emails_generated: int = Field(default=0, description="Total number of emails generated")
    average_processing_time: float = Field(default=0.0, description="Average processing time")
    most_common_type: Optional[str] = Field(default=None, description="Most commonly generated email type")
    most_common_tone: Optional[str] = Field(default=None, description="Most commonly used tone")
    success_rate: float = Field(default=0.0, description="Success rate percentage")