"""SHAP explanations for individual member scores."""
import shap
import numpy as np
import pandas as pd
from typing import List, Dict
from backend.ml.features import FEATURE_NAMES


def compute_shap_values(model, feature_df: pd.DataFrame) -> List[Dict[str, float]]:
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(feature_df)
    results = []
    for i in range(len(feature_df)):
        row_shap = {
            feat: round(float(shap_vals[i][j]), 4)
            for j, feat in enumerate(FEATURE_NAMES)
        }
        results.append(row_shap)
    return results


def get_human_readable_explanation(shap_dict: Dict[str, float], top_n: int = 5) -> List[dict]:
    LABELS = {
        "days_since_last_login": "Days since last login",
        "cpe_hours_last_90d": "CPE hours (last 90 days)",
        "email_open_rate_30d": "Email open rate (30 days)",
        "email_click_rate_30d": "Email click rate (30 days)",
        "events_attended_ytd": "Events attended (YTD)",
        "engagement_score": "Overall engagement score",
        "benefits_used_pct": "Benefits utilization %",
        "renewal_count": "Renewal history",
        "login_recency_score": "Login recency",
        "at_risk_behavior_count": "At-risk behavior signals",
        "cpe_deadline_days": "Days until CPE deadline",
        "community_posts_90d": "Community activity (90 days)",
    }
    sorted_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    return [
        {
            "feature": feat,
            "label": LABELS.get(feat, feat.replace("_", " ").title()),
            "impact": abs(val),
            "direction": "increases_risk" if val > 0 else "decreases_risk",
        }
        for feat, val in sorted_factors
    ]
