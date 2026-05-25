import uuid


def test_lead_capture_salary(client):
    r = client.post(
        "/leads/",
        json={
            "session_id": str(uuid.uuid4()),
            "email": "test@pharmacy.com",
            "name": "Test Pharmacist",
            "source_tool": "salary",
            "state": "TX",
            "salary_percentile": 45,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["unlocked"] is True
    assert "email" in data


def test_duplicate_lead_returns_existing(client):
    session = str(uuid.uuid4())
    email = f"dup-{uuid.uuid4().hex[:8]}@pharmacy.com"
    client.post(
        "/leads/",
        json={"session_id": session, "email": email, "source_tool": "salary"},
    )
    r = client.post(
        "/leads/",
        json={"session_id": session, "email": email, "source_tool": "salary"},
    )
    assert r.status_code == 200
    assert "Welcome back" in r.json()["message"]


def test_lead_capture_career(client):
    r = client.post(
        "/leads/",
        json={
            "session_id": str(uuid.uuid4()),
            "email": "career@pharmacy.com",
            "source_tool": "career",
            "career_score": 72,
            "top_gap_dimension": "leadership",
        },
    )
    assert r.status_code == 200
    assert r.json()["unlocked"] is True


def test_analytics_summary(client):
    r = client.get("/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_tool_uses" in data
    assert "by_tool" in data
