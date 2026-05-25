from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from apps.outreach.db.session import get_db
from apps.outreach.db.models.campaign import Campaign
from apps.outreach.db.models.prospect import Prospect
from apps.outreach.api.schemas.campaign import CampaignCreate, CampaignResponse
from apps.outreach.api.deps import get_current_user
from apps.outreach.delivery.tasks import generate_sequence_for_prospect
from apps.outreach.utils.logger import get_logger

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
logger = get_logger(__name__)


@router.post("/", response_model=CampaignResponse)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    campaign = Campaign(
        name=data.name,
        description=data.description,
        target_tier=data.target_tier,
        target_state=data.target_state,
        target_specialty=data.target_specialty,
        target_career_stage=data.target_career_stage,
        min_icp_score=data.min_icp_score,
        daily_send_cap=data.daily_send_cap,
        is_dry_run=data.is_dry_run,
        status="draft",
        created_by=user["username"],
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/launch")
def launch_campaign(
    campaign_id: UUID,
    max_prospects: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Launch a campaign: find matching prospects, generate sequences, queue sends.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status == "active":
        raise HTTPException(status_code=400, detail="Campaign already active")

    q = db.query(Prospect).filter(
        Prospect.status == "scored",
        Prospect.icp_score >= campaign.min_icp_score,
        Prospect.email != None,
        Prospect.do_not_contact == False,
    )
    if campaign.target_tier:
        q = q.filter(Prospect.license_type == campaign.target_tier)
    if campaign.target_state:
        q = q.filter(Prospect.state == campaign.target_state.upper())
    if campaign.target_specialty:
        q = q.filter(Prospect.specialty.ilike(f"%{campaign.target_specialty}%"))

    prospects = q.order_by(Prospect.icp_score.desc()).limit(max_prospects).all()

    if not prospects:
        raise HTTPException(status_code=400, detail="No eligible prospects for this campaign targeting")

    queued = 0
    for p in prospects:
        generate_sequence_for_prospect.delay(str(p.id), str(campaign.id))
        queued += 1

    campaign.status = "active"
    campaign.started_at = datetime.utcnow()
    campaign.prospects_total = queued
    db.commit()

    return {
        "campaign_id": str(campaign.id),
        "status": "active",
        "prospects_queued": queued,
        "is_dry_run": campaign.is_dry_run,
        "message": "Campaign launched. Emails will be generated and sent per schedule." if not campaign.is_dry_run
                   else "DRY RUN: Sequences will be generated but no emails will actually be sent."
    }


@router.patch("/{campaign_id}/pause")
def pause_campaign(campaign_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = "paused"
    db.commit()
    return {"campaign_id": str(campaign_id), "status": "paused"}


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c
