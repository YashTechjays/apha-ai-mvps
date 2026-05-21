import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "backend" / "data" / "state_requirements.json"


def test_all_50_states_plus_dc():
    data = json.loads(DATA_PATH.read_text())
    assert len(data) == 51, f"Expected 51 entries (50 states + DC), got {len(data)}"


def test_all_states_have_required_fields():
    data = json.loads(DATA_PATH.read_text())
    required = ["name", "hours_required", "cycle_years", "renewal_month", "notes"]
    for code, state in data.items():
        for field in required:
            assert field in state, f"{code} missing field: {field}"


def test_hours_are_positive():
    data = json.loads(DATA_PATH.read_text())
    for code, state in data.items():
        assert state["hours_required"] > 0, f"{code} has zero hours"
        assert state["cycle_years"] in [1, 2, 3], f"{code} has unusual cycle"


def test_california_has_mandatory_requirements():
    data = json.loads(DATA_PATH.read_text())
    ca = data["CA"]
    assert ca["hours_required"] == 30
    assert len(ca["special_requirements"]) > 0


def test_new_york_highest_hours():
    data = json.loads(DATA_PATH.read_text())
    ny = data["NY"]
    assert ny["hours_required"] == 45
