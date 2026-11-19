import logging
import uuid
from typing import Dict

from .config import settings

logger = logging.getLogger(__name__)

class PaymentError(RuntimeError):
    """Custom exception for payment failures."""

class StripeClient:
    """A minimal mock of Stripe's PaymentIntent API."""

    @staticmethod
    async def process_payment(amount: int, currency: str) -> Dict[str, str]:
        """
        Simulate an async call to Stripe.

        Args:
            amount: Amount in the smallest currency unit (e.g., cents).
            currency: Currency code (e.g., 'usd').

        Returns:
            dict containing ``success`` and a mock ``payment_intent_id``.
        """
        # In real life you'd use `httpx.AsyncClient` to call Stripe.
        # Here we simply log and return a deterministic result.
        logger.info(
            "Processing mock payment: %d %s with key %s",
            amount,
            currency,
            settings.stripe_api_key[:8] + "...",
        )
        # Simulate a possible failure for demonstration
        if amount <= 0:
            raise PaymentError("Invalid payment amount")
        payment_intent_id = f"pi_{uuid.uuid4().hex[:24]}"
        logger.debug("Mock payment succeeded, intent %s", payment_intent_id)
        return {"success": True, "payment_intent_id": payment_intent_id}