#!/usr/bin/env python3
"""
Simple Email Router for FastAPI
Just upload audio and get an email back
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.services.email.email import EmailGenerator

# Create router
router = APIRouter()

# Initialize email generator
email_generator = EmailGenerator()

@router.post("/generate/")
async def generate_email(audio: UploadFile = File(...)):
    """
    Upload an audio file and get back a generated email.
    Simple as that!
    """
    temp_file_path = None
    
    try:
        # Validate file type
        supported_audio_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
            'audio/mp4', 'audio/webm', 'audio/ogg', 'audio/flac'
        ]
        
        if audio.content_type not in supported_audio_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio type. Supported: MP3, WAV, M4A, MP4, WEBM, OGG, FLAC"
            )
        
        # Check file size (25MB limit)
        content = await audio.read()
        if len(content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(content)
        
        # Process voice to email
        result = email_generator.process_voice_to_email(
            audio_file_path=temp_file_path,
            email_type="general",
            tone="professional"
        )
        
        if result and result["status"] == "success":
            transcription_data = result.get("transcription", {})
            email_data = result.get("email", {})
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "filename": audio.filename,
                    "transcription": transcription_data.get("original", ""),
                    "email_subject": email_data.get("subject", ""),
                    "email_body": email_data.get("body", ""),
                    "message": "Email generated successfully"
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate email from audio"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)