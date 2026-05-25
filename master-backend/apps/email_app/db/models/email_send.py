import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey
from apps.email_app.db.base import Base


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    QC_PASSED = "qc_passed"
    QC_FAILED = "qc_failed"
    SENT = "sent"
    FAILED = "failed"


class EmailSend(Base):
    __tablename__ = "email_sends"

    id = Column(String, primary_key=True)
    member_id = Column(String, ForeignKey("email_members.id"), nullable=False, index=True)
    send_month = Column(String, nullable=False)  # "2026-05"

    subject_line = Column(String)
    html_body = Column(Text)
    plain_text_body = Column(Text)

    # Computed benefit summary
    total_value_usd = Column(Float, default=0.0)
    cpe_value_usd = Column(Float, default=0.0)
    webinar_value_usd = Column(Float, default=0.0)
    journal_value_usd = Column(Float, default=0.0)
    pharmacylibrary_value_usd = Column(Float, default=0.0)
    events_value_usd = Column(Float, default=0.0)

    # QC fields
    status = Column(String, default="pending")
    qc_score = Column(Float)
    qc_notes = Column(Text)
    personalization_score = Column(Float)
    token_count = Column(Integer, default=0)

    # Delivery
    sendgrid_message_id = Column(String)
    sent_at = Column(DateTime)

    # Engagement (populated via webhook events)
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    first_open_at = Column(DateTime)
    first_click_at = Column(DateTime)
    click_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
