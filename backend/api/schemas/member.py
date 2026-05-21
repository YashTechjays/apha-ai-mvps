from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MemberBase(BaseModel):
    external_id: str
    first_name: str
    last_name: str
    email: str
    tier: str
    state: Optional[str] = None
    specialty: Optional[str] = None
    renewal_date: Optional[datetime] = None


class MemberResponse(MemberBase):
    id: UUID
    is_active: bool
    years_as_member: float
    renewal_count: int
    churn_score: Optional[float] = None
    risk_tier: Optional[str] = None
    top_risk_factors: Optional[List[str]] = None
    days_since_last_login: Optional[float] = None
    cpe_hours_last_90d: Optional[float] = None
    email_open_rate_30d: Optional[float] = None
    events_attended_ytd: Optional[int] = None
    publications_read_30d: Optional[int] = None
    community_posts_90d: Optional[int] = None

    class Config:
        from_attributes = True
