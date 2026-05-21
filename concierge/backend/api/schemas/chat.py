from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    session_token: str
    message: str
    page_url: Optional[str] = None
    visitor_name: Optional[str] = None


class ChatResponse(BaseModel):
    session_token: str
    response: str
    intent: str
    turn_count: int
    should_capture_lead: bool
    tier_recommendation: Optional[str] = None
    join_url: Optional[str] = None


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: UUID
    session_token: str
    visitor_email: Optional[str] = None
    detected_intent: Optional[str] = None
    recommended_tier: Optional[str] = None
    status: str
    turn_count: int
    lead_captured: bool
    converted: bool
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True
