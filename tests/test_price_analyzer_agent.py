from __future__ import annotations

from src.mas.agents.budgeter import budget_agent


def test_price_analyzer_agent_computes_best_offer() -> None:
    state = {
        "trace_id": "analysis-1",
        "product_name": "coconut",
        "scraped_items": [
            {"store": "StoreA", "price": 200},
            {"store": "StoreB", "price": 150},
            {"store": "StoreC", "price": 175},
        ],
    }

    result = budget_agent(state)

    assert result["best_store"] == "StoreB"
    assert result["best_price"] == 150.0
    assert result["min_price"] == 150.0
    assert result["max_price"] == 200.0
    assert result["average_price"] == 175.0
    assert "best 150.00 LKR" in result["analysis_summary"]


def test_price_analyzer_agent_handles_invalid_items() -> None:
    state = {
        "trace_id": "analysis-2",
        "product_name": "coconut",
        "scraped_items": [
            {"store": "StoreA", "price": "bad"},
            {"store": "StoreB", "price": -5},
            {"store": "StoreC", "price": 111},
        ],
    }

    result = budget_agent(state)

    assert result["best_store"] == "StoreC"
    assert result["best_price"] == 111.0


def test_price_analyzer_agent_handles_all_invalid_prices() -> None:
    state = {
        "trace_id": "analysis-3",
        "product_name": "coconut",
        "scraped_items": [
            {"store": "StoreA", "price": None},
            {"store": "StoreB", "price": "bad"},
            {"store": "StoreC", "price": 0},
        ],
    }

    result = budget_agent(state)

    assert result["best_store"] == "N/A"
    assert result["best_price"] == 0.0
    assert "failed" in result["analysis_summary"].lower()
