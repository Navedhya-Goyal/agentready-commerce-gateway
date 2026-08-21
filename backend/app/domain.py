from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class WorkflowState(str, Enum):
    REQUEST_RECEIVED = "request_received"
    PRODUCTS_MATCHED = "products_matched"
    POLICY_VALIDATED = "policy_validated"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    ORDER_CREATED = "order_created"
    PAYMENT_LINK_CREATED = "payment_link_created"
    REJECTED = "rejected"


@dataclass(slots=True)
class Product:
    product_id: str
    sku: str
    name: str
    category: str
    description: str
    price_inr: int
    stock: int
    color: str
    size: str
    delivery_cities: list[str]
    return_days: int
    active: bool = True
    offer_percent: int = 0
    offer_expires_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PurchaseIntent:
    raw_query: str
    product_terms: list[str] = field(default_factory=list)
    color: str | None = None
    size: str | None = None
    max_price_inr: int | None = None
    city: str | None = None
    quantity: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CatalogueIssue:
    severity: str
    code: str
    product_id: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    reasons: list[str]
    subtotal_inr: int
    discount_inr: int
    delivery_inr: int
    total_inr: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditEvent:
    event_type: str
    detail: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class CommerceSession:
    session_id: str
    state: WorkflowState
    intent: PurchaseIntent
    matches: list[Product] = field(default_factory=list)
    selected_product_id: str | None = None
    policy_decision: PolicyDecision | None = None
    customer_confirmed: bool = False
    order_id: str | None = None
    payment_link: str | None = None
    audit: list[AuditEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "intent": self.intent.to_dict(),
            "matches": [item.to_dict() for item in self.matches],
            "selected_product_id": self.selected_product_id,
            "policy_decision": (
                self.policy_decision.to_dict() if self.policy_decision else None
            ),
            "customer_confirmed": self.customer_confirmed,
            "order_id": self.order_id,
            "payment_link": self.payment_link,
            "audit": [event.to_dict() for event in self.audit],
        }

