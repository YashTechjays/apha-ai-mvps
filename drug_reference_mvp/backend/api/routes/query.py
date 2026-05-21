"""Clinical query endpoint."""
from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.ai.clinical_assistant import get_assistant
from backend.api.deps import enforce_quota_and_rate_limit, get_current_user, get_db
from backend.api.schemas.query import (
    ChunkItem,
    CitationItem,
    FeedbackRequest,
    QueryRequest,
    QueryResponse,
)
from backend.db.models import QueryLog, Subscription, User

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def submit_query(
    req: QueryRequest,
    request: Request,
    db: Session = Depends(get_db),
    enforced=Depends(enforce_quota_and_rate_limit),
):
    user: User = enforced["user"]
    sub: Subscription = enforced["subscription"]

    assistant = get_assistant()
    result = assistant.answer(req.question, category=req.category)

    # Log
    api_key_id = getattr(request.state, "api_key_id", None)
    log = QueryLog(
        user_id=user.id,
        organization_id=user.organization_id,
        api_key_id=uuid.UUID(api_key_id) if api_key_id else None,
        query_text=req.question,
        query_type=result.query_type,
        chunks_retrieved=len(result.chunks),
        sources_cited=len(result.citations),
        retrieval_score_avg=(
            sum(c.get("max_score", 0) for c in result.citations) / max(1, len(result.citations))
            if result.citations
            else None
        ),
        answer_text=result.answer,
        answer_tokens=result.answer_tokens,
        latency_ms=result.latency_ms,
        safety_flagged=result.safety_flagged,
        safety_reason=result.safety_reason,
    )
    db.add(log)

    # Decrement quota
    sub.queries_used_this_month = (sub.queries_used_this_month or 0) + 1
    db.commit()
    db.refresh(log)

    return QueryResponse(
        query_id=str(log.id),
        answer=result.answer,
        query_type=result.query_type,
        citations=[CitationItem(**c) for c in result.citations],
        chunks_used=len(result.chunks),
        latency_ms=result.latency_ms,
        safety_flagged=result.safety_flagged,
        used_fallback=result.used_fallback,
    )


@router.post("/feedback")
def submit_feedback(
    req: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        query_uuid = uuid.UUID(str(req.query_id))
    except (ValueError, TypeError):
        return {"recorded": False, "reason": "Invalid query_id."}
    log = (
        db.query(QueryLog)
        .filter(QueryLog.id == query_uuid, QueryLog.user_id == user.id)
        .first()
    )
    if not log:
        return {"recorded": False, "reason": "Query not found."}
    log.thumbs_up = req.thumbs_up
    log.feedback_text = req.feedback_text
    db.commit()
    return {"recorded": True}


@router.get("/history")
def query_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 25,
):
    rows = (
        db.query(QueryLog)
        .filter(QueryLog.user_id == user.id)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "query_text": r.query_text,
            "query_type": r.query_type,
            "sources_cited": r.sources_cited,
            "latency_ms": r.latency_ms,
            "thumbs_up": r.thumbs_up,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
