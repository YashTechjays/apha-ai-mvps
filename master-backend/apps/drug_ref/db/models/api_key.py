import uuid
import secrets
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.drug_ref.db.base import Base


class ApiKey(Base):
    __tablename__ = "drugref_api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("drugref_organizations.id"), index=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("drugref_users.id"))
    key_prefix = Column(String(8), index=True)
    key_hash = Column(String, nullable=False)
    label = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    total_calls = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    @staticmethod
    def generate_key() -> tuple[str, str]:
        raw = f"apha_{secrets.token_urlsafe(32)}"
        prefix = raw[:8]
        return raw, prefix
