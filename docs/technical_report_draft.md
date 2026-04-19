# AI-Based Smart Price Comparison Multi-Agent System (MAS)

## 1. Introduction and Problem Domain
In modern digital commerce, users often inspect multiple websites to identify the best available price for a product. Manual comparison is repetitive, slow, and prone to missing good offers. This project implements a fully local Multi-Agent System (MAS) that automates this workflow.

The system uses four collaborating agents to process a user request, collect price information, analyze the data, and generate a final report. The implementation runs locally with no paid APIs, matching assignment constraints.

## 2. System Architecture
The MAS follows a sequential workflow implemented in LangGraph:

1. Coordinator Agent
2. Web Scraper Agent
3. Price Analyzer Agent
4. Report Generator Agent

Workflow:

1. User submits a product query.
2. Coordinator extracts and normalizes the product search target.
3. Web Scraper collects product-price entries from source content.
4. Price Analyzer computes best offer and statistics.
5. Report Generator writes a structured markdown report and observability artifacts.

Reference diagram: see docs/architecture.md.

## 3. Multi-Agent Design
### 3.1 Coordinator Agent
- Role: workflow orchestrator and request normalizer.
- Inputs: user_request, model, trace_id.
- Outputs: product_name, normalized_product_query, source_urls.
- Constraints: keeps extraction deterministic; uses local LLM refinement only when available.

### 3.2 Web Scraper Agent
- Role: data collection.
- Inputs: product_name, source_urls, offline mode config.
- Outputs: scraped_items list and collection summary notes.
- Constraints: robust fallback in offline mode for consistent demo behavior.

### 3.3 Price Analyzer Agent
- Role: statistical analysis and best-price detection.
- Inputs: scraped_items.
- Outputs: best_store, best_price, min_price, max_price, average_price, analysis_summary.
- Constraints: validates numeric inputs and handles empty/invalid data safely.

### 3.4 Report Generator Agent
- Role: output synthesis.
- Inputs: all previously accumulated state fields.
- Outputs: final_report markdown text and saved_report_path.
- Constraints: preserves traceability by adding runtime metadata and writing run summaries.

## 4. Tool Implementation
### 4.1 Web Scraping Tool
- File: src/mas/tools/public_api.py
- Main function: scrape_prices(product_name, source_urls, offline_mode)
- Internals: BeautifulSoup HTML parsing and regex-based price extraction.
- Error handling: URL failures are skipped without stopping the full workflow.

### 4.2 Price Analysis Tool
- File: src/mas/tools/price_tools.py
- Main function: analyze_prices(items)
- Outputs: min, max, average, best store, best price.
- Error handling: raises ValueError when no valid numeric prices exist.

### 4.3 File Saving Tool
- File: src/mas/tools/file_tools.py
- Main function: save_markdown_file(path, content)
- Behavior: creates parent directories and returns absolute path.

### 4.4 Secure Shell Tool
- File: src/mas/tools/shell_tools.py
- Main function: run_safe_shell(command)
- Behavior: blocks non-allowlisted commands to enforce safe local execution.

All tools include type hints and docstrings.

## 5. State Management
The system uses a shared typed dictionary (MASState) to preserve context across agent handoffs.

Example state snapshot:

```python
state = {
    "product_name": "coconut",
    "scraped_items": [
        {"store": "Glomark", "title": "coconut", "price": 120.0, "currency": "LKR"},
        {"store": "Keells", "title": "coconut", "price": 135.5, "currency": "LKR"},
        {"store": "Arpico", "title": "coconut", "price": 110.0, "currency": "LKR"},
    ],
    "best_price": 110.0,
    "best_store": "Arpico",
    "min_price": 110.0,
    "max_price": 135.5,
    "average_price": 121.83,
}
```

Each agent appends or updates only its relevant fields, preventing context loss.

## 6. Orchestration Framework
LangGraph is used for:
- Deterministic node sequencing.
- State passing between agents.
- Scalable orchestration structure for extension.

Current graph edges:
- coordinator -> web_scraper -> price_analyzer -> report_generator.

## 7. Observability and Logging
The system records:
- run_start and run_end events.
- agent_output events.
- tool_call events.

Artifacts:
- logs/trace_<trace_id>.jsonl
- logs/summary_<trace_id>.json

These artifacts improve debugging, reproducibility, and demonstration clarity.

## 8. Testing and Evaluation
Test layers:
1. Tool unit tests.
2. End-to-end graph smoke test.
3. Evaluation harness with multi-scenario checks.
4. Security validation for shell command blocking.

Evaluation scenarios:
- coconut
- rice
- milk powder

Core checks:
- product extraction and scraped data availability
- statistical consistency (best in min-max range)
- report generation success
- command safety enforcement

## 9. Individual Contributions
Each student contributes:
- one agent implementation
- one custom tool
- agent-specific tests
- challenge notes and resolution evidence

Use CONTRIBUTIONS.md and docs/contributions/student_<n>.md as evidence records.

## 10. Challenges and Resolutions
- Challenge: inconsistent HTML structures across sources.
- Resolution: resilient text-level extraction with normalization.

- Challenge: safe command execution requirements.
- Resolution: strict allowlist in shell tool and automated security checks.

- Challenge: maintaining context across multi-agent flow.
- Resolution: typed shared state and deterministic LangGraph routing.

## 11. Conclusion
The implemented MAS demonstrates how a local team of agents can automate complex price comparison tasks with structured orchestration, reliable tool usage, robust state management, and measurable evaluation. The architecture is extensible and aligned with real-world automation requirements under zero-cost local constraints.
