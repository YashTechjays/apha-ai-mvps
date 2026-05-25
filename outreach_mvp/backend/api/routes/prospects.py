from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from db.session import get_db
from db.models.prospect import Prospect
from api.schemas.prospect import ProspectResponse
from api.deps import get_current_user
from ml.icp_score import run_icp_scoring
from pipeline.npi_importer import run_npi_import

router = APIRouter(prefix="/prospects", tags=["prospects"])


@router.get("/", response_model=List[ProspectResponse])
def list_prospects(
    status: Optional[str] = None,
    tier: Optional[str] = None,
    state: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Prospect).filter(Prospect.do_not_contact == False)
    if status:
        q = q.filter(Prospect.status == status)
    if tier:
        q = q.filter(Prospect.icp_tier == tier)
    if state:
        q = q.filter(Prospect.state == state.upper())
    if min_score is not None:
        q = q.filter(Prospect.icp_score >= min_score)
    return q.order_by(desc(Prospect.icp_score)).offset(offset).limit(limit).all()


@router.post("/import")
def trigger_import(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Trigger NPI data import in background."""
    background_tasks.add_task(run_npi_import, db, True)
    return {"message": "Import started in background"}


@router.post("/score")
def trigger_scoring(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Trigger ICP scoring for all unscored prospects."""
    return run_icp_scoring(db)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.query(Prospect).count()
    by_status = db.query(Prospect.status, func.count()).group_by(Prospect.status).all()
    by_tier = db.query(Prospect.icp_tier, func.count()).filter(
        Prospect.icp_tier != None
    ).group_by(Prospect.icp_tier).all()
    avg_score = db.query(func.avg(Prospect.icp_score)).filter(
        Prospect.icp_score != None
    ).scalar() or 0

    return {
        "total": total,
        "avg_icp_score": round(float(avg_score), 1),
        "by_status": {s: c for s, c in by_status},
        "by_tier": {t: c for t, c in by_tier if t},
    }
