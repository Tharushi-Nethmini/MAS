from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.mas.config import settings
from src.mas.observability.logger import log_event
from src.mas.state import MASState
from src.mas.tools.file_tools import save_markdown_file
from src.mas.tools.shell_tools import run_safe_shell


def risk_and_report_agent(state: MASState) -> MASState:
    """Generate the final smart price comparison report and save it."""

    trace_id = state["trace_id"]
    product = state.get("product_name", "Unknown Product")

    shell_snapshot = ""
    try:
        shell_snapshot = run_safe_shell("Get-Date")
        log_event(
            trace_id,
            "tool_call",
            {
                "agent": "ReportGeneratorAgent",
                "tool": "run_safe_shell",
                "input": {"command": "Get-Date"},
                "output": shell_snapshot,
            },
        )
    except Exception as exc:
        shell_snapshot = f"Shell tool failed: {exc}"

    report_notes = (
        "Price availability can change rapidly. Verify stock and delivery costs at checkout. "
        f"Runtime snapshot: {shell_snapshot}."
    )

    scraped_items = state.get("scraped_items", [])
    lines = [
        f"- {entry.get('store', 'unknown')}: {entry.get('price', 'N/A')} {entry.get('currency', '')}".strip()
        for entry in scraped_items
    ]
    item_list = "\n".join(lines) if lines else "- No items scraped"

    report = "\n".join(
        [
            "# AI-Based Smart Price Comparison Report",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()} UTC",
            "",
            "## User Request",
            state.get("user_request", "N/A"),
            "",
            "## Coordinator Output",
            f"Product: {product}",
            f"Normalized Query: {state.get('normalized_product_query', 'N/A')}",
            "",
            "## Web Scraper Output",
            state.get("research_notes", "N/A"),
            item_list,
            "",
            "## Price Analyzer Output",
            state.get("analysis_summary", "N/A"),
            f"Best Store: {state.get('best_store', 'N/A')}",
            f"Best Price: {state.get('best_price', 'N/A')} LKR",
            f"Minimum Price: {state.get('min_price', 'N/A')} LKR",
            f"Maximum Price: {state.get('max_price', 'N/A')} LKR",
            f"Average Price: {state.get('average_price', 'N/A')} LKR",
            "",
            "## Report Generator Notes",
            report_notes,
            "",
            "## Conclusion",
            "Best available offer identified from collected data. Re-check before purchase.",
        ]
    )

    reports_dir = Path(settings.reports_dir)
    path = reports_dir / f"price_report_{trace_id}.md"
    saved_path = save_markdown_file(str(path), report)

    log_event(
        trace_id,
        "tool_call",
        {
            "agent": "ReportGeneratorAgent",
            "tool": "save_markdown_file",
            "input": {"path": str(path)},
            "output": saved_path,
        },
    )

    log_event(
        trace_id,
        "agent_output",
        {
            "agent": "ReportGeneratorAgent",
            "report_notes": report_notes,
            "saved_report_path": saved_path,
        },
    )

    return {
        "report_notes": report_notes,
        "risk_notes": report_notes,
        "final_report": report,
        "saved_report_path": saved_path,
    }
