from __future__ import annotations

from src.mas.agents.recommendation_explainer import recommendation_explanation_agent


def test_recommendation_explanation_agent_builds_options() -> None:
    state = {
        "trace_id": "recommend-1",
        "product_name": "coconut oil",
        "validated_items": [
            {"store": "StoreA", "title": "A", "price": 300.0, "currency": "LKR"},
            {"store": "StoreB", "title": "B", "price": 250.0, "currency": "LKR"},
        ],
    }

    result = recommendation_explanation_agent(state)

    assert len(result["recommendation_options"]) >= 2
    assert "best cheapest option is StoreB at 250.00 LKR" in result["recommendation_summary"]


def test_recommendation_explanation_agent_handles_empty_items() -> None:
    state = {"trace_id": "recommend-2", "product_name": "soap", "validated_items": []}

    result = recommendation_explanation_agent(state)

    assert result["recommendation_options"] == []
    assert "No validated offers available" in result["recommendation_summary"]
