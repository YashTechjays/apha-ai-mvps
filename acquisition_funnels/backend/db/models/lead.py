"""Leads captured from all 3 funnels."""
import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.db.base import Base


class Lead(Base):
    __tablename__ = "acquisition_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, index=True)
    email = Column(String, index=True)
    name = Column(String, nullable=True)

    # Source funnel
    source_tool = Column(String)  # salary | interaction | career
    state = Column(String(2), nullable=True)
    specialty = Column(String, nullable=True)
    license_type = Column(String, nullable=True)
    career_stage = Column(String, nullable=True)

    # Personalization data for email sequences
    salary_percentile = Column(Integer, nullable=True)
    salary_gap_usd = Column(Integer, nullable=True)
    career_score = Column(Integer, nullable=True)
    top_gap_dimension = Column(String, nullable=True)
    interaction_checks_used = Column(Integer, default=0)

    # Email sequence
    sequence_triggered = Column(String, nullable=True)
    crm_synced = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
