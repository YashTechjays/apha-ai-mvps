from pydantic import BaseModel
from typing import Optional


class SalaryRequest(BaseModel):
    session_id: str
    state: str
    specialty: str
    license_type: str = "pharmacist"
    years_experience: str = "6-10"
    current_salary: Optional[float] = None


class SalaryResponse(BaseModel):
    usage_id: str
    p25: int
    p50: int
    p75: int
    p90: int
    percentile: Optional[int] = None
    gap_to_median: Optional[int] = None
    gap_to_75th: Optional[int] = None
    member_premium_salary: int
    commentary: str
    headline: str
    state_name: str
    specialty: str
    is_preview: bool = True
    remaining_free_checks: int
