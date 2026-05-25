def test_prospect_stats(client, auth_headers):
    r = client.get("/prospects/stats", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "by_status" in data


def test_list_prospects(client, auth_headers):
    r = client.get("/prospects/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
