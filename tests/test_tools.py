from __future__ import annotations

from pathlib import Path

import pytest

from src.mas.tools.file_tools import load_json_file, save_markdown_file
from src.mas.tools.pdf_tools import save_report_pdf
from src.mas.tools.price_tools import analyze_prices
from src.mas.tools.public_api import scrape_prices
from src.mas.tools.shell_tools import run_safe_shell


def test_save_markdown_file_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "sample.md"
    saved = save_markdown_file(str(output), "# Hello")
    assert Path(saved).exists()
    assert output.read_text(encoding="utf-8") == "# Hello"


def test_load_json_file_validates_root_type(tmp_path: Path) -> None:
    p = tmp_path / "test.json"
    p.write_text("[1,2,3]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_json_file(str(p))


def test_run_safe_shell_blocks_untrusted_commands() -> None:
    with pytest.raises(ValueError):
        run_safe_shell("Remove-Item test.txt")


def test_scrape_prices_offline_returns_items() -> None:
    items = scrape_prices("coconut", offline_mode=True)
    assert len(items) >= 3
    assert all("store" in item and "price" in item for item in items)
    assert all(float(item["price"]) >= 100.0 for item in items)


def test_analyze_prices_returns_best_offer() -> None:
    summary = analyze_prices(
        [
            {"store": "StoreA", "price": 200},
            {"store": "StoreB", "price": 150},
            {"store": "StoreC", "price": 175},
        ]
    )
    assert summary["best_store"] == "StoreB"
    assert summary["best_price"] == 150.0


def test_save_report_pdf_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "runtime_report.pdf"
    saved = save_report_pdf(str(output), "Runtime Report", "Hello PDF")
    assert Path(saved).exists()
