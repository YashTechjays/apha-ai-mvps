from pydantic import BaseModel
from typing import Optional


class LeadCreate(BaseModel):
    session_id: str
    email: str
    name: Optional[str] = None
    calculation_id: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    email: str
    message: str
