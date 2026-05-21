import uuid
from backend.db.models.member import Member, MemberTier


def _seed_member(db):
    m = Member(
        id=str(uuid.uuid4()),
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        first_name="Test",
        last_name="User",
        tier=MemberTier.PHARMACIST,
        cpe_credits_ytd=8.0,
        cpe_courses_completed=3,
        webinars_attended_ytd=2,
        journal_articles_read_ytd=5,
        pharmacylibrary_sessions_ytd=4,
        annual_meeting_attended=False,
        events_registered_ytd=1,
        days_since_last_login=10,
        email_open_rate=0.35,
        portal_sessions_last_30d=4,
        career_center_applications=0,
        advocacy_actions_ytd=0,
    )
    db.add(m)
    db.commit()
    return m


def test_list_members(client, db):
    _seed_member(db)
    r = client.get("/members/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_get_member(client, db):
    m = _seed_member(db)
    r = client.get(f"/members/{m.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == m.id
    assert data["email"] == m.email


def test_get_member_not_found(client):
    r = client.get("/members/nonexistent-id")
    assert r.status_code == 404


def test_benefit_summary(client, db):
    m = _seed_member(db)
    r = client.get(f"/members/{m.id}/benefit-summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_value_usd" in data
    assert "roi_multiplier" in data
    assert data["total_value_usd"] >= 0
