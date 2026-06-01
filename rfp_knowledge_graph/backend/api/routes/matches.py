from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.api.deps import get_current_pharmacist
from backend.db.session import get_db
from backend.graph.queries import get_rfps_for_matching, get_rfp_detail
from backend.graph.pharmacist_graph import get_peer_recommendations
from backend.ai.matcher import score_rfp_for_profile
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/rfps", tags=["matches"])
logger = get_logger("matches")


@router.get("/matches")
def get_matches(
    limit: int = Query(20, le=100),
    min_score: int = Query(0, ge=0, le=100),
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    profile = user.profile
    profile_dict = {
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
        "location_state": profile.location_state if profile else None,
        "org_types_preferred": profile.org_types_preferred or [] if profile else [],
    }

    rfps = get_rfps_for_matching(status="open", limit=200)
    logger.info(f"Scoring {len(rfps)} RFPs for user {user.id}")

    scored = []
    for rfp in rfps:
        score = score_rfp_for_profile(rfp, profile_dict, user_id=str(user.id))
        if score >= min_score:
            scored.append({**rfp, "match_score": score})

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return {"items": scored[:limit], "total": len(scored)}


@router.get("/recommendations/collaborative")
def collaborative_recommendations(
    limit: int = Query(10, le=50),
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Enhancement #4 — 'pharmacists like you also pursued' recommendations,
    derived from shared application history in the graph."""
    items = get_peer_recommendations(str(user.id), limit=limit)
    logger.info(f"Collaborative recs for user {user.id}: {len(items)} items")
    return {"items": items, "total": len(items)}


@router.get("/{rfp_id}/match-explanation")
def match_explanation(
    rfp_id: str,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    """Enhancement #5a — natural-language 'why was this matched' rationale."""
    rfp = get_rfp_detail(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    profile = user.profile
    profile_dict = {
        "specialties": profile.specialties or [] if profile else [],
        "certifications": profile.certifications or [] if profile else [],
    }

    from backend.ai.explainer import explain_match
    return explain_match(str(user.id), rfp_id, profile_dict, rfp)
