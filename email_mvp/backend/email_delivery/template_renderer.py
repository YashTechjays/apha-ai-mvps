from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from backend.ai.benefit_valuation import BenefitSummary

TEMPLATES_DIR = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)


def render_html(summary: BenefitSummary, content: dict) -> str:
    template = _env.get_template("member_value.html")
    return template.render(
        subject=content.get("subject", ""),
        greeting=content.get("greeting", ""),
        highlights=content.get("highlights", []),
        value_statement=content.get("value_statement", ""),
        recommendation=content.get("recommendation", ""),
        cta=content.get("cta", "View Member Portal"),
        closing=content.get("closing", ""),
        total_value_usd=summary.total_value_usd,
        membership_fee_usd=summary.membership_fee_usd,
        roi_multiplier=summary.roi_multiplier,
        cpe_value_usd=summary.cpe_value_usd,
        cpe_credits_ytd=summary.cpe_credits_ytd,
        cpe_courses_completed=summary.cpe_courses_completed,
        webinar_value_usd=summary.webinar_value_usd,
        webinars_attended_ytd=summary.webinars_attended_ytd,
        journal_value_usd=summary.journal_value_usd,
        journal_articles_read_ytd=summary.journal_articles_read_ytd,
        pharmacylibrary_value_usd=summary.pharmacylibrary_value_usd,
        pharmacylibrary_sessions_ytd=summary.pharmacylibrary_sessions_ytd,
        events_value_usd=summary.events_value_usd,
        annual_meeting_attended=summary.annual_meeting_attended,
        events_registered_ytd=summary.events_registered_ytd,
    )


def render_plain_text(summary: BenefitSummary, content: dict) -> str:
    lines = [
        content.get("greeting", ""),
        "",
        content.get("value_statement", ""),
        "",
        "YOUR BENEFIT BREAKDOWN",
        "-" * 30,
    ]
    if summary.cpe_value_usd > 0:
        lines.append(f"CPE Credits: {summary.cpe_credits_ytd} credits — ${summary.cpe_value_usd:.0f}")
    if summary.webinar_value_usd > 0:
        lines.append(f"Webinars: {summary.webinars_attended_ytd} attended — ${summary.webinar_value_usd:.0f}")
    if summary.journal_value_usd > 0:
        lines.append(f"Journal Articles: {summary.journal_articles_read_ytd} read — ${summary.journal_value_usd:.0f}")
    if summary.pharmacylibrary_value_usd > 0:
        lines.append(f"PharmacyLibrary: {summary.pharmacylibrary_sessions_ytd} sessions — ${summary.pharmacylibrary_value_usd:.0f}")
    if summary.events_value_usd > 0:
        lines.append(f"Events: ${summary.events_value_usd:.0f}")
    lines += [
        "-" * 30,
        f"TOTAL VALUE: ${summary.total_value_usd:.0f} ({summary.roi_multiplier}x ROI)",
        "",
    ]
    for item in content.get("highlights", []):
        lines.append(f"• {item}")
    lines += [
        "",
        content.get("recommendation", ""),
        "",
        content.get("cta", ""),
        "https://pharmacist.com/member-portal",
        "",
        content.get("closing", ""),
        "",
        "APhA Membership Team",
        "Unsubscribe: https://pharmacist.com/unsubscribe",
    ]
    return "\n".join(lines)
