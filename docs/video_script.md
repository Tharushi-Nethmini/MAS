# Demo Video Script (4-5 Minutes)

## Goal
Demonstrate the full local execution of the AI-Based Smart Price Comparison MAS, including agent orchestration, tool usage, state handoff, logging, and final output generation.

## Total Duration
Target: 4 minutes 30 seconds (do not exceed 5 minutes)

## 0:00 - 0:30 | Introduction
Narration points:
- Introduce the project name and problem: manual price comparison is time-consuming.
- State that the system runs locally with no paid cloud API usage.
- Briefly mention the four agents and LangGraph orchestration.

On screen:
- Open project root.
- Show key folders: src, logs, reports, tests, docs.

## 0:30 - 1:10 | Show Architecture
Narration points:
- Explain the flow: Coordinator -> Web Scraper -> Price Analyzer -> Report Generator.
- Mention shared global state is passed between agents.

On screen:
- Open docs/architecture.md.
- Highlight each agent role in one sentence.

## 1:10 - 2:10 | Run the System
Narration points:
- Explain that this is a local run in offline-safe mode for reproducibility.
- State example request used for demo.

On screen (PowerShell):
1. Activate environment if needed.
2. Run:

```powershell
$env:MAS_OFFLINE_MODE="1"
python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b
```

Expected output to show:
- Trace ID
- Markdown report path
- PDF report path
- Summary path

## 2:10 - 3:00 | Show Outputs
Narration points:
- Explain what each generated artifact represents.

On screen:
- Open reports/price_report_<trace_id>.md.
- Show computed values: best price, best store, min/max/average.
- Open logs/trace_<trace_id>.jsonl and logs/summary_<trace_id>.json.
- Mention these provide observability and debugging evidence.

## 3:00 - 3:45 | Show Tests and Evaluation
Narration points:
- Explain that each agent has test coverage plus unified evaluation.
- Mention reliability and security checks.

On screen:

```powershell
python -m pytest -q
python evaluation.py
```

Highlight:
- Pass results
- Evaluation checks (best price validity, report saved, shell safety block)

## 3:45 - 4:25 | Individual Contribution Proof
Narration points:
- State each member contributed one agent, one tool, and tests.
- Mention contribution evidence is in contribution documents.

On screen:
- Open CONTRIBUTIONS.md.
- Quickly scroll student ownership sections.

## 4:25 - 4:45 | Closing
Narration points:
- Summarize that the MAS satisfies assignment constraints: multi-agent orchestration, custom tools, state management, observability, and evaluation.
- Mention future work: more sources, better extraction, optional UI.

## Recording Checklist
- Keep camera/audio clear and avoid long pauses.
- Use zoom on terminal output when showing trace/report paths.
- Keep each segment short to stay under 5 minutes.
- Ensure at least one complete successful run is captured.
