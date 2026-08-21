import unittest

from backend.app.domain import PurchaseIntent
from backend.app.sample_data import sample_products
from backend.app.services.catalogue import CatalogueService


class CatalogueServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = CatalogueService()
        self.products = sample_products()

    def test_detects_critical_catalogue_failures(self):
        analysis = self.service.analyse(self.products)
        codes = {issue["code"] for issue in analysis["issues"]}
        self.assertIn("invalid_price", codes)
        self.assertIn("negative_inventory", codes)
        self.assertIn("duplicate_sku", codes)
        self.assertGreater(analysis["blocked_products"], 0)

    def test_manifest_excludes_blocked_products(self):
        manifest = self.service.manifest(self.products)
        ids = {product["product_id"] for product in manifest["products"]}
        self.assertNotIn("prd_bad_001", ids)
        self.assertNotIn("prd_bad_002", ids)
        self.assertTrue(manifest["synthetic_data"])

    def test_search_is_grounded_in_catalogue(self):
        intent = PurchaseIntent(
            raw_query="black running shoes",
            product_terms=["running", "shoes"],
            color="black",
            size="9",
            max_price_inr=3000,
            city="bengaluru",
        )
        matches = self.service.search(self.products, intent)
        self.assertEqual([product.product_id for product in matches], ["prd_run_001"])

    def test_invalid_price_is_never_searchable(self):
        intent = PurchaseIntent(raw_query="demo", product_terms=["demo"])
        matches = self.service.search(self.products, intent)
        self.assertNotIn("prd_bad_001", {product.product_id for product in matches})

    def test_duplicate_skus_are_reported_for_both_records(self):
        issues = self.service.analyse(self.products)["issues"]
        duplicate_ids = {
            issue["product_id"] for issue in issues if issue["code"] == "duplicate_sku"
        }
        self.assertEqual(duplicate_ids, {"prd_bad_001", "prd_bad_002"})


if __name__ == "__main__":
    unittest.main()

