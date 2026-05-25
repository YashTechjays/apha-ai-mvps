from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from apps.cpe.db.session import get_db
from apps.cpe.db.models.calculation import Calculation
from apps.cpe.db.models.lead import Lead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_calcs = db.query(Calculation).count()
    leads = db.query(Lead).count()
    conversion_rate = round(leads / total_calcs, 3) if total_calcs > 0 else 0

    top_states = db.query(
        Calculation.state, func.count().label("count")
    ).group_by(Calculation.state).order_by(func.count().desc()).limit(10).all()

    avg_gap = db.query(func.avg(Calculation.hours_gap)).scalar() or 0

    return {
        "total_calculations": total_calcs,
        "leads_captured": leads,
        "lead_conversion_rate": f"{conversion_rate * 100:.1f}%",
        "avg_cpe_gap_hours": round(float(avg_gap), 1),
        "top_states": [{"state": r.state, "count": r.count} for r in top_states],
    }
