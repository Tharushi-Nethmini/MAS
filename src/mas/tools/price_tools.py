from __future__ import annotations

from typing import Any


def analyze_prices(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute min/max/average and best store from scraped item prices.

    Args:
        items: Scraped item dictionaries. Each item must include `store` and `price`.

    Returns:
        A summary dictionary with computed statistics and best offer details.

    Raises:
        ValueError: If no valid prices are available.
    """

    valid: list[dict[str, Any]] = []
    for item in items:
        try:
            store = str(item["store"])
            price = float(item["price"])
        except (KeyError, TypeError, ValueError):
            continue
        if price > 0:
            valid.append({"store": store, "price": round(price, 2)})

    if not valid:
        raise ValueError("No valid prices available for analysis.")

    min_item = min(valid, key=lambda entry: entry["price"])
    max_item = max(valid, key=lambda entry: entry["price"])
    avg_price = round(sum(entry["price"] for entry in valid) / len(valid), 2)

    return {
        "best_store": min_item["store"],
        "best_price": min_item["price"],
        "min_price": min_item["price"],
        "max_price": max_item["price"],
        "average_price": avg_price,
        "sample_size": len(valid),
    }
