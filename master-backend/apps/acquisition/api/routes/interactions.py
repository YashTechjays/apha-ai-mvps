from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from apps.acquisition.db.session import get_db
from apps.acquisition.db.models.usage import ToolUsage
from apps.acquisition.api.schemas.interaction import (
    InteractionRequest,
    InteractionResponse,
    DrugSearchRequest,
)
from apps.acquisition.ai.interaction_engine import check_interaction, search_drugs
from apps.acquisition.rate_limiter.redis_limiter import check_limit
from core.logger import get_logger

router = APIRouter(prefix="/interactions", tags=["acquisition-interactions"])
logger = get_logger(__name__)


@router.post("/check", response_model=InteractionResponse)
def check_drug_interaction(
    req: InteractionRequest, request: Request, db: Session = Depends(get_db)
):
    if not req.drug_a.strip() or not req.drug_b.strip():
        raise HTTPException(status_code=400, detail="Both drug names are required")

    if req.drug_a.lower().strip() == req.drug_b.lower().strip():
        raise HTTPException(
            status_code=400, detail="Please enter two different drugs"
        )

    ip = request.client.host or "unknown"
    allowed, rate_info = check_limit(ip, "interaction")

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": f"You've used your {rate_info['limit']} free interaction checks today.",
                "upgrade_message": "APhA members get unlimited drug interaction checks.",
                "join_url": "https://www.pharmacist.com/join",
            },
        )

    result = check_interaction(req.drug_a, req.drug_b)

    usage = ToolUsage(
        session_id=req.session_id,
        ip_hash=ip[:8],
        tool="interaction",
        input_summary=f"{result['drug_a']} + {result['drug_b']}",
        result_summary=result["severity"],
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)

    return InteractionResponse(
        usage_id=str(usage.id),
        drug_a=result["drug_a"],
        drug_b=result["drug_b"],
        severity=result["severity"],
        mechanism=result.get("mechanism"),
        clinical_effect=result.get("clinical_effect"),
        management=result.get("management"),
        summary=result["summary"],
        disclaimer=result["disclaimer"],
        remaining_free_checks=rate_info["remaining"],
        is_limited=rate_info["remaining"] == 0,
    )


@router.post("/search")
def drug_search(req: DrugSearchRequest):
    if len(req.prefix.strip()) < 2:
        return []
    return search_drugs(req.prefix, req.limit)
