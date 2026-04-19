from __future__ import annotations

import json
from pathlib import Path

from src.mas.observability.logger import write_run_summary


def test_write_run_summary_creates_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    summary_path = write_run_summary(
        "trace123",
        {
            "product_name": "coconut",
            "best_store": "Arpico",
            "best_price": 110.0,
        },
    )

    p = Path(summary_path)
    assert p.exists()

    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["trace_id"] == "trace123"
    assert data["summary"]["best_price"] == 110.0
