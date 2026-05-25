from dataclasses import dataclass
from apps.email_app.ai.benefit_valuation import BenefitSummary
from apps.email_app.utils.config import get_settings

settings = get_settings()

SPAM_TRIGGERS = [
    "free money", "guaranteed", "act now", "limited time offer",
    "click here", "congratulations", "winner", "no cost", "!!!",
]


@dataclass
class QCResult:
    passed: bool
    score: float  # 0.0–1.0
    personalization_score: float
    token_count: int
    notes: list[str]


def run_quality_check(summary: BenefitSummary, content: dict, html_body: str) -> QCResult:
    notes = []
    scores = []

    # 1. Subject line length
    subject = content.get("subject", "")
    if 20 <= len(subject) <= 60:
        scores.append(1.0)
    else:
        scores.append(0.5)
        notes.append(f"Subject length {len(subject)} outside 20-60 char range")

    # 2. Personalization — member name appears in body
    member_first = summary.member_name.split()[0]
    if member_first.lower() in html_body.lower():
        scores.append(1.0)
    else:
        scores.append(0.0)
        notes.append("Member first name not found in email body")

    # 3. Specific dollar figures present
    dollar_count = html_body.count("$")
    if dollar_count >= 3:
        scores.append(1.0)
    elif dollar_count >= 1:
        scores.append(0.6)
        notes.append("Fewer than 3 dollar figures — may lack specificity")
    else:
        scores.append(0.0)
        notes.append("No dollar figures found in email body")

    # 4. Spam trigger check
    body_lower = html_body.lower()
    triggered = [t for t in SPAM_TRIGGERS if t in body_lower]
    if not triggered:
        scores.append(1.0)
    else:
        scores.append(0.0)
        notes.append(f"Spam trigger words found: {triggered}")

    # 5. CTA present
    if content.get("cta"):
        scores.append(1.0)
    else:
        scores.append(0.0)
        notes.append("Missing call-to-action")

    # 6. Token count check (rough estimate: 1 token ≈ 4 chars)
    token_estimate = len(html_body) // 4
    if token_estimate <= settings.max_tokens_per_email:
        scores.append(1.0)
    else:
        scores.append(0.5)
        notes.append(f"Email may exceed token limit ({token_estimate} est. tokens)")

    # Personalization score: name + benefit specifics
    personalization = 0.0
    if member_first.lower() in html_body.lower():
        personalization += 0.4
    if summary.total_value_usd > 0 and f"{summary.total_value_usd:.0f}" in html_body:
        personalization += 0.3
    if summary.top_benefit.lower() in html_body.lower():
        personalization += 0.3

    overall = sum(scores) / len(scores)
    passed = overall >= 0.7 and not triggered and member_first.lower() in html_body.lower()

    return QCResult(
        passed=passed,
        score=round(overall, 3),
        personalization_score=round(personalization, 3),
        token_count=token_estimate,
        notes=notes,
    )
