"""AI salary analysis engine."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from apps.acquisition.ai.prompts import SALARY_ANALYSIS_PROMPT, SALARY_QUICK_INSIGHT_PROMPT
from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_salary_data = json.loads(
    (Path(__file__).parent.parent / "data" / "salary_data.json").read_text()
)


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def compute_salary_benchmark(
    state: str,
    specialty: str,
    license_type: str,
    years_experience: str,
    current_salary: float | None = None,
) -> dict:
    base = _salary_data["national_average"].get(
        license_type, _salary_data["national_average"]["pharmacist"]
    )

    specialty_data = _salary_data["by_specialty"].get(specialty, {})
    if specialty_data:
        p25, p50, p75, p90 = specialty_data["p25"], specialty_data["p50"], specialty_data["p75"], specialty_data["p90"]
    else:
        p25, p50, p75, p90 = base["p25"], base["p50"], base["p75"], base["p90"]

    state_data = _salary_data["by_state"].get(state.upper(), {"multiplier": 1.0})
    mult = state_data["multiplier"]
    p25, p50, p75, p90 = int(p25 * mult), int(p50 * mult), int(p75 * mult), int(p90 * mult)

    exp_mult = _salary_data["experience_multipliers"].get(years_experience, 1.0)
    p25, p50, p75, p90 = int(p25 * exp_mult), int(p50 * exp_mult), int(p75 * exp_mult), int(p90 * exp_mult)

    percentile = gap_to_median = gap_to_75th = None
    if current_salary:
        current_salary = float(current_salary)
        if current_salary <= p25:
            percentile = 20
        elif current_salary <= p50:
            percentile = 25 + int((current_salary - p25) / max(p50 - p25, 1) * 25)
        elif current_salary <= p75:
            percentile = 50 + int((current_salary - p50) / max(p75 - p50, 1) * 25)
        elif current_salary <= p90:
            percentile = 75 + int((current_salary - p75) / max(p90 - p75, 1) * 15)
        else:
            percentile = 90
        gap_to_median = int(p50 - current_salary)
        gap_to_75th = int(p75 - current_salary)

    member_premium_salary = int(p50 * (1 + _salary_data["apha_member_premium"]))

    return {
        "p25": p25, "p50": p50, "p75": p75, "p90": p90,
        "percentile": percentile, "gap_to_median": gap_to_median,
        "gap_to_75th": gap_to_75th, "member_premium_salary": member_premium_salary,
        "state_name": state_data.get("name", state),
        "member_survey_note": _salary_data["member_survey_note"],
    }


def generate_salary_analysis(
    state: str, specialty: str, license_type: str,
    years_experience: str, current_salary: float | None = None,
) -> dict:
    benchmark = compute_salary_benchmark(state, specialty, license_type, years_experience, current_salary)
    state_name = benchmark["state_name"]
    percentile = benchmark.get("percentile") or 50

    prompt = SALARY_ANALYSIS_PROMPT.format(
        license_type=license_type.replace("_", " ").title(), specialty=specialty,
        state_name=state_name, years_experience=years_experience,
        current_salary=int(current_salary) if current_salary else "Not provided",
        p25=benchmark["p25"], p50=benchmark["p50"], p75=benchmark["p75"],
        p90=benchmark["p90"], percentile=percentile,
    )

    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    commentary = response.content[0].text.strip()

    insight_prompt = SALARY_QUICK_INSIGHT_PROMPT.format(
        specialty=specialty, state=state_name, percentile=percentile
    )
    insight_response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=60,
        messages=[{"role": "user", "content": insight_prompt}],
    )
    headline = insight_response.content[0].text.strip().strip('"')

    return {
        **benchmark, "commentary": commentary, "headline": headline,
        "specialty": specialty, "state": state,
        "years_experience": years_experience, "license_type": license_type,
    }
