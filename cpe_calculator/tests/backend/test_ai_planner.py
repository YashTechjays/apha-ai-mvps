from datetime import date, timedelta
from backend.ai.planner import (
    get_state_requirements, get_days_until_renewal,
    filter_courses_for_state, generate_cpe_plan,
)


def test_get_state_requirements_valid():
    req = get_state_requirements("CA")
    assert req["name"] == "California"
    assert req["hours_required"] == 30


def test_get_state_requirements_case_insensitive():
    req = get_state_requirements("ca")
    assert req["name"] == "California"


def test_get_state_requirements_invalid():
    req = get_state_requirements("XX")
    assert req == {}


def test_days_until_renewal_future():
    future = (date.today() + timedelta(days=90)).isoformat()
    days = get_days_until_renewal(future)
    assert 88 <= days <= 91


def test_filter_courses_returns_list():
    req = get_state_requirements("TX")
    courses = filter_courses_for_state(req, "pharmacist", "General Pharmacy")
    assert isinstance(courses, list)
    assert len(courses) > 0


def test_fallback_plan_generation():
    """When Claude unavailable, fallback plan must still produce valid output."""
    future = (date.today() + timedelta(days=120)).isoformat()
    plan = generate_cpe_plan("TX", future, 10.0, "pharmacist", "General Pharmacy")
    assert plan["state"] == "TX"
    assert plan["hours_gap"] == 20.0
    assert len(plan["courses"]) > 0
    assert plan["total_plan_hours"] > 0


def test_mandatory_law_appears_in_plan_for_pa():
    """PA requires 2h law — fallback should include the law course."""
    future = (date.today() + timedelta(days=200)).isoformat()
    plan = generate_cpe_plan("PA", future, 0.0, "pharmacist", "General Pharmacy")
    mandatory_courses = [c for c in plan["courses"] if c["is_mandatory"]]
    assert len(mandatory_courses) > 0
