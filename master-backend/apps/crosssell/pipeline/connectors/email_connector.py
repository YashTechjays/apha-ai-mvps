"""Mock email engagement connector — pulls opens/clicks from SendGrid webhook events."""
from sqlalchemy.orm import Session
from apps.crosssell.utils.logger import get_logger

logger = get_logger(__name__)


def sync_email_engagement(db: Session):
    logger.info("[EMAIL MOCK] Would sync open/click events from SendGrid")
    return {"events_processed": 0}
