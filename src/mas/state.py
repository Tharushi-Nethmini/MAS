from __future__ import annotations

from typing import Any, TypedDict


class MASState(TypedDict, total=False):
    """Shared global state passed across all agents."""

    trace_id: str
    model: str
    user_request: str
    product_name: str
    normalized_product_query: str
    source_urls: list[str]
    scraped_items: list[dict[str, Any]]
    validated_items: list[dict[str, Any]]
    validation_notes: str
    analysis_summary: str
    best_price: float
    best_store: str
    min_price: float
    max_price: float
    average_price: float
    recommendation_summary: str
    recommendation_options: list[dict[str, Any]]
    report_notes: str
    final_report: str
    saved_report_path: str
    saved_report_pdf_path: str
    meta: dict[str, Any]
