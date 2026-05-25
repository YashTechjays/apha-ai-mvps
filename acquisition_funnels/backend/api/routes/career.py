import json

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.usage import ToolUsage
from backend.db.models.lead import Lead
from backend.api.schemas.career import CareerProfile, CareerScoreResponse
from backend.ai.career_engine import score_career, generate_action_plan
from backend.rate_limiter.redis_limiter import check_limit
from backend.utils.logger import get_logger

router = APIRouter(prefix="/career", tags=["career"])
logger = get_logger(__name__)


@router.post("/score", response_model=CareerScoreResponse)
def score_career_readiness(
    req: CareerProfile, request: Request, db: Session = Depends(get_db)
):
    ip = request.client.host or "unknown"
    allowed, rate_info = check_limit(ip, "career")

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "You've used your free career assessment for today.",
                "upgrade_message": "Join APhA for unlimited assessments and your personalized action plan.",
                "join_url": "https://www.pharmacist.com/join",
            },
        )

    profile = req.model_dump()
    scores = score_career(profile)
    action_plan = generate_action_plan(profile, scores)

    usage = ToolUsage(
        session_id=req.session_id,
        ip_hash=ip[:8],
        tool="career",
        input_summary=f"{req.license_type} / {req.specialty} / {req.career_stage}",
        result_score=float(scores.get("overall_score", 0)),
        result_summary=json.dumps(action_plan),
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)

    action_plan_preview = (
        f"Your top opportunity: {scores.get('top_gap_note', '')} "
        f"Unlock your full 90-day plan."
    )

    return CareerScoreResponse(
        usage_id=str(usage.id),
        overall_score=scores.get("overall_score", 0),
        scores=scores.get("scores", {}),
        summary=scores.get("summary", ""),
        top_strength=scores.get("top_strength", ""),
        top_strength_note=scores.get("top_strength_note", ""),
        top_gap=scores.get("top_gap", ""),
        top_gap_note=scores.get("top_gap_note", ""),
        peer_percentile=scores.get("peer_percentile", 50),
        trajectory=scores.get("trajectory", "On track"),
        action_plan_locked=True,
        action_plan_preview=action_plan_preview,
    )


@router.get("/action-plan/{usage_id}")
def get_action_plan(usage_id: str, session_id: str, db: Session = Depends(get_db)):
    """Return full action plan after lead is captured."""
    lead = db.query(Lead).filter(Lead.session_id == session_id).first()
    if not lead:
        raise HTTPException(
            status_code=403, detail="Email capture required to unlock action plan"
        )

    usage = db.query(ToolUsage).filter(ToolUsage.id == usage_id).first()
    if not usage:
        raise HTTPException(status_code=404, detail="Assessment not found")

    try:
        plan = json.loads(usage.result_summary)
        return {"action_plan": plan, "unlocked": True}
    except Exception:
        raise HTTPException(status_code=500, detail="Could not retrieve action plan")
