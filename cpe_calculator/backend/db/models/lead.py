import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class Lead(Base):
    __tablename__ = "cpe_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, index=True)
    email = Column(String, index=True)
    name = Column(String, nullable=True)
    state = Column(String(2))
    license_type = Column(String, default="pharmacist")
    hours_gap = Column(Float, nullable=True)
    days_until_renewal = Column(Integer, nullable=True)
    email_sequence_triggered = Column(Boolean, default=False)
    crm_synced = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
