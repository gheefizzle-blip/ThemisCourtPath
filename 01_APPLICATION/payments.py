"""
Themis Court Path - Payments Module
====================================
TCP-WO-300 Phase 1 implementation.

Stripe Checkout integration for $99 filing fee. Test mode only —
this WO does not enable live payments.

Security:
- Server-side verification only (no client-trust)
- Session metadata binds {filing_id, user_id} so we can re-confirm
  ownership after Stripe redirects back
- We never store card data; Stripe holds it
- Out of scope: subscriptions, refunds, invoices, tax, webhooks
  (sync verification at /success is acceptable for Phase 1)
"""

import os
import sys
from typing import Optional

import stripe


# ── Constants ─────────────────────────────────────────────────

PRODUCT_NAME = "Child Support Petition Filing Package"
UNIT_AMOUNT_CENTS = 9900   # $99.00
CURRENCY = "usd"


# ── Stripe init ───────────────────────────────────────────────

def init_stripe() -> bool:
    """Configure stripe.api_key from env. Returns True if a key was set.

    Does NOT raise if missing — call sites check is_configured() and
    return a clear API error. This keeps the app importable in dev
    environments without Stripe credentials.
    """
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        sys.stderr.write(
            "WARNING: STRIPE_SECRET_KEY not set. "
            "Payment endpoints will return 503 until configured.\n"
        )
        return False
    if not (key.startswith("sk_test_") or key.startswith("sk_live_")):
        sys.stderr.write(
            "WARNING: STRIPE_SECRET_KEY does not look like a Stripe key "
            "(expected sk_test_... or sk_live_...).\n"
        )
    stripe.api_key = key
    return True


def is_configured() -> bool:
    """True iff stripe.api_key has been set."""
    return bool(getattr(stripe, "api_key", None))


# ── Checkout ──────────────────────────────────────────────────

def create_checkout_session(
    filing_id: str,
    user_id: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout session for a filing. Returns {session_id, checkout_url}.

    success_url should include {CHECKOUT_SESSION_ID} so Stripe substitutes
    the real session id when it redirects the user back.
    """
    if not is_configured():
        raise RuntimeError("Stripe is not configured (STRIPE_SECRET_KEY missing)")
    if not filing_id or not user_id:
        raise ValueError("filing_id and user_id are required")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": CURRENCY,
                    "product_data": {"name": PRODUCT_NAME},
                    "unit_amount": UNIT_AMOUNT_CENTS,
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "filing_id": filing_id,
            "user_id": user_id,
        },
    )
    return {
        "session_id": session.id,
        "checkout_url": session.url,
    }


def verify_payment(session_id: str) -> Optional[dict]:
    """Fetch a Stripe Checkout session and return its key fields.

    Returns dict {payment_status, filing_id, user_id, amount_total} or
    None if the session cannot be retrieved.

    payment_status reflects Stripe's value (e.g. 'paid', 'unpaid',
    'no_payment_required'). Caller compares to 'paid' before unlocking.
    """
    if not is_configured():
        raise RuntimeError("Stripe is not configured")
    if not session_id or not isinstance(session_id, str):
        return None

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return None

    metadata = getattr(session, "metadata", None) or {}
    return {
        "payment_status": getattr(session, "payment_status", None),
        "filing_id": metadata.get("filing_id"),
        "user_id": metadata.get("user_id"),
        "amount_total": getattr(session, "amount_total", None),
    }
