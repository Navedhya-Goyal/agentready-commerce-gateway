from __future__ import annotations

import hashlib
import uuid

from ..domain import AuditEvent, CommerceSession, Product, WorkflowState
from .catalogue import CatalogueService
from .intent import IntentProvider
from .payments import SimulatedRazorpayAdapter
from .policy import PolicyEngine


class CommerceWorkflow:
    def __init__(
        self,
        products: list[Product],
        intent_provider: IntentProvider,
        catalogue: CatalogueService,
        policy: PolicyEngine,
        payments: SimulatedRazorpayAdapter,
    ):
        self.products = products
        self.intent_provider = intent_provider
        self.catalogue = catalogue
        self.policy = policy
        self.payments = payments
        self.sessions: dict[str, CommerceSession] = {}

    def start(self, query: str) -> CommerceSession:
        intent = self.intent_provider.parse(query)
        session = CommerceSession(
            session_id=f"session_{uuid.uuid4().hex[:12]}",
            state=WorkflowState.REQUEST_RECEIVED,
            intent=intent,
            audit=[AuditEvent("intent_parsed", "Customer request converted to structured intent.")],
        )
        session.matches = self.catalogue.search(self.products, intent)
        if not session.matches:
            session.state = WorkflowState.REJECTED
            session.audit.append(
                AuditEvent("request_rejected", "No policy-eligible catalogue product matched.")
            )
        else:
            session.state = WorkflowState.PRODUCTS_MATCHED
            session.audit.append(
                AuditEvent("products_matched", f"Found {len(session.matches)} eligible product(s).")
            )
        self.sessions[session.session_id] = session
        return session

    def select(self, session_id: str, product_id: str) -> CommerceSession:
        session = self.get(session_id)
        if session.state != WorkflowState.PRODUCTS_MATCHED:
            raise ValueError("Product selection is not allowed in the current workflow state.")
        selected = next((item for item in session.matches if item.product_id == product_id), None)
        if not selected:
            raise ValueError(
                "Selected product was not returned by the controlled catalogue search."
            )
        session.selected_product_id = product_id
        session.policy_decision = self.policy.evaluate(selected, session.intent)
        if not session.policy_decision.allowed:
            session.state = WorkflowState.REJECTED
            session.audit.append(
                AuditEvent(
                    "policy_rejected",
                    " ".join(session.policy_decision.reasons),
                )
            )
        else:
            session.state = WorkflowState.AWAITING_CONFIRMATION
            session.audit.append(
                AuditEvent(
                    "policy_validated",
                    "Price, inventory, offer, delivery and order limits passed.",
                )
            )
        return session

    def confirm(self, session_id: str, confirmed: bool) -> CommerceSession:
        session = self.get(session_id)
        if session.state != WorkflowState.AWAITING_CONFIRMATION:
            raise ValueError("Customer confirmation is not allowed in the current state.")
        if not confirmed:
            session.state = WorkflowState.REJECTED
            session.audit.append(AuditEvent("customer_declined", "Customer declined the proposal."))
            return session
        session.customer_confirmed = True
        session.state = WorkflowState.CONFIRMED
        session.audit.append(AuditEvent("customer_confirmed", "Customer explicitly confirmed."))
        return session

    def execute(self, session_id: str) -> CommerceSession:
        session = self.get(session_id)
        if session.state != WorkflowState.CONFIRMED or not session.customer_confirmed:
            raise ValueError("Execution requires explicit customer confirmation.")
        product = next(
            item for item in self.products if item.product_id == session.selected_product_id
        )
        current_decision = self.policy.evaluate(product, session.intent)
        if not current_decision.allowed:
            session.state = WorkflowState.REJECTED
            session.audit.append(
                AuditEvent("final_validation_failed", " ".join(current_decision.reasons))
            )
            return session
        session.policy_decision = current_decision
        key = hashlib.sha256(
            f"{session.session_id}:{product.product_id}:{current_decision.total_inr}".encode()
        ).hexdigest()
        result = self.payments.create_order_and_link(
            idempotency_key=key,
            session_id=session.session_id,
            product_id=product.product_id,
            amount_inr=current_decision.total_inr,
        )
        session.order_id = result.order_id
        session.state = WorkflowState.ORDER_CREATED
        session.audit.append(AuditEvent("order_created", f"Created {result.order_id}."))
        session.payment_link = result.payment_link
        session.state = WorkflowState.PAYMENT_LINK_CREATED
        session.audit.append(
            AuditEvent(
                "payment_link_created",
                (
                    "Returned existing link idempotently."
                    if result.reused
                    else "Created simulated link."
                ),
            )
        )
        return session

    def get(self, session_id: str) -> CommerceSession:
        if session_id not in self.sessions:
            raise KeyError("Commerce session not found.")
        return self.sessions[session_id]
