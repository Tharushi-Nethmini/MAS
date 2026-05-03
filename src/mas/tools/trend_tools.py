from __future__ import annotations

from typing import Any

from src.mas.tools.csv_loader import load_product_prices_from_csv


def compute_price_trend(
    product_name: str,
    current_price: float,
    sample_size: int = 20,
) -> dict[str, Any]:
    """Compare the current price against local dataset history.

    Args:
        product_name: Normalized product query string.
        current_price: Current best price in LKR.
        sample_size: Number of historical records to evaluate.

    Returns:
        Trend analysis data including summary, direction, and recommendation.
    """

    if current_price <= 0:
        raise ValueError("Current price must be greater than zero.")

    try:
        historical_items = load_product_prices_from_csv(
            csv_path="data/data.csv",
            products=[product_name] if product_name else None,
            sample_size=sample_size,
        )
    except Exception:
        historical_items = []

    historical_prices = []
    for item in historical_items:
        try:
            price = float(item.get("price", 0))
        except (TypeError, ValueError):
            continue
        if price > 0:
            historical_prices.append(price)

    if not historical_prices:
        return {
            "trend_direction": "unknown",
            "trend_change": 0.0,
            "trend_summary": (
                "Insufficient historical data to compute a price trend." 
                "Proceed with current comparison results."
            ),
            "trend_recommendation": "Use the current best price as the reference point.",
            "trend_history_average": 0.0,
            "trend_history_count": 0,
        }

    history_avg = round(sum(historical_prices) / len(historical_prices), 2)
    change_pct = round(((current_price - history_avg) / history_avg) * 100.0, 2)

    if change_pct <= -5.0:
        direction = "price drop"
        recommendation = "Current price is lower than history; this is a favorable purchase opportunity."
    elif change_pct >= 5.0:
        direction = "price rise"
        recommendation = "Current price is higher than historical average; consider waiting or checking alternative sources."
    else:
        direction = "stable"
        recommendation = "Current price is close to historical average; compare features before deciding."

    summary = (
        f"Current best price {current_price:.2f} LKR is {abs(change_pct):.2f}% "
        f"{'lower' if change_pct < 0 else 'higher' if change_pct > 0 else 'equal'} than the historical average of {history_avg:.2f} LKR."
    )

    return {
        "trend_direction": direction,
        "trend_change": change_pct,
        "trend_summary": summary,
        "trend_recommendation": recommendation,
        "trend_history_average": history_avg,
        "trend_history_count": len(historical_prices),
    }
