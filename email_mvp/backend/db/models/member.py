import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum as SAEnum
from backend.db.base import Base


class MemberTier(str, enum.Enum):
    PHARMACIST = "pharmacist"
    STUDENT = "student"
    TECHNICIAN = "technician"
    ASSOCIATE = "associate"


class Member(Base):
    __tablename__ = "members"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    tier = Column(SAEnum(MemberTier), default=MemberTier.PHARMACIST)
    join_date = Column(DateTime, default=datetime.utcnow)
    renewal_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # CPE / education activity
    cpe_credits_ytd = Column(Float, default=0.0)
    cpe_courses_completed = Column(Integer, default=0)
    webinars_attended_ytd = Column(Integer, default=0)

    # Publication usage
    journal_articles_read_ytd = Column(Integer, default=0)
    pharmacylibrary_sessions_ytd = Column(Integer, default=0)

    # Events
    annual_meeting_attended = Column(Boolean, default=False)
    events_registered_ytd = Column(Integer, default=0)

    # Engagement signals
    last_login_date = Column(DateTime)
    days_since_last_login = Column(Integer, default=0)
    email_open_rate = Column(Float, default=0.0)
    portal_sessions_last_30d = Column(Integer, default=0)

    # Career / advocacy
    career_center_applications = Column(Integer, default=0)
    advocacy_actions_ytd = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
