"""
SendGrid — trigger CPE nurture email sequence for captured leads.
MVP: mock. Production: set SENDGRID_API_KEY.
"""
from backend.db.models.lead import Lead
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def trigger_cpe_nurture_sequence(lead: Lead):
    """
    Trigger a 3-email nurture sequence:
      Email 1 (instant): Full CPE plan + state requirements summary
      Email 2 (day 3):   "Your renewal is X days away — here's what's still needed"
      Email 3 (day 7):   "APhA membership includes all your required CPE free"
    """
    logger.info(
        f"[SENDGRID MOCK] Triggering CPE nurture for {lead.email} | "
        f"State: {lead.state} | Gap: {lead.hours_gap}h | "
        f"Days: {lead.days_until_renewal}"
    )
