"""
Generate personalized 3-touch email sequences for individual prospects.
"""
import json
import anthropic
from apps.outreach.db.models.prospect import Prospect
from apps.outreach.ai.prompts import (
    TOUCH1_PROMPT, TOUCH2_PROMPT, TOUCH3_PROMPT, TIER_VALUE_PROPS
)
from apps.outreach.utils.config import get_settings
from apps.outreach.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _parse(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _infer_tier(prospect: Prospect) -> str:
    license_type = (prospect.license_type or "pharmacist").lower()
    career_stage = (prospect.career_stage or "mid_career").lower()
    if license_type == "student" or career_stage == "student":
        return "student"
    if license_type == "technician":
        return "technician"
    if license_type == "new_practitioner" or career_stage == "new_practitioner":
        return "new_practitioner"
    return "pharmacist"


def generate_touch1(prospect: Prospect) -> dict:
    """Generate Touch 1 -- introduction email."""
    tier = _infer_tier(prospect)
    value_prop = TIER_VALUE_PROPS.get(tier, TIER_VALUE_PROPS["pharmacist"])

    prompt = TOUCH1_PROMPT.format(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        license_type=(prospect.license_type or "pharmacist").replace("_", " ").title(),
        specialty=prospect.specialty or prospect.practice_setting or "General Pharmacy",
        state=prospect.state or "your state",
        career_stage=(prospect.career_stage or "mid-career").replace("_", " "),
        credential=prospect.credential or "PharmD",
        tier=tier.replace("_", " ").title(),
        value_prop=value_prop,
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
    )
    result = _parse(response.content[0].text)
    result["tier"] = tier
    logger.info(f"Touch 1 generated for {prospect.email or prospect.first_name} | tier={tier}")
    return result


def generate_touch2(prospect: Prospect, touch1_subject: str, days_since: int = 5) -> dict:
    """Generate Touch 2 -- follow-up value email."""
    prompt = TOUCH2_PROMPT.format(
        first_name=prospect.first_name,
        license_type=(prospect.license_type or "pharmacist").replace("_", " ").title(),
        specialty=prospect.specialty or "General Pharmacy",
        state=prospect.state or "your state",
        touch1_subject=touch1_subject,
        days_since_touch1=days_since,
    )
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse(response.content[0].text)


def generate_touch3(
    prospect: Prospect,
    touch1_subject: str,
    touch2_subject: str,
) -> dict:
    """Generate Touch 3 -- closing email."""
    prompt = TOUCH3_PROMPT.format(
        first_name=prospect.first_name,
        license_type=(prospect.license_type or "pharmacist").replace("_", " ").title(),
        specialty=prospect.specialty or "General Pharmacy",
        state=prospect.state or "your state",
        touch1_subject=touch1_subject,
        touch2_subject=touch2_subject,
    )
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse(response.content[0].text)


def generate_full_sequence(prospect: Prospect) -> list:
    """
    Generate all 3 touches for a single prospect.
    Returns list of {touch_number, subject, body}.
    """
    t1 = generate_touch1(prospect)
    t2 = generate_touch2(prospect, touch1_subject=t1["subject"])
    t3 = generate_touch3(prospect, touch1_subject=t1["subject"], touch2_subject=t2["subject"])

    return [
        {"touch_number": 1, **t1},
        {"touch_number": 2, **t2},
        {"touch_number": 3, **t3},
    ]
