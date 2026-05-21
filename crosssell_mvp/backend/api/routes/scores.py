from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.db.models.crosssell_score import CrossSellScore
from backend.api.schemas.score import CrossSellScoreResponse, MemberExpansionProfile
from backend.api.deps import get_current_user
from backend.ml.score import run_batch_scoring

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/run")
def trigger_scoring(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return run_batch_scoring(db)


@router.get("/members", response_model=List[MemberExpansionProfile])
def list_member_expansion_profiles(
    min_opportunity_score: float = 60,
    product: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    members = db.query(Member).filter(Member.is_active == True).limit(limit).all()
    profiles = []
    for member in members:
        scores_q = db.query(CrossSellScore).filter(
            CrossSellScore.member_id == member.id,
            CrossSellScore.already_active == False,
        )
        if product:
            scores_q = scores_q.filter(CrossSellScore.product == product)
        all_scores = scores_q.order_by(desc(CrossSellScore.score)).all()
        if not all_scores:
            continue
        top = all_scores[0]
        if top.score < min_opportunity_score:
            continue
        product_scores = {s.product: s.score for s in all_scores}
        profiles.append(MemberExpansionProfile(
            member_id=member.id,
            first_name=member.first_name,
            last_name=member.last_name,
            email=member.email,
            tier=member.tier or "pharmacist",
            active_stream_count=member.active_stream_count or 0,
            churn_score=member.churn_score,
            top_opportunity_product=top.product,
            top_opportunity_score=top.score,
            product_scores=product_scores,
        ))
    profiles.sort(key=lambda x: x.top_opportunity_score or 0, reverse=True)
    return profiles


@router.get("/member/{member_id}", response_model=List[CrossSellScoreResponse])
def get_member_scores(member_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(CrossSellScore).filter(
        CrossSellScore.member_id == member_id
    ).order_by(desc(CrossSellScore.score)).all()
