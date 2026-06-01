"""Graph-derived historical signals for win-prediction (Enhancement #3).

These features only carry signal once application/win history exists in the
graph (Enhancement #1). When no history is available they return None, and
the matcher falls back to its original 4-factor formula — fully backward
compatible for cold-start profiles.
"""
from typing import Optional
from backend.graph.pharmacist_graph import get_org_win_rate, get_category_affinity
from backend.utils.logger import get_logger

logger = get_logger("graph_features")


def history_score(user_id: Optional[str], rfp: dict) -> Optional[float]:
    """Blend org win-rate and the pharmacist's category affinity into a 0-1
    score. Returns None when there is no usable history."""
    if not user_id:
        return None

    signals: list[float] = []
    try:
        org_name = rfp.get("organization_name")
        if not org_name:
            org = rfp.get("organization")
            org_name = org.get("name") if isinstance(org, dict) else None

        org_rate = get_org_win_rate(org_name) if org_name else None
        if org_rate is not None:
            signals.append(org_rate)

        affinity = get_category_affinity(user_id, rfp.get("categories") or [])
        if affinity is not None:
            signals.append(affinity)
    except Exception as e:
        logger.warning(f"history_score failed: {e}")
        return None

    if not signals:
        return None
    return sum(signals) / len(signals)
