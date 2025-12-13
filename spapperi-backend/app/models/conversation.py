"""
Pydantic models for conversation data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """Incoming chat message from user"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response to user with AI message and metadata"""
    response: str
    conversation_id: str
    current_phase: str
    image_url: Optional[str] = None
    is_complete: bool = False
    export_file: Optional[str] = None
    ui_type: Optional[str] = None  # "text" or "checkbox"
    options: Optional[List[str]] = None  # Available options for checkbox


class Message(BaseModel):
    """Single message in conversation history"""
    id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant", "system"]
    content: str
    image_url: Optional[str] = None
    created_at: datetime


class Conversation(BaseModel):
    """Conversation metadata"""
    id: UUID
    user_id: Optional[UUID] = None
    current_phase: str = "phase_1_1"
    status: Literal["active", "completed", "abandoned"] = "active"
    created_at: datetime
    updated_at: datetime
