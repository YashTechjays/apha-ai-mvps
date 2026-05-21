from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc as sqldesc
from backend.db.models.member import Member
from backend.db.models.crosssell_score import CrossSellScore
from backend.db.models.nudge import Nudge
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def should_send_nudge(member: Member, product: str, score: float, db: Session) -> tuple[bool, str]:
    if score < settings.min_expansion_score_to_nudge:
        return False, f"Score {score:.0f} below threshold {settings.min_expansion_score_to_nudge}"

    active_flag = getattr(member, f"{product}_active", False)
    if active_flag:
        return False, f"Member already active on {product}"

    month_ago = datetime.utcnow() - timedelta(days=30)
    monthly_count = db.query(Nudge).filter(
        Nudge.member_id == member.id,
        Nudge.sent_at >= month_ago,
        Nudge.status == "sent",
    ).count()
    if monthly_count >= settings.max_nudges_per_member_per_month:
        return False, f"Monthly cap reached ({monthly_count} nudges sent)"

    cooldown_ago = datetime.utcnow() - timedelta(days=settings.nudge_cooldown_days)
    recent = db.query(Nudge).filter(
        Nudge.member_id == member.id,
        Nudge.product == product,
        Nudge.sent_at >= cooldown_ago,
    ).first()
    if recent:
        return False, f"Cooldown active for {product}"

    if (member.churn_score or 0) >= 90:
        return False, f"Churn score too high ({member.churn_score}) — defer to retention team"

    return True, "OK"


def pick_channel(member: Member, score: float) -> str:
    if score >= 80:
        return "email"
    return "banner"


def get_top_opportunity(member: Member, db: Session) -> tuple:
    scores = (
        db.query(CrossSellScore)
        .filter(
            CrossSellScore.member_id == member.id,
            CrossSellScore.already_active == False,
        )
        .order_by(sqldesc(CrossSellScore.score))
        .all()
    )
    for score in scores:
        should, reason = should_send_nudge(member, score.product, score.score, db)
        if should:
            return score, pick_channel(member, score.score)
        logger.debug(f"Skipped {member.id}×{score.product}: {reason}")
    return None, None
