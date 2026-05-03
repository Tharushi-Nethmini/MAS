from __future__ import annotations

from src.mas.agents.prompts import TREND_ANALYZER_SYSTEM_PROMPT
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.trend_tools import compute_price_trend


def trend_analyzer_agent(state: MASState) -> MASState:
    """Analyze current prices against historical trends in the local dataset."""

    trace_id = state["trace_id"]
    product_name = state.get("product_name", state.get("normalized_product_query", ""))
    best_price = state.get("best_price", 0.0)

    try:
        current_price = float(best_price)
    except (TypeError, ValueError):
        current_price = 0.0

    if current_price <= 0.0:
        trend = {
            "trend_direction": "unavailable",
            "trend_change": 0.0,
            "trend_summary": f"No available products found for '{product_name}'. Trend analysis was skipped.",
            "trend_recommendation": "Search for another product or update the dataset with this product.",
            "trend_history_average": 0.0,
            "trend_history_count": 0,
        }
        log_event(
            trace_id,
            "agent_output",
            {
                "agent": "TrendAnalyzerAgent",
                "system_prompt": TREND_ANALYZER_SYSTEM_PROMPT,
                "trend_summary": trend["trend_summary"],
                "trend_recommendation": trend["trend_recommendation"],
                "trend_direction": trend["trend_direction"],
            },
        )
        return trend

    try:
        trend = compute_price_trend(product_name=product_name, current_price=current_price)
    except Exception as exc:
        trend = {
            "trend_direction": "error",
            "trend_change": 0.0,
            "trend_summary": f"Trend analysis failed: {exc}",
            "trend_recommendation": "Review scraped prices and retry trend analysis.",
            "trend_history_average": 0.0,
            "trend_history_count": 0,
        }

    log_event(
        trace_id,
        "tool_call",
        {
            "agent": "TrendAnalyzerAgent",
            "tool": "compute_price_trend",
            "input": {"product_name": product_name, "best_price": best_price},
            "output": {
                "trend_direction": trend["trend_direction"],
                "trend_change": trend["trend_change"],
                "trend_history_count": trend["trend_history_count"],
            },
        },
    )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "TrendAnalyzerAgent",
            "system_prompt": TREND_ANALYZER_SYSTEM_PROMPT,
            "trend_summary": trend["trend_summary"],
            "trend_recommendation": trend["trend_recommendation"],
            "trend_direction": trend["trend_direction"],
        },
    )

    return {
        "trend_direction": trend["trend_direction"],
        "trend_change": trend["trend_change"],
        "trend_summary": trend["trend_summary"],
        "trend_recommendation": trend["trend_recommendation"],
        "trend_history_average": trend["trend_history_average"],
        "trend_history_count": trend["trend_history_count"],
    }
