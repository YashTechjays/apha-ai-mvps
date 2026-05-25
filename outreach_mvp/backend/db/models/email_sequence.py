"""
Email sequence template — 3-touch sequence (intro, value, close).
Each touch has a subject template + body template with merge fields.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base
import uuid


class EmailSequence(Base):
    __tablename__ = "email_sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    target_tier = Column(String)
    target_specialty = Column(String, nullable=True)
    touch_count = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)

    # Touch 1
    touch1_subject_template = Column(Text)
    touch1_body_template = Column(Text)
    touch1_delay_days = Column(Integer, default=0)

    # Touch 2
    touch2_subject_template = Column(Text, nullable=True)
    touch2_body_template = Column(Text, nullable=True)
    touch2_delay_days = Column(Integer, default=5)

    # Touch 3
    touch3_subject_template = Column(Text, nullable=True)
    touch3_body_template = Column(Text, nullable=True)
    touch3_delay_days = Column(Integer, default=10)

    created_at = Column(DateTime, server_default=func.now())
