import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class PharmacistProfile(Base):
    __tablename__ = "pharmacist_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    years_experience = Column(Integer, nullable=True)
    location_state = Column(String(2), nullable=True)
    location_city = Column(String, nullable=True)
    specialties = Column(JSON, default=list)           # ["clinical-pharmacy", "oncology"]
    certifications = Column(JSON, default=list)        # ["PharmD", "BCOP", "MTM"]
    org_types_preferred = Column(JSON, default=list)   # ["government", "nonprofit"]
    notify_on_match = Column(Boolean, default=True)
    notify_threshold = Column(Integer, default=70)
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="profile")
