from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.api.deps import get_current_pharmacist
from backend.db.session import get_db
from backend.ai.simulator import baseline, simulate

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


def _profile_dict(user) -> dict:
    profile = user.profile
    return {
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
        "location_state": profile.location_state if profile else None,
        "org_types_preferred": getattr(profile, "org_types_preferred", None) or [] if profile else [],
    }


@router.get("/{rfp_id}/baseline")
def simulator_baseline(
    rfp_id: str,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Current win probability, factor breakdown, and available what-if toggles."""
    result = baseline(rfp_id, _profile_dict(user))
    if not result:
        raise HTTPException(status_code=404, detail="RFP not found")
    return result


@router.post("/{rfp_id}")
def simulator_run(
    rfp_id: str,
    body: Optional[dict] = None,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Recompute win probability for a hypothetical profile (not persisted)."""
    result = simulate(rfp_id, _profile_dict(user), body or {})
    if not result:
        raise HTTPException(status_code=404, detail="RFP not found")
    return result
