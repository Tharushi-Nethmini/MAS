# AI-Based Smart Price Comparison Multi-Agent System (MAS)

## 1. Introduction and Problem Domain
In the digital retail environment, customers often compare multiple websites before purchasing a product. Manual price comparison is repetitive, time-consuming, and error-prone. This project addresses that problem by implementing a locally hosted Multi-Agent System (MAS) that automates product price comparison from request to final report.

The system is designed as an autonomous team of AI agents that collaborate through a shared state. It runs fully on local resources using a local model setup (Ollama-compatible), which satisfies zero-cost and privacy-oriented constraints of the assignment.

## 2. System Architecture
The architecture is a four-agent pipeline managed by LangGraph:

1. Coordinator Agent
2. Web Scraper Agent
3. Price Analyzer Agent
4. Report Generator Agent

### Workflow Overview
1. User submits a product request.
2. Coordinator extracts and normalizes the product target.
3. Web Scraper collects and normalizes price entries.
4. Price Analyzer computes best offer and summary statistics.
5. Report Generator writes markdown and PDF outputs and stores run artifacts.

Architecture diagram and interaction flow are documented in docs/architecture.md.

## 3. Multi-Agent Design

### 3.1 Coordinator Agent
- Role: Workflow orchestration and request normalization.
- Responsibilities:
    - Receive and validate user request.
    - Extract product name and initialize global state fields.
    - Prepare downstream inputs (product query, candidate sources).
- Inputs: user_request, model, trace_id.
- Outputs: product_name, normalized_product_query, source_urls.

### 3.2 Web Scraper Agent
- Role: Data collection from configured sources.
- Responsibilities:
    - Retrieve product-related content.
    - Extract valid price records.
    - Return normalized items with store/title/price/currency fields.
- Inputs: product_name, source_urls, offline_mode.
- Outputs: scraped_items and collection notes.

### 3.3 Price Analyzer Agent
- Role: Data processing and decision support.
- Responsibilities:
    - Compute minimum, maximum, and average prices.
    - Identify best price and corresponding store.
    - Produce concise analysis summary.
- Inputs: scraped_items.
- Outputs: best_price, best_store, min_price, max_price, average_price, analysis_summary.

### 3.4 Report Generator Agent
- Role: Final output generation and persistence.
- Responsibilities:
    - Format final comparison report.
    - Save report to local storage.
    - Write trace-friendly output metadata.
- Inputs: full shared state.
- Outputs: final_report, saved_report_path, summary artifacts.

## 4. Tools Implementation

### 4.1 Web Scraping Tool
- File: src/mas/tools/public_api.py
- Purpose: Extract product records from source data.
- Key implementation details:
    - BeautifulSoup-based parsing.
    - Numeric price extraction and normalization.
    - Fault tolerance for malformed pages or unavailable sources.

### 4.2 Price Analysis Tool
- File: src/mas/tools/price_tools.py
- Purpose: Calculate statistical insights and best deal.
- Key outputs:
    - min_price, max_price, average_price, best_price, best_store.
- Reliability features:
    - Rejects invalid prices.
    - Raises controlled errors for empty/invalid datasets.

### 4.3 File Persistence Tool
- File: src/mas/tools/file_tools.py
- Purpose: Save generated report files locally.
- Reliability features:
    - Ensures output directory creation.
    - Returns absolute, traceable file paths.

### 4.4 Safe Shell Tool
- File: src/mas/tools/shell_tools.py
- Purpose: Controlled local shell execution for safe automation.
- Security features:
    - Allowlist-based command filtering.
    - Blocks unsafe commands and raises explicit errors.

All tools include Python type hints, docstrings, and explicit error handling.

## 5. State Management
The system uses a shared MASState structure to preserve context across all agent handoffs.

Example state snapshot:

```python
state = {
        "product_name": "coconut",
        "scraped_items": [
                {"store": "Glomark", "title": "Fresh Coconut", "price": 120.0, "currency": "LKR"},
                {"store": "Keells", "title": "Coconut", "price": 135.5, "currency": "LKR"},
                {"store": "Arpico", "title": "Coconut", "price": 110.0, "currency": "LKR"},
        ],
        "best_price": 110.0,
        "best_store": "Arpico",
        "min_price": 110.0,
        "max_price": 135.5,
        "average_price": 121.83,
}
```

