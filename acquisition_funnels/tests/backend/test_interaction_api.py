import uuid


def test_drug_search(client):
    r = client.post("/interactions/search", json={"prefix": "war", "limit": 5})
    assert r.status_code == 200
    results = r.json()
    assert isinstance(results, list)
    assert any("Warfarin" in item["name"] for item in results)


def test_drug_search_short_prefix(client):
    r = client.post("/interactions/search", json={"prefix": "w", "limit": 5})
    assert r.status_code == 200
    assert r.json() == []


def test_known_major_interaction(client):
    r = client.post(
        "/interactions/check",
        json={
            "session_id": str(uuid.uuid4()),
            "drug_a": "warfarin",
            "drug_b": "amiodarone",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["severity"] == "major"
    assert "summary" in data
    assert len(data["summary"]) > 0


def test_same_drug_rejected(client):
    r = client.post(
        "/interactions/check",
        json={
            "session_id": str(uuid.uuid4()),
            "drug_a": "aspirin",
            "drug_b": "aspirin",
        },
    )
    assert r.status_code == 400


def test_unknown_pair_returns_summary(client):
    r = client.post(
        "/interactions/check",
        json={
            "session_id": str(uuid.uuid4()),
            "drug_a": "metformin",
            "drug_b": "amoxicillin",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert data["severity"] == "unknown"


def test_empty_drug_rejected(client):
    r = client.post(
        "/interactions/check",
        json={
            "session_id": str(uuid.uuid4()),
            "drug_a": "",
            "drug_b": "aspirin",
        },
    )
    assert r.status_code == 400
