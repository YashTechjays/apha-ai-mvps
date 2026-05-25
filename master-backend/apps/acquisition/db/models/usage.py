"""Every tool usage - anonymous (IP-based) until lead is captured."""
from __future__ import annotations

import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from core.database import Base


class ToolUsage(Base):
    __tablename__ = "acq_tool_usages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, index=True)
    ip_hash = Column(String, index=True)
    tool = Column(String, index=True)  # salary | interaction | career
    lead_id = Column(UUID(as_uuid=True), nullable=True)

    # Inputs (denormalized for analytics)
    input_summary = Column(String)

    # Outputs
    result_score = Column(Float, nullable=True)
    result_summary = Column(String, nullable=True)

    # Funnel tracking
    lead_captured = Column(Boolean, default=False)
    clicked_join = Column(Boolean, default=False)
    converted_to_member = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
