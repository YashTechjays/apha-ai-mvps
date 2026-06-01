from uuid import UUID
from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime


class CrawlTriggerRequest(BaseModel):
    url: Optional[str] = None


class CrawlTriggerResponse(BaseModel):
    job_id: str
    status: str
    message: str


class CrawlJobResponse(BaseModel):
    id: UUID
    url: str
    status: str
    pages_crawled: int
    rfps_extracted: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str:
        return str(v)
