import pandas as pd
import numpy as np
from typing import List
from apps.churn.db.models.member import Member

FEATURE_NAMES = [
    "days_since_last_login",
    "cpe_hours_last_90d",
    "cpe_hours_ytd",
    "email_open_rate_30d",
    "email_click_rate_30d",
    "events_attended_ytd",
    "events_registered_ytd",
    "event_attendance_rate",
    "publications_read_30d",
    "job_board_searches_30d",
    "community_posts_90d",
    "renewal_count",
    "years_as_member",
    "cpe_deadline_days",
    "benefits_used_pct",
    "tier_encoded",
    "is_student",
    "is_pharmacist",
    "login_recency_score",
    "cpe_velocity",
    "engagement_score",
    "email_engagement_score",
    "renewal_loyalty_flag",
    "deadline_urgency_flag",
    "at_risk_behavior_count",
]

TIER_ENCODING = {
    "student": 0,
    "new_practitioner": 1,
    "technician": 2,
    "supporter": 3,
    "pharmacist": 4,
    "researcher": 5,
}


def extract_features(member: Member) -> dict:
    tier = member.tier.value if hasattr(member.tier, "value") else str(member.tier)
    days = float(member.days_since_last_login or 0)
    years = float(member.years_as_member or 0)
    cpe_90d = float(member.cpe_hours_last_90d or 0)
    open_rate = float(member.email_open_rate_30d or 0)
    click_rate = float(member.email_click_rate_30d or 0)
    attended = int(member.events_attended_ytd or 0)
    registered = int(member.events_registered_ytd or 0)
    attendance_rate = attended / registered if registered > 0 else 0.0
    login_recency = 1.0 / (1.0 + np.log1p(days))
    cpe_velocity = cpe_90d / max(years, 0.1)
    email_score = open_rate * 0.6 + click_rate * 0.4
    engagement = (
        (1 - min(days / 90, 1)) * 0.3
        + min(cpe_90d / 10, 1) * 0.25
        + email_score * 0.2
        + attendance_rate * 0.15
        + min(float(member.publications_read_30d or 0) / 5, 1) * 0.1
    )
    at_risk_count = sum([
        days > 60,
        cpe_90d < 1,
        open_rate < 0.1,
        attended == 0,
        float(member.publications_read_30d or 0) == 0,
    ])

    return {
        "days_since_last_login": days,
        "cpe_hours_last_90d": cpe_90d,
        "cpe_hours_ytd": float(member.cpe_hours_ytd or 0),
        "email_open_rate_30d": open_rate,
        "email_click_rate_30d": click_rate,
        "events_attended_ytd": float(attended),
        "events_registered_ytd": float(registered),
        "event_attendance_rate": attendance_rate,
        "publications_read_30d": float(member.publications_read_30d or 0),
        "job_board_searches_30d": float(member.job_board_searches_30d or 0),
        "community_posts_90d": float(member.community_posts_90d or 0),
        "renewal_count": float(member.renewal_count or 0),
        "years_as_member": years,
        "cpe_deadline_days": float(member.cpe_deadline_days or 365),
        "benefits_used_pct": float(member.benefits_used_pct or 0),
        "tier_encoded": float(TIER_ENCODING.get(tier, 4)),
        "is_student": 1.0 if tier == "student" else 0.0,
        "is_pharmacist": 1.0 if tier == "pharmacist" else 0.0,
        "login_recency_score": login_recency,
        "cpe_velocity": cpe_velocity,
        "engagement_score": engagement,
        "email_engagement_score": email_score,
        "renewal_loyalty_flag": 1.0 if (member.renewal_count or 0) >= 3 else 0.0,
        "deadline_urgency_flag": 1.0 if (member.cpe_deadline_days or 365) < 90 else 0.0,
        "at_risk_behavior_count": float(at_risk_count),
    }


def members_to_dataframe(members: List[Member]) -> pd.DataFrame:
    rows = [extract_features(m) for m in members]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)
