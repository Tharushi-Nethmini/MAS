from __future__ import annotations

import re


def extract_product_name(text: str) -> str:
    """Extract a product name from a free-form user request.

    Falls back to a default product when the input is empty.
    """

    normalized = text.strip()
    if not normalized:
        return "coconut"

    patterns = [
        r"compare\s+prices\s+for\s+(.+)",
        r"price\s+of\s+(.+)",
        r"find\s+best\s+deal\s+for\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,")

    return normalized


def normalize_product_query(product_name: str) -> str:
    """Normalize a product string for downstream scraping and matching."""

    return re.sub(r"\s+", " ", product_name).strip().lower()
