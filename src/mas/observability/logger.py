from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import settings


def log_event(trace_id: str, event_type: str, payload: dict[str, Any]) -> None:
    """Append one structured event to a trace JSONL file."""

    log_dir = Path(settings.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "event_type": event_type,
        "payload": payload,
    }

    file_path = log_dir / f"trace_{trace_id}.jsonl"
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")


def write_run_summary(trace_id: str, summary: dict[str, Any]) -> str:
    """Write a compact per-run summary JSON for easy demo and report evidence."""

    log_dir = Path(settings.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "summary": summary,
    }

    file_path = log_dir / f"summary_{trace_id}.json"
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)
    return str(file_path)
