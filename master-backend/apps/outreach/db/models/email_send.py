"""
Individual email send record — one per prospect per touch.
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.outreach.db.base import Base
import uuid


class EmailSend(Base):
    __tablename__ = "outreach_email_sends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("outreach_prospects.id"), index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("outreach_campaigns.id"), index=True)
    sequence_id = Column(UUID(as_uuid=True), nullable=True)
    touch_number = Column(Integer)

    # Generated content
    subject = Column(String)
    body_text = Column(Text)
    body_html = Column(Text, nullable=True)

    # ICP context at time of send
    icp_score = Column(Float, nullable=True)
    personalization_vars = Column(String, nullable=True)

    # Delivery
    status = Column(String, default="pending")
    sendgrid_message_id = Column(String, nullable=True, index=True)
    sent_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)

    # Engagement
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    unsubscribed_at = Column(DateTime, nullable=True)
    spam_reported_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
