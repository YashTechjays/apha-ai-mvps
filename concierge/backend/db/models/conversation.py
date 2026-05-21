from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base
import uuid
import enum


class ConversationStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    lead_captured = "lead_captured"
    converted = "converted"
    abandoned = "abandoned"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String, unique=True, index=True)
    visitor_email = Column(String, nullable=True, index=True)
    visitor_name = Column(String, nullable=True)
    detected_intent = Column(String, nullable=True)
    recommended_tier = Column(String, nullable=True)
    status = Column(String, default=ConversationStatus.active)
    page_url = Column(String, nullable=True)
    turn_count = Column(Integer, default=0)
    lead_captured = Column(Boolean, default=False)
    converted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), index=True)
    role = Column(String)
    content = Column(Text)
    intent = Column(String, nullable=True)
    retrieved_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
