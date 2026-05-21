"""End-to-end API flow tests: signup -> login -> ask -> feedback."""
from __future__ import annotations


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_signup_and_login_flow(client):
    payload = {
        "email": "alice@pharm.com",
        "password": "supersecure123",
        "full_name": "Alice Patel, PharmD",
        "organization_name": "Riverside Pharmacy",
    }
    r = client.post("/api/v1/auth/signup", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == payload["email"]
    token = body["access_token"]
    assert token

    # Login with same creds
    r2 = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    assert r2.json()["email"] == payload["email"]

    # /me
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_query_flow_returns_answer(client):
    # Sign up
    r = client.post("/api/v1/auth/signup", json={
        "email": "bob@pharm.com", "password": "supersecure123",
    })
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ask
    q = client.post("/api/v1/query", json={"question": "What is metformin?"}, headers=headers)
    assert q.status_code == 200, q.text
    body = q.json()
    assert "answer" in body
    assert body["query_id"]
    assert body["latency_ms"] >= 0

    # Feedback
    fb = client.post(
        "/api/v1/query/feedback",
        json={"query_id": body["query_id"], "thumbs_up": True},
        headers=headers,
    )
    assert fb.status_code == 200
    assert fb.json()["recorded"] is True


def test_plans_listed(client):
    r = client.get("/api/v1/subscriptions/plans")
    assert r.status_code == 200
    codes = [p["code"] for p in r.json()]
    assert "trial" in codes
    assert "individual" in codes
    assert "team" in codes


def test_api_key_create_and_use(client):
    # signup
    r = client.post("/api/v1/auth/signup", json={
        "email": "carol@pharm.com", "password": "supersecure123",
    })
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create api key
    k = client.post("/api/v1/auth/api-keys", json={"label": "test"}, headers=headers)
    assert k.status_code == 200, k.text
    raw_key = k.json()["raw_key"]
    assert raw_key.startswith("apha_")

    # Use the API key to make a query (no bearer)
    q = client.post(
        "/api/v1/query",
        json={"question": "Tell me about warfarin"},
        headers={"X-API-Key": raw_key},
    )
    assert q.status_code == 200, q.text


def test_unauthenticated_blocked(client):
    r = client.post("/api/v1/query", json={"question": "metformin?"})
    assert r.status_code == 401
