# AI-Based Smart Price Comparison Multi-Agent System (MAS)

This project is a fully local, zero-cost Multi-Agent System for automated product price comparison.

## Problem Overview

Manual price comparison across multiple online sources is repetitive and time-consuming.

This MAS automates the workflow using four agents:
1. Coordinator Agent
2. Web Scraper Agent
3. Price Analyzer Agent
4. Report Generator Agent

The system accepts a product request, collects prices, computes the best offer, and outputs a final report in both Markdown and PDF.

## Tech Stack

- Python 3.12
- LangGraph (agent orchestration)
- Local model support via Ollama
- BeautifulSoup (scraping)
- ReportLab (PDF generation)
- Pytest (tests)

## Project Structure

```text
src/mas/
	agents/
		prompts.py
		coordinator.py
		researcher.py
		budgeter.py
		risk_reporter.py
	tools/
		public_api.py
		price_tools.py
		file_tools.py
		pdf_tools.py
		shell_tools.py
	observability/
		logger.py
	graph.py
	main.py
	state.py

docs/
	technical_report_draft.md
	technical_report_final.pdf

reports/
	price_report_<trace_id>.md
	price_report_<trace_id>.pdf

logs/
	trace_<trace_id>.jsonl
	summary_<trace_id>.json

tests/
evaluation.py
scripts/export_report_pdf.py
```

## Agent Workflow

Pipeline order:

1. Coordinator -> extracts product name and initializes global state.
2. Web Scraper -> collects and normalizes price entries.
3. Price Analyzer -> calculates best price, min, max, average.
4. Report Generator -> writes final Markdown + PDF reports and logs outputs.

Orchestration is handled in `src/mas/graph.py`.

## System Prompts

All explicit system prompts are centralized in:

- `src/mas/agents/prompts.py`

This includes prompts for all four agents and supports assignment criteria for prompt engineering visibility.

## Prerequisites

- Windows PowerShell
- Python installed
- Optional: Ollama installed if running with local model online mode

## Setup

From project root:

```powershell
cd "D:\SLIIT\Y4S2\CTSE\Assignment 2\MAS"
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& ".\.venv\Scripts\Activate.ps1")
python -m pip install -r requirements.txt
```

## Run the Project

Recommended deterministic mode for demo:

```powershell
$env:MAS_OFFLINE_MODE="1"; python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

Typical output:

```text
=== MAS Execution Complete ===
Trace ID: <trace_id>
Report (MD): ...\reports\price_report_<trace_id>.md
Report (PDF): ...\reports\price_report_<trace_id>.pdf
Run Summary: logs\summary_<trace_id>.json
```

## Outputs Generated Per Run

1. Markdown report in `reports/price_report_<trace_id>.md`
2. PDF report in `reports/price_report_<trace_id>.pdf`
3. Trace events in `logs/trace_<trace_id>.jsonl`
4. Run summary in `logs/summary_<trace_id>.json`

## Testing and Evaluation

Run all tests:

```powershell
python -m pytest -q
```

Run multi-case evaluation:

```powershell
python evaluation.py
```

## One-by-One Viva Commands (Per Member)

Set once:

```powershell
$env:MAS_OFFLINE_MODE="1"
```

Member 1 (Coordinator):

```powershell
python -c "from src.mas.agents.coordinator import coordinator_agent; s={'trace_id':'m1','model':'llama3:8b','user_request':'Compare prices for coconut'}; print(coordinator_agent(s))"
```

Member 2 (Web Scraper):

```powershell
python -c "from src.mas.agents.researcher import research_agent; s={'trace_id':'m2','product_name':'coconut','source_urls':[]}; print(research_agent(s))"
```

Member 3 (Price Analyzer):

```powershell
python -c "from src.mas.agents.budgeter import budget_agent; s={'trace_id':'m3','product_name':'coconut','scraped_items':[{'store':'Glomark','price':120.0},{'store':'Keells','price':135.5},{'store':'Arpico','price':110.0}]}; print(budget_agent(s))"
```

Member 4 (Full pipeline):

```powershell
python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

## Convert Any Markdown Report to PDF

Use the utility script:

```powershell
python scripts/export_report_pdf.py --input ".\reports\price_report_<trace_id>.md" --output ".\reports\price_report_<trace_id>.pdf"
```

## Observability Coverage

Structured logging is implemented via `log_event(...)` and `write_run_summary(...)` in `src/mas/observability/logger.py`.

Captured events include:
1. `run_start`
2. `tool_call`
3. `agent_output`
4. `run_end`

## Troubleshooting

If you get `ModuleNotFoundError: No module named 'bs4'`:

```powershell
python -m pip install -r requirements.txt
```

If PDF opens as unreadable text in editor:
1. Do not open `.pdf` as text.
2. Use:

```powershell
Start-Process ".\reports\price_report_<trace_id>.pdf"
```

If command quoting fails in PowerShell one-liners:
1. Use outer double quotes for `python -c`.
2. Use inner single quotes inside Python dictionaries.

