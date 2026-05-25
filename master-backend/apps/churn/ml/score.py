"""
Batch scoring: score all active members and write results to DB.
Called weekly by Airflow DAG.
"""
import numpy as np
from typing import List
from sqlalchemy.orm import Session
from apps.churn.db.models.member import Member
from apps.churn.db.models.churn_score import ChurnScore
from apps.churn.db.models.alert import Alert
from apps.churn.ml.features import members_to_dataframe
from apps.churn.ml.model_registry import load_latest_model
from apps.churn.ml.explain import compute_shap_values
from apps.churn.utils.logger import get_logger

logger = get_logger(__name__)


def score_to_risk_tier(score: float) -> str:
    if score >= 85:
        return "critical"
    elif score >= 70:
        return "high"
    elif score >= 50:
        return "medium"
    return "low"


def run_batch_scoring(db: Session) -> dict:
    members = db.query(Member).filter(Member.is_active == True).all()
    if not members:
        logger.warning("No active members found for scoring.")
        return {}

    logger.info(f"Scoring {len(members)} active members...")
    model, model_version = load_latest_model()
    feature_df = members_to_dataframe(members)
    raw_probs = model.predict_proba(feature_df)[:, 1]
    scores = (raw_probs * 100).round(1)
    shap_results = compute_shap_values(model, feature_df)

    new_scores = []
    new_alerts = []
    for i, member in enumerate(members):
        score_val = float(scores[i])
        tier = score_to_risk_tier(score_val)
        shap_dict = shap_results[i]
        top_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        top_factor_names = [f[0] for f in top_factors]

        churn_score = ChurnScore(
            member_id=member.id,
            score=score_val,
            risk_tier=tier,
            model_version=model_version,
            shap_values=shap_dict,
            top_risk_factors=top_factor_names,
        )
        new_scores.append(churn_score)

        if tier in ("high", "critical"):
            msg = _build_alert_message(member, score_val, top_factor_names)
            alert = Alert(member_id=member.id, risk_tier=tier, message=msg)
            new_alerts.append(alert)

    db.bulk_save_objects(new_scores)
    db.bulk_save_objects(new_alerts)
    db.commit()

    summary = {
        "total_scored": len(members),
        "critical": sum(1 for s in new_scores if s.risk_tier == "critical"),
        "high": sum(1 for s in new_scores if s.risk_tier == "high"),
        "medium": sum(1 for s in new_scores if s.risk_tier == "medium"),
        "low": sum(1 for s in new_scores if s.risk_tier == "low"),
        "alerts_created": len(new_alerts),
        "model_version": model_version,
    }
    logger.info(f"Scoring complete: {summary}")
    return summary


def _build_alert_message(member: Member, score: float, top_factors: List[str]) -> str:
    factor_map = {
        "days_since_last_login": "has not logged in recently",
        "cpe_hours_last_90d": "has completed very few CPE hours recently",
        "email_open_rate_30d": "has very low email engagement",
        "events_attended_ytd": "has not attended any events this year",
        "engagement_score": "shows overall low engagement",
        "at_risk_behavior_count": "shows multiple at-risk behaviors",
        "benefits_used_pct": "is underutilizing membership benefits",
    }
    reasons = [factor_map.get(f, f.replace("_", " ")) for f in top_factors[:2]]
    reason_str = " and ".join(reasons)
    return (
        f"{member.first_name} {member.last_name} ({member.email}) "
        f"has a churn risk score of {score:.0f}/100. "
        f"Primary signals: this member {reason_str}. "
        f"Renewal date: {member.renewal_date.strftime('%b %d, %Y') if member.renewal_date else 'Unknown'}."
    )
