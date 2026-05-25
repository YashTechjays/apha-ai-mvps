"""
Prospect universe — every non-member pharmacist identified via NPI + other sources.
The ICP score determines who gets contacted and in what order.
"""
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Boolean, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base
import uuid
import enum


class ProspectStatus(str, enum.Enum):
    new = "new"
    scored = "scored"
    queued = "queued"
    contacted = "contacted"
    replied = "replied"
    converted = "converted"
    unsubscribed = "unsubscribed"
    bounced = "bounced"
    excluded = "excluded"


class ProspectSource(str, enum.Enum):
    npi_registry = "npi_registry"
    state_board = "state_board"
    linkedin = "linkedin"
    manual_import = "manual_import"
    referral = "referral"


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    npi_number = Column(String, unique=True, nullable=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)

    # Professional profile (from NPI + enrichment)
    credential = Column(String, nullable=True)
    license_type = Column(String, default="pharmacist")
    specialty = Column(String, nullable=True)
    practice_setting = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    state = Column(String(2), nullable=True, index=True)
    city = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)

    # Career signals (derived / enriched)
    years_since_grad = Column(Integer, nullable=True)
    career_stage = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)

    # ICP scoring
    icp_score = Column(Float, nullable=True)
    icp_tier = Column(String, nullable=True)
    icp_scored_at = Column(DateTime, nullable=True)

    # Outreach state
    status = Column(String, default=ProspectStatus.new)
    source = Column(String, default=ProspectSource.npi_registry)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    emails_sent = Column(Integer, default=0)
    last_email_sent_at = Column(DateTime, nullable=True)
    last_opened_at = Column(DateTime, nullable=True)
    last_clicked_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)

    # Data quality
    email_verified = Column(Boolean, default=False)
    email_valid = Column(Boolean, nullable=True)
    do_not_contact = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
