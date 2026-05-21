from backend.db.models.member import MemberTier
from backend.ai.benefit_valuation import BenefitSummary
from backend.email_delivery.quality_check import run_quality_check


def _make_summary(**kwargs) -> BenefitSummary:
    defaults = dict(
        member_id="test-001",
        member_name="Jane Doe",
        tier="pharmacist",
        send_month="2026-05",
        cpe_credits_ytd=10.0,
        cpe_value_usd=250.0,
        cpe_courses_completed=4,
        webinars_attended_ytd=3,
        webinar_value_usd=150.0,
        journal_articles_read_ytd=12,
        journal_value_usd=36.0,
        pharmacylibrary_sessions_ytd=8,
        pharmacylibrary_value_usd=40.0,
        annual_meeting_attended=False,
        events_registered_ytd=0,
        events_value_usd=0.0,
        total_value_usd=476.0,
        membership_fee_usd=195.0,
        roi_multiplier=2.44,
        engagement_level="high",
        top_benefit="CPE courses",
    )
    defaults.update(kwargs)
    return BenefitSummary(**defaults)


def _make_content(**kwargs) -> dict:
    defaults = dict(
        subject="Jane, your APhA benefits: $476 in value",
        preview_text="See what your membership delivered.",
        greeting="Dear Jane,",
        highlights=["You earned 10 CPE credits worth $250.", "You attended 3 webinars worth $150."],
        value_statement="Your $195 membership returned $476 — a 2.44x ROI.",
        recommendation="Try PharmacyLibrary for exam prep.",
        cta="View Member Portal",
        closing="Thank you for your commitment.",
    )
    defaults.update(kwargs)
    return defaults


def test_passing_email():
    summary = _make_summary()
    content = _make_content()
    html = f"<p>Dear Jane, $476 $250 $150 value from CPE courses</p>"
    result = run_quality_check(summary, content, html)
    assert result.passed is True
    assert result.score >= 0.7


def test_missing_member_name_fails():
    summary = _make_summary()
    content = _make_content()
    html = "<p>Dear Member, $476 $250 $150</p>"
    result = run_quality_check(summary, content, html)
    assert result.passed is False
    assert any("name" in n.lower() for n in result.notes)


def test_spam_trigger_fails():
    summary = _make_summary()
    content = _make_content()
    html = "<p>Dear Jane, act now to claim your free money worth $476 $250 $150</p>"
    result = run_quality_check(summary, content, html)
    assert result.passed is False


def test_no_dollars_lowers_score():
    summary = _make_summary()
    content = _make_content()
    html = "<p>Dear Jane, you used many benefits this month.</p>"
    result = run_quality_check(summary, content, html)
    assert result.score < 0.8


def test_personalization_score():
    summary = _make_summary()
    content = _make_content()
    html = f"<p>Dear Jane, $476 in value. CPE courses were your top benefit.</p>"
    result = run_quality_check(summary, content, html)
    assert result.personalization_score > 0.0
