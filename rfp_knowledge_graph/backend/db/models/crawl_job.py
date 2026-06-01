import enum
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class CrawlStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    status = Column(Enum(CrawlStatus), default=CrawlStatus.pending)
    pages_crawled = Column(Integer, default=0)
    rfps_extracted = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    include_patterns = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
