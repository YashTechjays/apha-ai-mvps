from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.db.models.nudge import Nudge
from backend.api.schemas.nudge import NudgeResponse, SendNudgesRequest
from backend.api.deps import get_current_user
from backend.nudge_engine.router import get_top_opportunity
from backend.nudge_engine.email_sender import send_email_nudge
from backend.nudge_engine.banner_builder import build_banner
from backend.utils.logger import get_logger

router = APIRouter(prefix="/nudges", tags=["nudges"])
logger = get_logger(__name__)


@router.post("/send")
def send_nudges(req: SendNudgesRequest, db: Session = Depends(get_db), _=Depends(get_current_user)):
    members = db.query(Member).filter(Member.is_active == True).all()
    sent = skipped = failed = 0
    for member in members:
        score, channel = get_top_opportunity(member, db)
        if not score:
            skipped += 1
            continue
        if req.product_filter and score.product != req.product_filter:
            skipped += 1
            continue
        if req.dry_run:
            logger.info(f"[DRY RUN] Would nudge {member.email} → {score.product} via {channel}")
            sent += 1
            continue
        try:
            if channel == "email":
                send_email_nudge(member, score, db)
            else:
                build_banner(member, score, db)
            sent += 1
        except Exception as e:
            logger.error(f"Nudge failed for {member.id}: {e}")
            failed += 1
    return {"dry_run": req.dry_run, "sent": sent, "skipped": skipped, "failed": failed}


@router.get("/", response_model=List[NudgeResponse])
def list_nudges(
    product: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Nudge).filter(Nudge.status == "sent")
    if product:
        q = q.filter(Nudge.product == product)
    if channel:
        q = q.filter(Nudge.channel == channel)
    return q.order_by(desc(Nudge.created_at)).limit(limit).all()


@router.patch("/{nudge_id}/clicked")
def mark_clicked(nudge_id: UUID, db: Session = Depends(get_db)):
    nudge = db.query(Nudge).filter(Nudge.id == nudge_id).first()
    if nudge and not nudge.clicked_at:
        nudge.clicked_at = datetime.utcnow()
        db.commit()
    return {"ok": True}
