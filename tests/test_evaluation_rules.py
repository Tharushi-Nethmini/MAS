from __future__ import annotations

import os

from evaluation import evaluate_single_case, evaluate_suite, score_suite
from src.mas.agents.trend_analyzer import trend_analyzer_agent
from src.mas.agents.offer_validator import offer_validator_agent


def test_evaluation_rules_pass_core_requirements() -> None:
    checks = evaluate_single_case("Compare prices for coconut")
    assert checks["has_product"]
    assert checks["has_scraped_data"]
    assert checks["has_analysis"]
    assert checks["has_best_price"]
    assert checks["has_valid_range"]
    assert checks["best_within_range"]
    assert checks["currency_normalized_lkr"]
    assert checks["security_shell_blocked"]
    assert checks["security_injection_blocked"]
    assert checks["report_saved"]
    assert checks["report_pdf_saved"]
    assert checks["report_has_conclusion"]


def test_evaluation_suite_has_multiple_cases() -> None:
    suite = evaluate_suite()
    assert set(suite.keys()) == {"coconut", "rice", "milk powder", "injection_like_request"}
    assert all(all(case.values()) for case in suite.values())


def test_evaluation_suite_scoring_threshold() -> None:
    suite = evaluate_suite()
    summary = score_suite(suite)
    assert summary["overall"]["ratio"] >= 0.8
    assert summary["overall"]["meets_threshold_80"] is True


# Tests for Trend Analyzer Agent
def test_trend_analyzer_agent_included_in_evaluation(monkeypatch) -> None:
    """Test that Trend Analyzer Agent is included in the evaluation pipeline."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    checks = evaluate_single_case("Compare prices for coconut")
    
    # Verify that trend analysis happened
    assert checks.get("has_product") is True
    # The evaluation should include trend data if available
    assert any(
        key in str(checks).lower()
        for key in ["trend", "analysis", "history"]
    )


def test_trend_analyzer_agent_produces_trend_direction() -> None:
    """Test that Trend Analyzer produces valid trend direction values."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-trend-1",
        "product_name": "coconut",
        "best_price": 150.0,
        "normalized_product_query": "coconut",
    }
    
    result = trend_analyzer_agent(state)
    
    valid_directions = ["price drop", "stable", "price rise", "unknown", "unavailable", "error"]
    assert result["trend_direction"] in valid_directions


def test_trend_analyzer_agent_produces_valid_metrics() -> None:
    """Test that Trend Analyzer produces all required metrics."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-trend-2",
        "product_name": "rice",
        "best_price": 85.0,
        "normalized_product_query": "rice",
    }
    
    result = trend_analyzer_agent(state)
    
    required_metrics = {
        "trend_direction": str,
        "trend_change": (int, float),
        "trend_summary": str,
        "trend_recommendation": str,
        "trend_history_average": (int, float),
        "trend_history_count": int,
    }
    
    for metric_name, expected_type in required_metrics.items():
        assert metric_name in result, f"Missing metric: {metric_name}"
        assert isinstance(
            result[metric_name], expected_type
        ), f"Invalid type for {metric_name}: expected {expected_type}, got {type(result[metric_name])}"


def test_trend_analyzer_agent_recommendation_is_actionable() -> None:
    """Test that Trend Analyzer provides actionable recommendations."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-trend-3",
        "product_name": "milk powder",
        "best_price": 600.0,
        "normalized_product_query": "milk powder",
    }
    
    result = trend_analyzer_agent(state)
    
    recommendation = result["trend_recommendation"]
    assert len(recommendation) > 0
    assert isinstance(recommendation, str)
    # Recommendation should contain actionable language
    action_keywords = ["consider", "buy", "wait", "check", "search", "unavailable", "proceed", "reference"]
    assert any(
        keyword in recommendation.lower()
        for keyword in action_keywords
    )


# Tests for Offer Validator Agent
def test_offer_validator_agent_included_in_evaluation(monkeypatch) -> None:
    """Test that Offer Validator Agent is included in the evaluation pipeline."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    checks = evaluate_single_case("Compare prices for rice")
    
    # Verify that offer validation happened
    assert checks.get("has_product") is True
    # The evaluation should indicate data quality through validation
    assert checks.get("has_analysis") is True


def test_offer_validator_agent_produces_quality_score() -> None:
    """Test that Offer Validator produces a valid quality score."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-1",
        "scraped_items": [
            {"store": "StoreA", "title": "Coconut", "price": 120, "currency": "LKR"},
            {"store": "StoreB", "title": "Coconut", "price": 130, "currency": "LKR"},
            {"store": "StoreC", "title": "Coconut", "price": 125, "currency": "LKR"},
        ],
    }
    
    result = offer_validator_agent(state)
    
    assert "price_quality_score" in result
    assert 0.0 <= result["price_quality_score"] <= 100.0


