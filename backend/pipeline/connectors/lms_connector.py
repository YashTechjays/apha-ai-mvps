"""LMS Connector — CPE/course data from APhA's learning management system."""
import random
from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def pull_lms_data(db: Session):
    members = db.query(Member).filter(Member.is_active == True).all()
    for member in members:
        if random.random() < 0.3:
            member.cpe_hours_last_90d = min(
                (member.cpe_hours_last_90d or 0) + random.uniform(0.5, 3.0), 30.0
            )
    db.commit()
    logger.info(f"LMS sync: updated CPE data for {len(members)} members.")


def _fetch_from_api(member_id: str) -> dict:
    """TODO: Replace with real LMS API call."""
    raise NotImplementedError("Replace with real LMS API integration")
