from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from apps.churn.db.base import Base
import uuid
import enum


class MemberTier(str, enum.Enum):
    student = "student"
    new_practitioner = "new_practitioner"
    pharmacist = "pharmacist"
    technician = "technician"
    researcher = "researcher"
    supporter = "supporter"


class Member(Base):
    __tablename__ = "churn_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    tier = Column(String, default="pharmacist")
    state = Column(String(2))
    specialty = Column(String)
    join_date = Column(DateTime)
    renewal_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Raw behavioral features (updated weekly by ETL)
    days_since_last_login = Column(Float, default=0)
    cpe_hours_last_90d = Column(Float, default=0)
    cpe_hours_ytd = Column(Float, default=0)
    email_open_rate_30d = Column(Float, default=0)
    email_click_rate_30d = Column(Float, default=0)
    events_attended_ytd = Column(Integer, default=0)
    events_registered_ytd = Column(Integer, default=0)
    publications_read_30d = Column(Integer, default=0)
    job_board_searches_30d = Column(Integer, default=0)
    community_posts_90d = Column(Integer, default=0)
    renewal_count = Column(Integer, default=0)
    years_as_member = Column(Float, default=0)
    cpe_deadline_days = Column(Integer, default=365)
    benefits_used_pct = Column(Float, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
