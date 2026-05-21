import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    tier = Column(String, default="pharmacist")
    state = Column(String(2), nullable=True)
    specialty = Column(String, nullable=True)
    join_date = Column(DateTime, nullable=True)
    renewal_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    years_as_member = Column(Float, default=0)
    renewal_count = Column(Integer, default=0)
    churn_score = Column(Float, nullable=True)

    # Education & Training
    edu_cpe_hours_ytd = Column(Float, default=0)
    edu_courses_completed = Column(Integer, default=0)
    edu_last_activity_days = Column(Float, default=999)
    edu_certificates_earned = Column(Integer, default=0)
    edu_active = Column(Boolean, default=False)

    # Publications & Books
    pub_articles_read_30d = Column(Integer, default=0)
    pub_pharmacylibrary_sessions = Column(Integer, default=0)
    pub_journal_downloads = Column(Integer, default=0)
    pub_last_activity_days = Column(Float, default=999)
    pub_active = Column(Boolean, default=False)

    # Conferences & Events
    events_attended_ytd = Column(Integer, default=0)
    events_registered_ytd = Column(Integer, default=0)
    events_last_attended_days = Column(Float, default=999)
    events_annual_meeting_attended = Column(Boolean, default=False)
    events_active = Column(Boolean, default=False)

    # Career Services
    career_job_searches = Column(Integer, default=0)
    career_profile_complete_pct = Column(Float, default=0)
    career_applications = Column(Integer, default=0)
    career_advance_logins = Column(Integer, default=0)
    career_active = Column(Boolean, default=False)

    # Advocacy
    advocacy_action_center_visits = Column(Integer, default=0)
    advocacy_letters_sent = Column(Integer, default=0)
    advocacy_pac_donor = Column(Boolean, default=False)
    advocacy_newsletter_opens = Column(Integer, default=0)
    advocacy_active = Column(Boolean, default=False)

    active_stream_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