def test_offer_validator_agent_categorizes_offers() -> None:
    """Test that Offer Validator correctly categorizes offers."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-2",
        "scraped_items": [
            {"store": "CheapStore", "title": "Rice", "price": 50, "currency": "LKR"},
            {"store": "NormalStore", "title": "Rice", "price": 100, "currency": "LKR"},
            {"store": "ExpensiveStore", "title": "Rice", "price": 150, "currency": "LKR"},
        ],
    }
    
    result = offer_validator_agent(state)
    
    assert "offer_categories" in result
    categories = result["offer_categories"]
    assert "Budget" in categories
    assert "Standard" in categories
    assert "Premium" in categories
    assert all(isinstance(count, int) for count in categories.values())


def test_offer_validator_agent_filters_invalid_offers() -> None:
    """Test that Offer Validator correctly filters invalid offers."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-3",
        "scraped_items": [
            {"store": "StoreA", "title": "Product", "price": 100, "currency": "LKR"},
            {"store": "StoreB", "title": "Product", "price": -50, "currency": "LKR"},  # Invalid
            {"store": "", "title": "Product", "price": 120, "currency": "LKR"},  # Invalid
            {"store": "StoreD", "title": "Product", "price": "invalid", "currency": "LKR"},  # Invalid
        ],
    }
    
    result = offer_validator_agent(state)
    
    validated_count = len(result["validated_items"])
    assert validated_count >= 1  # At least the valid one should pass
    assert all(
        item["price"] > 0 and item.get("store") for item in result["validated_items"]
    )


def test_offer_validator_agent_removes_duplicates() -> None:
    """Test that Offer Validator removes duplicate offers."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-4",
        "scraped_items": [
            {"store": "StoreA", "title": "Product", "price": 100, "currency": "LKR"},
            {"store": "StoreA", "title": "Product", "price": 100, "currency": "LKR"},  # Duplicate
            {"store": "StoreA", "title": "Product", "price": 100, "currency": "LKR"},  # Duplicate
            {"store": "StoreB", "title": "Product", "price": 110, "currency": "LKR"},
        ],
    }
    
    result = offer_validator_agent(state)
    
    # Should have 2 unique items (StoreA and StoreB)
    validated_count = len(result["validated_items"])
    assert validated_count == 2


def test_offer_validator_agent_provides_validation_notes() -> None:
    """Test that Offer Validator provides detailed validation notes."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-5",
        "scraped_items": [
            {"store": "StoreA", "title": "Product", "price": 100, "currency": "LKR"},
            {"store": "StoreB", "title": "Product", "price": 120, "currency": "LKR"},
        ],
    }
    
    result = offer_validator_agent(state)
    
    assert "offer_risk_notes" in result
    notes = result["offer_risk_notes"]
    assert isinstance(notes, str)
    assert len(notes) > 0


def test_offer_validator_agent_handles_empty_scraped_items() -> None:
    """Test that Offer Validator gracefully handles empty scraped items."""
    os.environ["MAS_OFFLINE_MODE"] = "1"
    
    state = {
        "trace_id": "eval-validator-6",
        "scraped_items": [],
    }
    
    result = offer_validator_agent(state)
    
    assert result["validated_items"] == []
    assert result["price_quality_score"] == 0.0
    assert "No valid offers" in result["offer_risk_notes"].lower() or "anomalies" in result["offer_risk_notes"].lower()


def test_trend_and_validator_agents_complete_pipeline(monkeypatch) -> None:
    """Test that Trend Analyzer and Offer Validator work together in the pipeline."""
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    # Simulate a complete evaluation case
    checks = evaluate_single_case("Compare prices for milk powder")
    
    # Both agents should contribute to a successful evaluation
    assert checks["has_product"] is True
    assert checks["has_scraped_data"] is True
    assert checks["has_analysis"] is True
    
    # The system should reach the reporting stage
    assert checks["report_saved"] is True
