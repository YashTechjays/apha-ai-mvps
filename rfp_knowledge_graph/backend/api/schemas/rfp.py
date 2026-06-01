from pydantic import BaseModel
from typing import Optional


class RfpSummary(BaseModel):
    id: str
    title: str
    description: str = ""
    deadline: Optional[str] = None
    posted_date: Optional[str] = None
    status: str = "open"
    url: str = ""
    budget_range: Optional[str] = None
    organization_name: Optional[str] = None
    location: Optional[str] = None
    categories: list[str] = []
    match_score: Optional[int] = None


class OrganizationDetail(BaseModel):
    name: str
    type: Optional[str] = None
    website: Optional[str] = None


class LocationDetail(BaseModel):
    name: str
    state: Optional[str] = None
    city: Optional[str] = None


class RfpDetail(BaseModel):
    id: str
    title: str
    description: str = ""
    deadline: Optional[str] = None
    posted_date: Optional[str] = None
    status: str = "open"
    url: str = ""
    source_url: str = ""
    budget_range: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    organization: Optional[OrganizationDetail] = None
    location: Optional[LocationDetail] = None
    categories: list[str] = []
    requirements: list[str] = []
    similar_rfps: list[RfpSummary] = []


class RfpListResponse(BaseModel):
    items: list[RfpSummary]
    total: int
