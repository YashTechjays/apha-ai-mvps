"""
Core AI CPE plan generator.
Takes user inputs + state requirements + course catalog → personalized plan.
"""
import json
import anthropic
from pathlib import Path
from datetime import date, datetime
from backend.ai.prompts import CPE_PLAN_PROMPT
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

_state_data = json.loads((Path(__file__).parent.parent / "data" / "state_requirements.json").read_text())
_course_data = json.loads((Path(__file__).parent.parent / "data" / "apha_courses.json").read_text())


def get_state_requirements(state_code: str) -> dict:
    return _state_data.get(state_code.upper(), {})


def get_days_until_renewal(renewal_date_str: str) -> int:
    renewal = datetime.strptime(renewal_date_str, "%Y-%m-%d").date()
    delta = (renewal - date.today()).days
    return max(delta, 0)


def filter_courses_for_state(state_req: dict, license_type: str, specialty: str) -> list:
    """Return courses relevant to this pharmacist — mandatory topics first."""
    mandatory_topics = [r["topic"].lower() for r in state_req.get("special_requirements", [])]
    courses = _course_data["courses"]

    def score(c):
        topic_match = any(t in " ".join(c["topics"]).lower() for t in mandatory_topics)
        type_match = license_type in c.get("suitable_for", ["pharmacist"])
        return (not topic_match, not type_match)

    return sorted(
        [c for c in courses if license_type in c.get("suitable_for", ["pharmacist"])],
        key=score
    )


def build_course_list_text(courses: list) -> str:
    lines = []
    for c in courses[:12]:
        lines.append(
            f'- [{c["id"]}] "{c["title"]}" — {c["cpe_hours"]} CPE hours — '
            f'${c["price_nonmember"]} (non-member) / Free (member) — {c["url"]}'
        )
    return "\n".join(lines)


def _fallback_plan(state_req, hours_gap, days_until, relevant_courses, member_savings, state_name) -> dict:
    """Deterministic plan when Claude API is unavailable."""
    mandatory_topics = state_req.get("special_requirements", [])
    selected = []
    total = 0.0
    used_ids = set()

    # Mandatory law first
    for req in mandatory_topics:
        for c in relevant_courses:
            if c["id"] in used_ids:
                continue
            if req["topic"].lower() in " ".join(c["topics"]).lower():
                selected.append({
                    "course_id": c["id"], "title": c["title"], "cpe_hours": c["cpe_hours"],
                    "why_recommended": f"Covers {state_name}'s required {req['topic']} hours.",
                    "is_mandatory": True,
                    "mandatory_reason": f"Required by {state_name}: {req['hours']}h {req['topic']}",
                    "price_nonmember": c["price_nonmember"], "url": c["url"],
                    "priority": len(selected) + 1,
                })
                used_ids.add(c["id"])
                total += c["cpe_hours"]
                break

    # Fill remaining gap
    for c in relevant_courses:
        if c["id"] in used_ids or total >= hours_gap:
            continue
        selected.append({
            "course_id": c["id"], "title": c["title"], "cpe_hours": c["cpe_hours"],
            "why_recommended": f"Relevant clinical course to fill your remaining {hours_gap - total:.1f}h gap.",
            "is_mandatory": False, "mandatory_reason": None,
            "price_nonmember": c["price_nonmember"], "url": c["url"],
            "priority": len(selected) + 1,
        })
        used_ids.add(c["id"])
        total += c["cpe_hours"]

    urgency = "critical" if days_until < 30 else "high" if days_until < 90 else "medium" if days_until < 180 else "low"
    return {
        "summary": f"You need {hours_gap}h to renew in {state_name}. We've assembled a {total}h plan covering your mandatory topics first.",
        "urgency_level": urgency,
        "urgency_message": f"Your license expires in {days_until} days — start with mandatory courses." if days_until < 90 else None,
        "total_plan_hours": round(total, 1),
        "mandatory_covered": all(any(t["mandatory_reason"] and req["topic"] in t["mandatory_reason"] for t in selected) for req in mandatory_topics) if mandatory_topics else True,
        "courses": selected,
        "member_savings_usd": member_savings,
        "member_cta": f"All {round(total, 1)} hours are included free with APhA membership — saving you ${member_savings} vs. buying individually.",
    }


def generate_cpe_plan(
    state: str,
    renewal_date: str,
    hours_completed: float,
    license_type: str = "pharmacist",
    specialty: str = "General Pharmacy",
) -> dict:
    state_req = get_state_requirements(state)
    if not state_req:
        raise ValueError(f"Unknown state code: {state}")

    hours_required = float(state_req["hours_required"])
    hours_gap = max(hours_required - hours_completed, 0)
    days_until = get_days_until_renewal(renewal_date)
    mandatory_topics = state_req.get("special_requirements", [])
    mandatory_text = ", ".join([f"{r['hours']}h {r['topic']}" for r in mandatory_topics]) or "None"

    relevant_courses = filter_courses_for_state(state_req, license_type, specialty)
    course_list_text = build_course_list_text(relevant_courses)
    member_savings = sum(c["price_nonmember"] for c in relevant_courses if c["price_nonmember"] > 0)

    plan = None
    if client:
        prompt = CPE_PLAN_PROMPT.format(
            state_name=state_req["name"], license_type=license_type, specialty=specialty,
            hours_completed=hours_completed, hours_required=hours_required,
            hours_gap=round(hours_gap, 1), days_until_renewal=days_until,
            mandatory_topics=mandatory_text, course_list=course_list_text,
            total_plan_hours=round(hours_gap, 1), member_savings=member_savings,
        )
        try:
            logger.info(f"Generating CPE plan: {state} | {hours_gap}h gap | {days_until} days")
            response = client.messages.create(
                model="claude-sonnet-4-20250514", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            plan = json.loads(raw.strip())
        except Exception as exc:
            logger.warning(f"Claude unavailable, using fallback: {exc}")

    if plan is None:
        plan = _fallback_plan(state_req, hours_gap, days_until, relevant_courses, member_savings, state_req["name"])

    plan["state"] = state
    plan["state_name"] = state_req["name"]
    plan["hours_required"] = hours_required
    plan["hours_completed"] = hours_completed
    plan["hours_gap"] = round(hours_gap, 1)
    plan["days_until_renewal"] = days_until
    plan["renewal_date"] = renewal_date
    plan["pct_complete"] = round((hours_completed / hours_required * 100), 1) if hours_required > 0 else 0
    plan["state_notes"] = state_req.get("notes", "")
    return plan
