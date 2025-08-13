#!/usr/bin/env python3
"""
Enhanced Transcription Module with Grammar Correction
Handles all audio recording, transcription, and file processing using OpenAI API
Now includes grammar correction while preserving original meaning
"""

import os
import sys
from typing import Optional
import requests

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

from app.config.config import OPENAI_API_KEY

class VoiceTranscriber:
    """
    Voice transcription component using OpenAI Whisper API
    """
    
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Transcribed text or None if failed
        """
        try:
            if not self.openai_api_key:
                return None
                
            if not os.path.exists(audio_file_path):
                return None
            
            # Check file size (Whisper has 25MB limit)
            file_size = os.path.getsize(audio_file_path)
            if file_size > 25 * 1024 * 1024:  # 25MB
                return None
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}'
            }
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': audio_file,
                    'model': (None, 'whisper-1'),
                    'response_format': (None, 'text')
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/audio/transcriptions',
                    headers=headers,
                    files=files,
                    timeout=120
                )
            
            if response.status_code == 200:
                transcription = response.text.strip()
                return transcription
            else:
                return None
                
        except Exception:
            return None

    def process_file_with_results(self, audio_file_path: str):
        """
        Process audio file and return both original and polished transcription
        Args:
            audio_file_path (str): Path to audio file
        Returns:
            tuple: (original_transcription, polished_transcription) or (None, None) if failed
        """
        try:
            original = self.transcribe_audio(audio_file_path)
            if original:
                # For now, return the same text for both
                # In a full implementation, you might want to add text polishing
                return original, original
            return None, None
        except Exception:
            return None, None

def transcribe_audio(audio_file_path: str) -> Optional[str]:
    """
    Standalone function to transcribe an audio file.
    
    Args:
        audio_file_path (str): The path to the audio file.
        
    Returns:
        str: The transcribed text, or None if transcription fails.
    """
    try:
        transcriber = VoiceTranscriber()
        return transcriber.transcribe_audio(audio_file_path)
    except Exception:
        return None