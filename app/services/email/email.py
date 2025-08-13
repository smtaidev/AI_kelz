#!/usr/bin/env python3
"""
Email Generation Module
Handles voice input transcription and email generation using OpenAI API
"""
from typing import Optional, Dict, Any
import os
import sys
import requests

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

from app.config.config import OPENAI_API_KEY
from app.services.utils.transcription import VoiceTranscriber

class EmailGenerator:
    """
    Email generation component using OpenAI API for creating emails from voice input
    """
    
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.voice_transcriber = VoiceTranscriber()
    
    def generate_email_from_text(self, transcribed_text: str, email_type: str = "general", 
                                tone: str = "professional", recipient: str = None) -> Optional[Dict[str, Any]]:
        """
        Generate email content from transcribed text using OpenAI API
        
        Args:
            transcribed_text (str): The transcribed voice input
            email_type (str): Type of email (general, formal, casual, complaint, request, etc.)
            tone (str): Tone of the email (professional, casual, friendly, formal)
            recipient (str): Optional recipient context
            
        Returns:
            Dict: Email content with subject and body, or None if failed
        """
        try:
            if not self.openai_api_key:
                return None
            
            if not transcribed_text or not transcribed_text.strip():
                return None
            
            # Create prompt for email generation
            prompt = self._create_email_prompt(transcribed_text, email_type, tone, recipient)
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional email writing assistant. Generate well-structured, appropriate emails based on the given voice input and requirements.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                email_content = result['choices'][0]['message']['content']
                return self._parse_email_content(email_content)
            else:
                return None
                
        except Exception:
            return None
    
    def process_voice_to_email(self, audio_file_path: str, email_type: str = "general", 
                              tone: str = "professional", recipient: str = None) -> Optional[Dict[str, Any]]:
        """
        Complete pipeline: transcribe voice input and generate email
        
        Args:
            audio_file_path (str): Path to audio file
            email_type (str): Type of email
            tone (str): Tone of the email
            recipient (str): Optional recipient context
            
        Returns:
            Dict: Complete result with transcription and email content
        """
        try:
            # Step 1: Transcribe audio
            original_transcription, polished_transcription = self.voice_transcriber.process_file_with_results(audio_file_path)
            
            if not original_transcription:
                return None
            
            # Step 2: Generate email from transcription
            email_content = self.generate_email_from_text(
                original_transcription, email_type, tone, recipient
            )
            
            if not email_content:
                return None
            
            return {
                "status": "success",
                "message": "Voice-to-email pipeline completed successfully",
                "transcription": {
                    "original": original_transcription,
                    "polished": polished_transcription
                },
                "email": email_content
            }
            
        except Exception:
            return None
    
    def _create_email_prompt(self, transcribed_text: str, email_type: str, tone: str, recipient: str) -> str:
        """
        Create a prompt for email generation based on parameters
        """
        recipient_context = f" The recipient is: {recipient}." if recipient else ""
        
        prompt = f"""
        Based on the following voice input, please generate a professional email:
        
        Voice Input: "{transcribed_text}"
        
        Email Requirements:
        - Type: {email_type}
        - Tone: {tone}
        {recipient_context}
        
        Please format the response as:
        Subject: [email subject]
        
        Body:
        [email body content]
        
        Make sure the email is well-structured, appropriate for the specified tone and type, and captures the intent from the voice input.
        """
        
        return prompt
    
    def _parse_email_content(self, email_content: str) -> Dict[str, Any]:
        """
        Parse the generated email content to extract subject and body
        """
        try:
            lines = email_content.splitlines()
            subject = ""
            body_lines = []
            subject_found = False
            for line in lines:
                if line.lower().startswith("subject:"):
                    subject = line[len("subject:"):].strip()
                    subject_found = True
                elif subject_found:
                    if line.strip().lower() == "body:":
                        continue
                    body_lines.append(line)
            body = "\n".join(body_lines).strip()
            return {"subject": subject, "body": body}
        except Exception:
            return {"subject": "", "body": email_content}

def generate_email_from_voice(audio_file_path: str, email_type: str = "general", 
                             tone: str = "professional", recipient: str = None) -> Optional[Dict[str, Any]]:
    """
    Standalone function to generate email from voice input
    
    Args:
        audio_file_path (str): Path to audio file
        email_type (str): Type of email
        tone (str): Tone of the email
        recipient (str): Optional recipient context
        
    Returns:
        Dict: Email generation result
    """
    try:
        generator = EmailGenerator()
        return generator.process_voice_to_email(audio_file_path, email_type, tone, recipient)
    except Exception:
        return None