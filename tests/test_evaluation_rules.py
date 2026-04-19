from __future__ import annotations

from evaluation import evaluate_single_case, evaluate_suite


def test_evaluation_rules_pass_core_requirements() -> None:
    checks = evaluate_single_case("Compare prices for coconut")
    assert checks["has_product"]
    assert checks["has_scraped_data"]
    assert checks["has_analysis"]
    assert checks["has_best_price"]
    assert checks["has_valid_range"]
    assert checks["best_within_range"]
    assert checks["security_shell_blocked"]
    assert checks["report_saved"]


def test_evaluation_suite_has_multiple_cases() -> None:
    suite = evaluate_suite()
    assert set(suite.keys()) == {"coconut", "rice", "milk powder"}
    assert all(all(case.values()) for case in suite.values())
