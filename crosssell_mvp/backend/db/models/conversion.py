import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nudge_id = Column(UUID(as_uuid=True), ForeignKey("nudges.id"), nullable=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), index=True)
    product = Column(String)
    revenue_usd = Column(Float, default=0)
    converted_at = Column(DateTime, server_default=func.now())
