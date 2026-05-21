import random
from backend.db.models.member import Member


def fetch_cpe_activity(member: Member) -> dict:
    """Mock LMS connector — simulates incremental CPE data since last sync."""
    new_credits = round(random.uniform(0, 3), 1)
    new_courses = random.randint(0, 2)
    new_webinars = random.randint(0, 1)
    return {
        "member_id": member.id,
        "cpe_credits_delta": new_credits,
        "courses_delta": new_courses,
        "webinars_delta": new_webinars,
    }
