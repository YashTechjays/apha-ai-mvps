from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from apps.cpe.db.session import get_db
from apps.cpe.db.models.lead import Lead
from apps.cpe.db.models.calculation import Calculation
from apps.cpe.api.schemas.lead import LeadCreate, LeadResponse
from apps.cpe.integrations.sendgrid_client import trigger_cpe_nurture_sequence
from apps.cpe.utils.logger import get_logger

router = APIRouter(prefix="/leads", tags=["leads"])
logger = get_logger(__name__)


@router.post("/", response_model=LeadResponse)
def capture_lead(data: LeadCreate, db: Session = Depends(get_db)):
    existing = db.query(Lead).filter(Lead.email == data.email).first()
    if existing:
        return LeadResponse(
            id=str(existing.id), email=existing.email,
            message="Welcome back! Your full plan is unlocked.",
        )

    calc = None
    if data.calculation_id:
        calc = db.query(Calculation).filter(Calculation.id == data.calculation_id).first()

    lead = Lead(
        session_id=data.session_id,
        email=data.email,
        name=data.name,
        state=calc.state if calc else "Unknown",
        license_type=calc.license_type if calc else "pharmacist",
        hours_gap=calc.hours_gap if calc else None,
        days_until_renewal=calc.days_until_renewal if calc else None,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    try:
        trigger_cpe_nurture_sequence(lead)
    except Exception as e:
        logger.warning(f"Email sequence failed (non-blocking): {e}")

    return LeadResponse(
        id=str(lead.id),
        email=lead.email,
        message="Your full CPE plan is now unlocked! Check your email for a copy.",
    )
