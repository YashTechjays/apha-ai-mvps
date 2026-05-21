"""Subscription / billing endpoints."""
from __future__ import annotations

import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_active_subscription, get_current_user, get_db
from backend.api.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    PlanInfo,
    SubscriptionStatus,
)
from backend.billing.plan_definitions import PLANS, get_plan, list_plans
from backend.billing.stripe_client import (
    cancel_subscription,
    create_checkout_session,
    create_customer,
)
from backend.db.models import Subscription, User
from backend.utils.config import settings

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=list[PlanInfo])
def get_plans():
    return [
        PlanInfo(
            code=p.code,
            name=p.name,
            monthly_price_usd=p.monthly_price_usd,
            queries_per_month=p.queries_per_month,
            rate_limit_per_minute=p.rate_limit_per_minute,
            seats=p.seats,
            api_access=p.api_access,
            features=p.features,
        )
        for p in list_plans()
    ]


@router.get("/me", response_model=SubscriptionStatus)
def my_subscription(sub: Subscription = Depends(get_active_subscription)):
    return SubscriptionStatus(
        plan=sub.plan,
        status=sub.status,
        queries_used_this_month=sub.queries_used_this_month or 0,
        queries_limit_per_month=sub.queries_limit_per_month or 0,
        current_period_end=sub.current_period_end.isoformat() if sub.current_period_end else None,
        cancel_at_period_end=bool(sub.cancel_at_period_end),
    )


@router.post("/checkout", response_model=CheckoutResponse)
def start_checkout(
    req: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.plan_code not in PLANS:
        raise HTTPException(status_code=400, detail="Unknown plan.")
    plan = get_plan(req.plan_code)
    if plan.code == "trial":
        raise HTTPException(status_code=400, detail="Trial plan does not require checkout.")
    if plan.code == "enterprise":
        return CheckoutResponse(
            checkout_url=f"{settings.frontend_url}/contact-sales",
            session_id="enterprise_contact",
            mock=True,
        )

    # Ensure Stripe customer
    if not user.stripe_customer_id:
        cust = create_customer(email=user.email, name=user.full_name)
        if cust:
            user.stripe_customer_id = cust
            db.commit()

    price_id = os.getenv(plan.stripe_price_id_env or "", "price_mock")
    session = create_checkout_session(
        price_id=price_id,
        customer_email=user.email,
        success_url=f"{settings.frontend_url}/billing/success",
        cancel_url=f"{settings.frontend_url}/pricing",
        organization_id=str(user.organization_id) if user.organization_id else None,
        plan_code=plan.code,
    )
    return CheckoutResponse(
        checkout_url=session["url"],
        session_id=session["id"],
        mock=bool(session.get("mock")),
    )


@router.post("/cancel")
def cancel_my_subscription(
    sub: Subscription = Depends(get_active_subscription),
    db: Session = Depends(get_db),
):
    if sub.stripe_subscription_id:
        ok = cancel_subscription(sub.stripe_subscription_id)
        if not ok:
            raise HTTPException(status_code=502, detail="Failed to cancel with Stripe.")
    sub.cancel_at_period_end = True
    db.commit()
    return {"canceled": True, "ends_at": sub.current_period_end.isoformat() if sub.current_period_end else None}
