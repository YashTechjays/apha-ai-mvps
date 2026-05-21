from sqlalchemy import Column, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base
import uuid


class ChurnScore(Base):
    __tablename__ = "churn_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), index=True)
    score = Column(Float)
    risk_tier = Column(String)
    model_version = Column(String)
    shap_values = Column(JSON)
    top_risk_factors = Column(JSON)
    scored_at = Column(DateTime, server_default=func.now())
