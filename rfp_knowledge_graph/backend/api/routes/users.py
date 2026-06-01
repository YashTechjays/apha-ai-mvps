from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models.user import User
from backend.db.models.pharmacist_profile import PharmacistProfile
from backend.db.models.application import Application
from backend.api.deps import get_current_pharmacist
from backend.api.schemas.user import ProfileUpdateRequest, UserMeResponse, ProfileResponse
from backend.graph.queries import get_rfp_detail
from backend.graph.pharmacist_graph import sync_pharmacist_profile_to_graph

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_pharmacist)):
    profile = current_user.profile
    return UserMeResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        profile=ProfileResponse(
            full_name=profile.full_name,
            bio=profile.bio,
            years_experience=profile.years_experience,
            location_state=profile.location_state,
            location_city=profile.location_city,
            specialties=profile.specialties or [],
            certifications=profile.certifications or [],
            org_types_preferred=profile.org_types_preferred or [],
            notify_on_match=profile.notify_on_match,
            notify_threshold=profile.notify_threshold,
        ) if profile else None,
    )


@router.put("/me/profile", response_model=UserMeResponse)
def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    profile = db.query(PharmacistProfile).filter(
        PharmacistProfile.user_id == current_user.id
    ).first()
    if not profile:
        profile = PharmacistProfile(user_id=current_user.id)
        db.add(profile)

    profile.full_name = body.full_name
    profile.bio = body.bio
    profile.years_experience = body.years_experience
    profile.location_state = body.location_state
    profile.location_city = body.location_city
    profile.specialties = body.specialties
    profile.certifications = body.certifications
    profile.org_types_preferred = body.org_types_preferred
    profile.notify_on_match = body.notify_on_match
    profile.notify_threshold = body.notify_threshold
    db.commit()
    db.refresh(profile)

    sync_pharmacist_profile_to_graph(
        user_id=current_user.id,
        full_name=profile.full_name,
        location_state=profile.location_state,
        specialties=profile.specialties,
        certifications=profile.certifications,
    )

    return UserMeResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        profile=ProfileResponse(
            full_name=profile.full_name,
            bio=profile.bio,
            years_experience=profile.years_experience,
            location_state=profile.location_state,
            location_city=profile.location_city,
            specialties=profile.specialties or [],
            certifications=profile.certifications or [],
            org_types_preferred=profile.org_types_preferred or [],
            notify_on_match=profile.notify_on_match,
            notify_threshold=profile.notify_threshold,
        ),
    )


@router.get("/me/applications")
def my_applications(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    q = db.query(Application).filter(Application.user_id == current_user.id)
    if status:
        q = q.filter(Application.status == status)
    apps = q.order_by(Application.created_at.desc()).all()

    result = []
    for app in apps:
        rfp = get_rfp_detail(app.rfp_id) or {}
        org = rfp.get("organization") or {}
        result.append({
            "id": str(app.id),
            "rfp_id": app.rfp_id,
            "status": app.status.value,
            "proposal_text": app.proposal_text,
            "notes": app.notes,
            "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            "rfp_title": rfp.get("title"),
            "rfp_deadline": rfp.get("deadline"),
            "rfp_org": org.get("name") if isinstance(org, dict) else None,
        })
    return result
