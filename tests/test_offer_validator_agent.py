from __future__ import annotations

from src.mas.agents.offer_validator import offer_validator_agent


def test_offer_validator_agent_filters_invalid_prices() -> None:
    state = {
        "trace_id": "validator-1",
        "scraped_items": [
            {"store": "StoreA", "title": "Coconut", "price": 120, "currency": "LKR"},
            {"store": "StoreB", "title": "Coconut", "price": -5, "currency": "LKR"},
            {"store": "StoreC", "title": "Coconut", "price": "bad", "currency": "LKR"},
        ],
    }

    result = offer_validator_agent(state)

    assert result["price_quality_score"] == 33.33
    assert len(result["validated_items"]) == 1
    assert result["offer_categories"]["Standard"] == 1
    assert "anomalies removed" in result["offer_risk_notes"].lower()


def test_offer_validator_agent_categorizes_offers() -> None:
    state = {
        "trace_id": "validator-2",
        "scraped_items": [
            {"store": "StoreA", "title": "Coconut", "price": 100, "currency": "LKR"},
            {"store": "StoreB", "title": "Coconut", "price": 110, "currency": "LKR"},
            {"store": "StoreC", "title": "Coconut", "price": 130, "currency": "LKR"},
        ],
    }

    result = offer_validator_agent(state)

    assert result["offer_categories"]["Budget"] >= 0
    assert result["offer_categories"]["Standard"] >= 0
    assert result["offer_categories"]["Premium"] >= 0
    assert all("category" in item for item in result["validated_items"])
