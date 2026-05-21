def test_list_members_unauthenticated(client):
    res = client.get("/members/")
    assert res.status_code == 401


def test_list_members_authenticated(client, auth_headers):
    res = client.get("/members/", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_nonexistent_member(client, auth_headers):
    res = client.get("/members/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert res.status_code == 404
