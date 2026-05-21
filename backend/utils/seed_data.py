"""
Generate realistic mock member data for training and development.
Uses Faker to produce plausible APhA member records.
"""
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

TIERS = ["student", "new_practitioner", "pharmacist", "technician", "researcher"]
SPECIALTIES = [
    "Community Pharmacy", "Hospital/Health-System", "Ambulatory Care",
    "Long-Term Care", "Managed Care", "Academia", "Industry", "Government",
]
STATES = ["CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI"]


def _make_member_features(churned: bool) -> dict:
    tier = random.choice(TIERS)
    years = random.uniform(0.5, 15)

    if churned:
        days_login = random.uniform(45, 180)
        cpe_90d = random.uniform(0, 3)
        open_rate = random.uniform(0.0, 0.15)
        click_rate = random.uniform(0.0, 0.05)
        events = random.randint(0, 1)
        pubs = random.randint(0, 2)
        renewals = random.randint(0, 2)
        benefits_used = random.uniform(0.0, 0.25)
    else:
        days_login = random.uniform(1, 30)
        cpe_90d = random.uniform(2, 15)
        open_rate = random.uniform(0.2, 0.8)
        click_rate = random.uniform(0.05, 0.3)
        events = random.randint(1, 6)
        pubs = random.randint(3, 20)
        renewals = random.randint(2, 10)
        benefits_used = random.uniform(0.3, 0.9)

    registered = max(events, random.randint(events, events + 3))
    attendance_rate = events / registered if registered > 0 else 0
    login_recency = 1.0 / (1.0 + np.log1p(days_login))
    cpe_velocity = cpe_90d / max(years, 0.1)
    email_score = open_rate * 0.6 + click_rate * 0.4
    engagement = (
        (1 - min(days_login / 90, 1)) * 0.3
        + min(cpe_90d / 10, 1) * 0.25
        + email_score * 0.2
        + attendance_rate * 0.15
        + min(pubs / 5, 1) * 0.1
    )
    at_risk = sum([days_login > 60, cpe_90d < 1, open_rate < 0.1, events == 0, pubs == 0])
    tier_enc = {
        "student": 0, "new_practitioner": 1, "technician": 2,
        "supporter": 3, "pharmacist": 4, "researcher": 5,
    }.get(tier, 4)
    deadline_days = random.randint(30, 400)

    return {
        "days_since_last_login": days_login,
        "cpe_hours_last_90d": cpe_90d,
        "cpe_hours_ytd": cpe_90d * random.uniform(1.5, 4),
        "email_open_rate_30d": open_rate,
        "email_click_rate_30d": click_rate,
        "events_attended_ytd": float(events),
        "events_registered_ytd": float(registered),
        "event_attendance_rate": attendance_rate,
        "publications_read_30d": float(pubs),
        "job_board_searches_30d": float(random.randint(0, 10)),
        "community_posts_90d": float(random.randint(0, 20)),
        "renewal_count": float(renewals),
        "years_as_member": years,
        "cpe_deadline_days": float(deadline_days),
        "benefits_used_pct": benefits_used,
        "tier_encoded": float(tier_enc),
        "is_student": 1.0 if tier == "student" else 0.0,
        "is_pharmacist": 1.0 if tier == "pharmacist" else 0.0,
        "login_recency_score": login_recency,
        "cpe_velocity": cpe_velocity,
        "engagement_score": engagement,
        "email_engagement_score": email_score,
        "renewal_loyalty_flag": 1.0 if renewals >= 3 else 0.0,
        "deadline_urgency_flag": 1.0 if deadline_days < 90 else 0.0,
        "at_risk_behavior_count": float(at_risk),
        "churned": int(churned),
    }


def generate_training_dataset(n_samples: int = 5000) -> pd.DataFrame:
    n_churned = int(n_samples * 0.25)
    n_active = n_samples - n_churned
    rows = (
        [_make_member_features(churned=True) for _ in range(n_churned)]
        + [_make_member_features(churned=False) for _ in range(n_active)]
    )
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def generate_mock_members(n: int = 200):
    members = []
    for _ in range(n):
        churned = random.random() < 0.25
        feats = _make_member_features(churned)
        tier = TIERS[int(feats["tier_encoded"])] if int(feats["tier_encoded"]) < len(TIERS) else "pharmacist"
        join_dt = datetime.now() - timedelta(days=int(feats["years_as_member"] * 365))
        renewal_dt = datetime.now() + timedelta(days=random.randint(30, 365))
        members.append({
            "external_id": f"CRM-{fake.unique.random_int(10000, 99999)}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "tier": tier,
            "state": random.choice(STATES),
            "specialty": random.choice(SPECIALTIES),
            "join_date": join_dt,
            "renewal_date": renewal_dt,
            "is_active": True,
            **{k: v for k, v in feats.items() if k != "churned"},
        })
    return members
