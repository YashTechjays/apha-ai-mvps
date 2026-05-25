import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.cpe.db.base import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, index=True)

    state = Column(String(2), index=True)
    renewal_date = Column(String)
    hours_completed = Column(Float)
    specialty = Column(String, nullable=True)
    license_type = Column(String, default="pharmacist")

    hours_required = Column(Float)
    hours_gap = Column(Float)
    days_until_renewal = Column(Integer)

    plan_json = Column(Text, nullable=True)

    lead_captured = Column(Boolean, default=False)
    clicked_join = Column(Boolean, default=False)
    is_member = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
