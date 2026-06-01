from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_current_pharmacist
from backend.db.session import get_db
from backend.ai.foresight import (
    forecast_reposts,
    personalize_predictions,
    organization_timeline,
)

router = APIRouter(prefix="/api/foresight", tags=["foresight"])


@router.get("/predictions")
def predictions(
    horizon_days: int = Query(180, ge=30, le=730),
    limit: int = Query(10, le=50),
    _=Depends(get_current_user),
):
    """Predicted upcoming RFPs across all tracked organizations."""
    preds = forecast_reposts(horizon_days=horizon_days)
    return {"items": preds[:limit], "total": len(preds)}


@router.get("/predictions/personalized")
def personalized(
    horizon_days: int = Query(180, ge=30, le=730),
    limit: int = Query(10, le=50),
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Predicted RFPs ranked by fit to the current pharmacist's profile."""
    profile = user.profile
    profile_dict = {
        "specialties": profile.specialties or [] if profile else [],
        "location_state": profile.location_state if profile else None,
    }
    preds = personalize_predictions(forecast_reposts(horizon_days=horizon_days), profile_dict)
    return {"items": preds[:limit], "total": len(preds)}


@router.get("/organization/{org_name}")
def org_timeline(org_name: str, _=Depends(get_current_user)):
    """Posting history + projected next window for one organization."""
    return organization_timeline(org_name)
