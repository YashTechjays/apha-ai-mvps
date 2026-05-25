from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_tier: Optional[str] = None
    target_state: Optional[str] = None
    target_specialty: Optional[str] = None
    target_career_stage: Optional[str] = None
    min_icp_score: float = 60.0
    daily_send_cap: int = 200
    is_dry_run: bool = True


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    status: str
    is_dry_run: bool
    target_tier: Optional[str] = None
    target_state: Optional[str] = None
    min_icp_score: float
    prospects_total: int
    emails_sent: int
    emails_opened: int
    emails_clicked: int
    replies: int
    conversions: int
    created_at: datetime

    class Config:
        from_attributes = True
