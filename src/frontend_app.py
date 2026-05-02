from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_from_directory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "frontend" / "templates"),
    static_folder=str(PROJECT_ROOT / "frontend" / "static"),
)


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _recent_summary_files(limit: int = 10) -> list[Path]:
    files = sorted(
        LOGS_DIR.glob("summary_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[:limit]


def _summary_to_payload(summary_path: Path) -> dict[str, Any]:
    data = _read_json_file(summary_path)
    # Extract the nested 'summary' field if it exists
    summary_data = data.get("summary", data)
    md_path = Path(str(summary_data.get("saved_report_path", "")))
    pdf_path = Path(str(summary_data.get("saved_report_pdf_path", "")))

    return {
        "summary_file": summary_path.name,
        "trace_id": data.get("trace_id", ""),
        "product_name": summary_data.get("product_name", ""),
        "best_store": summary_data.get("best_store", ""),
        "best_price": summary_data.get("best_price", ""),
        "model": summary_data.get("model", ""),
        "request": summary_data.get("request", ""),
        "md_report": md_path.name if md_path.name else "",
        "pdf_report": pdf_path.name if pdf_path.name else "",
        "md_report_url": f"/reports/{md_path.name}" if md_path.name else "",
        "pdf_report_url": f"/reports/{pdf_path.name}" if pdf_path.name else "",
    }


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.get("/api/summaries")
def summaries() -> Any:
    payload = [_summary_to_payload(path) for path in _recent_summary_files(limit=12)]
    return jsonify({"summaries": payload})


@app.post("/api/run")
def run_pipeline() -> Any:
    body = request.get_json(silent=True) or {}
    user_request = str(body.get("request", "Compare prices for coconut")).strip() or "Compare prices for coconut"
    model = str(body.get("model", "llama3:8b")).strip() or "llama3:8b"

    command = [
        sys.executable,
        "-m",
        "src.mas.main",
        "--request",
        user_request,
        "--model",
        model,
    ]

    try:
        process = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Pipeline timed out after 180 seconds."}), 504

    if process.returncode != 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "Pipeline run failed.",
                    "stdout": process.stdout[-4000:],
                    "stderr": process.stderr[-4000:],
                }
            ),
            500,
        )

    latest = _recent_summary_files(limit=1)
    summary_payload = _summary_to_payload(latest[0]) if latest else {}

    print(f"[DEBUG] Latest summary payload: {summary_payload}")

    return jsonify(
        {
            "ok": True,
            "summary": summary_payload,
            "stdout": process.stdout[-4000:],
        }
    )


@app.get("/reports/<path:filename>")
def get_report(filename: str):
    return send_from_directory(REPORTS_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
