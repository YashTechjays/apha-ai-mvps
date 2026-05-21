"""Mock CRM connector — placeholder for production Salesforce/HubSpot integration."""
from sqlalchemy.orm import Session
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def sync_member_profiles(db: Session):
    logger.info("[CRM MOCK] Would sync member profile updates from CRM")
    return {"synced": 0}
