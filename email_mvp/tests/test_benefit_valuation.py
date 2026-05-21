from datetime import datetime
from backend.db.models.member import Member, MemberTier
from backend.ai.benefit_valuation import compute_benefit_summary, TIER_FEES


def _make_member(**kwargs) -> Member:
    defaults = dict(
        id="test-001",
        email="test@example.com",
        first_name="Jane",
        last_name="Doe",
        tier=MemberTier.PHARMACIST,
        cpe_credits_ytd=10.0,
        cpe_courses_completed=4,
        webinars_attended_ytd=3,
        journal_articles_read_ytd=12,
        pharmacylibrary_sessions_ytd=8,
        annual_meeting_attended=False,
        events_registered_ytd=2,
        portal_sessions_last_30d=6,
        email_open_rate=0.4,
        days_since_last_login=5,
        career_center_applications=0,
        advocacy_actions_ytd=0,
    )
    defaults.update(kwargs)
    m = Member.__new__(Member)
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def test_basic_valuation():
    member = _make_member()
    summary = compute_benefit_summary(member, "2026-05")
    assert summary.cpe_value_usd == 250.0
    assert summary.webinar_value_usd == 150.0
    assert summary.total_value_usd > 0
    assert summary.roi_multiplier > 1.0


def test_roi_multiplier_calculation():
    member = _make_member(cpe_credits_ytd=20.0, webinars_attended_ytd=5, annual_meeting_attended=True)
    summary = compute_benefit_summary(member, "2026-05")
    fee = TIER_FEES["pharmacist"]
    expected_roi = round(summary.total_value_usd / fee, 2)
    assert summary.roi_multiplier == expected_roi


def test_zero_activity_member():
    member = _make_member(
        cpe_credits_ytd=0, cpe_courses_completed=0, webinars_attended_ytd=0,
        journal_articles_read_ytd=0, pharmacylibrary_sessions_ytd=0,
        annual_meeting_attended=False, events_registered_ytd=0,
    )
    summary = compute_benefit_summary(member, "2026-05")
    assert summary.total_value_usd == 0.0
    assert summary.engagement_level == "low"
    assert summary.top_benefit == "membership network"


def test_engagement_levels():
    high = _make_member(portal_sessions_last_30d=10, cpe_credits_ytd=10, email_open_rate=0.5, webinars_attended_ytd=3)
    low = _make_member(portal_sessions_last_30d=0, cpe_credits_ytd=0, email_open_rate=0.1, webinars_attended_ytd=0)
    assert compute_benefit_summary(high, "2026-05").engagement_level == "high"
    assert compute_benefit_summary(low, "2026-05").engagement_level == "low"


def test_member_name_and_tier():
    member = _make_member(first_name="Alice", last_name="Smith", tier=MemberTier.STUDENT)
    summary = compute_benefit_summary(member, "2026-05")
    assert summary.member_name == "Alice Smith"
    assert summary.tier == "student"
    assert summary.membership_fee_usd == 50.0
