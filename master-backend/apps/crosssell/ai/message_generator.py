import json
from openai import OpenAI
from apps.crosssell.db.models.member import Member
from apps.crosssell.db.models.crosssell_score import CrossSellScore
from apps.crosssell.ai.prompts import (
    NUDGE_EMAIL_PROMPT, BANNER_PROMPT,
    PRODUCT_DESCRIPTIONS, PRODUCT_CTA_URLS,
)
from apps.crosssell.utils.config import get_settings
from apps.crosssell.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

ACTIVE_STREAM_LABELS = {
    "education": "CPE / Learning Library",
    "publications": "Journals & Publications",
    "events": "Conferences & Events",
    "career": "Career Services",
    "advocacy": "Advocacy",
}


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _fallback_email(member: Member, score: CrossSellScore) -> dict:
    label = ACTIVE_STREAM_LABELS.get(score.product, score.product.title())
    reason = (score.top_reasons or [f"Explore {label}"])[0]
    return {
        "subject": f"{member.first_name}, explore APhA {label}",
        "body": (
            f"Hi {member.first_name},\n\n"
            f"{reason} — that's why we wanted to share APhA's {label} with you. "
            f"{PRODUCT_DESCRIPTIONS.get(score.product, '')}\n\n"
            f"Take a look when you have a moment.\n\n"
            f"— APhA Membership Team"
        ),
    }


def _fallback_banner(member: Member, score: CrossSellScore) -> dict:
    label = ACTIVE_STREAM_LABELS.get(score.product, score.product.title())
    reason = (score.top_reasons or [f"Try {label}"])[0]
    return {
        "headline": f"{member.first_name}, discover {label}",
        "body": reason,
        "cta_label": "Explore now",
    }


def generate_email_nudge(member: Member, score: CrossSellScore) -> dict:
    tier = member.tier if isinstance(member.tier, str) else str(member.tier)
    active_streams = [
        ACTIVE_STREAM_LABELS[p] for p in ["education", "publications", "events", "career", "advocacy"]
        if getattr(member, f"{p}_active", False)
    ] or ["Membership"]

    if client:
        prompt = NUDGE_EMAIL_PROMPT.format(
            first_name=member.first_name, last_name=member.last_name,
            tier=tier.replace("_", " ").title(),
            specialty=member.specialty or "General Pharmacy",
            years_as_member=round(member.years_as_member or 0, 1),
            active_streams=", ".join(active_streams),
            target_product=ACTIVE_STREAM_LABELS.get(score.product, score.product.title()),
            reasons="\n".join([f"- {r}" for r in (score.top_reasons or [])]),
            product_description=PRODUCT_DESCRIPTIONS.get(score.product, ""),
            cta_url=PRODUCT_CTA_URLS.get(score.product, "https://pharmacist.com"),
        )
        try:
            response = client.chat.completions.create(
                model=settings.openai_model_name,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            result = _parse_json_response(response.choices[0].message.content or "")
        except Exception as e:
            logger.warning(f"OpenAI email gen failed, using fallback: {e}")
            result = _fallback_email(member, score)
    else:
        result = _fallback_email(member, score)

    result["cta_url"] = PRODUCT_CTA_URLS.get(score.product, "https://pharmacist.com")
    result["cta_label"] = "Explore now →"
    return result


def generate_banner_nudge(member: Member, score: CrossSellScore) -> dict:
    if client:
        top_reason = (score.top_reasons or ["Explore this APhA benefit"])[0]
        prompt = BANNER_PROMPT.format(
            first_name=member.first_name,
            tier=(member.tier or "pharmacist").replace("_", " ").title(),
            specialty=member.specialty or "General Pharmacy",
            target_product=ACTIVE_STREAM_LABELS.get(score.product, score.product.title()),
            top_reason=top_reason,
        )
        try:
            response = client.chat.completions.create(
                model=settings.openai_model_name,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            result = _parse_json_response(response.choices[0].message.content or "")
        except Exception as e:
            logger.warning(f"OpenAI banner gen failed, using fallback: {e}")
            result = _fallback_banner(member, score)
    else:
        result = _fallback_banner(member, score)

    result["cta_url"] = PRODUCT_CTA_URLS.get(score.product, "https://pharmacist.com")
    result["product"] = score.product
    return result
