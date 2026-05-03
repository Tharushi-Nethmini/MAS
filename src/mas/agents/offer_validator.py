from __future__ import annotations

from src.mas.agents.prompts import PRICE_VALIDATOR_SYSTEM_PROMPT
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.validation_tools import validate_price_offers


def offer_validator_agent(state: MASState) -> MASState:
    """Validate and categorize scraped price offers before analysis."""

    trace_id = state["trace_id"]
    scraped_items = state.get("scraped_items", [])

    validation = validate_price_offers(scraped_items)

    log_event(
        trace_id,
        "tool_call",
        {
            "agent": "OfferValidatorAgent",
            "tool": "validate_price_offers",
            "input": {"scraped_item_count": len(scraped_items)},
            "output": {
                "validated_item_count": len(validation["validated_items"]),
                "quality_score": validation["quality_score"],
            },
        },
    )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "OfferValidatorAgent",
            "system_prompt": PRICE_VALIDATOR_SYSTEM_PROMPT,
            "validation_notes": validation["validation_notes"],
            "quality_score": validation["quality_score"],
            "category_summary": validation["category_summary"],
        },
    )

    return {
        "validated_items": validation["validated_items"],
        "price_quality_score": validation["quality_score"],
        "offer_categories": validation["category_summary"],
        "offer_risk_notes": validation["validation_notes"],
    }
