"""
AI drug interaction checker engine.
Looks up known interactions + generates AI clinical summary.
"""
from __future__ import annotations

import json
from pathlib import Path

import anthropic

from backend.ai.prompts import INTERACTION_ANALYSIS_PROMPT
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_drug_db = json.loads(
    (Path(__file__).parent.parent / "data" / "drug_database.json").read_text()
)

# Build lookup index
_drug_index: dict[str, dict] = {}
for drug in _drug_db["drugs"]:
    _drug_index[drug["id"]] = drug
    _drug_index[drug["name"].lower()] = drug
    for alias in drug.get("aliases", []):
        _drug_index[alias.lower()] = drug

_interaction_index: dict[str, dict] = {}
for ix in _drug_db["interactions"]:
    key1 = f"{ix['drug_a']}|{ix['drug_b']}"
    key2 = f"{ix['drug_b']}|{ix['drug_a']}"
    _interaction_index[key1] = ix
    _interaction_index[key2] = ix


def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def lookup_drug(query: str) -> dict | None:
    """Find a drug by name or alias."""
    return _drug_index.get(query.lower().strip())


def search_drugs(prefix: str, limit: int = 8) -> list[dict]:
    """Autocomplete drug search."""
    prefix = prefix.lower().strip()
    seen: set[str] = set()
    results: list[dict] = []
    for drug in _drug_db["drugs"]:
        if drug["id"] in seen:
            continue
        if drug["name"].lower().startswith(prefix) or any(
            a.startswith(prefix) for a in drug.get("aliases", [])
        ):
            results.append({"id": drug["id"], "name": drug["name"]})
            seen.add(drug["id"])
        if len(results) >= limit:
            break
    return results


def check_interaction(drug_a_query: str, drug_b_query: str) -> dict:
    """Check interaction between two drugs. Returns full analysis."""
    drug_a = lookup_drug(drug_a_query)
    drug_b = lookup_drug(drug_b_query)

    drug_a_name = drug_a["name"] if drug_a else drug_a_query.title()
    drug_b_name = drug_b["name"] if drug_b else drug_b_query.title()

    known_interaction = None
    if drug_a and drug_b:
        key = f"{drug_a['id']}|{drug_b['id']}"
        known_interaction = _interaction_index.get(key)

    interaction_data_str = (
        json.dumps(known_interaction, indent=2)
        if known_interaction
        else "No specific interaction data found in APhA database for this pair."
    )

    prompt = INTERACTION_ANALYSIS_PROMPT.format(
        drug_a=drug_a_name,
        drug_b=drug_b_name,
        interaction_data=interaction_data_str,
    )

    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
    )
    summary = response.content[0].text.strip()

    return {
        "drug_a": drug_a_name,
        "drug_b": drug_b_name,
        "severity": known_interaction["severity"] if known_interaction else "unknown",
        "mechanism": known_interaction["mechanism"] if known_interaction else None,
        "clinical_effect": (
            known_interaction["clinical_effect"] if known_interaction else None
        ),
        "management": known_interaction["management"] if known_interaction else None,
        "summary": summary,
        "data_source": "APhA Drug Interaction Database",
        "disclaimer": (
            "For informational purposes only. "
            "Always verify interactions with current clinical resources. "
            "Absence of data does not indicate absence of interaction."
        ),
    }
