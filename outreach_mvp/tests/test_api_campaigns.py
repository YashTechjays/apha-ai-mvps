def test_health(client):
    assert client.get("/health").status_code == 200


def test_create_campaign(client, auth_headers):
    r = client.post("/campaigns/", headers=auth_headers, json={
        "name": "Test Campaign - Hospital Pharmacists",
        "target_tier": "pharmacist",
        "target_state": "TX",
        "min_icp_score": 60,
        "is_dry_run": True,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Campaign - Hospital Pharmacists"
    assert data["is_dry_run"] is True
    assert data["status"] == "draft"


def test_list_campaigns(client, auth_headers):
    r = client.get("/campaigns/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_analytics_overview(client, auth_headers):
    r = client.get("/analytics/overview", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "total_prospects" in data
    assert "open_rate" in data
