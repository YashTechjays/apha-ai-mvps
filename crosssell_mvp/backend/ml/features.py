import numpy as np
import pandas as pd
from typing import List
from backend.db.models.member import Member

PRODUCTS = ["education", "publications", "events", "career", "advocacy"]

FEATURE_NAMES = [
    "tenure_years", "renewal_count", "tier_encoded",
    "churn_score_normalized", "active_stream_count",
    "product_usage_score", "product_last_activity_days_norm", "product_already_active",
    "other_streams_active_count",
    "edu_active_flag", "pub_active_flag", "events_active_flag",
    "career_active_flag", "advocacy_active_flag",
    "overall_engagement_score", "email_open_rate", "login_recency_score",
    "is_student", "is_researcher", "is_hospital_pharmacist",
    "times_nudged_this_product", "days_since_last_nudge",
]

TIER_ENCODING = {
    "student": 0, "new_practitioner": 1, "technician": 2,
    "supporter": 3, "pharmacist": 4, "researcher": 5,
}


def _product_usage_score(member: Member, product: str) -> float:
    if product == "education":
        signals = [
            min((member.edu_cpe_hours_ytd or 0) / 20, 1),
            min((member.edu_courses_completed or 0) / 5, 1),
            1.0 if member.edu_active else 0.0,
        ]
    elif product == "publications":
        signals = [
            min((member.pub_articles_read_30d or 0) / 10, 1),
            min((member.pub_pharmacylibrary_sessions or 0) / 5, 1),
            1.0 if member.pub_active else 0.0,
        ]
    elif product == "events":
        signals = [
            min((member.events_attended_ytd or 0) / 4, 1),
            1.0 if member.events_annual_meeting_attended else 0.0,
            1.0 if member.events_active else 0.0,
        ]
    elif product == "career":
        signals = [
            min((member.career_job_searches or 0) / 10, 1),
            (member.career_profile_complete_pct or 0) / 100,
            1.0 if member.career_active else 0.0,
        ]
    elif product == "advocacy":
        signals = [
            min((member.advocacy_action_center_visits or 0) / 5, 1),
            min((member.advocacy_letters_sent or 0) / 3, 1),
            1.0 if member.advocacy_active else 0.0,
        ]
    else:
        return 0.0
    return float(np.mean(signals))


def extract_features(member: Member, product: str, nudge_history: dict = None) -> dict:
    tier = member.tier if isinstance(member.tier, str) else str(member.tier)
    nudge_history = nudge_history or {"times_nudged": 0, "days_since_last_nudge": 999}
    usage_score = _product_usage_score(member, product)
    last_activity = {
        "education": member.edu_last_activity_days,
        "publications": member.pub_last_activity_days,
        "events": member.events_last_attended_days,
        "career": 999.0,
        "advocacy": 999.0,
    }.get(product, 999.0) or 999.0
    active_flags = {
        "education": float(member.edu_active or False),
        "publications": float(member.pub_active or False),
        "events": float(member.events_active or False),
        "career": float(member.career_active or False),
        "advocacy": float(member.advocacy_active or False),
    }
    other_active = sum(v for k, v in active_flags.items() if k != product)
    overall_engagement = float(np.mean(list(active_flags.values())))
    login_recency = 1.0 / (1.0 + np.log1p(last_activity))
    return {
        "tenure_years": float(member.years_as_member or 0),
        "renewal_count": float(member.renewal_count or 0),
        "tier_encoded": float(TIER_ENCODING.get(tier, 4)),
        "churn_score_normalized": float((member.churn_score or 50) / 100),
        "active_stream_count": float(member.active_stream_count or 0),
        "product_usage_score": usage_score,
        "product_last_activity_days_norm": min(last_activity / 365, 1),
        "product_already_active": active_flags[product],
        "other_streams_active_count": other_active,
        "edu_active_flag": active_flags["education"],
        "pub_active_flag": active_flags["publications"],
        "events_active_flag": active_flags["events"],
        "career_active_flag": active_flags["career"],
        "advocacy_active_flag": active_flags["advocacy"],
        "overall_engagement_score": overall_engagement,
        "email_open_rate": float(getattr(member, "email_open_rate_30d", 0.3) or 0.3),
        "login_recency_score": login_recency,
        "is_student": 1.0 if tier == "student" else 0.0,
        "is_researcher": 1.0 if tier == "researcher" else 0.0,
        "is_hospital_pharmacist": 1.0 if (member.specialty or "").lower().startswith("hospital") else 0.0,
        "times_nudged_this_product": float(nudge_history["times_nudged"]),
        "days_since_last_nudge": min(float(nudge_history["days_since_last_nudge"]) / 90, 1),
    }


def members_to_dataframe(members: List[Member], product: str, nudge_histories: dict = None) -> pd.DataFrame:
    nudge_histories = nudge_histories or {}
    rows = [
        extract_features(m, product, nudge_histories.get(str(m.id), {}))
        for m in members
    ]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)
