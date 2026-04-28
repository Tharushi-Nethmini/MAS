from __future__ import annotations

from src.mas.config import is_offline_mode, settings
from src.mas.agents.prompts import COORDINATOR_SYSTEM_PROMPT
from src.mas.llm import ask_ollama
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.query_tools import extract_product_name, normalize_product_query


def coordinator_agent(state: MASState) -> MASState:
    """Parse user intent and initialize shared state for price comparison."""

    trace_id = state["trace_id"]
    request = state.get("user_request", "")

    product_name = extract_product_name(request)
    normalized_product_query = normalize_product_query(product_name)
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
