from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationCreateRequest(BaseModel):
    proposal_text: Optional[str] = None
    notes: Optional[str] = None
    status: str = "draft"


class ApplicationUpdateRequest(BaseModel):
    status: Optional[str] = None
    proposal_text: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: str
    rfp_id: str
    status: str
    proposal_text: Optional[str] = None
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Enriched from Neo4j
    rfp_title: Optional[str] = None
    rfp_deadline: Optional[str] = None
    rfp_org: Optional[str] = None

    class Config:
        from_attributes = True
