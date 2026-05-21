"""Create Stripe products and prices for APhA Clinical Assistant plans.

Usage:
    STRIPE_SECRET_KEY=sk_test_... python -m scripts.create_stripe_products

Outputs price IDs to copy into .env as:
    STRIPE_PRICE_INDIVIDUAL=...
    STRIPE_PRICE_TEAM=...
    STRIPE_PRICE_INSTITUTION=...
    STRIPE_PRICE_ENTERPRISE=...
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.billing.plan_definitions import PLANS  # noqa: E402

try:
    import stripe
except ImportError:
    print("ERROR: stripe package not installed. Run: pip install stripe", file=sys.stderr)
    sys.exit(1)


def main():
    key = os.getenv("STRIPE_SECRET_KEY", "")
    if not key:
        print("ERROR: STRIPE_SECRET_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    stripe.api_key = key
    env_lines = []

    for code, plan in PLANS.items():
        if code == "trial":
            continue
        if plan.monthly_price_usd <= 0 and code != "enterprise":
            continue

        product = stripe.Product.create(
            name=f"APhA Clinical Assistant — {plan.name}",
            description=f"{plan.queries_per_month} queries/month · {plan.seats} seats · {'API access' if plan.api_access else 'Web only'}",
            metadata={"plan_code": plan.code},
        )

        if code == "enterprise":
            # No price object — handled via custom quotes
            print(f"# {code}: created product {product.id} (no price — enterprise contact sales)")
            continue

        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(plan.monthly_price_usd * 100),
            currency="usd",
            recurring={"interval": "month"},
            nickname=plan.name,
            metadata={"plan_code": plan.code},
        )

        env_var = plan.stripe_price_id_env or f"STRIPE_PRICE_{code.upper()}"
        env_lines.append(f"{env_var}={price.id}")
        print(f"# {code}: product={product.id}  price={price.id}  amount=${plan.monthly_price_usd}/mo")

    print("\n# Copy these into your .env:")
    print("\n".join(env_lines))


if __name__ == "__main__":
    main()
