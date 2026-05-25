from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.acquisition.db.session import get_db
from apps.acquisition.db.models.lead import AcquisitionLead
from apps.acquisition.db.models.usage import ToolUsage
from apps.acquisition.api.schemas.lead import LeadCreate, LeadResponse
from apps.acquisition.integrations.sendgrid_client import trigger_nurture_sequence
from core.config import get_settings
from core.logger import get_logger

router = APIRouter(prefix="/leads", tags=["acquisition-leads"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("/", response_model=LeadResponse)
def capture_lead(data: LeadCreate, db: Session = Depends(get_db)):
    # Check for existing lead
    existing = db.query(AcquisitionLead).filter(AcquisitionLead.email == data.email).first()
    if existing:
        return LeadResponse(
            id=str(existing.id),
            email=existing.email,
            unlocked=True,
            message="Welcome back! Your full report is unlocked.",
            next_action_url=_get_next_action(data.source_tool),
        )

    lead = AcquisitionLead(
        session_id=data.session_id,
        email=data.email,
        name=data.name,
        source_tool=data.source_tool,
        state=data.state,
        specialty=data.specialty,
        license_type=data.license_type,
        career_stage=data.career_stage,
        salary_percentile=data.salary_percentile,
        salary_gap_usd=data.salary_gap_usd,
        career_score=data.career_score,
        top_gap_dimension=data.top_gap_dimension,
    )
    db.add(lead)

    # Mark usage as converted
    if data.usage_id:
        usage = db.query(ToolUsage).filter(ToolUsage.id == data.usage_id).first()
        if usage:
            usage.lead_captured = True
            usage.lead_id = lead.id

    db.commit()
    db.refresh(lead)

    try:
        trigger_nurture_sequence(lead)
    except Exception as e:
        logger.warning(f"Email sequence failed (non-blocking): {e}")

    return LeadResponse(
        id=str(lead.id),
        email=lead.email,
        unlocked=True,
        message=_unlock_message(data.source_tool, data),
        next_action_url=_get_next_action(data.source_tool),
    )


def _unlock_message(tool: str, data: LeadCreate) -> str:
    if tool == "salary":
        gap = data.salary_gap_usd
        if gap and gap > 0:
            return f"Your full report is unlocked! You're ${gap:,} below the median for your role."
        return "Your full salary report is unlocked!"
    elif tool == "interaction":
        return "Unlimited interaction checks unlocked for today!"
    elif tool == "career":
        score = data.career_score
        return f"Your action plan is unlocked! Your score: {score}/100. Check your email for the full plan."
    return "Your full report is unlocked!"


def _get_next_action(tool: str) -> str:
    urls = {
        "salary": "https://www.pharmacist.com/join?utm_source=salary_tool",
        "interaction": "https://www.pharmacist.com/join?utm_source=interaction_tool",
        "career": "https://www.pharmacist.com/join?utm_source=career_tool",
    }
    return urls.get(tool, "https://www.pharmacist.com/join")
