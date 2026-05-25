import uuid
from unittest.mock import MagicMock, patch
import json


def _make_profile():
    return {
        "session_id": str(uuid.uuid4()),
        "license_type": "pharmacist",
        "specialty": "Hospital/Health-System",
        "state": "TX",
        "years_experience": "6-10",
        "career_stage": "mid_career",
        "board_certifications": 1,
        "cpe_hours_2yr": 30,
        "certificates_earned": 2,
        "immunization_certified": True,
        "mtm_experience": True,
        "leadership_roles": 1,
        "advocacy_activities": False,
        "mentorship_active": True,
        "technology_skills": 4,
        "association_member": True,
        "presentations_given": 0,
        "research_collaborations": False,
    }


def test_career_score(client):
    # Mock career engine to return valid JSON
    mock_scores = {
        "overall_score": 65,
        "scores": {
            "clinical_knowledge": 72,
            "patient_care": 65,
            "professional_development": 58,
            "leadership": 45,
            "business_acumen": 70,
            "networking": 50,
        },
        "summary": "Solid mid-career pharmacist with strong clinical knowledge.",
        "top_strength": "clinical_knowledge",
        "top_strength_note": "Strong board certification and CPE commitment.",
        "top_gap": "leadership",
        "top_gap_note": "Limited leadership experience for career stage.",
        "peer_comparison": "You score higher than 55% of mid-career pharmacists.",
        "trajectory": "On track",
    }
    mock_plan = {
        "headline": "Your 90-day plan for Leadership development",
        "actions": [
            {
                "title": "Join a committee",
                "description": "Take on a leadership role.",
                "apha_resource": "APhA Leadership Program",
                "apha_resource_url": "https://pharmacist.com/leadership",
                "timeline": "Week 1-2",
            }
        ],
    }

    mock_response_score = MagicMock()
    mock_response_score.content = [MagicMock(text=json.dumps(mock_scores))]
    mock_response_plan = MagicMock()
    mock_response_plan.content = [MagicMock(text=json.dumps(mock_plan))]

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [mock_response_score, mock_response_plan]

    with patch("backend.ai.career_engine._get_client", return_value=mock_client):
        r = client.post("/career/score", json=_make_profile())
        assert r.status_code == 200
        data = r.json()
        assert 0 <= data["overall_score"] <= 100
        assert "scores" in data
        assert len(data["scores"]) == 6
        assert "top_gap" in data
        assert "action_plan_locked" in data
