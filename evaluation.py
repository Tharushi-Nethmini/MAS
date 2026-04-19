from __future__ import annotations

import os
import uuid

from src.mas.graph import build_graph
from src.mas.state import MASState
from src.mas.tools.shell_tools import run_safe_shell


def evaluate_single_case(request: str) -> dict[str, bool]:
    """Run one scenario and return rule-based quality checks.

    This acts as an automated evaluation harness and can be extended
    with LLM-as-a-Judge later if required.
    """

    os.environ["MAS_OFFLINE_MODE"] = "1"
    graph = build_graph()
    state: MASState = {
        "trace_id": f"eval_{uuid.uuid4().hex[:8]}",
        "model": "llama3:8b",
        "user_request": request,
    }
    result = graph.invoke(state)

    best_price = float(result.get("best_price", 0.0))
    min_price = float(result.get("min_price", 0.0))
    max_price = float(result.get("max_price", 0.0))

    blocked_untrusted_shell = False
    try:
        run_safe_shell("Remove-Item test.txt")
    except ValueError:
        blocked_untrusted_shell = True

    checks = {
        "has_product": bool(result.get("product_name")),
        "has_scraped_data": bool(result.get("scraped_items")),
        "has_analysis": bool(result.get("analysis_summary")),
        "has_best_price": best_price > 0,
        "has_valid_range": min_price > 0 and max_price >= min_price,
        "best_within_range": min_price <= best_price <= max_price,
        "security_shell_blocked": blocked_untrusted_shell,
        "report_saved": bool(result.get("saved_report_path")),
    }
    return checks


def evaluate_suite() -> dict[str, dict[str, bool]]:
    """Run multiple product scenarios for broader reliability checks."""

    scenarios = {
        "coconut": "Compare prices for coconut",
        "rice": "Compare prices for rice",
        "milk powder": "Find best deal for milk powder",
    }
    return {name: evaluate_single_case(prompt) for name, prompt in scenarios.items()}


def main() -> None:
    suite = evaluate_suite()
    total = 0
    passed = 0

    print("=== Evaluation Summary ===")
    for case_name, checks in suite.items():
        print(f"Case: {case_name}")
        for key, value in checks.items():
            print(f"  {key}: {value}")
            total += 1
            passed += int(value)
    print(f"Overall Score: {passed}/{total}")


if __name__ == "__main__":
    main()
