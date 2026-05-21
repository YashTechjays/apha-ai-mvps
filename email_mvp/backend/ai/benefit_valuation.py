from dataclasses import dataclass
from backend.db.models.member import Member
from backend.utils.config import get_settings

settings = get_settings()


@dataclass
class BenefitSummary:
    member_id: str
    member_name: str
    tier: str
    send_month: str

    cpe_credits_ytd: float
    cpe_value_usd: float
    cpe_courses_completed: int

    webinars_attended_ytd: int
    webinar_value_usd: float

    journal_articles_read_ytd: int
    journal_value_usd: float

    pharmacylibrary_sessions_ytd: int
    pharmacylibrary_value_usd: float

    annual_meeting_attended: bool
    events_registered_ytd: int
    events_value_usd: float

    total_value_usd: float
    membership_fee_usd: float
    roi_multiplier: float

    engagement_level: str  # high / medium / low
    top_benefit: str


TIER_FEES = {
    "pharmacist": 195.0,
    "student": 50.0,
    "technician": 75.0,
    "associate": 150.0,
}


def compute_benefit_summary(member: Member, send_month: str) -> BenefitSummary:
    cpe_value = member.cpe_credits_ytd * settings.cpe_credit_value_usd
    webinar_value = member.webinars_attended_ytd * settings.webinar_value_usd
    journal_value = member.journal_articles_read_ytd * (settings.journal_monthly_value_usd / 10)
    pharma_value = member.pharmacylibrary_sessions_ytd * (settings.pharmacylibrary_monthly_value_usd / 4)
    events_value = (settings.annual_meeting_value_usd if member.annual_meeting_attended else 0.0) + \
                   (member.events_registered_ytd * 25.0)

    total = cpe_value + webinar_value + journal_value + pharma_value + events_value
    fee = TIER_FEES.get(member.tier.value if hasattr(member.tier, "value") else member.tier, 195.0)
    roi = total / fee if fee > 0 else 0.0

    # Engagement level
    score = (
        (1 if member.portal_sessions_last_30d >= 5 else 0) +
        (1 if member.cpe_credits_ytd >= 5 else 0) +
        (1 if member.email_open_rate >= 0.3 else 0) +
        (1 if member.webinars_attended_ytd >= 2 else 0)
    )
    engagement = "high" if score >= 3 else ("medium" if score >= 1 else "low")

    # Top benefit by value
    benefit_values = {
        "CPE courses": cpe_value,
        "webinars": webinar_value,
        "Journal access": journal_value,
        "PharmacyLibrary": pharma_value,
        "events": events_value,
    }
    top_benefit = max(benefit_values, key=benefit_values.get)
    if benefit_values[top_benefit] == 0:
        top_benefit = "membership network"

    return BenefitSummary(
        member_id=member.id,
        member_name=f"{member.first_name} {member.last_name}",
        tier=member.tier.value if hasattr(member.tier, "value") else member.tier,
        send_month=send_month,
        cpe_credits_ytd=member.cpe_credits_ytd,
        cpe_value_usd=round(cpe_value, 2),
        cpe_courses_completed=member.cpe_courses_completed,
        webinars_attended_ytd=member.webinars_attended_ytd,
        webinar_value_usd=round(webinar_value, 2),
        journal_articles_read_ytd=member.journal_articles_read_ytd,
        journal_value_usd=round(journal_value, 2),
        pharmacylibrary_sessions_ytd=member.pharmacylibrary_sessions_ytd,
        pharmacylibrary_value_usd=round(pharma_value, 2),
        annual_meeting_attended=member.annual_meeting_attended,
        events_registered_ytd=member.events_registered_ytd,
        events_value_usd=round(events_value, 2),
        total_value_usd=round(total, 2),
        membership_fee_usd=fee,
        roi_multiplier=round(roi, 2),
        engagement_level=engagement,
        top_benefit=top_benefit,
    )
