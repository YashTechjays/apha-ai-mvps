from fastapi import APIRouter, Depends, Query
from backend.api.deps import get_current_user
from backend.api.schemas.graph import GraphStatsResponse
from backend.graph.queries import get_graph_stats
from backend.ai.graph_insights import get_insights

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/stats", response_model=GraphStatsResponse)
def graph_stats(_=Depends(get_current_user)):
    return get_graph_stats()


@router.get("/insights")
def graph_insights(limit: int = Query(10, le=50), _=Depends(get_current_user)):
    """Enhancement #5b — most active organizations + trending categories."""
    return get_insights(limit)
