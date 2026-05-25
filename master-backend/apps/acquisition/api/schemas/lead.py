from pydantic import BaseModel
from typing import Optional


class LeadCreate(BaseModel):
    session_id: str
    email: str
    name: Optional[str] = None
    source_tool: str
    usage_id: Optional[str] = None
    # Tool-specific data for email personalization
    state: Optional[str] = None
    specialty: Optional[str] = None
    license_type: Optional[str] = None
    career_stage: Optional[str] = None
    salary_percentile: Optional[int] = None
    salary_gap_usd: Optional[int] = None
    career_score: Optional[int] = None
    top_gap_dimension: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    email: str
    unlocked: bool
    message: str
    next_action_url: str
