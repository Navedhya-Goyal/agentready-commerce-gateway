from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Iterable

from ..domain import CatalogueIssue, Product, PurchaseIntent


class CatalogueService:
    required_text_fields = ("sku", "name", "category", "description", "color", "size")

    def analyse(self, products: Iterable[Product]) -> dict:
        products = list(products)
        issues: list[CatalogueIssue] = []
        sku_counts = Counter(product.sku.strip().lower() for product in products if product.sku)

        for product in products:
            for field_name in self.required_text_fields:
                if not str(getattr(product, field_name, "")).strip():
                    issues.append(
                        CatalogueIssue(
                            "high",
                            f"missing_{field_name}",
                            product.product_id,
                            f"Required field '{field_name}' is missing.",
                        )
                    )
            if product.price_inr <= 0:
                issues.append(
                    CatalogueIssue(
                        "critical",
                        "invalid_price",
                        product.product_id,
                        "Price must be greater than zero.",
                    )
                )
            if product.stock < 0:
                issues.append(
                    CatalogueIssue(
                        "critical",
                        "negative_inventory",
                        product.product_id,
                        "Inventory cannot be negative.",
                    )
                )
            if product.return_days < 0:
                issues.append(
                    CatalogueIssue(
                        "high",
                        "invalid_return_window",
                        product.product_id,
                        "Return window cannot be negative.",
                    )
                )
            if not product.delivery_cities:
                issues.append(
                    CatalogueIssue(
                        "high",
                        "missing_delivery_coverage",
                        product.product_id,
                        "At least one supported delivery city is required.",
                    )
                )
            if sku_counts[product.sku.strip().lower()] > 1:
                issues.append(
                    CatalogueIssue(
                        "critical",
                        "duplicate_sku",
                        product.product_id,
                        f"SKU '{product.sku}' is not unique.",
                    )
                )
            if product.offer_percent < 0 or product.offer_percent > 50:
                issues.append(
                    CatalogueIssue(
                        "high",
                        "unsafe_offer",
                        product.product_id,
                        "Offer must be between 0 and 50 percent.",
                    )
                )
            if product.offer_expires_at:
                try:
                    expires = datetime.fromisoformat(product.offer_expires_at)
                    if expires.tzinfo is None:
                        expires = expires.replace(tzinfo=UTC)
                    if expires < datetime.now(UTC):
                        issues.append(
                            CatalogueIssue(
                                "medium",
                                "expired_offer",
                                product.product_id,
                                "Offer has expired and will not be applied.",
                            )
                        )
                except ValueError:
                    issues.append(
                        CatalogueIssue(
                            "high",
                            "invalid_offer_expiry",
                            product.product_id,
                            "Offer expiry is not a valid ISO timestamp.",
                        )
                    )

        weights = {"critical": 12, "high": 7, "medium": 3, "low": 1}
        penalty = sum(weights[issue.severity] for issue in issues)
        readiness_score = max(0, round(100 - (penalty / max(len(products), 1))))
        blocked_ids = sorted(
            {issue.product_id for issue in issues if issue.severity in {"critical", "high"}}
        )
        return {
            "readiness_score": readiness_score,
            "total_products": len(products),
            "ready_products": len(products) - len(blocked_ids),
            "blocked_products": len(blocked_ids),
            "issues": [issue.to_dict() for issue in issues],
        }

    def search(self, products: Iterable[Product], intent: PurchaseIntent) -> list[Product]:
        matches: list[Product] = []
        for product in products:
            if not product.active or product.stock < intent.quantity or product.price_inr <= 0:
                continue
            haystack = f"{product.name} {product.category} {product.description}".lower()
            if intent.product_terms and not any(term in haystack for term in intent.product_terms):
                continue
            if intent.color and product.color.lower() != intent.color.lower():
                continue
            if intent.size and product.size.lower() != intent.size.lower():
                continue
            if intent.max_price_inr and product.price_inr > intent.max_price_inr:
                continue
            supported_cities = [city.lower() for city in product.delivery_cities]
            if intent.city and intent.city.lower() not in supported_cities:
                continue
            matches.append(product)
        return sorted(matches, key=lambda product: (product.price_inr, -product.stock))

    def manifest(self, products: Iterable[Product], merchant_id: str = "merchant_demo") -> dict:
        analysis = self.analyse(products)
        blocked = {
            issue["product_id"]
            for issue in analysis["issues"]
            if issue["severity"] in {"critical", "high"}
        }
        safe_products = [
            product.to_dict() for product in products if product.product_id not in blocked
        ]
        return {
            "manifest_version": f"{merchant_id}:{int(datetime.now(UTC).timestamp())}",
            "merchant_id": merchant_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "synthetic_data": True,
            "products": safe_products,
            "policy": {
                "customer_confirmation_required": True,
                "max_offer_percent": 50,
                "payment_mode": "simulated_payment_link",
            },
        }
