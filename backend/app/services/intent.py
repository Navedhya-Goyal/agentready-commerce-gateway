from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod

from ..domain import PurchaseIntent

KNOWN_COLORS = {"black", "blue", "red", "white", "green", "grey", "gray"}
KNOWN_CITIES = {"bengaluru", "bangalore", "mumbai", "delhi", "ujjain"}
PRODUCT_TERMS = {
    "shoe": "shoes",
    "shoes": "shoes",
    "running": "running",
    "shirt": "shirt",
    "headphone": "headphones",
    "headphones": "headphones",
}


class IntentProvider(ABC):
    @abstractmethod
    def parse(self, query: str) -> PurchaseIntent:
        raise NotImplementedError


class DeterministicIntentProvider(IntentProvider):
    """Reproducible fallback used for demos, tests, and zero-key deployments."""

    def parse(self, query: str) -> PurchaseIntent:
        # Remove digit grouping separators so ₹3,000 remains the numeric value 3000.
        normalized = query.lower().replace(",", "")
        tokens = re.findall(r"[a-zA-Z]+|\d+", normalized)
        color = next((token for token in tokens if token in KNOWN_COLORS), None)
        city = next((token for token in tokens if token in KNOWN_CITIES), None)
        if city == "bangalore":
            city = "bengaluru"

        # A size is transactional data: infer it only when the customer explicitly
        # uses a size label. The previous optional prefix could mistake the "s" in
        # words such as "shoes" for a clothing size.
        size_match = re.search(r"\bsize\s*(\d{1,2}|xs|s|m|l|xl)\b", normalized)
        size = size_match.group(1) if size_match else None

        price_match = re.search(
            r"(?:under|below|maximum|max|less than)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
            normalized,
        )
        max_price = int(price_match.group(1).replace(",", "")) if price_match else None

        quantity_match = re.search(r"(?:quantity|qty)\s*(\d+)", normalized)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        product_terms = sorted({PRODUCT_TERMS[token] for token in tokens if token in PRODUCT_TERMS})

        return PurchaseIntent(
            raw_query=query,
            product_terms=product_terms,
            color=color,
            size=size,
            max_price_inr=max_price,
            city=city,
            quantity=max(1, min(quantity, 10)),
        )


class OpenAIIntentProvider(IntentProvider):
    """Optional provider using Structured Outputs. Imported lazily to keep demo mode free."""

    def __init__(self, model: str):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the 'openai' package to use AI_PROVIDER=openai") from exc
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        self.client = OpenAI()
        self.model = model

    def parse(self, query: str) -> PurchaseIntent:
        schema = {
            "type": "object",
            "properties": {
                "product_terms": {"type": "array", "items": {"type": "string"}},
                "color": {"type": ["string", "null"]},
                "size": {"type": ["string", "null"]},
                "max_price_inr": {"type": ["integer", "null"]},
                "city": {"type": ["string", "null"]},
                "quantity": {"type": "integer"},
            },
            "required": [
                "product_terms",
                "color",
                "size",
                "max_price_inr",
                "city",
                "quantity",
            ],
            "additionalProperties": False,
        }
        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Extract only the customer's explicit shopping constraints. "
                "Return null for missing values and never invent a preference."
            ),
            input=query,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "purchase_intent",
                    "strict": True,
                    "schema": schema,
                }
            },
        )
        payload = json.loads(response.output_text)
        return PurchaseIntent(raw_query=query, **payload)


def build_intent_provider(provider: str, model: str) -> IntentProvider:
    if provider.lower() == "openai":
        return OpenAIIntentProvider(model)
    return DeterministicIntentProvider()
