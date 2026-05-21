"""Analytics endpoints (admin / team-level usage)."""
from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_db
from backend.db.models import QueryLog, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/usage")
def usage_summary(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    base_q = db.query(QueryLog).filter(QueryLog.created_at >= cutoff)
    if user.organization_id:
        base_q = base_q.filter(QueryLog.organization_id == user.organization_id)
    else:
        base_q = base_q.filter(QueryLog.user_id == user.id)

    total = base_q.count()
    flagged = base_q.filter(QueryLog.safety_flagged == True).count()
    avg_latency = base_q.with_entities(func.avg(QueryLog.latency_ms)).scalar() or 0
    avg_sources = base_q.with_entities(func.avg(QueryLog.sources_cited)).scalar() or 0
    thumbs_up = base_q.filter(QueryLog.thumbs_up == True).count()
    thumbs_down = base_q.filter(QueryLog.thumbs_up == False).count()

    # Top query types
    rows = (
        base_q.with_entities(QueryLog.query_type, func.count(QueryLog.id))
        .group_by(QueryLog.query_type)
        .order_by(func.count(QueryLog.id).desc())
        .limit(10)
        .all()
    )
    by_type = [{"query_type": r[0] or "general", "count": int(r[1])} for r in rows]

    return {
        "period_days": days,
        "total_queries": total,
        "safety_flagged": flagged,
        "avg_latency_ms": round(float(avg_latency), 1),
        "avg_sources_cited": round(float(avg_sources), 2),
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "by_query_type": by_type,
    }


@router.get("/health")
def analytics_health():
    return {"status": "ok"}
