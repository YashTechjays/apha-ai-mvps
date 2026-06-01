import enum
import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    in_review = "in_review"
    won = "won"
    lost = "lost"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rfp_id = Column(String, nullable=False)  # Neo4j ID stored as string
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.draft, nullable=False)
    proposal_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="applications")
