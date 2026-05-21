from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.db.models.nudge import Nudge
from backend.api.deps import get_current_user
from backend.utils.config import get_settings

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_members = db.query(Member).filter(Member.is_active == True).count()
    total_nudges = db.query(Nudge).filter(Nudge.status == "sent").count()
    opens = db.query(Nudge).filter(Nudge.opened_at != None).count()
    clicks = db.query(Nudge).filter(Nudge.clicked_at != None).count()
    conversions = db.query(Nudge).filter(Nudge.converted == True).count()
    avg_streams = db.query(func.avg(Member.active_stream_count)).scalar() or 0

    return {
        "total_active_members": total_members,
        "avg_active_streams_per_member": round(float(avg_streams), 2),
        "total_nudges_sent": total_nudges,
        "open_rate": round(opens / max(total_nudges, 1), 3),
        "click_rate": round(clicks / max(total_nudges, 1), 3),
        "conversion_rate": round(conversions / max(total_nudges, 1), 3),
    }


@router.get("/by-product")
def by_product(db: Session = Depends(get_db), _=Depends(get_current_user)):
    result = {}
    total_members = db.query(Member).count()
    for product in get_settings().products:
        nudges = db.query(Nudge).filter(Nudge.product == product, Nudge.status == "sent").count()
        clicks = db.query(Nudge).filter(Nudge.product == product, Nudge.clicked_at != None).count()
        active = db.query(Member).filter(
            getattr(Member, f"{product}_active") == True
        ).count()
        result[product] = {
            "nudges_sent": nudges,
            "click_rate": round(clicks / max(nudges, 1), 3),
            "active_members": active,
            "active_pct": round(active / max(total_members, 1), 3),
        }
    return result
