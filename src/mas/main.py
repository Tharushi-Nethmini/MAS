from __future__ import annotations

import argparse
import uuid

from src.mas.config import is_offline_mode, settings
from src.mas.graph import build_graph
from src.mas.observability.logger import log_event, write_run_summary
from src.mas.state import MASState


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for MAS execution."""

    parser = argparse.ArgumentParser(description="Run local CTSE MAS")
    parser.add_argument("--request", required=True, help="User request for planning")
    parser.add_argument("--model", default=settings.default_model, help="Ollama model name")
    parser.add_argument(
        "--urls",
        default="",
        help="Comma-separated source URLs for live scraping in online mode.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the local MAS pipeline."""

    args = parse_args()
    trace_id = uuid.uuid4().hex[:10]
    source_urls = [item.strip() for item in args.urls.split(",") if item.strip()]

    initial_state: MASState = {
        "trace_id": trace_id,
        "model": args.model,
        "user_request": args.request,
        "source_urls": source_urls,
        "meta": {"offline_mode": is_offline_mode()},
    }

    log_event(trace_id, "run_start", {"request": args.request, "model": args.model})

    graph = build_graph()
    result = graph.invoke(initial_state)

    summary_path = write_run_summary(
        trace_id,
        {
            "model": args.model,
            "request": args.request,
            "product_name": result.get("product_name", ""),
            "best_store": result.get("best_store", ""),
            "best_price": result.get("best_price", ""),
            "saved_report_path": result.get("saved_report_path", ""),
            "saved_report_pdf_path": result.get("saved_report_pdf_path", ""),
        },
    )

    log_event(
        trace_id,
        "run_end",
        {
            "saved_report_path": result.get("saved_report_path", ""),
            "product_name": result.get("product_name", ""),
            "best_store": result.get("best_store", ""),
            "best_price": result.get("best_price", ""),
            "saved_report_pdf_path": result.get("saved_report_pdf_path", ""),
            "summary_path": summary_path,
        },
    )

    print("=== MAS Execution Complete ===")
    print(f"Trace ID: {trace_id}")
    print(f"Report (MD): {result.get('saved_report_path', 'not created')}")
    print(f"Report (PDF): {result.get('saved_report_pdf_path', 'not created')}")
    print(f"Run Summary: {summary_path}")


if __name__ == "__main__":
    main()
