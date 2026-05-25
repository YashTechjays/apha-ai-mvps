from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.concierge.db.base import Base
import uuid


class Lead(Base):
    __tablename__ = "concierge_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=True)
    email = Column(String, index=True)
    name = Column(String, nullable=True)
    interested_tier = Column(String, nullable=True)
    visitor_intent = Column(String, nullable=True)
    crm_synced = Column(Boolean, default=False)
    email_sequence_triggered = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
