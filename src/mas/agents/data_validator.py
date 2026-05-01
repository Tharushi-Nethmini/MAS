from __future__ import annotations

from typing import Any

from .prompts import DATA_VALIDATION_SYSTEM_PROMPT
from ..observability.logger import log_event
from ..state import MASState


def _normalize_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Validate and normalize a single scraped offer record."""

    try:
        store = str(item.get("store", "")).strip()
        title = str(item.get("title", "")).strip()
        price = float(item.get("price"))
        currency = str(item.get("currency", "LKR")).strip().upper() or "LKR"
    except (TypeError, ValueError):
        return None

    if not store or price <= 0:
        return None

    return {
        "store": store,
        "title": title or "N/A",
        "price": round(price, 2),
        "currency": currency,
    }


def data_validation_agent(state: MASState) -> MASState:
    """Clean, validate, and deduplicate scraped price offers."""

    trace_id = state["trace_id"]
    items = state.get("scraped_items", [])
    validated: list[dict[str, Any]] = []
    seen: set[tuple[str, float, str]] = set()

    for item in items:
        normalized = _normalize_item(item)
        if not normalized:
            continue
        dedupe_key = (normalized["store"], normalized["price"], normalized["currency"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        validated.append(normalized)

    validation_notes = (
        f"Validated {len(validated)} offers from {len(items)} scraped records."
    )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "DataValidationAgent",
            "system_prompt": DATA_VALIDATION_SYSTEM_PROMPT,
            "input_count": len(items),
            "validated_count": len(validated),
            "validation_notes": validation_notes,
        },
    )

    return {
        "validated_items": validated,
        "validation_notes": validation_notes,
    }
