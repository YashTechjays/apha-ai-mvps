from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


class CrossSellScoreResponse(BaseModel):
    id: UUID
    member_id: UUID
    product: str
    score: float
    already_active: bool
    top_reasons: Optional[List[str]] = []
    scored_at: datetime

    class Config:
        from_attributes = True


class MemberExpansionProfile(BaseModel):
    member_id: UUID
    first_name: str
    last_name: str
    email: str
    tier: str
    active_stream_count: int
    churn_score: Optional[float]
    top_opportunity_product: Optional[str]
    top_opportunity_score: Optional[float]
    product_scores: Dict[str, float]
