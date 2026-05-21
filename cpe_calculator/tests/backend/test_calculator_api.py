import uuid
from datetime import date, timedelta


def _future_date(days=180):
    return (date.today() + timedelta(days=days)).isoformat()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_calculate_valid_request(client):
    res = client.post("/calculate/", json={
        "session_id": str(uuid.uuid4()),
        "state": "TX",
        "renewal_date": _future_date(200),
        "hours_completed": 10,
        "license_type": "pharmacist",
        "specialty": "General / Community Pharmacy",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["state"] == "TX"
    assert data["hours_gap"] == 20.0
    assert data["is_preview"] is True
    assert len(data["courses"]) <= 3


def test_calculate_invalid_state(client):
    res = client.post("/calculate/", json={
        "session_id": str(uuid.uuid4()),
        "state": "XX",
        "renewal_date": _future_date(),
        "hours_completed": 5,
    })
    assert res.status_code == 400


def test_calculate_negative_hours(client):
    res = client.post("/calculate/", json={
        "session_id": str(uuid.uuid4()),
        "state": "CA",
        "renewal_date": _future_date(),
        "hours_completed": -1,
    })
    assert res.status_code == 422


def test_lead_capture(client):
    session_id = str(uuid.uuid4())
    client.post("/calculate/", json={
        "session_id": session_id,
        "state": "NY",
        "renewal_date": _future_date(300),
        "hours_completed": 15,
    })
    res = client.post("/leads/", json={
        "session_id": session_id,
        "email": f"test_{uuid.uuid4().hex[:6]}@pharmacist.com",
        "name": "Test Pharmacist",
    })
    assert res.status_code == 200
    assert "email" in res.json()


def test_analytics_summary(client):
    res = client.get("/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_calculations" in data
    assert "leads_captured" in data


def test_seo_state(client):
    res = client.get("/seo/state/CA")
    assert res.status_code == 200
    data = res.json()
    assert "California" in data["title"]
    assert data["hours_required"] == 30
