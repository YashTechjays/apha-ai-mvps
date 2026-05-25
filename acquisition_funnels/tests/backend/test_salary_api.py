import uuid


def test_health(client):
    assert client.get("/health").status_code == 200


def test_salary_benchmark_basic(client):
    r = client.post(
        "/salary/benchmark",
        json={
            "session_id": str(uuid.uuid4()),
            "state": "TX",
            "specialty": "Hospital/Health-System",
            "license_type": "pharmacist",
            "years_experience": "6-10",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["p50"] > data["p25"]
    assert data["p75"] > data["p50"]
    assert data["p90"] > data["p75"]
    assert "commentary" in data
    assert "headline" in data


def test_salary_with_current_salary(client):
    r = client.post(
        "/salary/benchmark",
        json={
            "session_id": str(uuid.uuid4()),
            "state": "CA",
            "specialty": "Community Pharmacy",
            "license_type": "pharmacist",
            "years_experience": "3-5",
            "current_salary": 120000,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["percentile"] is not None
    assert 0 <= data["percentile"] <= 100


def test_specialties_endpoint(client):
    r = client.get("/salary/specialties")
    assert r.status_code == 200
    assert len(r.json()) > 5


def test_states_endpoint(client):
    r = client.get("/salary/states")
    assert r.status_code == 200
    states = r.json()
    assert len(states) > 30
    assert any(s["code"] == "TX" for s in states)
