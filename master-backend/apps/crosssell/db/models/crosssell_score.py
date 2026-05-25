import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.crosssell.db.base import Base


class CrossSellScore(Base):
    __tablename__ = "crosssell_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("crosssell_members.id"), index=True)
    product = Column(String, index=True)
    score = Column(Float)
    already_active = Column(Boolean, default=False)
    top_reasons = Column(JSON)
    feature_values = Column(JSON)
    model_version = Column(String)
    scored_at = Column(DateTime, server_default=func.now())
