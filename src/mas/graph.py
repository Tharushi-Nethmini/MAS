from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.mas.agents.budgeter import budget_agent
from src.mas.agents.coordinator import coordinator_agent
from src.mas.agents.offer_validator import offer_validator_agent
from src.mas.agents.researcher import research_agent
from src.mas.agents.risk_reporter import risk_and_report_agent
from src.mas.agents.trend_analyzer import trend_analyzer_agent
from src.mas.state import MASState


def build_graph():
    """Build and compile the MAS LangGraph pipeline."""

    workflow = StateGraph(MASState)
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("web_scraper", research_agent)
    workflow.add_node("offer_validator", offer_validator_agent)
    workflow.add_node("price_analyzer", budget_agent)
    workflow.add_node("trend_analyzer", trend_analyzer_agent)
    workflow.add_node("report_generator", risk_and_report_agent)

    workflow.add_edge(START, "coordinator")
    workflow.add_edge("coordinator", "web_scraper")
    workflow.add_edge("web_scraper", "offer_validator")
    workflow.add_edge("offer_validator", "price_analyzer")
    workflow.add_edge("price_analyzer", "trend_analyzer")
    workflow.add_edge("trend_analyzer", "report_generator")
    workflow.add_edge("report_generator", END)

    return workflow.compile()
