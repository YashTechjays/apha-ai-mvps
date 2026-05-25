import json
from pathlib import Path

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.usage import ToolUsage
from backend.api.schemas.salary import SalaryRequest, SalaryResponse
from backend.ai.salary_engine import generate_salary_analysis
from backend.rate_limiter.redis_limiter import check_limit
from backend.utils.logger import get_logger

router = APIRouter(prefix="/salary", tags=["salary"])
logger = get_logger(__name__)

_salary_data = json.loads(
    (Path(__file__).parent.parent.parent / "data" / "salary_data.json").read_text()
)


@router.post("/benchmark", response_model=SalaryResponse)
def salary_benchmark(
    req: SalaryRequest, request: Request, db: Session = Depends(get_db)
):
    ip = request.client.host or "unknown"
    allowed, rate_info = check_limit(ip, "salary")

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": f"You've used your {rate_info['limit']} free salary checks today.",
                "upgrade_message": "Join APhA for unlimited access to salary benchmarks.",
                "join_url": "https://www.pharmacist.com/join",
            },
        )

    result = generate_salary_analysis(
        state=req.state,
        specialty=req.specialty,
        license_type=req.license_type,
        years_experience=req.years_experience,
        current_salary=req.current_salary,
    )

    usage = ToolUsage(
        session_id=req.session_id,
        ip_hash=ip[:8],
        tool="salary",
        input_summary=f"{req.state} / {req.specialty} / {req.years_experience}yrs",
        result_score=float(result.get("percentile") or 0),
        result_summary=result.get("headline", ""),
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)

    return SalaryResponse(
        usage_id=str(usage.id),
        p25=result["p25"],
        p50=result["p50"],
        p75=result["p75"],
        p90=result["p90"],
        percentile=result.get("percentile"),
        gap_to_median=result.get("gap_to_median"),
        gap_to_75th=result.get("gap_to_75th"),
        member_premium_salary=result["member_premium_salary"],
        commentary=result["commentary"],
        headline=result["headline"],
        state_name=result["state_name"],
        specialty=result["specialty"],
        remaining_free_checks=rate_info["remaining"],
    )


@router.get("/states")
def get_salary_states():
    return [
        {"code": k, "name": v["name"]} for k, v in _salary_data["by_state"].items()
    ]


@router.get("/specialties")
def get_specialties():
    return list(_salary_data["by_specialty"].keys())
