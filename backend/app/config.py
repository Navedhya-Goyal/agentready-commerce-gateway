from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    ai_provider: str = os.getenv("AI_PROVIDER", "deterministic")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    max_order_value_inr: int = int(os.getenv("MAX_ORDER_VALUE_INR", "50000"))
    manifest_ttl_minutes: int = int(os.getenv("MANIFEST_TTL_MINUTES", "30"))


settings = Settings()

