from pydantic import BaseModel
from typing import Optional, Dict, Any


class CareerProfile(BaseModel):
    session_id: str
    license_type: str
    specialty: str
    state: str
    years_experience: str
    career_stage: str
    # Assessment answers
    board_certifications: int = 0
    cpe_hours_2yr: float = 0
    certificates_earned: int = 0
    immunization_certified: bool = False
    mtm_experience: bool = False
    leadership_roles: int = 0
    advocacy_activities: bool = False
    mentorship_active: bool = False
    technology_skills: int = 3
    association_member: bool = False
    presentations_given: int = 0
    research_collaborations: bool = False


class CareerScoreResponse(BaseModel):
    usage_id: str
    overall_score: int
    scores: Dict[str, Any]
    summary: str
    top_strength: str
    top_strength_note: str
    top_gap: str
    top_gap_note: str
    peer_percentile: int
    trajectory: str
    action_plan_locked: bool = True
    action_plan_preview: str
