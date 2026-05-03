from __future__ import annotations

import os

from src.mas.agents.researcher import research_agent


def test_web_scraper_agent_collects_offline_items(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "scrape-1",
        "product_name": "coconut",
        "source_urls": [],
        "model": "llama3:8b",
    }

    result = research_agent(state)

    assert result["scraped_items"]
    assert len(result["scraped_items"]) >= 3
    assert all(float(item["price"]) > 0 for item in result["scraped_items"])
    assert result["research_notes"].startswith("Collected")


def test_web_scraper_agent_handles_unknown_product_in_offline_mode(monkeypatch) -> None:
    monkeypatch.setenv("MAS_OFFLINE_MODE", "1")
    os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": "scrape-2",
        "product_name": "product-that-does-not-exist-xyz",
        "source_urls": [],
        "model": "llama3:8b",
    }

    result = research_agent(state)

    assert result["scraped_items"] == []
    assert result["product_available"] is False
    assert "No available products found" in result["research_notes"]
