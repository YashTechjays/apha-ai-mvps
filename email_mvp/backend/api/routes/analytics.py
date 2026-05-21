from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.session import get_db
from backend.db.models.email_send import EmailSend, EmailStatus
from backend.db.models.member import Member

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(send_month: str | None = None, db: Session = Depends(get_db)):
    q = db.query(EmailSend)
    if send_month:
        q = q.filter(EmailSend.send_month == send_month)

    sends = q.all()
    total = len(sends)
    if total == 0:
        return {"send_month": send_month, "total_sends": 0}

    sent = [s for s in sends if s.status == EmailStatus.SENT]
    qc_failed = [s for s in sends if s.status == EmailStatus.QC_FAILED]
    opened = [s for s in sent if s.opened]
    clicked = [s for s in sent if s.clicked]

    avg_value = sum(s.total_value_usd for s in sends) / total
    avg_roi = avg_value / 195.0

    return {
        "send_month": send_month,
        "total_sends": total,
        "sent": len(sent),
        "qc_failed": len(qc_failed),
        "delivery_rate": round(len(sent) / total, 3) if total else 0,
        "open_rate": round(len(opened) / len(sent), 3) if sent else 0,
        "click_rate": round(len(clicked) / len(sent), 3) if sent else 0,
        "avg_benefit_value_usd": round(avg_value, 2),
        "avg_roi_multiplier": round(avg_roi, 2),
        "total_value_delivered_usd": round(sum(s.total_value_usd for s in sends), 2),
        "avg_qc_score": round(sum(s.qc_score or 0 for s in sends) / total, 3),
        "avg_personalization_score": round(sum(s.personalization_score or 0 for s in sends) / total, 3),
    }


@router.get("/by-status")
def get_by_status(send_month: str | None = None, db: Session = Depends(get_db)):
    q = db.query(EmailSend.status, func.count(EmailSend.id).label("count"))
    if send_month:
        q = q.filter(EmailSend.send_month == send_month)
    rows = q.group_by(EmailSend.status).all()
    return [{"status": r.status, "count": r.count} for r in rows]


@router.get("/top-members")
def get_top_members(send_month: str | None = None, limit: int = 10, db: Session = Depends(get_db)):
    q = db.query(EmailSend, Member).join(Member, EmailSend.member_id == Member.id)
    if send_month:
        q = q.filter(EmailSend.send_month == send_month)
    rows = q.order_by(EmailSend.total_value_usd.desc()).limit(limit).all()
    return [
        {
            "member_id": m.id,
            "name": f"{m.first_name} {m.last_name}",
            "tier": m.tier,
            "total_value_usd": s.total_value_usd,
            "status": s.status,
            "opened": s.opened,
        }
        for s, m in rows
    ]
