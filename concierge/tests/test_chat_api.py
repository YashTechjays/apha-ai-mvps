import uuid


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_chat_creates_conversation(client):
    token = str(uuid.uuid4())
    res = client.post("/chat/", json={
        "session_token": token,
        "message": "How much does APhA membership cost?",
    })
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert data["turn_count"] == 1


def test_chat_off_topic(client):
    token = str(uuid.uuid4())
    res = client.post("/chat/", json={
        "session_token": token,
        "message": "What's the stock market doing today?",
    })
    assert res.status_code == 200
    assert res.json()["intent"] == "off_topic"


def test_lead_capture(client):
    token = str(uuid.uuid4())
    res = client.post("/leads/", json={
        "session_token": token,
        "email": "test@example.com",
        "name": "Test User",
    })
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"
