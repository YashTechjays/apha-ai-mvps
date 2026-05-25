"""Pydantic schemas for subscription / billing endpoints."""
from typing import Optional, List
from pydantic import BaseModel


class PlanInfo(BaseModel):
    code: str
    name: str
    monthly_price_usd: float
    queries_per_month: int
    rate_limit_per_minute: int
    seats: int
    api_access: bool
    features: List[str]


class CheckoutRequest(BaseModel):
    plan_code: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    mock: bool = False


class SubscriptionStatus(BaseModel):
    plan: str
    status: str
    queries_used_this_month: int
    queries_limit_per_month: int
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
