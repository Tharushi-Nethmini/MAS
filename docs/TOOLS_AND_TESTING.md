# MAS Project: Tools & Testing Guide

A comprehensive reference for understanding how each of the 4 agents implements its custom tools and how they are validated through testing.

---

## Project Structure Overview

```
src/mas/
├── agents/               # 4 agents, each with unique responsibility
│   ├── coordinator.py    # Student 1: Request normalization
│   ├── researcher.py     # Student 2: Web scraping
│   ├── budgeter.py       # Student 3: Price analysis
│   └── risk_reporter.py  # Student 4: Report generation
├── tools/                # Custom tool implementations
│   ├── public_api.py     # Scraping tools
│   ├── price_tools.py    # Analysis tools
│   ├── file_tools.py     # File operations
│   ├── pdf_tools.py      # PDF generation
│   └── shell_tools.py    # Safe shell execution
├── state.py              # Shared MASState TypedDict
├── config.py             # Ollama configuration
└── graph.py              # LangGraph orchestration

tests/
├── test_coordinator_agent.py        # Student 1 validation
├── test_web_scraper_agent.py        # Student 2 validation
├── test_price_analyzer_agent.py     # Student 3 validation
├── test_report_generator_agent.py   # Student 4 validation
├── test_tools.py                    # Shared tool tests
└── test_graph_smoke.py              # End-to-end pipeline

evaluation.py                        # Multi-scenario reliability checks
```

---

## Student 1: Coordinator Agent

**Agent**: `src/mas/agents/coordinator.py`  
**Tool**: Request Normalization  
**Test File**: `tests/test_coordinator_agent.py`

### Tool Implementation
- **Function**: `coordinator_agent(state: MASState) -> dict`
- **Purpose**: Extract and normalize user product queries
- **Pipeline**:
  1. Regex pattern matching: `r"(for|of)\s+([\w\s]+?)(?:\s+in|$)"`
  2. Keyword fallback: ["coconut", "rice", "milk powder"]
  3. LLM validation via Ollama
  4. Output: product_name, normalized_product_query

### Testing
**Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q tests/test_coordinator_agent.py
```

**Tests** (2 total):
1. `test_coordinator_agent_extracts_product_name` - Valid extraction
2. `test_coordinator_agent_uses_fallback_for_empty_request` - Fallback activation

**Expected Output**:
```
.. [100%]
2 passed in 0.04s
```

---

## Student 2: Web Scraper Agent

**Agent**: `src/mas/agents/researcher.py`  
**Tool**: Price Scraper (`scrape_prices`)  
**Tool File**: `src/mas/tools/public_api.py`  
**Test File**: `tests/test_web_scraper_agent.py`

### Tool Implementation
- **Function**: `scrape_prices(product_name: str, source_urls: list[str] | None = None, offline_mode: bool = False, model: str | None = None) -> list[dict[str, Any]]`
- **Purpose**: Collect product prices from multiple sources
- **Features**:
  - Shopify endpoint detection
  - HTML parsing with BeautifulSoup4
  - Price regex: `r"\$(\d+(?:\.\d{2})?)"`
  - Offline mode with deterministic mock data
  - Normalization of store names, titles, prices

### Testing
**Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q tests/test_web_scraper_agent.py
```

**Tests** (1 total):
1. `test_research_agent_returns_scraped_items` - ≥3 items with valid prices

**Expected Output**:
```
. [100%]
1 passed in 0.11s
```

**Shared Tests** (`tests/test_tools.py`):
- `test_scrape_prices_offline_mode()`
- `test_scrape_prices_returns_valid_structure()`

---

## Student 3: Price Analyzer Agent

**Agent**: `src/mas/agents/budgeter.py`  
**Tool**: Price Analysis (`analyze_prices`)  
**Tool File**: `src/mas/tools/price_tools.py`  
**Test File**: `tests/test_price_analyzer_agent.py`

### Tool Implementation
- **Function**: `analyze_prices(scraped_items: list[dict]) -> dict`
- **Purpose**: Perform statistical analysis on price data
- **Computation**:
  - Best price: minimum across all items
  - Min/Max/Average prices
  - Sample size (valid item count)
  - Validation: min ≤ avg ≤ max

### Testing
**Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q tests/test_price_analyzer_agent.py
```

**Tests** (2 total):
1. `test_budget_agent_finds_best_price` - Correct minimum detection
2. `test_budget_agent_filters_invalid_items` - Invalid data exclusion

**Expected Output**:
```
.. [100%]
2 passed in 0.08s
```

**Shared Tests** (`tests/test_tools.py`):
- `test_analyze_prices_returns_correct_structure()`
- `test_analyze_prices_filters_invalid_items()`

---

## Student 4: Report Generator Agent

**Agent**: `src/mas/agents/risk_reporter.py`  
**Tools**: 
- Markdown Report (`save_markdown_file`)
- PDF Report (`save_report_pdf`)
- Safe Shell (`run_safe_shell`)

**Tool Files**: `src/mas/tools/file_tools.py`, `src/mas/tools/pdf_tools.py`, `src/mas/tools/shell_tools.py`  
**Test File**: `tests/test_report_generator_agent.py`

### Tool Implementation

#### Tool 1: Markdown File (`save_markdown_file`)
- **Location**: `src/mas/tools/file_tools.py`
- **Function**: `save_markdown_file(file_path: str, content: str) -> str`
- **Purpose**: Create formatted markdown reports
- **Features**: Parent dir creation, content validation, file existence check

#### Tool 2: PDF Report (`save_report_pdf`)
- **Location**: `src/mas/tools/pdf_tools.py`
- **Function**: `save_report_pdf(path: str, title: str, content: str) -> str`
- **Purpose**: Generate professional A4 PDF documents
- **Features**: ReportLab formatting, header/table styling, content embedding

#### Tool 3: Safe Shell (`run_safe_shell`)
- **Location**: `src/mas/tools/shell_tools.py`
- **Function**: `run_safe_shell(command: str) -> str`
- **Purpose**: Execute only safe shell commands
- **Allowlist**: Get-ChildItem, dir, pwd, Get-Date, Get-Location
- **Blocks**: Dangerous commands (rm, del, curl, package managers)

### Testing
**Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q tests/test_report_generator_agent.py
```

