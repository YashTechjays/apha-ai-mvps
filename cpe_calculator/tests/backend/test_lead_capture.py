import uuid
from datetime import date, timedelta


def _future():
    return (date.today() + timedelta(days=150)).isoformat()


def test_full_plan_requires_lead(client):
    session_id = str(uuid.uuid4())
    calc_res = client.post("/calculate/", json={
        "session_id": session_id,
        "state": "FL",
        "renewal_date": _future(),
        "hours_completed": 5,
    })
    calc_id = calc_res.json()["calculation_id"]
    # Without lead, full plan blocked
    res = client.get(f"/calculate/full/{calc_id}?session_id={session_id}")
    assert res.status_code == 403


def test_full_plan_unlocks_after_lead(client):
    session_id = str(uuid.uuid4())
    calc_res = client.post("/calculate/", json={
        "session_id": session_id,
        "state": "FL",
        "renewal_date": _future(),
        "hours_completed": 5,
    })
    calc_id = calc_res.json()["calculation_id"]
    client.post("/leads/", json={
        "session_id": session_id,
        "email": f"unlock_{uuid.uuid4().hex[:6]}@pharmacist.com",
    })
    res = client.get(f"/calculate/full/{calc_id}?session_id={session_id}")
    assert res.status_code == 200
    assert res.json()["is_preview"] is False
