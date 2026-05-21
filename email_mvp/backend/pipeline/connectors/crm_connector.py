import random
from datetime import datetime, timedelta
from backend.db.models.member import Member


def fetch_portal_activity(member: Member) -> dict:
    """Mock CRM/portal connector — simulates login and engagement data."""
    days_ago = random.randint(0, 60)
    return {
        "member_id": member.id,
        "last_login_date": datetime.utcnow() - timedelta(days=days_ago),
        "days_since_last_login": days_ago,
        "portal_sessions_last_30d": random.randint(0, 20),
        "email_open_rate": round(random.uniform(0.05, 0.75), 2),
        "career_center_applications": random.randint(0, 3),
        "advocacy_actions_ytd": random.randint(0, 5),
    }
