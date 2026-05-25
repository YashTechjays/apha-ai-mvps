"""High-level retriever that wraps the vector store with filtering and scoring."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from apps.drug_ref.rag.vector_store import get_vector_store
from apps.drug_ref.utils.config import settings
from apps.drug_ref.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    source_title: str
    source_type: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "score": round(self.score, 4),
            "source_title": self.source_title,
            "source_type": self.source_type,
            "category": self.category,
            "metadata": self.metadata,
        }


class Retriever:
    """Retrieves and filters chunks from the vector store."""

    def __init__(
        self,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ):
        self.top_k = top_k or settings.rag_top_k
        self.min_score = min_score if min_score is not None else settings.rag_min_score
        self.store = get_vector_store()

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[RetrievedChunk]:
        if not query or not query.strip():
            return []

        where_clause: Dict[str, Any] = {}
        if category:
            where_clause["category"] = category
        if source_type:
            where_clause["source_type"] = source_type

        k = top_k or self.top_k

        try:
            raw = self.store.query(
                query_text=query,
                top_k=k * 2,  # over-fetch then filter by min_score
                where=where_clause if where_clause else None,
            )
        except Exception as e:
            logger.warning(f"Retrieval failed: {e}")
            return []

        chunks: List[RetrievedChunk] = []
        for r in raw:
            score = r.get("score", 0.0)
            if score < self.min_score:
                continue
            meta = r.get("metadata") or {}
            chunks.append(RetrievedChunk(
                chunk_id=r.get("id", ""),
                text=r.get("text", ""),
                score=score,
                source_title=meta.get("source_title", "Unknown"),
                source_type=meta.get("source_type", "unknown"),
                category=meta.get("category", "general"),
                metadata=meta,
            ))
            if len(chunks) >= k:
                break

        return chunks

    def retrieve_with_diversity(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[RetrievedChunk]:
        """Retrieve chunks, deduplicating by source to maximize diversity."""
        k = top_k or self.top_k
        raw_chunks = self.retrieve(query, top_k=k * 2)

        seen_sources = set()
        diverse: List[RetrievedChunk] = []
        for c in raw_chunks:
            if c.source_title in seen_sources and len(diverse) >= k // 2:
                continue
            seen_sources.add(c.source_title)
            diverse.append(c)
            if len(diverse) >= k:
                break
        return diverse


_retriever_instance: Optional[Retriever] = None


def get_retriever() -> Retriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance
