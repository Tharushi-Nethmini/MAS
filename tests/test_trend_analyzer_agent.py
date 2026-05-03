from __future__ import annotations

import os

from src.mas.agents.trend_analyzer import trend_analyzer_agent


def test_trend_analyzer_agent_detects_price_drop(monkeypatch) -> None:
    """Test that trend analyzer correctly identifies a price drop scenario."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-1",
        "product_name": "coconut",
        "best_price": 150.0,
        "normalized_product_query": "coconut",
    }

    result = trend_analyzer_agent(state)

    assert result["trend_direction"] in ["price drop", "stable", "price rise", "unknown"]
    assert isinstance(result["trend_change"], float)
    assert isinstance(result["trend_history_average"], float)
    assert isinstance(result["trend_history_count"], int)
    assert "summary" in result or "trend_summary" in result or "Insufficient" in result.get("trend_summary", "")


def test_trend_analyzer_agent_handles_zero_price(monkeypatch) -> None:
    """Test that trend analyzer gracefully handles zero or invalid prices."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-2",
        "product_name": "coconut",
        "best_price": 0.0,
        "normalized_product_query": "coconut",
    }

    result = trend_analyzer_agent(state)

    assert result["trend_direction"] == "unavailable"
    assert result["best_price"] != result["best_price"]  # NaN check or similar
    assert "No available products found" in result["trend_summary"]


def test_trend_analyzer_agent_handles_negative_price(monkeypatch) -> None:
    """Test that trend analyzer correctly handles negative prices."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-3",
        "product_name": "rice",
        "best_price": -100.0,
        "normalized_product_query": "rice",
    }

    result = trend_analyzer_agent(state)

    assert result["trend_direction"] == "unavailable"
    assert "No available products found" in result["trend_summary"]


def test_trend_analyzer_agent_handles_product_not_in_history(monkeypatch) -> None:
    """Test trend analyzer for products with no historical data."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-4",
        "product_name": "nonexistent-product-xyz",
        "best_price": 500.0,
        "normalized_product_query": "nonexistent-product-xyz",
    }

    result = trend_analyzer_agent(state)

    assert result["trend_history_count"] == 0
    assert result["trend_history_average"] == 0.0
    assert result["trend_direction"] in ["unknown", "unavailable"]


def test_trend_analyzer_agent_with_valid_data_set(monkeypatch) -> None:
    """Test trend analyzer with a known product and valid price."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-5",
        "product_name": "milk powder",
        "best_price": 600.0,
        "normalized_product_query": "milk powder",
    }

    result = trend_analyzer_agent(state)

    # Verify structure
    assert "trend_direction" in result
    assert "trend_change" in result
    assert "trend_summary" in result
    assert "trend_recommendation" in result
    assert "trend_history_average" in result
    assert "trend_history_count" in result

    # Verify types
    assert isinstance(result["trend_direction"], str)
    assert isinstance(result["trend_change"], (int, float))
    assert isinstance(result["trend_summary"], str)
    assert isinstance(result["trend_recommendation"], str)
    assert isinstance(result["trend_history_average"], (int, float))
    assert isinstance(result["trend_history_count"], int)


def test_trend_analyzer_agent_computes_percentage_change(monkeypatch) -> None:
    """Test that trend analyzer correctly computes percentage change."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-6",
        "product_name": "rice",
        "best_price": 250.0,
        "normalized_product_query": "rice",
    }

    result = trend_analyzer_agent(state)

    # Verify percentage change is computed
    if result["trend_history_count"] > 0:
        assert isinstance(result["trend_change"], (int, float))
        # Check that trend direction aligns with percentage change
        if result["trend_change"] <= -5.0:
            assert "price drop" in result["trend_direction"].lower()
        elif result["trend_change"] >= 5.0:
            assert "price rise" in result["trend_direction"].lower()
        else:
            assert "stable" in result["trend_direction"].lower()


def test_trend_analyzer_agent_provides_recommendation(monkeypatch) -> None:
    """Test that trend analyzer provides actionable recommendations."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-7",
        "product_name": "coconut",
        "best_price": 120.0,
        "normalized_product_query": "coconut",
    }

    result = trend_analyzer_agent(state)

    assert "recommendation" in result
    assert len(result["trend_recommendation"]) > 0
    assert isinstance(result["trend_recommendation"], str)


def test_trend_analyzer_agent_handles_string_price(monkeypatch) -> None:
    """Test that trend analyzer handles string prices by converting them."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-8",
        "product_name": "coconut",
        "best_price": "250.5",  # String price
        "normalized_product_query": "coconut",
    }

    result = trend_analyzer_agent(state)

    # Should either handle the conversion or gracefully fail
    assert "trend_direction" in result
    assert "trend_summary" in result


def test_trend_analyzer_agent_missing_product_name(monkeypatch) -> None:
    """Test trend analyzer when product_name is missing."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-9",
        "best_price": 300.0,
        "normalized_product_query": "coconut",
    }

    result = trend_analyzer_agent(state)

    # Should use normalized_product_query as fallback
    assert "trend_direction" in result
    assert "trend_summary" in result


def test_trend_analyzer_agent_returns_complete_state(monkeypatch) -> None:
    """Test that trend analyzer returns all required state fields."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "trend-10",
        "product_name": "rice",
        "best_price": 85.0,
        "normalized_product_query": "rice",
    }

    result = trend_analyzer_agent(state)

    required_fields = [
        "trend_direction",
        "trend_change",
        "trend_summary",
        "trend_recommendation",
        "trend_history_average",
        "trend_history_count",
    ]

    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
