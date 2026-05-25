from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.churn.db.base import Base
import uuid


class Alert(Base):
    __tablename__ = "churn_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("churn_members.id"), index=True)
    risk_tier = Column(String)
    message = Column(Text)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    outcome = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
