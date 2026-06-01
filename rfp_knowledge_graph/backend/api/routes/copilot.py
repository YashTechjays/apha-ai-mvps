from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_current_pharmacist
from backend.db.session import get_db
from backend.ai.copilot import run_copilot

router = APIRouter(prefix="/api/copilot", tags=["copilot"])


@router.post("/chat")
def chat(
    body: dict,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Ask the Copilot. Identity is bound server-side from the JWT."""
    message = (body or {}).get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    profile = user.profile
    profile_dict = {
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
        "location_state": profile.location_state if profile else None,
        "org_types_preferred": getattr(profile, "org_types_preferred", None) or [] if profile else [],
    }
    return run_copilot(message, user_id=str(user.id), profile=profile_dict)
