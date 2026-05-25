"""
Global suppression list — unsubscribes, bounces, spam reports.
Always checked before any send. Takes priority over everything.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from apps.outreach.db.base import Base


class Suppression(Base):
    __tablename__ = "outreach_suppressions"

    email = Column(String, primary_key=True, index=True)
    reason = Column(String)
    source = Column(String, nullable=True)
    added_at = Column(DateTime, server_default=func.now())
