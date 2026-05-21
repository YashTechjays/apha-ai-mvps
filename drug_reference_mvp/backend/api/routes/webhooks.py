"""Stripe webhook handler."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend.api.deps import get_db
from backend.billing.plan_definitions import PLANS, get_plan
from backend.billing.stripe_client import construct_webhook_event, parse_subscription_event
from backend.db.models import Subscription, User
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(default="", alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    event = construct_webhook_event(payload, stripe_signature, secret)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    parsed = parse_subscription_event(event)
    etype = parsed.get("type")
    logger.info(f"Stripe webhook received: {etype}")

    if etype in (
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
    ):
        _handle_subscription_upsert(parsed, db)
    elif etype in (
        "customer.subscription.deleted",
        "customer.subscription.canceled",
    ):
        _handle_subscription_cancel(parsed, db)
    elif etype == "invoice.payment_failed":
        _handle_payment_failed(parsed, db)
    else:
        logger.debug(f"Unhandled stripe event type: {etype}")

    return {"received": True}


def _handle_subscription_upsert(parsed: dict, db: Session):
    stripe_sub_id = parsed.get("subscription_id")
    customer_id = parsed.get("customer_id")
    metadata = parsed.get("metadata") or {}
    plan_code = metadata.get("plan_code") or "individual"
    plan = get_plan(plan_code)

    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if not user:
        logger.warning(f"Stripe customer {customer_id} not found in DB.")
        return

    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if not sub:
        sub = Subscription(user_id=user.id, organization_id=user.organization_id)
        db.add(sub)

    sub.plan = plan.code
    sub.status = parsed.get("status") or "active"
    sub.stripe_subscription_id = stripe_sub_id
    sub.queries_limit_per_month = plan.queries_per_month
    period_end = parsed.get("current_period_end")
    if period_end:
        try:
            sub.current_period_end = datetime.fromtimestamp(int(period_end), tz=timezone.utc)
        except Exception:
            pass
    db.commit()
    logger.info(f"Subscription upserted for {user.email}: {plan.code}")


def _handle_subscription_cancel(parsed: dict, db: Session):
    stripe_sub_id = parsed.get("subscription_id")
    if not stripe_sub_id:
        return
    sub = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == stripe_sub_id)
        .first()
    )
    if sub:
        sub.status = "canceled"
        sub.plan = "trial"
        sub.queries_limit_per_month = 10
        db.commit()


def _handle_payment_failed(parsed: dict, db: Session):
    stripe_sub_id = parsed.get("subscription_id")
    if not stripe_sub_id:
        return
    sub = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == stripe_sub_id)
        .first()
    )
    if sub:
        sub.status = "past_due"
        db.commit()
