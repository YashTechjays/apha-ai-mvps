def test_send_nudges_dry_run(client, auth_headers):
    client.post("/scores/run", headers=auth_headers)
    r = client.post("/nudges/send", headers=auth_headers, json={"dry_run": True})
    assert r.status_code == 200
    data = r.json()
    assert "sent" in data
    assert data["dry_run"] is True


def test_list_nudges(client, auth_headers):
    r = client.get("/nudges/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_login_bad_credentials(client):
    r = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert r.status_code == 401
