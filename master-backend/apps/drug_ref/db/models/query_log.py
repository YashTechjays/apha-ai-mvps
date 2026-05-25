import uuid
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.drug_ref.db.base import Base


class QueryLog(Base):
    __tablename__ = "drugref_query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("drugref_users.id"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    api_key_id = Column(UUID(as_uuid=True), nullable=True)

    query_text = Column(Text, nullable=False)
    query_type = Column(String, nullable=True)
    query_tokens = Column(Integer, default=0)

    chunks_retrieved = Column(Integer, default=0)
    sources_cited = Column(Integer, default=0)
    retrieval_score_avg = Column(Float, nullable=True)

    answer_text = Column(Text, nullable=True)
    answer_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, nullable=True)

    safety_flagged = Column(Boolean, default=False)
    safety_reason = Column(String, nullable=True)

    thumbs_up = Column(Boolean, nullable=True)
    feedback_text = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
