from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.api.schemas.member import MemberResponse
from backend.ai.benefit_valuation import compute_benefit_summary
from datetime import datetime

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/", response_model=List[MemberResponse])
def list_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Member).filter(Member.is_active == True).offset(skip).limit(limit).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.get("/{member_id}/benefit-summary")
def get_benefit_summary(member_id: str, send_month: str | None = None, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    month = send_month or datetime.utcnow().strftime("%Y-%m")
    summary = compute_benefit_summary(member, month)
    return summary.__dict__
