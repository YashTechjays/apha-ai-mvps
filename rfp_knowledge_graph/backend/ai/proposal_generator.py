from typing import Optional
from backend.ai.prompts import (
    PROPOSAL_GENERATION_SYSTEM,
    PROPOSAL_GENERATION_USER,
    PROPOSAL_CONTEXT_BLOCK,
)
from backend.utils.logger import get_logger

logger = get_logger("proposal_generator")


def generate_proposal(
    rfp: dict, profile: dict, username: str, context: Optional[dict] = None
) -> str:
    """Generate a markdown proposal for an RFP given a pharmacist profile.

    When ``context`` (from GraphRAG, Enhancement #6) is supplied, graph-derived
    institutional knowledge is appended to the prompt. ``context=None`` keeps the
    original single-RFP behavior — fully backward compatible.
    """
    from backend.utils.config import get_settings
    from openai import OpenAI

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    org = rfp.get("organization") or {}
    org_name = org.get("name") if isinstance(org, dict) else rfp.get("organization_name", "")
    location_parts = [profile.get("location_city"), profile.get("location_state")]
    location_str = ", ".join(p for p in location_parts if p) or "Not specified"

    user_prompt = PROPOSAL_GENERATION_USER.format(
        rfp_title=rfp.get("title", ""),
        rfp_org=org_name or "Not specified",
        rfp_description=rfp.get("description", "")[:500],
        rfp_requirements=", ".join(rfp.get("requirements", [])[:10]) or "See RFP document",
        rfp_budget=rfp.get("budget_range") or "Not specified",
        rfp_deadline=rfp.get("deadline") or "Not specified",
        pharmacist_name=profile.get("full_name") or username,
        pharmacist_location=location_str,
        pharmacist_experience=str(profile.get("years_experience") or "Not specified"),
        pharmacist_specialties=", ".join(profile.get("specialties") or []) or "General pharmacy",
        pharmacist_certifications=", ".join(profile.get("certifications") or []) or "PharmD",
        pharmacist_bio=profile.get("bio") or "Experienced pharmacist.",
    )

    if context:
        from backend.ai.graph_rag import format_context_block
        block = format_context_block(context)
        if block:
            user_prompt += PROPOSAL_CONTEXT_BLOCK.format(graph_context=block)

    logger.info(f"Generating proposal for RFP: {rfp.get('id')} by user: {username}")

    resp = client.chat.completions.create(
        model=settings.openai_model_name,
        messages=[
            {"role": "system", "content": PROPOSAL_GENERATION_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    return resp.choices[0].message.content
