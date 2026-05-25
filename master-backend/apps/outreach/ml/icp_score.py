"""Batch score all unscored prospects."""
from datetime import datetime
from sqlalchemy.orm import Session
from apps.outreach.db.models.prospect import Prospect
from apps.outreach.ml.icp_features import prospects_to_dataframe
from apps.outreach.ml.model_registry import load_icp_model
from apps.outreach.utils.logger import get_logger
from apps.outreach.utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


def score_to_tier(score: float) -> str:
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    return "C"


def run_icp_scoring(db: Session, force_rescore: bool = False) -> dict:
    """Score all prospects. force_rescore=True rescores already-scored prospects."""
    query = db.query(Prospect).filter(
        Prospect.do_not_contact == False,
        Prospect.status.notin_(["unsubscribed", "bounced", "excluded"])
    )
    if not force_rescore:
        query = query.filter(Prospect.icp_score == None)

    prospects = query.all()
    if not prospects:
        logger.info("No prospects to score")
        return {"scored": 0}

    logger.info(f"Scoring {len(prospects)} prospects...")
    model = load_icp_model()
    feature_df = prospects_to_dataframe(prospects)
    raw_probs = model.predict_proba(feature_df)[:, 1]
    scores = (raw_probs * 100).round(1)

    for i, prospect in enumerate(prospects):
        prospect.icp_score = float(scores[i])
        prospect.icp_tier = score_to_tier(prospect.icp_score)
        prospect.icp_scored_at = datetime.utcnow()
        if prospect.status == "new":
            prospect.status = "scored"

    db.commit()
    summary = {
        "scored": len(prospects),
        "tier_a": sum(1 for p in prospects if p.icp_tier == "A"),
        "tier_b": sum(1 for p in prospects if p.icp_tier == "B"),
        "tier_c": sum(1 for p in prospects if p.icp_tier == "C"),
    }
    logger.info(f"ICP scoring complete: {summary}")
    return summary
