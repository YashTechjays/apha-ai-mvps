"""Sliding-window rate limiter backed by Redis (with in-memory fallback)."""
from __future__ import annotations

import time
from collections import deque
from typing import Dict, Deque, Tuple

from backend.billing.plan_definitions import get_plan
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


class _InMemoryWindow:
    """Fallback per-process sliding window."""

    def __init__(self):
        self.events: Dict[str, Deque[float]] = {}

    def add_and_count(self, key: str, window_seconds: int) -> int:
        now = time.time()
        cutoff = now - window_seconds
        dq = self.events.setdefault(key, deque())
        while dq and dq[0] < cutoff:
            dq.popleft()
        dq.append(now)
        return len(dq)


class RateLimiter:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self._client = None
        self._fallback = _InMemoryWindow()
        self._connected_attempted = False

    def _get_client(self):
        if self._connected_attempted:
            return self._client
        self._connected_attempted = True
        if redis is None:
            logger.info("redis package unavailable; rate limiter using in-memory fallback")
            return None
        try:
            client = redis.Redis.from_url(self.redis_url, decode_responses=True, socket_timeout=1.0)
            client.ping()
            self._client = client
        except Exception as e:
            logger.info(f"Redis unavailable, rate limiter using in-memory fallback: {e}")
            self._client = None
        return self._client

    def check(self, identity: str, plan_code: str) -> Tuple[bool, Dict[str, int]]:
        """Check whether a request is allowed.

        Returns (allowed, info) where info has keys:
          - limit, remaining, retry_after
        """
        plan = get_plan(plan_code)
        limit = plan.rate_limit_per_minute
        window_seconds = 60
        key = f"rl:{plan_code}:{identity}"

        client = self._get_client()
        count = 0

        if client is not None:
            try:
                now_ms = int(time.time() * 1000)
                cutoff_ms = now_ms - window_seconds * 1000
                pipe = client.pipeline()
                pipe.zremrangebyscore(key, 0, cutoff_ms)
                pipe.zadd(key, {f"{now_ms}-{identity}-{int(time.time()*1e6)}": now_ms})
                pipe.zcard(key)
                pipe.expire(key, window_seconds * 2)
                _, _, count, _ = pipe.execute()
            except Exception as e:
                logger.warning(f"Redis rate limit error, falling back: {e}")
                count = self._fallback.add_and_count(key, window_seconds)
        else:
            count = self._fallback.add_and_count(key, window_seconds)

        remaining = max(0, limit - count)
        allowed = count <= limit
        info = {
            "limit": limit,
            "remaining": remaining,
            "retry_after": 0 if allowed else 60,
            "count": int(count),
        }
        return allowed, info


_limiter: RateLimiter = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter
