"""Tests for billing/plan definitions, stripe fallback, and rate limiter."""
from __future__ import annotations

from backend.billing.plan_definitions import PLANS, get_plan, list_plans
from backend.billing.stripe_client import create_checkout_session, parse_subscription_event
from backend.rate_limiter.redis_limiter import RateLimiter


def test_plan_definitions_complete():
    expected = {"trial", "individual", "team", "institution", "enterprise"}
    assert expected.issubset(PLANS.keys())
    for code in expected:
        p = get_plan(code)
        assert p.code == code
        assert p.queries_per_month > 0
        assert isinstance(p.features, list) and p.features


def test_list_plans_returns_all():
    assert len(list_plans()) >= 5


def test_stripe_checkout_mock_when_no_key():
    s = create_checkout_session(
        price_id="price_test",
        customer_email="x@y.com",
        success_url="http://localhost/ok",
        cancel_url="http://localhost/no",
        plan_code="individual",
    )
    assert s["mock"] is True
    assert s["url"].startswith("http://localhost/ok")


def test_parse_subscription_event():
    event = {
        "type": "customer.subscription.created",
        "data": {"object": {
            "id": "sub_1",
            "customer": "cus_1",
            "status": "active",
            "current_period_end": 1700000000,
            "metadata": {"plan_code": "team"},
        }},
    }
    parsed = parse_subscription_event(event)
    assert parsed["type"] == "customer.subscription.created"
    assert parsed["subscription_id"] == "sub_1"
    assert parsed["metadata"]["plan_code"] == "team"


def test_rate_limiter_allows_under_limit():
    limiter = RateLimiter()
    for _ in range(2):
        allowed, info = limiter.check("user-1", "trial")
        assert allowed
    assert info["limit"] >= 2


def test_rate_limiter_blocks_over_limit():
    limiter = RateLimiter()
    plan_limit = get_plan("trial").rate_limit_per_minute
    for _ in range(plan_limit):
        allowed, _ = limiter.check("user-2", "trial")
        assert allowed
    # Next one should exceed
    allowed, info = limiter.check("user-2", "trial")
    assert not allowed
    assert info["retry_after"] > 0
