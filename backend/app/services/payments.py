from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(slots=True)
class PaymentResult:
    order_id: str
    payment_link: str
    reused: bool


class SimulatedRazorpayAdapter:
    """Idempotent sandbox adapter. It never moves money or contacts a customer."""

    def __init__(self):
        self._executions: dict[str, PaymentResult] = {}

    def create_order_and_link(
        self,
        idempotency_key: str,
        session_id: str,
        product_id: str,
        amount_inr: int,
    ) -> PaymentResult:
        if idempotency_key in self._executions:
            existing = self._executions[idempotency_key]
            return PaymentResult(existing.order_id, existing.payment_link, True)
        digest = hashlib.sha256(
            f"{idempotency_key}:{session_id}:{product_id}:{amount_inr}".encode()
        ).hexdigest()[:14]
        result = PaymentResult(
            order_id=f"order_sim_{digest}",
            payment_link=f"https://example.invalid/pay/plink_sim_{digest}",
            reused=False,
        )
        self._executions[idempotency_key] = result
        return result

