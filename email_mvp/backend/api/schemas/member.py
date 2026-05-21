from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MemberResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    tier: str
    is_active: bool
    join_date: Optional[datetime]
    renewal_date: Optional[datetime]
    cpe_credits_ytd: float
    cpe_courses_completed: int
    webinars_attended_ytd: int
    journal_articles_read_ytd: int
    pharmacylibrary_sessions_ytd: int
    annual_meeting_attended: bool
    events_registered_ytd: int
    days_since_last_login: int
    email_open_rate: float
    portal_sessions_last_30d: int

    class Config:
        from_attributes = True
