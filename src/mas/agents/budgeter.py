from __future__ import annotations

from src.mas.agents.prompts import PRICE_ANALYZER_SYSTEM_PROMPT
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.price_tools import analyze_prices


def budget_agent(state: MASState) -> MASState:
    """Analyze scraped prices and derive best offer plus summary metrics."""

    trace_id = state["trace_id"]
    product_name = state.get("product_name", "product")
    items = state.get("validated_items", state.get("scraped_items", []))
    quality_score = state.get("price_quality_score")

    if not items:
        summary = f"No available products found for '{product_name}'. Price analysis was skipped."
        analysis = {
            "best_store": "N/A",
            "best_price": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
            "average_price": 0.0,
        }
        budget_plan = summary
        log_event(
            trace_id,
            "agent_output",
            {
                "agent": "PriceAnalyzerAgent",
                "system_prompt": PRICE_ANALYZER_SYSTEM_PROMPT,
                "budget_plan": budget_plan,
                "best_store": analysis["best_store"],
                "best_price": analysis["best_price"],
            },
        )
        return {
            "budget_plan": budget_plan,
            "analysis_summary": budget_plan,
            "best_store": analysis["best_store"],
            "best_price": analysis["best_price"],
            "min_price": analysis["min_price"],
            "max_price": analysis["max_price"],
            "average_price": analysis["average_price"],
        }

    try:
        analysis = analyze_prices(items)
        summary = (
            f"Price analysis for {product_name}: best {analysis['best_price']:.2f} LKR "
            f"at {analysis['best_store']}. Range {analysis['min_price']:.2f} - "
            f"{analysis['max_price']:.2f} LKR, average {analysis['average_price']:.2f} LKR."
        )
        if quality_score is not None:
            summary += f" Data quality score: {quality_score:.2f}% valid."
    except Exception as exc:
        analysis = {
            "best_store": "N/A",
            "best_price": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
            "average_price": 0.0,
        }
        summary = f"Price analysis failed for {product_name}: {exc}"

    budget_plan = summary

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "PriceAnalyzerAgent",
            "system_prompt": PRICE_ANALYZER_SYSTEM_PROMPT,
            "budget_plan": budget_plan,
            "best_store": analysis["best_store"],
            "best_price": analysis["best_price"],
        },
    )
    return {
        "budget_plan": budget_plan,
        "analysis_summary": budget_plan,
        "best_store": analysis["best_store"],
        "best_price": analysis["best_price"],
        "min_price": analysis["min_price"],
        "max_price": analysis["max_price"],
        "average_price": analysis["average_price"],
    }
