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
    product_available: bool
    research_notes: str
    validated_items: list[dict[str, Any]]
    analysis_summary: str
    budget_plan: str
    price_quality_score: float
    best_price: float
    best_store: str
    min_price: float
    max_price: float
    average_price: float
    offer_categories: dict[str, int]
    offer_risk_notes: str
    trend_direction: str
    trend_change: float
    trend_summary: str
    trend_recommendation: str
    trend_history_average: float
    trend_history_count: int
    planning_notes: str
    store_candidates: list[str]
    report_notes: str
    final_report: str
    saved_report_path: str
    saved_report_pdf_path: str
    meta: dict[str, Any]
