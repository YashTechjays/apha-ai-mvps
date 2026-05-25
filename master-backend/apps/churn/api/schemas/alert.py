from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AlertResponse(BaseModel):
    id: UUID
    member_id: UUID
    risk_tier: str
    message: str
    is_resolved: bool
    outcome: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_resolved: bool
    resolved_by: Optional[str] = None
    outcome: Optional[str] = None
