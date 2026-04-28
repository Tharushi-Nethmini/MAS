from __future__ import annotations

import os

from src.mas.agents.coordinator import coordinator_agent


def test_coordinator_agent_extracts_product_name(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "coord-1",
        "model": "llama3:8b",
        "user_request": "Compare prices for coconut",
        "source_urls": ["https://example.com"],
    }

    result = coordinator_agent(state)

    assert result["product_name"].lower() == "coconut"
    assert result["normalized_product_query"] == "coconut"
    assert result["source_urls"] == ["https://example.com"]


def test_coordinator_agent_uses_fallback_for_empty_request(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "coord-2",
        "model": "llama3:8b",
        "user_request": "",
    }

    result = coordinator_agent(state)

    assert result["product_name"] == "coconut"
    assert result["normalized_product_query"] == "coconut"


def test_coordinator_agent_normalizes_spacing_and_case(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "coord-3",
        "model": "llama3:8b",
        "user_request": "   CoConut   Milk  ",
    }

    result = coordinator_agent(state)

    assert result["product_name"] == "CoConut   Milk"
    assert result["normalized_product_query"] == "coconut milk"
