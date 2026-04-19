from __future__ import annotations

from src.mas.config import settings
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.public_api import scrape_prices


def research_agent(state: MASState) -> MASState:
    """Collect product prices using scraping tool across sources."""

    trace_id = state["trace_id"]
    product_name = state.get("product_name", "coconut")
    source_urls = state.get("source_urls", [])

    try:
        scraped_items = scrape_prices(
            product_name=product_name,
            source_urls=source_urls,
            offline_mode=settings.offline_mode,
        )
        log_event(
            trace_id,
            "tool_call",
            {
                "agent": "WebScraperAgent",
                "tool": "scrape_prices",
                "input": {"product_name": product_name, "source_urls": source_urls},
                "output_count": len(scraped_items),
            },
        )
    except Exception as exc:
        scraped_items = []
        log_event(
            trace_id,
            "tool_call",
            {
                "agent": "WebScraperAgent",
                "tool": "scrape_prices",
                "error": str(exc),
            },
        )

    research_notes = (
        f"Collected {len(scraped_items)} price entries for '{product_name}'."
    )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "WebScraperAgent",
            "scraped_item_count": len(scraped_items),
            "research_notes": research_notes,
        },
    )
    return {"scraped_items": scraped_items, "research_notes": research_notes}
