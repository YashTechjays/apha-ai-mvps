"""Stripe client wrapper with safe fallbacks when Stripe is unavailable."""
from __future__ import annotations

import os
import time
import uuid
from typing import Dict, Any, Optional

from apps.drug_ref.utils.config import settings
from apps.drug_ref.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None


def _configured() -> bool:
    return stripe is not None and bool(settings.stripe_secret_key)


def _init_stripe():
    if _configured():
        stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    *,
    price_id: str,
    customer_email: str,
    success_url: str,
    cancel_url: str,
    organization_id: Optional[str] = None,
    plan_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a Stripe Checkout session or return a deterministic mock."""
    if not _configured():
        # Mock checkout for local dev / tests
        return {
            "id": f"cs_test_{uuid.uuid4().hex[:24]}",
            "url": f"{success_url}?mock=true&plan={plan_code or 'unknown'}",
            "mock": True,
        }
    _init_stripe()
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=customer_email,
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={
                "organization_id": organization_id or "",
                "plan_code": plan_code or "",
            },
        )
        return {"id": session.id, "url": session.url, "mock": False}
    except Exception as e:
        logger.error(f"Stripe checkout creation failed: {e}")
        return {
            "id": f"cs_failed_{uuid.uuid4().hex[:24]}",
            "url": f"{success_url}?error=stripe_unavailable",
            "mock": True,
            "error": str(e),
        }


def create_customer(email: str, name: Optional[str] = None) -> Optional[str]:
    if not _configured():
        return f"cus_mock_{uuid.uuid4().hex[:14]}"
    _init_stripe()
    try:
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id
    except Exception as e:
        logger.error(f"Stripe customer creation failed: {e}")
        return None


def cancel_subscription(subscription_id: str) -> bool:
    if not _configured():
        logger.info(f"[MOCK] Cancel subscription {subscription_id}")
        return True
    _init_stripe()
    try:
        stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
        return True
    except Exception as e:
        logger.error(f"Stripe cancel failed: {e}")
        return False


def construct_webhook_event(payload: bytes, signature: str, webhook_secret: str) -> Optional[Dict[str, Any]]:
    if not _configured():
        # Test mode: trust the payload as JSON
        import json
        try:
            return json.loads(payload.decode("utf-8")) if isinstance(payload, (bytes, bytearray)) else json.loads(payload)
        except Exception:
            return None
    _init_stripe()
    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
        return event  # type: ignore[return-value]
    except Exception as e:
        logger.warning(f"Stripe webhook signature failed: {e}")
        return None


def parse_subscription_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a Stripe event into a dict our code understands."""
    if isinstance(event, dict):
        etype = event.get("type")
        data = event.get("data", {}).get("object", {})
    else:
        etype = getattr(event, "type", None)
        data = getattr(event, "data", {})
        if hasattr(data, "object"):
            data = data.object

    return {
        "type": etype,
        "subscription_id": data.get("id") if isinstance(data, dict) else getattr(data, "id", None),
        "customer_id": data.get("customer") if isinstance(data, dict) else getattr(data, "customer", None),
        "status": data.get("status") if isinstance(data, dict) else getattr(data, "status", None),
        "current_period_end": data.get("current_period_end") if isinstance(data, dict) else getattr(data, "current_period_end", None),
        "metadata": (data.get("metadata") if isinstance(data, dict) else getattr(data, "metadata", {})) or {},
        "raw": data,
        "ts": int(time.time()),
    }
