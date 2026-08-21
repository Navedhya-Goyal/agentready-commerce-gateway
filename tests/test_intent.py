import unittest

from backend.app.services.intent import DeterministicIntentProvider


class IntentProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = DeterministicIntentProvider()

    def test_extracts_explicit_constraints(self):
        intent = self.provider.parse(
            "Find black running shoes size 9 under ₹3,000 for delivery to Bangalore"
        )
        self.assertEqual(intent.color, "black")
        self.assertEqual(intent.size, "9")
        self.assertEqual(intent.max_price_inr, 3000)
        self.assertEqual(intent.city, "bengaluru")
        self.assertIn("shoes", intent.product_terms)

    def test_missing_preferences_remain_empty(self):
        intent = self.provider.parse("Show me a shirt")
        self.assertIsNone(intent.color)
        self.assertIsNone(intent.max_price_inr)
        self.assertEqual(intent.quantity, 1)

    def test_quantity_is_bounded(self):
        intent = self.provider.parse("black headphones quantity 900")
        self.assertEqual(intent.quantity, 10)


if __name__ == "__main__":
    unittest.main()

