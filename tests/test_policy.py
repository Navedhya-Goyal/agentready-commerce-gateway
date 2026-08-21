import unittest

from backend.app.domain import Product, PurchaseIntent
from backend.app.sample_data import sample_products
from backend.app.services.policy import PolicyEngine


class PolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngine(max_order_value_inr=50_000)
        self.product = sample_products()[0]

    def test_valid_order_is_allowed_and_calculated_deterministically(self):
        intent = PurchaseIntent(raw_query="shoes", quantity=1, city="bengaluru")
        decision = self.engine.evaluate(self.product, intent)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.subtotal_inr, 2799)
        self.assertEqual(decision.discount_inr, 280)
        self.assertEqual(decision.total_inr, 2519)

    def test_unsupported_delivery_is_rejected(self):
        intent = PurchaseIntent(raw_query="shoes", quantity=1, city="pune")
        decision = self.engine.evaluate(self.product, intent)
        self.assertFalse(decision.allowed)
        self.assertIn("Delivery is not supported for the requested city.", decision.reasons)

    def test_unsafe_offer_is_rejected(self):
        unsafe = Product(
            product_id="unsafe",
            sku="UNSAFE",
            name="Unsafe",
            category="demo",
            description="Unsafe discount",
            price_inr=1000,
            stock=10,
            color="black",
            size="m",
            delivery_cities=["bengaluru"],
            return_days=7,
            offer_percent=90,
        )
        decision = self.engine.evaluate(unsafe, PurchaseIntent(raw_query="demo"))
        self.assertFalse(decision.allowed)
        self.assertIn("Offer exceeds the merchant's 50 percent safety limit.", decision.reasons)


if __name__ == "__main__":
    unittest.main()

