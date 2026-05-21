"""
HubSpot email integration — trigger follow-up sequences for captured leads.
MVP: mock. Production: replace with real HubSpot API calls.
"""
from backend.db.models.lead import Lead
from backend.utils.logger import get_logger

logger = get_logger(__name__)

SEQUENCE_MAP = {
    "student": "sequence_student_join",
    "new_practitioner": "sequence_newprac_join",
    "pharmacist": "sequence_pharmacist_join",
    "technician": "sequence_tech_join",
    None: "sequence_general_join",
}


def trigger_followup_sequence(lead: Lead):
    """Trigger the right email nurture sequence for this lead in HubSpot."""
    sequence = SEQUENCE_MAP.get(lead.interested_tier, "sequence_general_join")
    logger.info(f"[EMAIL MOCK] Triggering sequence '{sequence}' for {lead.email}")
    # In production:
    # response = httpx.post(
    #     "https://api.hubspot.com/crm/v3/objects/contacts",
    #     json={"properties": {"email": lead.email, "hs_email_optout": False}},
    #     headers={"Authorization": f"Bearer {settings.hubspot_api_key}"},
    # )
    # then enroll in sequence via HubSpot Sequences API