**Tests** (1 total):
1. `test_report_generator_agent_creates_files` - Markdown + PDF creation, content validation

**Expected Output**:
```
. [100%]
1 passed in 0.15s
```

**Shared Tests** (`tests/test_tools.py`, `tests/test_graph_smoke.py`):
- `test_save_markdown_file_creates_file()`
- `test_save_report_pdf_creates_valid_pdf()`
- End-to-end pipeline validation

---

## Running All Tests

### Run All Agent-Specific Tests
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q tests/test_coordinator_agent.py tests/test_web_scraper_agent.py tests/test_price_analyzer_agent.py tests/test_report_generator_agent.py
```

**Expected Output**:
```
...... [100%]
6 passed in ~1.70s
```

### Run All Tests (Including Shared)
```bash
& ".\.venv\Scripts\python.exe" -m pytest -q
```

### Run Multi-Scenario Evaluation
```bash
& ".\.venv\Scripts\python.exe" evaluation.py
```

---

## State Flow Through Agents

Each agent receives and modifies shared `MASState`:

```
┌─ Coordinator Agent (Student 1)
│  Input: user_request
│  Output: product_name, normalized_product_query
│
├─ Web Scraper Agent (Student 2)
│  Input: normalized_product_query
│  Output: scraped_items (list of dicts)
│
├─ Price Analyzer Agent (Student 3)
│  Input: scraped_items
│  Output: best_price, best_store, min_price, max_price, average_price
│
└─ Report Generator Agent (Student 4)
   Input: All previous outputs
   Output: final_report, saved_report_path, saved_report_pdf_path
```

---

## Tool Testing Summary

| Agent | Tool | Test File | Tests | Status |
|-------|------|-----------|-------|--------|
| 1 (Coordinator) | Request Normalization | test_coordinator_agent.py | 2 | ✅ 2 passed |
| 2 (Web Scraper) | scrape_prices | test_web_scraper_agent.py | 1 | ✅ 1 passed |
| 3 (Price Analyzer) | analyze_prices | test_price_analyzer_agent.py | 2 | ✅ 2 passed |
| 4 (Report Generator) | file/pdf/shell tools | test_report_generator_agent.py | 1 | ✅ 1 passed |
| **TOTAL** | - | - | **6** | **✅ 6 passed** |

---

## Quick Reference: Test Commands

### Per-Agent Testing
```bash
# Student 1
& ".\.venv\Scripts\python.exe" -m pytest tests/test_coordinator_agent.py -v

# Student 2
& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_scraper_agent.py -v

# Student 3
& ".\.venv\Scripts\python.exe" -m pytest tests/test_price_analyzer_agent.py -v

# Student 4
& ".\.venv\Scripts\python.exe" -m pytest tests/test_report_generator_agent.py -v
```

### Shared Tool Testing
```bash
# All tool unit tests
& ".\.venv\Scripts\python.exe" -m pytest tests/test_tools.py -v

# End-to-end smoke test
& ".\.venv\Scripts\python.exe" -m pytest tests/test_graph_smoke.py -v
```

### Full Test Suite
```bash
# All tests
& ".\.venv\Scripts\python.exe" -m pytest -v

# All tests with coverage
& ".\.venv\Scripts\python.exe" -m pytest --cov=src/mas tests/
```

---

## Offline Mode

All tests run with offline mode enabled (`MAS_OFFLINE_MODE=1`) for reproducibility:

**Benefits**:
- No network dependencies
- Deterministic test results
- Fast execution (no API calls)
- Demo-ready data profiles

**Example**:
```python
# Inside test, offline mode is automatically enabled
result = coordinator_agent(state)  # Uses Ollama local
result = scrape_prices("coconut", "demo", offline_mode=True)  # Uses mock data
```

---

## Documentation Links

- Individual contribution proof files:
  - [Student 1 Details](contributions/student_1.md)
  - [Student 2 Details](contributions/student_2.md)
  - [Student 3 Details](contributions/student_3.md)
  - [Student 4 Details](contributions/student_4.md)

- Architecture overview: [architecture.md](architecture.md)
- Technical report: [technical_report_final.md](technical_report_final.md)

---

## Viva Preparation

Each student should be able to:

1. **Explain their tool**:
   - What it does
   - How it works (input → processing → output)
   - Key algorithms/libraries used

2. **Run their tests**:
   - Command to run agent-specific tests
   - Interpretation of output (dots = passed tests)
   - How to verify all tests pass

3. **Discuss challenges**:
   - Problems encountered during implementation
   - How they were solved
   - Alternative approaches considered

4. **Demo the system**:
   - Run full pipeline: `python -c "from src.mas.graph import workflow; print(workflow.invoke({'user_request': 'Compare prices for coconut', ...}))"`
   - Show report generation in reports/ folder
   - Explain trace files in logs/ folder

---

## Key Takeaways

- **Each student** owns 1 agent + develops 1+ custom tools
- **Testing** validates individual tools AND full pipeline
- **Offline mode** ensures reproducible, fast test execution
- **State management** (TypedDict) ensures type safety across agents
- **Tool allowlisting** (shell, etc.) ensures security
- **Clear documentation** (this file) helps with viva preparation
