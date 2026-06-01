from fastapi import APIRouter, Depends, Query

from backend.api.deps import get_current_user
from backend.ai.coalition import find_coalition

router = APIRouter(prefix="/api/rfps", tags=["coalition"])


@router.get("/{rfp_id}/coalition")
def coalition(
    rfp_id: str,
    max_team_size: int = Query(4, ge=1, le=8),
    _=Depends(get_current_user),
):
    """Assemble a complementary pharmacist team covering this RFP's specialties."""
    return find_coalition(rfp_id, max_team_size=max_team_size)
