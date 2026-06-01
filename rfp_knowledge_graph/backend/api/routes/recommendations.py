from fastapi import APIRouter, Depends, Query
from typing import Optional
from backend.api.deps import get_current_user
from backend.graph.queries import get_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/")
def recommendations(
    categories: Optional[str] = Query(None, description="Comma-separated category names"),
    states: Optional[str] = Query(None, description="Comma-separated state names"),
    limit: int = Query(10, le=50),
    _=Depends(get_current_user),
):
    cat_list = [c.strip() for c in categories.split(",")] if categories else None
    state_list = [s.strip() for s in states.split(",")] if states else None
    return get_recommendations(categories=cat_list, states=state_list, limit=limit)
