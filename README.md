# AI-Based Smart Price Comparison Multi-Agent System (MAS)

This project is a fully local, zero-cost Multi-Agent System for automated product price comparison.

## Assignment Compliance (Local-Only + Ollama)

- Runs fully on local machines.
- Uses local SLM inference through Ollama (`llama3:8b` by default).
- No paid cloud API keys are required (no OpenAI/Anthropic/Gemini runtime dependency).
- Supports deterministic offline demo mode with `MAS_OFFLINE_MODE=1`.

## Problem Overview

Manual price comparison across multiple online sources is repetitive and time-consuming.

This MAS automates the workflow using six coordinated agents:

1. Coordinator Agent
2. Web Scraper Agent
3. Offer Validator Agent
4. Price Analyzer Agent
5. Trend Analyzer Agent
6. Report Generator Agent

The system accepts a product request, checks available dataset/source prices, validates offers, computes the best offer, compares the current price with historical data, and outputs a final report in both Markdown and PDF. If the product is not available in the dataset or provided sources, the system returns a clear "No available products found" message instead of generating fake prices.

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
2. Web Scraper -> collects and normalizes price entries from URLs or the local dataset.
3. Offer Validator -> removes invalid/duplicate offers and categorizes valid offers.
4. Price Analyzer -> calculates best price, min, max, and average.
5. Trend Analyzer -> compares the current best price with historical dataset prices.
6. Report Generator -> writes final Markdown + PDF reports and logs outputs.

Orchestration is handled in `src/mas/graph.py`.

## Agent Purposes and Outcomes

| Agent                     | Purpose                                                                                                           | Main input                                        | Main outcome                                                                                                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Coordinator Agent      | Understands the user request and prepares shared state for the rest of the MAS.                                   | User request such as `Compare prices for coconut` | `product_name`, `normalized_product_query`, source URL plan, and planning notes.                                                                                                  |
| 2. Web Scraper Agent      | Finds product price entries from provided source URLs or from the local dataset in offline mode.                  | Product name and optional source URLs             | `scraped_items` with store/title/price/currency and `research_notes`. If no match exists, returns `No available products found...`.                                               |
| 3. Offer Validator Agent  | Checks scraped offers before analysis, removes invalid entries, removes duplicates, and assigns price categories. | `scraped_items`                                   | `validated_items`, quality score, category summary, and validation notes. If no items exist, returns no valid offers instead of sample data.                                      |
| 4. Price Analyzer Agent   | Computes price statistics and identifies the best available offer.                                                | Validated or scraped items                        | `best_store`, `best_price`, `min_price`, `max_price`, `average_price`, and `analysis_summary`. If no items exist, price analysis is skipped with a no-available-products message. |
| 5. Trend Analyzer Agent   | Compares the current best price against historical dataset prices.                                                | Product name and current best price               | Trend direction, percentage change, historical average, and recommendation. If no valid price exists, trend analysis is skipped cleanly.                                          |
| 6. Report Generator Agent | Builds the final user-facing report and saves it to disk.                                                         | Full shared MAS state                             | Markdown report, PDF report, report notes, and final conclusion. If no product is available, the conclusion states that no products were found.                                   |

## System Prompts

All explicit system prompts are centralized in:

- `src/mas/agents/prompts.py`

This includes prompts for all six agents and supports assignment criteria for prompt engineering visibility.

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

## Copy-Paste Quick Start (Examiner)

Run these commands exactly in PowerShell:

```powershell
cd "D:\SLIIT\Y4S2\CTSE\Assignment 2\MAS"
& ".\.venv\Scripts\Activate.ps1"
$env:MAS_OFFLINE_MODE="1"
python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

### Interpreter-Safe Mode (Recommended)

To avoid `ModuleNotFoundError` due to wrong Python interpreter, use this variable in all commands:

```powershell
$py = "d:/SLIIT/Y4S2/CTSE/Assignment 2/MAS/.venv/Scripts/python.exe"
```

Then run commands as `& $py ...` instead of plain `python ...`.

## Run the Project

Recommended deterministic mode for demo:

```powershell
$env:MAS_OFFLINE_MODE="1"; python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

Interpreter-safe equivalent:

