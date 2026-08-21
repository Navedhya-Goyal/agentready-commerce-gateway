from __future__ import annotations

from datetime import UTC, datetime

from ..domain import PolicyDecision, Product, PurchaseIntent


class PolicyEngine:
    def __init__(self, max_order_value_inr: int = 50_000):
        self.max_order_value_inr = max_order_value_inr

    def evaluate(self, product: Product, intent: PurchaseIntent) -> PolicyDecision:
        reasons: list[str] = []
        quantity = intent.quantity
        subtotal = product.price_inr * quantity

        if not product.active:
            reasons.append("Product is inactive.")
        if product.price_inr <= 0:
            reasons.append("Product price is invalid.")
        if quantity < 1 or quantity > 10:
            reasons.append("Quantity must be between 1 and 10.")
        if product.stock < quantity:
            reasons.append("Insufficient inventory.")
        supported_cities = [city.lower() for city in product.delivery_cities]
        if intent.city and intent.city.lower() not in supported_cities:
            reasons.append("Delivery is not supported for the requested city.")
        if subtotal > self.max_order_value_inr:
            reasons.append("Order value exceeds the merchant's configured limit.")

        discount_percent = 0
        if product.offer_percent:
            if product.offer_percent > 50:
                reasons.append("Offer exceeds the merchant's 50 percent safety limit.")
            elif product.offer_expires_at:
                try:
                    expiry = datetime.fromisoformat(product.offer_expires_at)
                    if expiry.tzinfo is None:
                        expiry = expiry.replace(tzinfo=UTC)
                    if expiry >= datetime.now(UTC):
                        discount_percent = product.offer_percent
                except ValueError:
                    reasons.append("Offer expiry is invalid.")
            else:
                discount_percent = product.offer_percent

        discount = round(subtotal * discount_percent / 100)
        delivery = 0 if subtotal - discount >= 1_000 else 99
        total = subtotal - discount + delivery
        return PolicyDecision(
            allowed=not reasons,
            reasons=reasons,
            subtotal_inr=subtotal,
            discount_inr=discount,
            delivery_inr=delivery,
            total_inr=total,
        )
