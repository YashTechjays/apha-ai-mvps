"""
IP-based rate limiter for free tier usage.
Each tool has its own daily limit per IP.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import redis as redis_lib

from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

TOOL_LIMITS = {
    "salary": settings.salary_free_checks_per_day,
    "interaction": settings.interaction_free_checks_per_day,
    "career": settings.career_free_assessments_per_day,
}

REDIS_AVAILABLE = False
_redis = None

try:
    _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
    _redis.ping()
    REDIS_AVAILABLE = True
except Exception:
    logger.warning("Redis unavailable - rate limiting disabled")


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def check_limit(ip: str, tool: str) -> tuple[bool, dict]:
    """
    Returns (allowed: bool, info: dict with remaining + limit).
    """
    limit = TOOL_LIMITS.get(tool, 3)
    if not REDIS_AVAILABLE:
        return True, {"allowed": True, "remaining": limit, "used": 0, "limit": limit}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"rl:{tool}:{_hash_ip(ip)}:{today}"

    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    results = pipe.execute()

    used = results[0]
    remaining = max(0, limit - used)
    allowed = used <= limit

    return allowed, {
        "allowed": allowed,
        "used": used,
        "remaining": remaining,
        "limit": limit,
    }


def get_usage(ip: str, tool: str) -> dict:
    """Get current usage without incrementing."""
    limit = TOOL_LIMITS.get(tool, 3)
    if not REDIS_AVAILABLE:
        return {"used": 0, "remaining": limit, "limit": limit}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"rl:{tool}:{_hash_ip(ip)}:{today}"
    used = int(_redis.get(key) or 0)
    return {"used": used, "remaining": max(0, limit - used), "limit": limit}
