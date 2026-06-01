"""Score an RFP against a pharmacist profile (0-100)."""
import hashlib
from functools import lru_cache
from typing import Optional
from backend.utils.logger import get_logger

logger = get_logger("matcher")

# Weight constants (the four base factors sum to 1.0)
W_CATEGORY = 0.40
W_REQUIREMENTS = 0.35
W_LOCATION = 0.15
W_ORG_TYPE = 0.10

# Enhancement #3 — when graph history is available, it contributes this share
# and the four base factors are scaled down to (1 - W_HISTORY) so the total
# still sums to 1.0.
W_HISTORY = 0.15


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# Full state/territory name -> USPS 2-letter code. Lets a profile that stores the
# 2-letter code (DB column is VARCHAR(2)) match an RFP whose location is the full
# state name (e.g. "TX" == "Texas").
_STATE_TO_CODE = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR",
    "CALIFORNIA": "CA", "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE",
    "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS",
    "KENTUCKY": "KY", "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD",
    "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS",
    "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY",
    "NORTH CAROLINA": "NC", "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK",
    "OREGON": "OR", "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
    "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC",
    "PUERTO RICO": "PR",
}

NATIONAL_STATE_KEYWORDS = {"NATIONAL", "REMOTE", "ANYWHERE", "ALL", "US", "USA"}


def normalize_state(value: Optional[str]) -> Optional[str]:
    """Canonicalize a state to its USPS 2-letter code, accepting either a full
    name ("Texas") or a code ("TX"). Returns None when not a recognizable state."""
    if not value:
        return None
    v = value.upper().strip()
    if v in NATIONAL_STATE_KEYWORDS:
        return None
    if v in _STATE_TO_CODE:
        return _STATE_TO_CODE[v]
    if len(v) == 2 and v in _STATE_TO_CODE.values():
        return v
    return v  # unknown token — compare as-is so identical strings still match


def _location_score(rfp_state: Optional[str], profile_state: Optional[str]) -> float:
    if not rfp_state or not profile_state:
        return 0.5  # unknown — neutral
    if rfp_state.upper().strip() in NATIONAL_STATE_KEYWORDS:
        return 0.5
    if normalize_state(rfp_state) == normalize_state(profile_state):
        return 1.0
    return 0.0


def _org_type_score(rfp_org_type: Optional[str], preferred: list[str]) -> float:
    if not preferred:
        return 0.5  # no preference — neutral
    if not rfp_org_type:
        return 0.5
    return 1.0 if rfp_org_type.lower() in [p.lower() for p in preferred] else 0.0


def _requirements_key(requirements: list[str], certifications: list[str]) -> str:
    r_part = "|".join(sorted(requirements))
    c_part = "|".join(sorted(certifications))
    return hashlib.md5(f"{r_part}::{c_part}".encode()).hexdigest()


@lru_cache(maxsize=512)
def _cached_semantic_score(cache_key: str, req_text: str, cert_text: str) -> float:
    """Call OpenAI once per unique (requirements, certifications) pair."""
    try:
        from backend.utils.config import get_settings
        from openai import OpenAI
        settings = get_settings()
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            f"Requirements:\n{req_text}\n\n"
            f"Pharmacist certifications/skills:\n{cert_text}\n\n"
            "On a scale 0-100, how well do the pharmacist's certifications and skills satisfy "
            "these RFP requirements? Reply with a single integer only."
        )
        resp = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        return min(100, max(0, int("".join(filter(str.isdigit, raw)) or "50"))) / 100
    except Exception as e:
        logger.warning(f"Semantic score failed: {e}")
        return 0.5


def _requirements_score(requirements: list[str], certifications: list[str]) -> float:
    if not requirements:
        return 0.5
    if not certifications:
        return 0.3  # no certs listed — below average
    req_text = "\n".join(requirements[:15])  # cap to avoid huge prompts
    cert_text = ", ".join(certifications[:20])
    key = _requirements_key(requirements[:15], certifications[:20])
    return _cached_semantic_score(key, req_text, cert_text)


def score_rfp_for_profile(rfp: dict, profile: dict, user_id: Optional[str] = None) -> int:
    """Return integer match score 0–100.

    When ``user_id`` is given and the graph holds application/win history for
    that pharmacist, a historical signal (Enhancement #3) is blended in.
    Without history the original 4-factor formula is used unchanged.
    """
    cat_score = _jaccard(rfp.get("categories", []), profile.get("specialties", []))
    req_score = _requirements_score(
        rfp.get("requirements", []),
        profile.get("certifications", []),
    )
    loc_score = _location_score(
        rfp.get("location_state"),
        profile.get("location_state"),
    )
    org_score = _org_type_score(
        rfp.get("org_type"),
        profile.get("org_types_preferred", []),
    )

    base = (
        W_CATEGORY * cat_score
        + W_REQUIREMENTS * req_score
        + W_LOCATION * loc_score
        + W_ORG_TYPE * org_score
    )

    hist = None
    if user_id:
        try:
            from backend.ai.graph_features import history_score
            hist = history_score(user_id, rfp)
        except Exception as e:
            logger.warning(f"history_score unavailable: {e}")

    if hist is None:
        weighted = base
    else:
        weighted = (1 - W_HISTORY) * base + W_HISTORY * hist

    return round(weighted * 100)
