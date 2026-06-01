from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from backend.api.deps import get_current_user, get_current_pharmacist
from backend.api.schemas.rfp import RfpListResponse, RfpDetail
from backend.graph.queries import search_rfps, get_rfp_detail
from backend.db.session import get_db

router = APIRouter(prefix="/api/rfps", tags=["rfps"])


@router.get("/", response_model=RfpListResponse)
def list_rfps(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    _=Depends(get_current_user),
):
    result = search_rfps(
        query=q, category=category, state=state,
        status=status, limit=limit, offset=offset,
    )
    return RfpListResponse(**result)


@router.post("/{rfp_id}/generate-proposal")
def generate_proposal(
    rfp_id: str,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    rfp = get_rfp_detail(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    profile = user.profile
    profile_dict = {
        "full_name": profile.full_name if profile else None,
        "bio": profile.bio if profile else None,
        "years_experience": profile.years_experience if profile else None,
        "location_state": profile.location_state if profile else None,
        "location_city": profile.location_city if profile else None,
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
    }

    from backend.ai.graph_rag import gather_proposal_context
    from backend.ai.proposal_generator import generate_proposal as _generate
    context = gather_proposal_context(rfp, user_id=str(user.id))
    proposal_text = _generate(rfp, profile_dict, user.username, context=context)
    return {"proposal": proposal_text, "rfp_id": rfp_id, "rfp_title": rfp["title"]}


@router.post("/{rfp_id}/win-room")
def win_room(
    rfp_id: str,
    body: Optional[dict] = None,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Run the AI evaluation committee: score, revise across rounds, climb."""
    rfp = get_rfp_detail(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    profile = user.profile
    profile_dict = {
        "full_name": profile.full_name if profile else None,
        "bio": profile.bio if profile else None,
        "years_experience": profile.years_experience if profile else None,
        "location_state": profile.location_state if profile else None,
        "location_city": profile.location_city if profile else None,
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
    }

    from backend.ai.win_room import run_win_room, weak_starter_draft

    # Use the caller's proposal when supplied; otherwise start from a deliberately
    # thin draft so the committee has room to improve and the score climbs live.
    proposal = (body or {}).get("proposal") or weak_starter_draft(rfp, profile_dict)

    result = run_win_room(rfp, profile_dict, proposal)
    result["rfp_id"] = rfp_id
    result["rfp_title"] = rfp["title"]
    return result


@router.get("/{rfp_id}")
def rfp_detail(rfp_id: str, _=Depends(get_current_user)):
    detail = get_rfp_detail(rfp_id)
    if not detail:
        raise HTTPException(status_code=404, detail="RFP not found")
    return detail
