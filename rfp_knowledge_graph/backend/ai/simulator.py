"""Win-Probability Simulator — interactive what-if scoring.

Recomputes a pharmacist's win probability for an RFP when they toggle
hypothetical profile changes (add a specialty, earn a certification, relocate).
Uses a deterministic variant of the production matcher's factor model so every
toggle is instant and works fully offline (no LLM/network per keystroke). The
factor *weights* match ``matcher`` so simulated odds line up with real matches.
"""
import re

from backend.ai.matcher import (
    W_CATEGORY, W_REQUIREMENTS, W_LOCATION, W_ORG_TYPE,
    _jaccard, _location_score, _org_type_score, normalize_state,
)
from backend.graph.neo4j_client import get_session
from backend.graph.queries import get_rfp_detail
from backend.utils.logger import get_logger

logger = get_logger("simulator")


def _deterministic_req_score(requirements: list[str], certifications: list[str]) -> float:
    """Offline stand-in for the LLM requirements score: keyword overlap between
    each requirement and the pharmacist's certifications/skills (0-1)."""
    if not requirements:
        return 0.5
    if not certifications:
        return 0.3
    cert_text = " ".join(certifications).lower()
    hits = 0
    for req in requirements:
        tokens = [t for t in re.split(r"[^a-z0-9]+", req.lower()) if len(t) > 3]
        if tokens and sum(1 for t in tokens if t in cert_text) / len(tokens) >= 0.34:
            hits += 1
    return hits / len(requirements)


def _score(rfp: dict, profile: dict) -> dict:
    """Deterministic 4-factor probability with a per-factor breakdown."""
    cat = _jaccard(rfp.get("categories", []), profile.get("specialties", []))
    req = _deterministic_req_score(rfp.get("requirements", []), profile.get("certifications", []))
    loc = _location_score(rfp.get("location_state"), profile.get("location_state"))
    org = _org_type_score(rfp.get("org_type"), profile.get("org_types_preferred", []))
    total = W_CATEGORY * cat + W_REQUIREMENTS * req + W_LOCATION * loc + W_ORG_TYPE * org
    return {
        "probability": round(total * 100),
        "factors": {
            "category": {"score": round(cat * 100), "weight": W_CATEGORY},
            "requirements": {"score": round(req * 100), "weight": W_REQUIREMENTS},
            "location": {"score": round(loc * 100), "weight": W_LOCATION},
            "org_type": {"score": round(org * 100), "weight": W_ORG_TYPE},
        },
    }


def _rfp_for_sim(rfp_id: str) -> dict:
    """Normalize an RFP detail into the flat shape the scorer expects."""
    rfp = get_rfp_detail(rfp_id)
    if not rfp:
        return {}
    org = rfp.get("organization") or {}
    loc = rfp.get("location") or {}
    return {
        "id": rfp.get("id"),
        "title": rfp.get("title"),
        "categories": rfp.get("categories", []),
        "requirements": rfp.get("requirements", []),
        "org_type": org.get("type") if isinstance(org, dict) else None,
        "location_state": loc.get("state") if isinstance(loc, dict) else None,
    }


def _all_categories() -> list[str]:
    """Distinct categories in the graph — the toggle palette for specialties."""
    query = "MATCH (c:Category) RETURN DISTINCT c.name AS name ORDER BY name"
    with get_session() as session:
        return [r["name"] for r in session.run(query) if r["name"]]


def _levers(rfp: dict, profile: dict, current: dict) -> list[dict]:
    """Rank the highest-impact single changes the pharmacist could make."""
    levers = []
    have = set(profile.get("specialties") or [])
    for cat in rfp.get("categories", []):
        if cat in have:
            continue
        hypo = {**profile, "specialties": list(have | {cat})}
        gain = _score(rfp, hypo)["probability"] - current["probability"]
        if gain > 0:
            levers.append({"type": "specialty", "value": cat, "delta": gain})

    rfp_state = rfp.get("location_state")
    if rfp_state and normalize_state(profile.get("location_state")) != normalize_state(rfp_state):
        hypo = {**profile, "location_state": rfp_state}
        gain = _score(rfp, hypo)["probability"] - current["probability"]
        if gain > 0:
            levers.append({"type": "location", "value": rfp_state, "delta": gain})

    levers.sort(key=lambda x: x["delta"], reverse=True)
    return levers[:5]


def baseline(rfp_id: str, profile: dict) -> dict:
    """Current win probability + breakdown + the palette of available toggles."""
    rfp = _rfp_for_sim(rfp_id)
    if not rfp:
        return {}
    current = _score(rfp, profile)
    return {
        "rfp_id": rfp_id,
        "rfp_title": rfp.get("title"),
        "profile": {
            "specialties": profile.get("specialties") or [],
            "certifications": profile.get("certifications") or [],
            "location_state": profile.get("location_state"),
            "org_types_preferred": profile.get("org_types_preferred") or [],
        },
        "rfp_categories": rfp.get("categories", []),
        "available_specialties": _all_categories(),
        "baseline": current,
        "levers": _levers(rfp, profile, current),
    }


def simulate(rfp_id: str, base_profile: dict, hypothetical: dict) -> dict:
    """Compare baseline odds to a hypothetical profile (no persistence)."""
    rfp = _rfp_for_sim(rfp_id)
    if not rfp:
        return {}
    base = _score(rfp, base_profile)
    sim = _score(rfp, {
        "specialties": hypothetical.get("specialties", base_profile.get("specialties") or []),
        "certifications": hypothetical.get("certifications", base_profile.get("certifications") or []),
        "location_state": hypothetical.get("location_state", base_profile.get("location_state")),
        "org_types_preferred": hypothetical.get(
            "org_types_preferred", base_profile.get("org_types_preferred") or []
        ),
    })
    return {
        "rfp_id": rfp_id,
        "rfp_title": rfp.get("title"),
        "baseline": base,
        "simulated": sim,
        "delta": sim["probability"] - base["probability"],
    }
