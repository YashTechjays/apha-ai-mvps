from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from uuid import UUID
from backend.db.session import get_db
from backend.db.models.churn_score import ChurnScore
from backend.db.models.member import Member
from backend.api.schemas.score import ScoreResponse, ScoringRunResponse
from backend.api.deps import get_current_user
from backend.ml.score import run_batch_scoring
from backend.ml.explain import get_human_readable_explanation

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/run", response_model=ScoringRunResponse)
def trigger_scoring_run(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    result = run_batch_scoring(db)
    return ScoringRunResponse(**result)


@router.get("/member/{member_id}", response_model=List[ScoreResponse])
def get_member_scores(
    member_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    scores = (
        db.query(ChurnScore)
        .filter(ChurnScore.member_id == member_id)
        .order_by(desc(ChurnScore.scored_at))
        .limit(limit)
        .all()
    )
    return scores


@router.get("/member/{member_id}/explain")
def get_score_explanation(
    member_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    latest = (
        db.query(ChurnScore)
        .filter(ChurnScore.member_id == member_id)
        .order_by(desc(ChurnScore.scored_at))
        .first()
    )
    if not latest or not latest.shap_values:
        return {"factors": []}
    factors = get_human_readable_explanation(latest.shap_values)
    return {"score": latest.score, "risk_tier": latest.risk_tier, "factors": factors}


@router.get("/distribution")
def get_score_distribution(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    subq = (
        db.query(
            ChurnScore.member_id,
            func.max(ChurnScore.scored_at).label("latest"),
        )
        .group_by(ChurnScore.member_id)
        .subquery()
    )
    scores = (
        db.query(ChurnScore.risk_tier, func.count().label("count"))
        .join(
            subq,
            (ChurnScore.member_id == subq.c.member_id)
            & (ChurnScore.scored_at == subq.c.latest),
        )
        .group_by(ChurnScore.risk_tier)
        .all()
    )
    total = db.query(Member).filter(Member.is_active == True).count()
    dist = {row.risk_tier: row.count for row in scores}
    return {
        "total_members": total,
        "critical": dist.get("critical", 0),
        "high": dist.get("high", 0),
        "medium": dist.get("medium", 0),
        "low": dist.get("low", 0),
        "scored": sum(dist.values()),
    }
