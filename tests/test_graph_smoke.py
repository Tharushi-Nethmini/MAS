from __future__ import annotations

import os

from src.mas.graph import build_graph
from src.mas.state import MASState


def test_graph_smoke_runs_end_to_end(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    graph = build_graph()
    state: MASState = {
        "trace_id": "smoke123",
        "model": "llama3:8b",
        "user_request": "Compare prices for coconut",
    }

    result = graph.invoke(state)

    assert "product_name" in result
    assert "best_store" in result
    assert "best_price" in result
    assert "final_report" in result
    assert "saved_report_path" in result


def test_graph_reports_no_available_products_for_unknown_dataset_item(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    graph = build_graph()
    state: MASState = {
        "trace_id": "smoke-empty",
        "model": "llama3:8b",
        "user_request": "Compare prices for product-that-does-not-exist-xyz",
    }

    result = graph.invoke(state)

    assert result["scraped_items"] == []
    assert result["product_available"] is False
    assert result["best_store"] == "N/A"
    assert result["best_price"] == 0.0
    assert "No available products found" in result["research_notes"]
    assert "No available products found" in result["final_report"]
