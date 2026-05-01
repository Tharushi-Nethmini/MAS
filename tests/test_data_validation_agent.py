from __future__ import annotations

from src.mas.agents.data_validator import data_validation_agent


def test_data_validation_agent_cleans_and_deduplicates() -> None:
    state = {
        "trace_id": "validate-1",
        "scraped_items": [
            {"store": "StoreA", "title": "Item A", "price": 200, "currency": "lkr"},
            {"store": "StoreA", "title": "Item A duplicate", "price": 200, "currency": "LKR"},
            {"store": "StoreB", "title": "Item B", "price": "bad", "currency": "LKR"},
            {"store": "", "title": "Item C", "price": 150, "currency": "LKR"},
            {"store": "StoreC", "title": "Item C", "price": 150, "currency": "LKR"},
        ],
    }

    result = data_validation_agent(state)

    assert len(result["validated_items"]) == 2
    assert result["validated_items"][0]["store"] == "StoreA"
    assert result["validated_items"][0]["currency"] == "LKR"
    assert result["validated_items"][1]["store"] == "StoreC"
