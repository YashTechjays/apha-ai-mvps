"""Core concierge logic — takes conversation history and returns AI response."""
from openai import OpenAI
from typing import List, Dict
from apps.concierge.ai.prompts import SYSTEM_PROMPT, LEAD_CAPTURE_PROMPT
from apps.concierge.ai.intent_detector import detect_intent
from apps.concierge.rag.retriever import retrieve_context, format_context_for_prompt
from apps.concierge.utils.config import get_settings
from apps.concierge.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def build_system_prompt(context: str, turn_count: int, intent: str) -> str:
    return SYSTEM_PROMPT.format(
        context=context,
        turn_count=turn_count,
        intent=intent,
    )


def should_request_lead(turn_count: int, lead_captured: bool, intent: str) -> bool:
    return (
        not lead_captured
        and turn_count >= settings.lead_capture_after_turns
        and intent not in ("off_topic",)
        and turn_count % 3 == 0
    )


def generate_response(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    turn_count: int = 0,
    lead_captured: bool = False,
) -> Dict:
    """
    Generate an AI response for the given conversation.

    Returns:
        {response, intent, chunks_used, should_capture_lead, tier_recommendation}
    """
    intent = detect_intent(user_message)
    logger.info(f"Detected intent: {intent} | Turn: {turn_count}")

    if intent == "off_topic":
        return {
            "response": (
                "I'm specifically here to help with APhA membership questions — "
                "things like joining, renewal, CPE programs, and member benefits. "
                "Is there anything along those lines I can help you with?"
            ),
            "intent": intent,
            "chunks_used": 0,
            "should_capture_lead": False,
            "tier_recommendation": None,
        }

    chunks = retrieve_context(user_message, k=4)
    context_str = format_context_for_prompt(chunks)
    system_prompt = build_system_prompt(context_str, turn_count, intent)

    if should_request_lead(turn_count, lead_captured, intent):
        lead_nudge = LEAD_CAPTURE_PROMPT.format(turn_count=turn_count)
        system_prompt += f"\n\nIMPORTANT: {lead_nudge}"

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=settings.openai_model_name,
        max_tokens=600,
        messages=messages,
    )
    response_text = response.choices[0].message.content or ""

    tier_rec = None
    tier_keywords = {
        "student": "student",
        "new practitioner": "new_practitioner",
        "full member": "pharmacist",
        "pharmacist membership": "pharmacist",
        "technician": "technician",
        "researcher": "researcher",
    }
    for keyword, tier in tier_keywords.items():
        if keyword in response_text.lower():
            tier_rec = tier
            break

    return {
        "response": response_text,
        "intent": intent,
        "chunks_used": len(chunks),
        "should_capture_lead": should_request_lead(turn_count, lead_captured, intent),
        "tier_recommendation": tier_rec,
    }
