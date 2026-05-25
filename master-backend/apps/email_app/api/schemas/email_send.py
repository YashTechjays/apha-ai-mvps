from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EmailSendResponse(BaseModel):
    id: str
    member_id: str
    send_month: str
    subject_line: Optional[str]
    status: str
    qc_score: Optional[float]
    personalization_score: Optional[float]
    token_count: int
    qc_notes: Optional[str]
    total_value_usd: float
    cpe_value_usd: float
    webinar_value_usd: float
    journal_value_usd: float
    pharmacylibrary_value_usd: float
    events_value_usd: float
    opened: bool
    clicked: bool
    click_count: int
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailPreviewResponse(BaseModel):
    member_id: str
    member_email: str
    send_month: str
    subject: str
    preview_text: str
    total_value_usd: float
    roi_multiplier: float
    engagement_level: str
    html_body: str
