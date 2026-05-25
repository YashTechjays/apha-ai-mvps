from backend.rate_limiter.redis_limiter import check_limit, get_usage, REDIS_AVAILABLE


def test_rate_limiter_allows_when_redis_unavailable():
    """When Redis is down, requests should still be allowed."""
    if REDIS_AVAILABLE:
        return  # Skip if Redis is actually running

    allowed, info = check_limit("127.0.0.1", "salary")
    assert allowed is True
    assert info["remaining"] > 0


def test_get_usage_when_redis_unavailable():
    """Usage should return defaults when Redis is down."""
    if REDIS_AVAILABLE:
        return

    info = get_usage("127.0.0.1", "salary")
    assert info["used"] == 0
    assert info["limit"] == 3
