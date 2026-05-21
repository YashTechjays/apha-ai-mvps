from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class ScoreResponse(BaseModel):
    id: UUID
    member_id: UUID
    score: float
    risk_tier: str
    model_version: str
    top_risk_factors: Optional[List[str]] = []
    shap_values: Optional[Dict[str, float]] = {}
    scored_at: datetime

    class Config:
        from_attributes = True


class ScoringRunResponse(BaseModel):
    total_scored: int
    critical: int
    high: int
    medium: int
    low: int
    alerts_created: int
    model_version: str
