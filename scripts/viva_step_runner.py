from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SESSION_FILE = PROJECT_ROOT / "logs" / "viva_session.json"

from src.mas.agents.budgeter import budget_agent
from src.mas.agents.coordinator import coordinator_agent
from src.mas.agents.researcher import research_agent
from src.mas.config import is_offline_mode
from src.mas.graph import build_graph
from src.mas.observability.logger import log_event, write_run_summary
from src.mas.state import MASState


def _input_default(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default


def _read_session_data() -> dict[str, Any]:
    if not SESSION_FILE.exists():
        return {}
    try:
        data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write_session_data(data: dict[str, Any]) -> None:
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_or_create_shared_trace_id(reset: bool = False) -> str:
    data = _read_session_data()

    if reset:
        data.pop("trace_id", None)

    trace_id = data.get("trace_id")
    if isinstance(trace_id, str) and trace_id.strip():
        return trace_id

    trace_id = f"demo_{uuid.uuid4().hex[:8]}"
    data["trace_id"] = trace_id
    _write_session_data(data)
    return trace_id


def _clear_shared_trace_id() -> None:
    data = _read_session_data()
    if "trace_id" in data:
        data.pop("trace_id", None)
        if data:
            _write_session_data(data)
        elif SESSION_FILE.exists():
            SESSION_FILE.unlink()


def _get_last_source_urls() -> list[str]:
    data = _read_session_data()
    urls = data.get("last_source_urls", [])
    if isinstance(urls, list):
        return [str(u).strip() for u in urls if str(u).strip()]
    return []


def _save_last_source_urls(urls: list[str]) -> None:
    data = _read_session_data()
    data["last_source_urls"] = [u.strip() for u in urls if u.strip()]
    _write_session_data(data)


def _get_last_scraped_items() -> list[dict[str, Any]]:
    data = _read_session_data()
    items = data.get("last_scraped_items", [])
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def _save_last_scraped_items(items: list[dict[str, Any]]) -> None:
    data = _read_session_data()
    data["last_scraped_items"] = items
    _write_session_data(data)


def _select_source_urls_for_demo() -> tuple[list[str], bool]:
    """Return offline-only source mode for stable viva demos."""
    return [], True


def run_member_1(trace_id: str) -> None:
    model = "llama3:8b"
    print(f"Trace ID (shared auto): {trace_id}")
    print(f"Model (auto): {model}")
    user_request = _input_default("User request", "Compare prices for coconut")

    state = {
        "trace_id": trace_id,
        "model": model,
        "user_request": user_request,
    }
    print("\n--- Member 1 Output (Coordinator) ---")
    print(json.dumps(coordinator_agent(state), indent=2))


def run_member_2(trace_id: str) -> None:
    model = "llama3:8b"
    print(f"Trace ID (shared auto): {trace_id}")
    print(f"Model (auto): {model}")
    product_name = _input_default("Product name", "coconut")
    source_urls, force_offline = _select_source_urls_for_demo()

    prev_offline = os.getenv("MAS_OFFLINE_MODE")
    if force_offline:
        os.environ["MAS_OFFLINE_MODE"] = "1"

    state = {
        "trace_id": trace_id,
        "model": model,
        "product_name": product_name,
        "source_urls": source_urls,
    }
    print("\n--- Member 2 Output (Web Scraper) ---")
    try:
        result = research_agent(state)
        scraped = result.get("scraped_items", [])
        if isinstance(scraped, list):
            _save_last_scraped_items(scraped)
        print(json.dumps(result, indent=2))
    finally:
        if force_offline:
            if prev_offline is None:
                os.environ.pop("MAS_OFFLINE_MODE", None)
            else:
                os.environ["MAS_OFFLINE_MODE"] = prev_offline


def run_member_3(trace_id: str) -> None:
    print(f"Trace ID (shared auto): {trace_id}")
    product_name = _input_default("Product name", "coconut")

    last_scraped_items = _get_last_scraped_items()
    use_member_2_data = "yes"
    if last_scraped_items:
        use_member_2_data = _input_default("Use Member 2 scraped data? (yes/no)", "yes").lower()

    if last_scraped_items and use_member_2_data in {"yes", "y"}:
        scraped_items = last_scraped_items
    else:
        use_default = _input_default("Use default sample prices? (yes/no)", "yes").lower()
        if use_default in {"yes", "y"}:
            scraped_items = [
                {"store": "Glomark", "price": 120.0},
                {"store": "Keells", "price": 135.5},
                {"store": "Arpico", "price": 110.0},
            ]
        else:
            scraped_items = []
            count = int(_input_default("How many price entries", "3"))
            for idx in range(1, count + 1):
                store = _input_default(f"Entry {idx} store", f"Store{idx}")
                price = float(_input_default(f"Entry {idx} price", "100"))
                scraped_items.append({"store": store, "price": price})

    state = {
        "trace_id": trace_id,
        "product_name": product_name,
        "scraped_items": scraped_items,
    }
    print("\n--- Member 3 Output (Price Analyzer) ---")
    print(json.dumps(budget_agent(state), indent=2))


def run_member_4(trace_id: str) -> None:
    model = "llama3:8b"
    print(f"Trace ID (shared auto): {trace_id}")
    print(f"Model (auto): {model}")
    user_request = _input_default("User request", "Compare prices for coconut")
    source_urls, force_offline = _select_source_urls_for_demo()

    prev_offline = os.getenv("MAS_OFFLINE_MODE")
    if force_offline:
        os.environ["MAS_OFFLINE_MODE"] = "1"

    initial_state: MASState = {
        "trace_id": trace_id,
        "model": model,
        "user_request": user_request,
        "source_urls": source_urls,
        "meta": {"offline_mode": is_offline_mode()},
    }

    try:
        log_event(trace_id, "run_start", {"request": user_request, "model": model})
        graph = build_graph()
        result = graph.invoke(initial_state)

        summary_path = write_run_summary(
            trace_id,
            {
                "model": model,
                "request": user_request,
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

        print("\n--- Member 4 Output (Full Pipeline) ---")
        print("=== MAS Execution Complete ===")
        print(f"Trace ID: {trace_id}")
        print(f"Report (MD): {result.get('saved_report_path', 'not created')}")
        print(f"Report (PDF): {result.get('saved_report_pdf_path', 'not created')}")
        print(f"Run Summary: {summary_path}")
        _clear_shared_trace_id()
        print("Next round will auto-generate a new shared Trace ID.")
    finally:
        if force_offline:
            if prev_offline is None:
                os.environ.pop("MAS_OFFLINE_MODE", None)
            else:
                os.environ["MAS_OFFLINE_MODE"] = prev_offline


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive step-by-step runner for viva member demos")
    parser.add_argument(
        "--member",
        choices=["1", "2", "3", "4"],
        help="Member number to run directly. If omitted, menu is shown.",
    )
    parser.add_argument(
        "--new-trace",
        action="store_true",
        help="Generate a new shared trace id for this and subsequent runs.",
    )
    args = parser.parse_args()

    member = args.member
    if not member:
        print("Select member demo to run:")
        print("1. Coordinator Agent")
        print("2. Web Scraper Agent")
        print("3. Price Analyzer Agent")
        print("4. Full Pipeline (Report Generator Demo)")
        member = input("Enter member number (1/2/3/4): ").strip()

    reset_trace = args.new_trace or member == "1"
    shared_trace_id = _get_or_create_shared_trace_id(reset=reset_trace)

    if member == "1":
        run_member_1(shared_trace_id)
    elif member == "2":
        run_member_2(shared_trace_id)
    elif member == "3":
        run_member_3(shared_trace_id)
    elif member == "4":
        run_member_4(shared_trace_id)
    else:
        raise ValueError("Invalid member selection. Use 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
