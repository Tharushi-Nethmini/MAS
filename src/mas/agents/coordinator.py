from __future__ import annotations

import re

from src.mas.config import is_offline_mode, settings
from src.mas.agents.prompts import COORDINATOR_SYSTEM_PROMPT
from src.mas.llm import ask_ollama
from src.mas.observability.logger import log_event
from src.mas.state import MASState


def _extract_product_name(text: str) -> str:
    """Infer product name from free-form user request."""

    normalized = text.strip()
    if not normalized:
        return "coconut"

    patterns = [
        r"compare\s+prices\s+for\s+(.+)",
        r"price\s+of\s+(.+)",
        r"find\s+best\s+deal\s+for\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,")

    return normalized


def coordinator_agent(state: MASState) -> MASState:
    """Parse user intent and initialize shared state for price comparison."""

    trace_id = state["trace_id"]
    request = state.get("user_request", "")

    product_name = _extract_product_name(request)
    normalized_product_query = re.sub(r"\s+", " ", product_name).strip().lower()
    source_urls: list[str] = state.get("source_urls", [])

    if not is_offline_mode():
        try:
            refinement = ask_ollama(
                base_url=settings.ollama_base_url,
                model=state.get("model", settings.default_model),
                system_prompt=COORDINATOR_SYSTEM_PROMPT,
                user_prompt=request,
            )
            normalized_product_query = refinement[:120].strip().lower() or normalized_product_query
        except Exception as exc:  # pragma: no cover
            log_event(
                trace_id,
                "model_error",
                {
                    "agent": "CoordinatorAgent",
                    "message": str(exc)[:200],
                    "action": "using extracted product query fallback",
                },
            )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "CoordinatorAgent",
            "system_prompt": COORDINATOR_SYSTEM_PROMPT,
            "product_name": product_name,
            "normalized_product_query": normalized_product_query,
        },
    )

    return {
        "product_name": product_name,
        "normalized_product_query": normalized_product_query,
        "source_urls": source_urls,
    }
