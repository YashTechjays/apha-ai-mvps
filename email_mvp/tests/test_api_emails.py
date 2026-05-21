import uuid
from unittest.mock import patch
from backend.db.models.member import Member, MemberTier


def _seed_member(db):
    m = Member(
        id=str(uuid.uuid4()),
        email=f"emailtest_{uuid.uuid4().hex[:6]}@example.com",
        first_name="Email",
        last_name="Tester",
        tier=MemberTier.PHARMACIST,
        cpe_credits_ytd=5.0,
        cpe_courses_completed=2,
        webinars_attended_ytd=1,
        journal_articles_read_ytd=3,
        pharmacylibrary_sessions_ytd=2,
        annual_meeting_attended=False,
        events_registered_ytd=0,
        days_since_last_login=7,
        email_open_rate=0.4,
        portal_sessions_last_30d=3,
        career_center_applications=0,
        advocacy_actions_ytd=0,
    )
    db.add(m)
    db.commit()
    return m


MOCK_CONTENT = {
    "subject": "Email Tester, your APhA benefits: $175 in value",
    "preview_text": "See what your membership delivered.",
    "greeting": "Dear Email,",
    "highlights": ["You earned 5 CPE credits worth $125.", "You attended 1 webinar."],
    "value_statement": "Your $195 membership returned $175.",
    "recommendation": "Try the Annual Meeting next year.",
    "cta": "View Member Portal",
    "closing": "Thank you.",
}


def test_list_emails(client):
    r = client.get("/emails/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_send_single_email(client, db):
    m = _seed_member(db)
    with patch("backend.ai.email_generator.generate_email_content", return_value=MOCK_CONTENT):
        r = client.post(f"/emails/send/{m.id}", params={"send_month": "2026-05"})
    assert r.status_code == 200
    data = r.json()
    assert data["member_id"] == m.id
    assert data["send_month"] == "2026-05"
    assert data["status"] in ("sent", "qc_failed", "failed")


def test_member_emails(client, db):
    m = _seed_member(db)
    with patch("backend.ai.email_generator.generate_email_content", return_value=MOCK_CONTENT):
        client.post(f"/emails/send/{m.id}", params={"send_month": "2026-04"})
    r = client.get(f"/emails/member/{m.id}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_run_batch_dry_run(client):
    r = client.post("/emails/run-batch", params={"send_month": "2026-05", "dry_run": "true"})
    assert r.status_code == 200
    data = r.json()
    assert "skipped" in data or "sent" in data


def test_analytics_summary(client):
    r = client.get("/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_sends" in data
