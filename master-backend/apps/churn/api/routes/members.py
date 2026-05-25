from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from apps.churn.db.session import get_db
from apps.churn.db.models.member import Member
from apps.churn.db.models.churn_score import ChurnScore
from apps.churn.api.schemas.member import MemberResponse
from apps.churn.api.deps import get_current_user

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/", response_model=List[MemberResponse])
def list_members(
    risk_tier: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Member).filter(Member.is_active == True)
    if tier:
        query = query.filter(Member.tier == tier)
    members = query.offset(offset).limit(limit).all()

    result = []
    for m in members:
        latest_score = (
            db.query(ChurnScore)
            .filter(ChurnScore.member_id == m.id)
            .order_by(desc(ChurnScore.scored_at))
            .first()
        )
        resp = MemberResponse.model_validate(m)
        if latest_score:
            resp.churn_score = latest_score.score
            resp.risk_tier = latest_score.risk_tier
            resp.top_risk_factors = latest_score.top_risk_factors
        if risk_tier and (resp.risk_tier != risk_tier):
            continue
        result.append(resp)

    result.sort(key=lambda x: x.churn_score or 0, reverse=True)
    return result


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    latest_score = (
        db.query(ChurnScore)
        .filter(ChurnScore.member_id == member_id)
        .order_by(desc(ChurnScore.scored_at))
        .first()
    )
    resp = MemberResponse.model_validate(member)
    if latest_score:
        resp.churn_score = latest_score.score
        resp.risk_tier = latest_score.risk_tier
        resp.top_risk_factors = latest_score.top_risk_factors
    return resp
