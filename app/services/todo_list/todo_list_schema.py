#!/usr/bin/env python3
"""
Todo List Schema
Pydantic models for todo list API
"""

from pydantic import BaseModel
from typing import List, Optional

class TodoListResponse(BaseModel):
    """Response model for todo list generation"""
    success: bool
    todo_items: Optional[List[str]] = None
    message: str
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }

class TodoError(BaseModel):
    """Error response model for todo list operations"""
    error_code: str
    message: str