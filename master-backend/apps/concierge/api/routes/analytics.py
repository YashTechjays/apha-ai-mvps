from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from apps.concierge.db.session import get_db
from apps.concierge.db.models.conversation import Conversation
from apps.concierge.db.models.lead import Lead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_convs = db.query(Conversation).count()
    leads = db.query(Lead).count()
    converted = db.query(Conversation).filter(Conversation.converted == True).count()
    avg_turns = db.query(func.avg(Conversation.turn_count)).scalar() or 0

    intent_counts = (
        db.query(Conversation.detected_intent, func.count().label("count"))
        .group_by(Conversation.detected_intent)
        .all()
    )
    tier_counts = (
        db.query(Conversation.recommended_tier, func.count().label("count"))
        .filter(Conversation.recommended_tier != None)
        .group_by(Conversation.recommended_tier)
        .all()
    )

    return {
        "total_conversations": total_convs,
        "leads_captured": leads,
        "conversions": converted,
        "lead_capture_rate": round(leads / total_convs, 3) if total_convs > 0 else 0,
        "avg_turns_per_conversation": round(float(avg_turns), 1),
        "intent_breakdown": {row.detected_intent: row.count for row in intent_counts},
        "tier_recommendations": {row.recommended_tier: row.count for row in tier_counts},
    }
