from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class NudgeResponse(BaseModel):
    id: UUID
    member_id: UUID
    product: str
    channel: str
    expansion_score: float
    subject_line: Optional[str]
    message_body: str
    cta_url: str
    cta_label: str
    status: str
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    converted: bool

    class Config:
        from_attributes = True


class SendNudgesRequest(BaseModel):
    dry_run: bool = True
    max_per_product: Optional[int] = None
    product_filter: Optional[str] = None
