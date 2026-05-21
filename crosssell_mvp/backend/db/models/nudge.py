import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), index=True)
    product = Column(String, index=True)
    channel = Column(String)
    expansion_score = Column(Float)

    subject_line = Column(String, nullable=True)
    message_body = Column(Text)
    cta_url = Column(String)
    cta_label = Column(String)

    status = Column(String, default="pending")
    sent_at = Column(DateTime, nullable=True)
    sendgrid_message_id = Column(String, nullable=True)

    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    converted = Column(Boolean, default=False)
    conversion_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
