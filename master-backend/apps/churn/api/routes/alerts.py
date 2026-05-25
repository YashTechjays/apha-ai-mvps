from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from apps.churn.db.session import get_db
from apps.churn.db.models.alert import Alert
from apps.churn.api.schemas.alert import AlertResponse, AlertUpdate
from apps.churn.api.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    resolved: Optional[bool] = False,
    risk_tier: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Alert).filter(Alert.is_resolved == resolved)
    if risk_tier:
        query = query.filter(Alert.risk_tier == risk_tier)
    return query.order_by(desc(Alert.created_at)).limit(limit).all()


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: UUID,
    update: AlertUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = update.is_resolved
    if update.is_resolved:
        alert.resolved_by = update.resolved_by or user["username"]
        alert.resolved_at = datetime.utcnow()
    if update.outcome:
        alert.outcome = update.outcome
    db.commit()
    db.refresh(alert)
    return alert
