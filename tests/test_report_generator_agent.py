from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.mas.agents import risk_reporter


def test_report_generator_agent_writes_report_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(risk_reporter, "settings", SimpleNamespace(reports_dir=str(tmp_path)))
    monkeypatch.setattr(risk_reporter, "run_safe_shell", lambda command: "Tue Apr 22 12:00:00 2026")

    state = {
        "trace_id": "report-1",
        "user_request": "Compare prices for coconut",
        "product_name": "coconut",
        "normalized_product_query": "coconut",
        "research_notes": "Collected 3 price entries for 'coconut'.",
        "scraped_items": [
            {"store": "StoreA", "price": 200, "currency": "LKR"},
            {"store": "StoreB", "price": 150, "currency": "LKR"},
        ],
        "analysis_summary": "Price analysis for coconut: best 150.00 LKR at StoreB.",
        "best_store": "StoreB",
        "best_price": 150.0,
        "min_price": 150.0,
        "max_price": 200.0,
        "average_price": 175.0,
    }

    result = risk_reporter.risk_and_report_agent(state)

    md_path = Path(result["saved_report_path"])
    pdf_path = Path(result["saved_report_pdf_path"])

    assert md_path.exists()
    assert pdf_path.exists()
    assert "AI-Based Smart Price Comparison Report" in result["final_report"]
    assert "StoreB" in result["final_report"]
    assert "Tue Apr 22 12:00:00 2026" in result["report_notes"]


def test_report_generator_agent_handles_shell_tool_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(risk_reporter, "settings", SimpleNamespace(reports_dir=str(tmp_path)))

    def _raise_shell_error(_: str) -> str:
        raise RuntimeError("blocked command")

    monkeypatch.setattr(risk_reporter, "run_safe_shell", _raise_shell_error)

    state = {
        "trace_id": "report-2",
        "user_request": "Compare prices for coconut",
        "product_name": "coconut",
        "scraped_items": [{"store": "StoreA", "price": 200, "currency": "LKR"}],
        "analysis_summary": "Price analysis summary.",
        "best_store": "StoreA",
        "best_price": 200.0,
        "min_price": 200.0,
        "max_price": 200.0,
        "average_price": 200.0,
    }

    result = risk_reporter.risk_and_report_agent(state)

    assert Path(result["saved_report_path"]).exists()
    assert Path(result["saved_report_pdf_path"]).exists()
    assert "Shell tool failed" in result["report_notes"]


def test_report_generator_agent_reports_no_available_products(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(risk_reporter, "settings", SimpleNamespace(reports_dir=str(tmp_path)))
    monkeypatch.setattr(risk_reporter, "run_safe_shell", lambda command: "Tue Apr 22 12:00:00 2026")

    state = {
        "trace_id": "report-empty",
        "user_request": "Compare prices for unknown product",
        "product_name": "unknown product",
        "scraped_items": [],
        "validated_items": [],
        "analysis_summary": "No available products found for 'unknown product'. Price analysis was skipped.",
        "best_store": "N/A",
        "best_price": 0.0,
        "min_price": 0.0,
        "max_price": 0.0,
        "average_price": 0.0,
    }

    result = risk_reporter.risk_and_report_agent(state)

    assert "No available products found for 'unknown product'" in result["final_report"]
    assert "No available products found in the dataset" in result["final_report"]