```powershell
$env:MAS_OFFLINE_MODE="1"; & $py -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

Typical output:

```text
=== MAS Execution Complete ===
Trace ID: <trace_id>
Report (MD): ...\reports\price_report_<trace_id>.md
Report (PDF): ...\reports\price_report_<trace_id>.pdf
Run Summary: logs\summary_<trace_id>.json
```

## Simple Web Frontend

A lightweight web UI is available for running the MAS pipeline from your browser.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the frontend:

```powershell
$env:MAS_OFFLINE_MODE="1"
python -m src.mas.web
```

Open: http://localhost:5000

The UI now supports running each member separately:

- Member 1: Coordinator Agent
- Member 2: Web Scraper Agent
- Member 3: Price Analyzer Agent
- Member 4: Full Pipeline including Report Generator Agent
- Member 5: Offer Validator Agent
- Member 6: Trend Analyzer Agent

Enter the request/product text, optional source URLs, and member-specific inputs for scraped items or best price, then submit to view the agent result. For wrong product names or products missing from `data/data.csv`, the UI shows a no-available-products message instead of fallback demo prices.

Frontend member outcomes:

| Member | Runs                                      | Outcome shown in UI                                                                     |
| ------ | ----------------------------------------- | --------------------------------------------------------------------------------------- |
| 1      | Coordinator Agent                         | Extracted product name, normalized query, source URL plan, and planning notes.          |
| 2      | Web Scraper Agent                         | Real scraped/dataset items, research notes, and product availability status.            |
| 3      | Web Scraper Agent + Price Analyzer Agent  | Best store, best price, min/max/average, or no-available-products message.              |
| 4      | Full Pipeline                             | Complete MAS output plus Markdown/PDF report paths.                                     |
| 5      | Web Scraper Agent + Offer Validator Agent | Validated items, offer categories, quality score, or no valid offers if unavailable.    |
| 6      | Trend Analyzer Agent                      | Trend summary and recommendation using the entered best price or current scraped items. |

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

Interpreter-safe equivalent:

```powershell
& $py -m pytest -q
```

Run agent ownership tests only (student-by-student evidence):

```powershell
& $py -m pytest tests/test_coordinator_agent.py tests/test_web_scraper_agent.py tests/test_price_analyzer_agent.py tests/test_report_generator_agent.py -v
```

Run multi-case evaluation:

```powershell
python evaluation.py
```

Interpreter-safe equivalent:

```powershell
& $py evaluation.py
```

## One-by-One Viva Commands (Per Member)

Set once:

```powershell
$env:MAS_OFFLINE_MODE="1"
```

### Recommended: Step-by-Step Input Mode (No long one-liners)

Use this interactive runner:

```powershell
python scripts/viva_step_runner.py
```

Interpreter-safe equivalent:

```powershell
& $py scripts/viva_step_runner.py
```

It will ask inputs one by one:

1. Member selection
2. Trace ID
3. Product/Request details
4. Sample prices (for member 3 if needed)

You can also run a member directly:

```powershell
python scripts/viva_step_runner.py --member 1
python scripts/viva_step_runner.py --member 2
python scripts/viva_step_runner.py --member 3
python scripts/viva_step_runner.py --member 4
python scripts/viva_step_runner.py --member 5
python scripts/viva_step_runner.py --member 6
```

Interpreter-safe equivalents:

```powershell
& $py scripts/viva_step_runner.py --member 1
& $py scripts/viva_step_runner.py --member 2
& $py scripts/viva_step_runner.py --member 3
& $py scripts/viva_step_runner.py --member 4
& $py scripts/viva_step_runner.py --member 5
& $py scripts/viva_step_runner.py --member 6
```

### Alternative: Direct one-line commands

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

Member 5 (Offer Validator):

```powershell
python scripts/viva_step_runner.py --member 5
```

Member 6 (Trend Analyzer):

```powershell
python scripts/viva_step_runner.py --member 6
```

Interpreter-safe equivalents:

```powershell
& $py -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
& $py scripts/viva_step_runner.py --member 5
& $py scripts/viva_step_runner.py --member 6
```

## Convert Any Markdown Report to PDF

Use the utility script:

```powershell
python scripts/export_report_pdf.py --input ".\reports\price_report_<trace_id>.md" --output ".\reports\price_report_<trace_id>.pdf"
```

Interpreter-safe equivalent:

```powershell
& $py scripts/export_report_pdf.py --input ".\reports\price_report_<trace_id>.md" --output ".\reports\price_report_<trace_id>.pdf"
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

If the error still appears, you are likely using the wrong interpreter. Use:

```powershell
& $py -m pip install -r requirements.txt
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
