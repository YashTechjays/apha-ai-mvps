import uuid


def test_duplicate_lead_returns_existing(client):
    token = str(uuid.uuid4())
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"

    res1 = client.post("/leads/", json={"session_token": token, "email": email})
    res2 = client.post("/leads/", json={"session_token": token, "email": email})

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json()["id"] == res2.json()["id"]


def test_list_leads(client):
    res = client.get("/leads/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_analytics_summary(client):
    res = client.get("/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_conversations" in data
    assert "leads_captured" in data
    assert "lead_capture_rate" in data
