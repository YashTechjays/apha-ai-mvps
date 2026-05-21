"""
CRM Connector — Personify API interface.
MVP: returns mock data. Production: replace _fetch_from_api() with real API calls.
"""
import random
from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def pull_crm_data(db: Session):
    members = db.query(Member).filter(Member.is_active == True).all()
    for member in members:
        delta = random.uniform(-5, 10)
        member.days_since_last_login = max(0, (member.days_since_last_login or 0) + delta)
    db.commit()
    logger.info(f"CRM sync: updated {len(members)} member login records.")


def _fetch_from_api(endpoint: str, params: dict) -> dict:
    """
    TODO: Replace with real Personify API call.
    Example:
        import httpx
        response = httpx.get(
            f"https://api.personify.com/{endpoint}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params=params,
        )
        return response.json()
    """
    raise NotImplementedError("Replace with real Personify API integration")
