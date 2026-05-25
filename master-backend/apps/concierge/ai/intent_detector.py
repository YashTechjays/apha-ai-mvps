"""
Classify user message intent using keyword pattern matching.

Intent categories:
  join, renew, cpe, benefits, pricing, events, career, question, off_topic
"""
import re
from apps.concierge.utils.logger import get_logger

logger = get_logger(__name__)

INTENT_PATTERNS = {
    "join": [
        r"join", r"sign up", r"become a member", r"membership", r"how do i (get|start|enroll)",
        r"want to (join|apply)", r"interested in joining",
    ],
    "renew": [
        r"renew", r"renewal", r"expired", r"lapsed", r"reinstate", r"my membership",
    ],
    "cpe": [
        r"cpe", r"continuing education", r"ce credits", r"license renewal",
        r"credit hours", r"acpe", r"certificate program",
    ],
    "benefits": [
        r"benefit", r"get with", r"included", r"what do i get", r"worth it",
        r"value", r"access to", r"features",
    ],
    "pricing": [
        r"cost", r"price", r"how much", r"fee", r"dues", r"discount", r"afford",
    ],
    "events": [
        r"annual meeting", r"conference", r"event", r"webinar", r"np life",
        r"midyear", r"attend",
    ],
    "career": [
        r"job", r"career", r"resume", r"residency", r"fellowship", r"advance",
    ],
}

OFF_TOPIC_PATTERNS = [
    r"politics", r"election", r"stock", r"invest", r"recipe", r"weather",
    r"sports", r"movie", r"music",
]


def detect_intent(message: str) -> str:
    """Classify the intent of a user message using pattern matching."""
    text = message.lower()

    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, text):
            return "off_topic"

    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, text))
        if score > 0:
            scores[intent] = score

    if not scores:
        return "question"

    return max(scores, key=scores.get)
