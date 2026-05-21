import json
from openai import OpenAI
from backend.ai.benefit_valuation import BenefitSummary
from backend.ai.prompts import EMAIL_GENERATION_PROMPT, SUBJECT_LINE_VARIANTS_PROMPT
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


def generate_email_content(summary: BenefitSummary) -> dict:
    prompt = EMAIL_GENERATION_PROMPT.format(
        member_name=summary.member_name,
        tier=summary.tier,
        send_month=summary.send_month,
        cpe_credits_ytd=summary.cpe_credits_ytd,
        cpe_value_usd=summary.cpe_value_usd,
        cpe_courses_completed=summary.cpe_courses_completed,
        webinars_attended_ytd=summary.webinars_attended_ytd,
        webinar_value_usd=summary.webinar_value_usd,
        journal_articles_read_ytd=summary.journal_articles_read_ytd,
        journal_value_usd=summary.journal_value_usd,
        pharmacylibrary_sessions_ytd=summary.pharmacylibrary_sessions_ytd,
        pharmacylibrary_value_usd=summary.pharmacylibrary_value_usd,
        annual_meeting_attended=summary.annual_meeting_attended,
        events_value_usd=summary.events_value_usd,
        total_value_usd=summary.total_value_usd,
        membership_fee_usd=summary.membership_fee_usd,
        roi_multiplier=summary.roi_multiplier,
        engagement_level=summary.engagement_level,
        top_benefit=summary.top_benefit,
        max_tokens=settings.max_tokens_per_email,
    )

    try:
        response = _client().chat.completions.create(
            model=settings.openai_model_name,
            max_tokens=settings.max_tokens_per_email,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as exc:
        logger.error(f"Email generation failed for {summary.member_id}: {exc}")
        return _fallback_content(summary)


def generate_subject_variants(summary: BenefitSummary) -> list[str]:
    prompt = SUBJECT_LINE_VARIANTS_PROMPT.format(
        member_name=summary.member_name.split()[0],
        tier=summary.tier,
        total_value_usd=summary.total_value_usd,
        roi_multiplier=summary.roi_multiplier,
    )
    try:
        response = _client().chat.completions.create(
            model=settings.openai_subject_model_name,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as exc:
        logger.error(f"Subject variant generation failed: {exc}")
        first_name = summary.member_name.split()[0]
        return [
            f"Your APhA benefits this month: ${summary.total_value_usd:.0f} in value",
            f"{first_name}, see what your membership delivered",
            f"{summary.roi_multiplier}x ROI on your APhA investment",
        ]


def _fallback_content(summary: BenefitSummary) -> dict:
    first_name = summary.member_name.split()[0]
    return {
        "subject": f"Your APhA Member Value Summary — {summary.send_month}",
        "preview_text": f"You've received ${summary.total_value_usd:.0f} in benefits this period.",
        "greeting": f"Dear {first_name},",
        "highlights": [
            f"You earned {summary.cpe_credits_ytd} CPE credits valued at ${summary.cpe_value_usd:.0f}.",
            f"You attended {summary.webinars_attended_ytd} webinars worth ${summary.webinar_value_usd:.0f}.",
            f"Your total benefit value this period: ${summary.total_value_usd:.0f}.",
        ],
        "value_statement": (
            f"Your ${summary.membership_fee_usd:.0f} membership has returned "
            f"${summary.total_value_usd:.0f} in value — a {summary.roi_multiplier}x return."
        ),
        "recommendation": "Explore PharmacyLibrary and upcoming CPE webinars to maximize your membership.",
        "cta": "Log in to your APhA member portal to see available courses and events.",
        "closing": "Thank you for your commitment to pharmacy excellence.",
    }
