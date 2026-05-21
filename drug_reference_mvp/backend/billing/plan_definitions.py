"""Plan definitions for APhA Clinical Assistant B2B SaaS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Plan:
    code: str
    name: str
    monthly_price_usd: float
    queries_per_month: int
    rate_limit_per_minute: int
    seats: int
    api_access: bool
    features: List[str] = field(default_factory=list)
    stripe_price_id_env: Optional[str] = None


PLANS: Dict[str, Plan] = {
    "trial": Plan(
        code="trial",
        name="Free Trial",
        monthly_price_usd=0.0,
        queries_per_month=10,
        rate_limit_per_minute=2,
        seats=1,
        api_access=False,
        features=[
            "10 queries / month",
            "Single user",
            "Web interface only",
            "Email support",
        ],
    ),
    "individual": Plan(
        code="individual",
        name="Individual Pharmacist",
        monthly_price_usd=99.0,
        queries_per_month=500,
        rate_limit_per_minute=10,
        seats=1,
        api_access=False,
        features=[
            "500 queries / month",
            "Single user",
            "Full APhA reference library",
            "Citation tracking",
            "Email support",
        ],
        stripe_price_id_env="STRIPE_PRICE_INDIVIDUAL",
    ),
    "team": Plan(
        code="team",
        name="Pharmacy Team",
        monthly_price_usd=299.0,
        queries_per_month=2500,
        rate_limit_per_minute=30,
        seats=10,
        api_access=True,
        features=[
            "2,500 queries / month (shared pool)",
            "Up to 10 seats",
            "API access (10 keys included)",
            "Usage analytics dashboard",
            "Priority email support",
        ],
        stripe_price_id_env="STRIPE_PRICE_TEAM",
    ),
    "institution": Plan(
        code="institution",
        name="Health-System / Institution",
        monthly_price_usd=799.0,
        queries_per_month=15000,
        rate_limit_per_minute=120,
        seats=50,
        api_access=True,
        features=[
            "15,000 queries / month",
            "Up to 50 seats",
            "API access (unlimited keys)",
            "SSO (SAML/OIDC) — coming soon",
            "Advanced analytics",
            "Dedicated success manager",
        ],
        stripe_price_id_env="STRIPE_PRICE_INSTITUTION",
    ),
    "enterprise": Plan(
        code="enterprise",
        name="Enterprise",
        monthly_price_usd=0.0,  # Custom quote
        queries_per_month=1_000_000,
        rate_limit_per_minute=1000,
        seats=10000,
        api_access=True,
        features=[
            "Custom query volume",
            "Unlimited seats",
            "Custom content ingestion",
            "On-prem / private cloud deployment available",
            "Custom SLA",
            "24/7 support",
        ],
        stripe_price_id_env="STRIPE_PRICE_ENTERPRISE",
    ),
}


def get_plan(code: str) -> Plan:
    return PLANS.get(code, PLANS["trial"])


def list_plans() -> List[Plan]:
    return list(PLANS.values())
