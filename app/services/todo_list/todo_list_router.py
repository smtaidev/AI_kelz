#!/usr/bin/env python3
"""
Todo List Router
FastAPI router for todo list voice processing endpoints
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.services.todo_list.todo_list_schema import TodoListResponse, TodoError
from app.services.todo_list.todo_list import TodoListGenerator

router = APIRouter()

@router.post("/voice-to-todo/", response_model=TodoListResponse)
async def voice_to_todo(audio_file: UploadFile = File(...)):
    """
    Convert voice input to todo list
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Generate todo list from voice
            generator = TodoListGenerator()
            todo_items = generator.generate_todo_from_voice(tmp_file_path)
            
            if todo_items:
                return TodoListResponse(
                    success=True,
                    todo_items=todo_items,
                    message="Todo list generated successfully"
                )
            else:
                return TodoListResponse(
                    success=False,
                    todo_items=None,
                    message="Failed to generate todo list from audio"
                )
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing audio"
        )

@router.get("/health/")
def todo_health_check():
    """
    Health check endpoint for todo service
    """
    return {
        "status": "healthy",
        "service": "todo-list",
        "message": "Todo list service is running normally"
    }