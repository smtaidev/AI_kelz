#!/usr/bin/env python3
"""
Todo List Module
Handles voice input transcription and generates todo lists using OpenAI
"""

import os
import sys
from typing import Optional, List
import requests
import json

# Add the app directory to Python path for imports
app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_dir)

from app.config.config import OPENAI_API_KEY
from app.services.utils.transcription import VoiceTranscriber

class TodoListGenerator:
    """
    Todo list generator using voice transcription and OpenAI
    """
    
    def __init__(self):
        self.openai_api_key = OPENAI_API_KEY
        self.transcriber = VoiceTranscriber()
    
    def generate_todo_from_voice(self, audio_file_path: str) -> Optional[List[str]]:
        """
        Generate todo list from voice input
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            List[str]: Generated todo items or None if failed
        """
        try:
            # First transcribe the audio
            transcribed_text = self.transcriber.transcribe_audio(audio_file_path)
            if not transcribed_text:
                return None
            
            # Generate todo list from transcribed text
            return self.generate_todo_from_text(transcribed_text)
            
        except Exception:
            return None
    
    def generate_todo_from_text(self, text: str) -> Optional[List[str]]:
        """
        Generate todo list from text using OpenAI
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: Generated todo items or None if failed
        """
        try:
            if not self.openai_api_key or not text:
                return None
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""
            Based on the following input, create a clear and actionable todo list. 
            Extract specific tasks and organize them logically.
            Return only the todo items as a JSON array of strings.
            
            Input: {text}
            
            Response format: ["task 1", "task 2", "task 3"]
            """
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Try to parse as JSON
                try:
                    todo_items = json.loads(content)
                    if isinstance(todo_items, list):
                        return todo_items
                except json.JSONDecodeError:
                    # If JSON parsing fails, split by lines and clean up
                    lines = content.split('\n')
                    todo_items = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('[') and not line.startswith(']'):
                            # Remove quotes and numbering
                            line = line.strip('"').strip("'")
                            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*')):
                                line = line[2:].strip()
                            if line:
                                todo_items.append(line)
                    return todo_items if todo_items else None
                
            return None
            
        except Exception:
            return None