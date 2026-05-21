"""Pydantic schemas for clinical query endpoints."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    category: Optional[str] = None  # drug_monograph | clinical_guideline | pharmacy_practice


class CitationItem(BaseModel):
    title: str
    category: str
    source_type: str
    file_path: Optional[str] = None
    max_score: float
    snippet_count: int


class ChunkItem(BaseModel):
    chunk_id: str
    source_title: str
    score: float
    snippet: Optional[str] = None


class QueryResponse(BaseModel):
    query_id: str
    answer: str
    query_type: str
    citations: List[CitationItem]
    chunks_used: int
    latency_ms: int
    safety_flagged: bool
    used_fallback: bool


class FeedbackRequest(BaseModel):
    query_id: str
    thumbs_up: bool
    feedback_text: Optional[str] = None
