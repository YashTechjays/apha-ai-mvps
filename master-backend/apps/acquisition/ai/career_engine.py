"""AI career readiness scoring engine."""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from apps.acquisition.ai.prompts import CAREER_SCORE_PROMPT, CAREER_ACTION_PLAN_PROMPT
from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_competencies = json.loads(
    (Path(__file__).parent.parent / "data" / "career_competencies.json").read_text()
)

DIMENSION_LABELS = {
    "clinical_knowledge": "Clinical Knowledge",
    "patient_care": "Patient Care Skills",
    "professional_development": "Professional Development",
    "leadership": "Leadership & Advocacy",
    "business_acumen": "Business & Technology",
    "networking": "Professional Network",
}


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def score_career(profile: dict) -> dict:
    prompt = CAREER_SCORE_PROMPT.format(profile_json=json.dumps(profile, indent=2))
    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    scores = _parse_json_response(response.content[0].text)

    enriched_scores = {}
    for dim_id, score in scores.get("scores", {}).items():
        enriched_scores[dim_id] = {
            "score": score,
            "label": DIMENSION_LABELS.get(dim_id, dim_id.replace("_", " ").title()),
            "apha_resources": next(
                (d["apha_resources"] for d in _competencies["dimensions"] if d["id"] == dim_id), []
            ),
        }

    career_stage = profile.get("career_stage", "mid_career")
    expected = _competencies["career_stages"].get(career_stage, {"expected_score": 60})["expected_score"]
    overall = scores.get("overall_score", 0)
    peer_pct = max(10, min(95, 50 + (overall - expected) * 2))

    scores["scores"] = enriched_scores
    scores["peer_percentile"] = int(peer_pct)
    scores["expected_score_for_stage"] = expected
    return scores


def generate_action_plan(profile: dict, scores: dict) -> dict:
    top_gap = scores.get("top_gap", "professional_development")
    gap_score = scores.get("scores", {}).get(top_gap, {})
    gap_score_val = gap_score.get("score", 50) if isinstance(gap_score, dict) else 50

    prompt = CAREER_ACTION_PLAN_PROMPT.format(
        profile_summary=json.dumps({
            k: v for k, v in profile.items()
            if k in ["license_type", "specialty", "state", "career_stage", "years_experience"]
        }),
        scores_json=json.dumps({
            k: v.get("score") if isinstance(v, dict) else v
            for k, v in scores.get("scores", {}).items()
        }),
        top_gap=top_gap, gap_score=gap_score_val,
        career_stage=profile.get("career_stage", "mid_career"),
        top_gap_label=DIMENSION_LABELS.get(top_gap, top_gap),
    )
    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_response(response.content[0].text)
