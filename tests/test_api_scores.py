def test_score_distribution_authenticated(client, auth_headers):
    res = client.get("/scores/distribution", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_members" in data
    assert "critical" in data
    assert "high" in data
    assert "medium" in data
    assert "low" in data


def test_score_distribution_unauthenticated(client):
    res = client.get("/scores/distribution")
    assert res.status_code == 401


def test_member_scores_nonexistent(client, auth_headers):
    res = client.get("/scores/member/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []
