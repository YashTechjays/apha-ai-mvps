from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from db.models.campaign import Campaign
from db.models.email_send import EmailSend
from db.models.prospect import Prospect
from api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_prospects = db.query(Prospect).filter(Prospect.do_not_contact == False).count()
    scored = db.query(Prospect).filter(Prospect.icp_score != None).count()
    contacted = db.query(Prospect).filter(Prospect.emails_sent > 0).count()
    converted = db.query(Prospect).filter(Prospect.status == "converted").count()
    total_sent = db.query(EmailSend).filter(EmailSend.status == "sent").count()
    opens = db.query(EmailSend).filter(EmailSend.opened_at != None).count()
    clicks = db.query(EmailSend).filter(EmailSend.clicked_at != None).count()
    avg_score = db.query(func.avg(Prospect.icp_score)).filter(
        Prospect.icp_score != None
    ).scalar() or 0

    return {
        "total_prospects": total_prospects,
        "scored": scored,
        "contacted": contacted,
        "converted": converted,
        "conversion_rate": round(converted / max(contacted, 1), 4),
        "total_emails_sent": total_sent,
        "open_rate": round(opens / max(total_sent, 1), 3),
        "click_rate": round(clicks / max(total_sent, 1), 3),
        "avg_icp_score": round(float(avg_score), 1),
    }


@router.get("/campaigns")
def campaign_analytics(db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "status": c.status,
            "is_dry_run": c.is_dry_run,
            "prospects": c.prospects_total,
            "sent": c.emails_sent,
            "open_rate": round((c.emails_opened or 0) / max(c.emails_sent or 1, 1), 3),
            "click_rate": round((c.emails_clicked or 0) / max(c.emails_sent or 1, 1), 3),
            "conversions": c.conversions,
        }
        for c in campaigns
    ]
