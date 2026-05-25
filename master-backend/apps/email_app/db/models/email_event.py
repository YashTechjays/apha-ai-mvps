from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from apps.email_app.db.base import Base


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(String, primary_key=True)
    email_send_id = Column(String, ForeignKey("email_sends.id"), nullable=False, index=True)
    member_id = Column(String, ForeignKey("email_members.id"), nullable=False, index=True)

    event_type = Column(String, nullable=False)  # open, click, bounce, unsubscribe, spam_report
    sendgrid_event_id = Column(String)
    url_clicked = Column(String)
    user_agent = Column(String)
    ip_address = Column(String)
    raw_payload = Column(JSON)

    occurred_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
