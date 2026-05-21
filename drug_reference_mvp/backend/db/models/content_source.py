import uuid
from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.db.base import Base


class ContentSource(Base):
    __tablename__ = "content_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    source_type = Column(String)
    category = Column(String)
    file_path = Column(String, nullable=True)
    chunk_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    version = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    ingested_at = Column(DateTime, server_default=func.now())
