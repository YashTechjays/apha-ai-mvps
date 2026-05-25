import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.drug_ref.db.base import Base


class User(Base):
    __tablename__ = "drugref_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="pharmacist")
    organization_id = Column(UUID(as_uuid=True), ForeignKey("drugref_organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    license_state = Column(String(2), nullable=True)
    specialty = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)
