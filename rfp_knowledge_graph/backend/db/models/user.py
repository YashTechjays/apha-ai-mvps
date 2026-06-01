import enum
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class UserRole(str, enum.Enum):
    pharmacist = "pharmacist"
    admin = "admin"
    analyst = "analyst"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.pharmacist)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("PharmacistProfile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
