from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from apps.concierge.db.session import get_db
from apps.concierge.db.models.lead import Lead
from apps.concierge.db.models.conversation import Conversation
from apps.concierge.api.schemas.lead import LeadCreate, LeadResponse
from apps.concierge.integrations.crm_connector import push_lead_to_crm
from apps.concierge.integrations.email_connector import trigger_followup_sequence
from apps.concierge.utils.logger import get_logger

router = APIRouter(prefix="/leads", tags=["leads"])
logger = get_logger(__name__)


@router.post("/", response_model=LeadResponse)
def capture_lead(data: LeadCreate, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(
        Conversation.session_token == data.session_token
    ).first()

    existing = db.query(Lead).filter(Lead.email == data.email).first()
    if existing:
        return existing

    lead = Lead(
        conversation_id=conv.id if conv else None,
        email=data.email,
        name=data.name,
        interested_tier=data.interested_tier or (conv.recommended_tier if conv else None),
        visitor_intent=conv.detected_intent if conv else None,
    )
    db.add(lead)

    if conv:
        conv.lead_captured = True
        conv.visitor_email = data.email
        conv.visitor_name = data.name

    db.commit()
    db.refresh(lead)

    try:
        push_lead_to_crm(lead)
        trigger_followup_sequence(lead)
    except Exception as e:
        logger.warning(f"Integration failed (non-blocking): {e}")

    return lead


@router.get("/", response_model=List[LeadResponse])
def list_leads(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Lead).order_by(Lead.created_at.desc()).limit(limit).all()
