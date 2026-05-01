from __future__ import annotations

from typing import Any

from src.mas.agents.prompts import RECOMMENDATION_EXPLANATION_SYSTEM_PROMPT
from src.mas.observability.logger import log_event
from src.mas.state import MASState


def _build_options(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build recommendation options from validated offers."""

    if not items:
        return []

    sorted_by_price = sorted(items, key=lambda item: float(item.get("price", 0.0)))
    cheapest = sorted_by_price[0]
    priciest = sorted_by_price[-1]

    return [
        {
            "category": "best_cheapest",
            "store": cheapest.get("store", "N/A"),
            "price": float(cheapest.get("price", 0.0)),
            "reason": "Lowest available validated price.",
        },
        {
            "category": "best_value",
            "store": stateful_store_name(cheapest, priciest),
            "price": stateful_value_price(cheapest, priciest),
            "reason": "Balanced recommendation using validated price range.",
        },
    ]


def stateful_store_name(cheapest: dict[str, Any], priciest: dict[str, Any]) -> str:
    """Choose best-value store using simple midpoint rule."""

    cheap_price = float(cheapest.get("price", 0.0))
    high_price = float(priciest.get("price", cheap_price))
    if high_price <= cheap_price * 1.25:
        return str(cheapest.get("store", "N/A"))
    return str(priciest.get("store", "N/A"))


def stateful_value_price(cheapest: dict[str, Any], priciest: dict[str, Any]) -> float:
    """Choose best-value price to match midpoint rule."""

    cheap_price = float(cheapest.get("price", 0.0))
    high_price = float(priciest.get("price", cheap_price))
    if high_price <= cheap_price * 1.25:
        return round(cheap_price, 2)
    return round(high_price, 2)


def recommendation_explanation_agent(state: MASState) -> MASState:
    """Create recommendation narratives from validated items and analysis."""

    trace_id = state["trace_id"]
    product_name = state.get("product_name", "product")
    validated_items = state.get("validated_items", [])
    options = _build_options(validated_items)

    if options:
        cheapest = next((option for option in options if option["category"] == "best_cheapest"), options[0])
        recommendation_summary = (
            f"For {product_name}, best cheapest option is {cheapest['store']} at "
            f"{cheapest['price']:.2f} LKR. "
            "Use best_value option when you prefer a balanced choice."
        )
    else:
        recommendation_summary = f"No validated offers available to recommend for {product_name}."

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "RecommendationExplanationAgent",
            "system_prompt": RECOMMENDATION_EXPLANATION_SYSTEM_PROMPT,
            "option_count": len(options),
            "recommendation_summary": recommendation_summary,
        },
    )

    return {
        "recommendation_summary": recommendation_summary,
        "recommendation_options": options,
    }
