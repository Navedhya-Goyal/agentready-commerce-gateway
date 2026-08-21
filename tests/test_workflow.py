import unittest

from backend.app.domain import WorkflowState
from backend.app.sample_data import sample_products
from backend.app.services.catalogue import CatalogueService
from backend.app.services.intent import DeterministicIntentProvider
from backend.app.services.payments import SimulatedRazorpayAdapter
from backend.app.services.policy import PolicyEngine
from backend.app.services.workflow import CommerceWorkflow


class CommerceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.payments = SimulatedRazorpayAdapter()
        self.workflow = CommerceWorkflow(
            products=sample_products(),
            intent_provider=DeterministicIntentProvider(),
            catalogue=CatalogueService(),
            policy=PolicyEngine(),
            payments=self.payments,
        )

    def test_complete_happy_path(self):
        session = self.workflow.start(
            "black running shoes size 9 under ₹3,000 for Bengaluru"
        )
        self.assertEqual(session.state, WorkflowState.PRODUCTS_MATCHED)
        session = self.workflow.select(session.session_id, "prd_run_001")
        self.assertEqual(session.state, WorkflowState.AWAITING_CONFIRMATION)
        session = self.workflow.confirm(session.session_id, True)
        self.assertEqual(session.state, WorkflowState.CONFIRMED)
        session = self.workflow.execute(session.session_id)
        self.assertEqual(session.state, WorkflowState.PAYMENT_LINK_CREATED)
        self.assertTrue(session.order_id.startswith("order_sim_"))
        self.assertIn("example.invalid", session.payment_link)

    def test_execution_without_confirmation_is_blocked(self):
        session = self.workflow.start("black running shoes size 9 under 3000 in Bengaluru")
        session = self.workflow.select(session.session_id, "prd_run_001")
        with self.assertRaisesRegex(ValueError, "explicit customer confirmation"):
            self.workflow.execute(session.session_id)

    def test_out_of_catalogue_selection_is_blocked(self):
        session = self.workflow.start("black running shoes size 9 under 3000 in Bengaluru")
        with self.assertRaisesRegex(ValueError, "controlled catalogue search"):
            self.workflow.select(session.session_id, "prd_headphone_001")

    def test_impossible_request_refuses_to_invent_product(self):
        session = self.workflow.start("red running shoes size 12 under 500 in Delhi")
        self.assertEqual(session.state, WorkflowState.REJECTED)
        self.assertEqual(session.matches, [])

    def test_payment_adapter_is_idempotent(self):
        first = self.payments.create_order_and_link("same-key", "s1", "p1", 1000)
        second = self.payments.create_order_and_link("same-key", "s1", "p1", 1000)
        self.assertEqual(first.order_id, second.order_id)
        self.assertTrue(second.reused)


if __name__ == "__main__":
    unittest.main()

