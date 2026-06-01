from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.api.deps import get_current_pharmacist
from backend.db.session import get_db
from backend.db.models.application import Application, ApplicationStatus
from backend.api.schemas.application import ApplicationCreateRequest, ApplicationUpdateRequest
from backend.graph.queries import get_rfp_detail
from backend.graph.pharmacist_graph import sync_application_to_graph

router = APIRouter(prefix="/api/rfps", tags=["applications"])


@router.post("/{rfp_id}/applications", status_code=201)
def create_application(
    rfp_id: str,
    body: ApplicationCreateRequest,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    # Verify RFP exists in Neo4j
    rfp = get_rfp_detail(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    app = Application(
        user_id=user.id,
        rfp_id=rfp_id,
        proposal_text=body.proposal_text,
        notes=body.notes,
        status=ApplicationStatus(body.status) if body.status else ApplicationStatus.draft,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    sync_application_to_graph(
        user_id=user.id,
        rfp_id=rfp_id,
        status=app.status.value,
        applied_at=app.created_at.isoformat() if app.created_at else None,
    )

    return _enrich(app, rfp)


@router.put("/{rfp_id}/applications/{app_id}")
def update_application(
    rfp_id: str,
    app_id: str,
    body: ApplicationUpdateRequest,
    user=Depends(get_current_pharmacist),
    db: Session = Depends(get_db),
):
    app = db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user.id,
        Application.rfp_id == rfp_id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if body.status is not None:
        new_status = ApplicationStatus(body.status)
        if new_status == ApplicationStatus.submitted and app.status == ApplicationStatus.draft:
            app.submitted_at = datetime.utcnow()
        app.status = new_status
    if body.proposal_text is not None:
        app.proposal_text = body.proposal_text
    if body.notes is not None:
        app.notes = body.notes

    db.commit()
    db.refresh(app)

    sync_application_to_graph(
        user_id=user.id,
        rfp_id=rfp_id,
        status=app.status.value,
        applied_at=app.created_at.isoformat() if app.created_at else None,
    )

    rfp = get_rfp_detail(rfp_id)
    return _enrich(app, rfp or {})


def _enrich(app: Application, rfp: dict) -> dict:
    org = rfp.get("organization") or {}
    return {
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
    }
