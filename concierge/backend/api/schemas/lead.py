from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class LeadCreate(BaseModel):
    session_token: str
    email: str
    name: Optional[str] = None
    interested_tier: Optional[str] = None


class LeadResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None
    interested_tier: Optional[str] = None
    visitor_intent: Optional[str] = None
    crm_synced: bool
    created_at: datetime

    class Config:
        from_attributes = True
