from pydantic import BaseModel, field_validator
from typing import Optional, List


class CalculatorRequest(BaseModel):
    session_id: str
    state: str
    renewal_date: str
    hours_completed: float
    license_type: str = "pharmacist"
    specialty: Optional[str] = "General Pharmacy"

    @field_validator("hours_completed")
    @classmethod
    def validate_hours(cls, v):
        if v < 0:
            raise ValueError("Hours completed cannot be negative")
        if v > 100:
            raise ValueError("Hours completed seems too high — please check")
        return v

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return v.upper()


class CourseRecommendation(BaseModel):
    course_id: str
    title: str
    cpe_hours: float
    why_recommended: str
    is_mandatory: bool
    mandatory_reason: Optional[str] = None
    price_nonmember: float
    url: str
    priority: int


class CalculatorResponse(BaseModel):
    calculation_id: str
    state: str
    state_name: str
    hours_required: float
    hours_completed: float
    hours_gap: float
    pct_complete: float
    days_until_renewal: int
    renewal_date: str
    urgency_level: str
    urgency_message: Optional[str] = None
    summary: str
    total_plan_hours: float
    mandatory_covered: bool
    courses: List[CourseRecommendation]
    member_savings_usd: float
    member_cta: str
    state_notes: str
    is_preview: bool = True
    preview_courses_count: int = 3
