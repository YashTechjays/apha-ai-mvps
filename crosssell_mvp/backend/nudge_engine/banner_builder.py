from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.db.models.nudge import Nudge
from backend.db.models.crosssell_score import CrossSellScore
from backend.ai.message_generator import generate_banner_nudge
from backend.utils.logger import get_logger

logger = get_logger(__name__)

PRODUCT_ICONS = {
    "education": "🎓",
    "publications": "📖",
    "events": "🎪",
    "career": "💼",
    "advocacy": "🏛️",
}


def build_banner(member: Member, score: CrossSellScore, db: Session) -> dict:
    content = generate_banner_nudge(member, score)

    nudge = Nudge(
        member_id=member.id,
        product=score.product,
        channel="banner",
        expansion_score=score.score,
        message_body=content.get("body", ""),
        cta_url=content["cta_url"],
        cta_label=content["cta_label"],
        status="sent",
    )
    db.add(nudge)
    db.commit()
    db.refresh(nudge)

    logger.info(f"[BANNER] Member {member.id} | Product: {score.product} | Score: {score.score}")
    return {
        "nudge_id": str(nudge.id),
        "product": score.product,
        "icon": PRODUCT_ICONS.get(score.product, "✨"),
        "headline": content.get("headline", f"Explore {score.product.title()}"),
        "body": content.get("body", ""),
        "cta_label": content["cta_label"],
        "cta_url": content["cta_url"],
        "expansion_score": score.score,
    }
