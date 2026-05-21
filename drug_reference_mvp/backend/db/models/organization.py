import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    org_type = Column(String, default="hospital")
    domain = Column(String, nullable=True, index=True)
    max_seats = Column(Integer, default=10)
    stripe_customer_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    billing_email = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
