from backend.db.models.member import Member
from backend.db.models.crosssell_score import CrossSellScore
from backend.ai.message_generator import generate_email_nudge, generate_banner_nudge


def _member():
    m = Member()
    m.first_name = "Alex"
    m.last_name = "Chen"
    m.email = "alex@example.com"
    m.tier = "pharmacist"
    m.specialty = "Community Pharmacy"
    m.years_as_member = 2.5
    m.edu_active = True
    m.pub_active = False
    m.events_active = False
    m.career_active = False
    m.advocacy_active = False
    return m


def _score(product="publications"):
    s = CrossSellScore()
    s.product = product
    s.score = 75.0
    s.top_reasons = ["Active CPE learner", "High engagement"]
    return s


def test_email_fallback_returns_subject_and_body():
    """With client patched to None, fallback path must produce valid output."""
    result = generate_email_nudge(_member(), _score())
    assert "subject" in result and "body" in result
    assert "Alex" in result["body"]
    assert result["cta_url"].startswith("http")


def test_banner_fallback_returns_required_keys():
    result = generate_banner_nudge(_member(), _score())
    assert "headline" in result and "body" in result and "cta_label" in result
    assert result["product"] == "publications"
