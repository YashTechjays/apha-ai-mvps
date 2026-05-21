import random
from backend.db.models.member import Member


def fetch_publication_activity(member: Member) -> dict:
    """Mock publications connector — simulates journal and PharmacyLibrary usage."""
    return {
        "member_id": member.id,
        "journal_articles_read_ytd": random.randint(0, 30),
        "pharmacylibrary_sessions_ytd": random.randint(0, 40),
    }
