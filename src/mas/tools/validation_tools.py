from __future__ import annotations

from typing import Any


def validate_price_offers(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate and categorize scraped price offers.

    Args:
        items: A list of raw scraped offer dictionaries.

    Returns:
        A validation dictionary containing cleaned offers, quality score, and notes.
    """

    seen: set[tuple[str, str, float]] = set()
    validated_items: list[dict[str, Any]] = []
    anomaly_count = 0

    for item in items:
        try:
            store = str(item.get("store", "")).strip()
            title = str(item.get("title", "")).strip() or "Unknown product"
            price = float(item.get("price", 0))
            currency = str(item.get("currency", "LKR")).strip() or "LKR"
        except (TypeError, ValueError):
            anomaly_count += 1
            continue

        if price <= 0 or not store:
            anomaly_count += 1
            continue

        key = (store, title, price)
        if key in seen:
            continue
        seen.add(key)

        validated_items.append(
            {
                "store": store,
                "title": title,
                "price": round(price, 2),
                "currency": currency,
            }
        )

    if not validated_items:
        return {
            "validated_items": [],
            "quality_score": 0.0,
            "category_summary": {"Budget": 0, "Standard": 0, "Premium": 0},
            "validation_notes": (
                "No valid offers were found after validation. "
                f"Anomaly count: {anomaly_count}."
            ),
        }

    average_price = sum(item["price"] for item in validated_items) / len(validated_items)
    lower_bound = average_price * 0.92
    upper_bound = average_price * 1.08
    category_summary = {"Budget": 0, "Standard": 0, "Premium": 0}

    for entry in validated_items:
        price = entry["price"]
        if price <= lower_bound:
            category = "Budget"
        elif price >= upper_bound:
            category = "Premium"
        else:
            category = "Standard"
        entry["category"] = category
        category_summary[category] += 1

    total_items = anomaly_count + len(validated_items)
    quality_score = round(100.0 * len(validated_items) / total_items, 2) if total_items else 0.0
    validation_notes = (
        f"Validated {len(validated_items)} offers with {anomaly_count} anomalies removed. "
        f"Quality score: {quality_score}%."
    )

    return {
        "validated_items": validated_items,
        "quality_score": quality_score,
        "category_summary": category_summary,
        "validation_notes": validation_notes,
    }
