"""
Deliverability controls:
  - Sending rate limits (per hour, per day)
  - Send window enforcement (9 AM - 5 PM)
  - Domain throttling (max N sends to same domain per hour)
  - Warm-up ramp (start slow, increase gradually)
"""
import redis as redis_lib
from datetime import datetime
from apps.outreach.utils.config import get_settings
from apps.outreach.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

try:
    _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
    _redis.ping()
    REDIS_OK = True
except Exception:
    REDIS_OK = False
    logger.warning("Redis unavailable -- deliverability controls disabled")


def is_send_window_open() -> bool:
    """Check if current time is within allowed sending window."""
    if settings.env == "development":
        return True
    hour = datetime.utcnow().hour
    return settings.send_window_start_hour <= hour < settings.send_window_end_hour


def check_hourly_rate(campaign_id: str) -> tuple[bool, int]:
    """Check if campaign is within hourly send rate. Returns (allowed, count)."""
    if not REDIS_OK:
        return True, 0
    key = f"rate:hourly:{campaign_id}:{datetime.utcnow().strftime('%Y%m%d%H')}"
    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)
    count = pipe.execute()[0]
    return count <= settings.max_sends_per_hour, count


def check_daily_rate(campaign_id: str) -> tuple[bool, int]:
    """Check if campaign is within daily send rate."""
    if not REDIS_OK:
        return True, 0
    key = f"rate:daily:{campaign_id}:{datetime.utcnow().strftime('%Y%m%d')}"
    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)
    count = pipe.execute()[0]
    return count <= settings.max_sends_per_day, count


def check_domain_throttle(domain: str, max_per_hour: int = 10) -> bool:
    """Prevent too many sends to same domain (e.g., one employer) per hour."""
    if not REDIS_OK:
        return True
    key = f"domain:{domain}:{datetime.utcnow().strftime('%Y%m%d%H')}"
    pipe = _redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)
    count = pipe.execute()[0]
    return count <= max_per_hour
