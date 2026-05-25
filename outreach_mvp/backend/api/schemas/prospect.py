from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProspectResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    credential: Optional[str] = None
    license_type: str
    specialty: Optional[str] = None
    practice_setting: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    icp_score: Optional[float] = None
    icp_tier: Optional[str] = None
    status: str
    emails_sent: int
    last_email_sent_at: Optional[datetime] = None
    last_opened_at: Optional[datetime] = None
    last_clicked_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
