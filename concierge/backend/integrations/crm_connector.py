"""
Personify CRM integration — push captured leads into APhA's CRM.
MVP: mock implementation. Production: replace _call_api with real Personify calls.
"""
from backend.db.models.lead import Lead
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def push_lead_to_crm(lead: Lead):
    """Push a captured lead to APhA's Personify CRM."""
    logger.info(f"[CRM MOCK] Pushing lead to Personify: {lead.email} | Tier: {lead.interested_tier}")
    # In production:
    # payload = {
    #     "email": lead.email,
    #     "name": lead.name,
    #     "source": "ai_concierge",
    #     "interested_tier": lead.interested_tier,
    #     "intent": lead.visitor_intent,
    # }
    # response = httpx.post(
    #     "https://api.personify.com/leads",
    #     json=payload,
    #     headers={"Authorization": f"Bearer {settings.personify_api_key}"},
    # )
    # response.raise_for_status()
