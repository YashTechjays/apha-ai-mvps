"""
An outreach campaign = a defined prospect segment + email sequence + sending schedule.
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base
import uuid


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Targeting
    target_tier = Column(String, nullable=True)
    target_state = Column(String, nullable=True)
    target_specialty = Column(String, nullable=True)
    target_career_stage = Column(String, nullable=True)
    min_icp_score = Column(Float, default=60.0)
    segment_filter = Column(JSON, nullable=True)

    # Sequence
    sequence_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String, default="draft")
    is_dry_run = Column(Boolean, default=True)

    # Metrics (denormalized for speed)
    prospects_total = Column(Integer, default=0)
    prospects_queued = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    unsubscribes = Column(Integer, default=0)
    bounces = Column(Integer, default=0)

    # Schedule
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    daily_send_cap = Column(Integer, default=200)

    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
