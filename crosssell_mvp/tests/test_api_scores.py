def test_health(client):
    assert client.get("/health").status_code == 200


def test_run_scoring(client, auth_headers):
    r = client.post("/scores/run", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "members_scored" in body or "error" in body


def test_list_members_requires_auth(client):
    r = client.get("/scores/members")
    assert r.status_code == 401


def test_list_members(client, auth_headers):
    r = client.get("/scores/members", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_analytics_overview(client, auth_headers):
    r = client.get("/analytics/overview", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "total_active_members" in data
    assert "avg_active_streams_per_member" in data


def test_analytics_by_product(client, auth_headers):
    r = client.get("/analytics/by-product", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    for product in ["education", "publications", "events", "career", "advocacy"]:
        assert product in data