Each agent reads and updates only its relevant fields. This minimizes context loss and keeps state transitions predictable.

## 6. Orchestration, Observability, and Evaluation

### 6.1 Orchestration Framework
LangGraph is used for deterministic and extensible multi-agent control with the following behavior:
- Structured node routing with explicit edges.
- Shared-state transitions between agents.
- Reproducible workflow execution.

Current execution route:
```
coordinator → web_scraper → price_analyzer → report_generator
```

### 6.2 Observability and Logging
The system includes structured observability with per-run and per-event tracking.

Tracked events:
- Agent inputs and outputs.
- Tool invocation details.
- Run start and completion metadata.

Generated artifacts:
- `logs/trace_<trace_id>.jsonl` – Newline-delimited JSON event stream.
- `logs/summary_<trace_id>.json` – Compact run summary for quick reference.

### 6.3 Testing and Evaluation Methodology
The project uses a layered testing and evaluation strategy.

The team developed a single unified testing harness to evaluate the MAS as a whole, while each student contributed agent-specific test cases and assertions to validate the output of their own component.

**Validation Layers:**
1. Tool-level unit tests.
2. Agent behavior tests.
3. End-to-end graph smoke tests.
4. Evaluation harness in evaluation.py.

**Student Ownership in the Shared Harness:**
- Student 1: Coordinator extraction and fallback assertions.
- Student 2: Web scraper output and malformed-source assertions.
- Student 3: Price analysis, numeric validation, and range assertions.
- Student 4: Report generation, persistence, and completion assertions.

**Evaluation Scenarios:**
- Compare prices for coconut
- Compare prices for rice
- Find best deal for milk powder

**Core Quality Assertions:**
- Product extraction is present and non-empty.
- Scraped dataset exists with valid items.
- Analysis summary is generated.
- Best price is positive and within [min_price, max_price].
- Report output persists to local storage.
- Unsafe shell commands are blocked by allowlist.

## 7. Individual Contributions
Each team member is responsible for one major part of the MAS implementation, one supporting tool or test area, and documented proof of work.

### Student 1
- Implemented the Coordinator Agent.
- Added request parsing and product normalization logic.
- Contributed tests for product extraction and fallback behavior.
- Evidence: commit links and pull request ID recorded in CONTRIBUTIONS.md.

### Student 2
- Implemented the Web Scraper Agent.
- Added price extraction and normalization routines.
- Contributed tests for offline scraping and malformed source handling.
- Evidence: commit links and pull request ID recorded in CONTRIBUTIONS.md.

### Student 3
- Implemented the Price Analyzer Agent.
- Added statistical analysis for minimum, maximum, average, and best price.
- Contributed tests for numeric validation and range consistency.
- Evidence: commit links and pull request ID recorded in CONTRIBUTIONS.md.

### Student 4
- Implemented the Report Generator Agent.
- Added report formatting and local file persistence.
- Contributed tests for output generation and end-to-end completion.
- Evidence: commit links and pull request ID recorded in CONTRIBUTIONS.md.

Contribution evidence is maintained in CONTRIBUTIONS.md and docs/contributions/.

## 8. Challenges Faced and Solutions
- Challenge: Inconsistent HTML structures and price patterns.
- Solution: Flexible parsing and robust normalization rules.

- Challenge: Maintaining consistent state across multi-agent handoffs.
- Solution: Typed shared state and deterministic graph sequencing.

- Challenge: Tool safety for local command execution.
- Solution: Allowlist-based shell restriction plus security assertions in evaluation.

## 9. System Demonstration
The demo (4 to 5 minutes) should clearly show:
1. User input and execution start.
2. Agent-by-agent workflow progression.
3. Tool usage and logging artifacts.
4. Final markdown/PDF report output.

## 10. Conclusion
This project demonstrates that a locally hosted Multi-Agent System can automate a real-world workflow efficiently and transparently. By combining specialized agents, custom tools, structured state management, and robust evaluation, the system meets assignment requirements while remaining scalable for future enhancements.

## 11. GitHub Repository
Repository link: INSERT_GITHUB_OR_GITLAB_URL_HERE

## 12. Future Improvements
- Add additional data sources for broader market coverage.
- Improve extraction accuracy for dynamic site layouts.
- Add a lightweight UI for user-friendly operation.
- Introduce more advanced reasoning and fallback strategies for ambiguous requests.
