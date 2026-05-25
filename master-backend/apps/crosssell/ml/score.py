from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from apps.crosssell.db.models.member import Member
from apps.crosssell.db.models.crosssell_score import CrossSellScore
from apps.crosssell.db.models.nudge import Nudge
from apps.crosssell.ml.features import members_to_dataframe, FEATURE_NAMES, PRODUCTS, _product_usage_score
from apps.crosssell.ml.model_registry import load_models
from apps.crosssell.utils.logger import get_logger
from apps.crosssell.utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


def _score_to_reasons(member: Member, product: str, score: float) -> list:
    reasons = []
    if product == "education":
        if (member.edu_cpe_hours_ytd or 0) < 5:
            reasons.append("Has completed fewer CPE hours than peers with similar tenure")
        if (member.edu_certificates_earned or 0) == 0:
            reasons.append("Has not earned any certificate credentials yet")
        if member.events_active:
            reasons.append("Active events attendee — likely interested in structured learning")
    elif product == "publications":
        if (member.edu_cpe_hours_ytd or 0) > 5:
            reasons.append("Active CPE learner — publications align with learning behavior")
        if member.tier in ("researcher", "pharmacist"):
            reasons.append("Member tier typically has high publication engagement")
    elif product == "events":
        if (member.edu_courses_completed or 0) > 2:
            reasons.append("Strong CPE engagement suggests interest in live learning")
        if (member.years_as_member or 0) > 2 and not member.events_annual_meeting_attended:
            reasons.append("Multi-year member who has never attended Annual Meeting")
    elif product == "career":
        if member.tier in ("new_practitioner", "student"):
            reasons.append("Career stage aligns strongly with career service needs")
        if (member.years_as_member or 0) < 3:
            reasons.append("Early-career members see high value from job board and ADVANCE")
    elif product == "advocacy":
        if (member.edu_cpe_hours_ytd or 0) > 8:
            reasons.append("Highly engaged member — advocacy is the next natural step")
        if member.tier == "pharmacist":
            reasons.append("Full pharmacist members are most impacted by advocacy outcomes")
    if not reasons:
        reasons.append(f"Low current engagement with {product.title()} — high growth potential")
    return reasons[:3]


def run_batch_scoring(db: Session) -> dict:
    members = db.query(Member).filter(Member.is_active == True).all()
    if not members:
        return {"error": "No active members found"}

    logger.info(f"Scoring {len(members)} members across {len(PRODUCTS)} products...")
    models = load_models()

    nudge_histories = {}
    for product in PRODUCTS:
        for member in members:
            key = (str(member.id), product)
            last_nudge = (
                db.query(Nudge)
                .filter(Nudge.member_id == member.id, Nudge.product == product)
                .order_by(desc(Nudge.sent_at))
                .first()
            )
            days_since = 999
            times_nudged = db.query(Nudge).filter(
                Nudge.member_id == member.id, Nudge.product == product
            ).count()
            if last_nudge and last_nudge.sent_at:
                days_since = (datetime.utcnow() - last_nudge.sent_at).days
            nudge_histories[key] = {
                "times_nudged": times_nudged,
                "days_since_last_nudge": days_since,
            }

    scores_created = 0
    product_stats = {p: {"scored": 0, "already_active": 0} for p in PRODUCTS}

    for product in PRODUCTS:
        model = models.get(product)
        if not model:
            logger.warning(f"No model for product {product} — skipping")
            continue

        nudge_hist = {str(m.id): nudge_histories.get((str(m.id), product), {}) for m in members}
        feature_df = members_to_dataframe(members, product, nudge_hist)
        raw_probs = model.predict_proba(feature_df)[:, 1]
        scores = (raw_probs * 100).round(1)

        for i, member in enumerate(members):
            already_active = bool(_product_usage_score(member, product) > 0.3)
            score_val = float(scores[i])
            reasons = _score_to_reasons(member, product, score_val)
            feature_snapshot = {
                k: round(float(feature_df.iloc[i][k]), 3) for k in FEATURE_NAMES[:10]
            }
            cs = CrossSellScore(
                member_id=member.id,
                product=product,
                score=score_val,
                already_active=already_active,
                top_reasons=reasons,
                feature_values=feature_snapshot,
                model_version=f"{product}_v1",
            )
            db.add(cs)
            scores_created += 1
            product_stats[product]["scored"] += 1
            if already_active:
                product_stats[product]["already_active"] += 1

    db.commit()
    summary = {
        "members_scored": len(members),
        "score_records_created": scores_created,
        "product_breakdown": product_stats,
    }
    logger.info(f"Scoring complete: {summary}")
    return summary
