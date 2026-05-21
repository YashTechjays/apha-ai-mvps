"""Run before deploying to verify all state data is complete and correct."""
import json
import sys
from pathlib import Path

data_path = Path(__file__).parent.parent / "backend" / "data" / "state_requirements.json"
data = json.loads(data_path.read_text())

errors = []
for code, state in data.items():
    if not state.get("hours_required"):
        errors.append(f"{code}: missing hours_required")
    if not state.get("cycle_years"):
        errors.append(f"{code}: missing cycle_years")
    if not state.get("notes"):
        errors.append(f"{code}: missing notes")

if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"All {len(data)} states validated successfully.")
