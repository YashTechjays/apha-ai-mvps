"""Pull APhA member email list from CRM to exclude from outreach."""
from utils.logger import get_logger

logger = get_logger(__name__)


def pull_member_emails() -> list:
    """
    Pull all current APhA member emails from Personify CRM.
    MVP: returns mock list. Production: replace with real API call.
    """
    logger.info("[CRM MOCK] Pulling APhA member email list...")
    return []
