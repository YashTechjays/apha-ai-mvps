import random
from backend.db.models.member import Member


def fetch_events_activity(member: Member) -> dict:
    """Mock events connector — simulates meeting and event registration data."""
    return {
        "member_id": member.id,
        "annual_meeting_attended": random.random() < 0.25,
        "events_registered_ytd": random.randint(0, 4),
    }
