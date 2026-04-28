# Individual Contribution Tracker

Each student owns one agent, one custom tool suite, and one agent-specific test file. Evidence is recorded in docs/contributions/*.md.

## Submission Proof Matrix

This section is the direct proof required by the assignment:

| Student | Agent Built | Custom Tool Built | Tests Contributed |
|---|---|---|---|
| Student 1 | `src/mas/agents/coordinator.py` | `src/mas/tools/query_tools.py` | `tests/test_coordinator_agent.py` |
| Student 2 | `src/mas/agents/researcher.py` | `src/mas/tools/public_api.py` | `tests/test_web_scraper_agent.py` |
| Student 3 | `src/mas/agents/budgeter.py` | `src/mas/tools/price_tools.py` | `tests/test_price_analyzer_agent.py` |
| Student 4 | `src/mas/agents/risk_reporter.py` | `src/mas/tools/file_tools.py`, `src/mas/tools/pdf_tools.py`, `src/mas/tools/shell_tools.py` | `tests/test_report_generator_agent.py` |

---

## Student 1: Coordinator Agent

**Agent**: `src/mas/agents/coordinator.py`  
**Tool**: Request Normalization  
**Test File**: `tests/test_coordinator_agent.py` (3 tests, PASS 3 passed)

**Quick Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest tests/test_coordinator_agent.py -v
```

**Tool Details**:
- Regex pattern extraction for product names
- Keyword fallback ["coconut", "rice", "milk powder"]
- LLM validation via Ollama
- Output: product_name, normalized_product_query

**Evidence**: [docs/contributions/student_1.md](docs/contributions/student_1.md)  
**Key Commits**: `ca43650`, `c940a18`  
**Challenges Faced**: Handling vague user queries while keeping output structured for downstream agents

---

## Student 2: Web Scraper Agent

**Agent**: `src/mas/agents/researcher.py`  
**Tool**: Price Scraper (`scrape_prices`)  
**Tool File**: `src/mas/tools/public_api.py`  
**Test File**: `tests/test_web_scraper_agent.py` (2 tests, PASS 2 passed)

**Quick Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest tests/test_web_scraper_agent.py -v
```

**Tool Details**:
- BeautifulSoup4-based HTML parsing
- Price regex extraction: `r"\$(\d+(?:\.\d{2})?)"`
- Shopify endpoint detection
- Offline mode with deterministic mock data
- Output: list of dicts with store/title/price/currency

**Evidence**: [docs/contributions/student_2.md](docs/contributions/student_2.md)  
**Key Commits**: `87f7a84`, `ca43650`  
**Challenges Faced**: Inconsistent HTML structures and extracting clean store/title/price/currency fields

---

## Student 3: Price Analyzer Agent

**Agent**: `src/mas/agents/budgeter.py`  
**Tool**: Price Analysis (`analyze_prices`)  
**Tool File**: `src/mas/tools/price_tools.py`  
**Test File**: `tests/test_price_analyzer_agent.py` (3 tests, PASS 3 passed)

**Quick Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest tests/test_price_analyzer_agent.py -v
```

**Tool Details**:
- Data validation and filtering (price > 0, valid numeric)
- Best price detection (minimum across sources)
- Statistical computation: min/max/average/sample_size
- Range consistency validation: min <= avg <= max
- Output: best_store, best_price, min_price, max_price, average_price

**Evidence**: [docs/contributions/student_3.md](docs/contributions/student_3.md)  
**Key Commits**: `c940a18`, `ca43650`  
**Challenges Faced**: Filtering invalid numeric values and keeping best price within computed range

---

## Student 4: Report Generator Agent

**Agent**: `src/mas/agents/risk_reporter.py`  
**Tools**:
  - Markdown Report: `save_markdown_file` (src/mas/tools/file_tools.py)
  - PDF Report: `save_report_pdf` (src/mas/tools/pdf_tools.py)
  - Safe Shell: `run_safe_shell` (src/mas/tools/shell_tools.py)

**Test File**: `tests/test_report_generator_agent.py` (2 tests, PASS 2 passed)

**Quick Run**:
```bash
& ".\.venv\Scripts\python.exe" -m pytest tests/test_report_generator_agent.py -v
```

**Tool Details**:
- Markdown file creation with parent directory handling
- PDF generation using ReportLab (A4 professional formatting)
- Safe shell execution with command allowlist (Get-ChildItem, dir, pwd, Get-Date)
- Output: final_report, saved_report_path, saved_report_pdf_path

**Evidence**: [docs/contributions/student_4.md](docs/contributions/student_4.md)  
**Key Commits**: `22a8d59`, `1ea4ff1`  
**Challenges Faced**: Preserving complete context in output and keeping Markdown/PDF artifacts synchronized

---

## Testing Summary

### Agent-Specific Tests
| Student | Agent | Test File | Tests | Status |
|---------|-------|-----------|-------|--------|
| 1 | Coordinator | test_coordinator_agent.py | 3 | PASS 3 passed |
| 2 | Web Scraper | test_web_scraper_agent.py | 2 | PASS 2 passed |
| 3 | Price Analyzer | test_price_analyzer_agent.py | 3 | PASS 3 passed |
| 4 | Report Generator | test_report_generator_agent.py | 2 | PASS 2 passed |

### Run All Agent Tests
```bash
& ".\.venv\Scripts\python.exe" -m pytest tests/test_coordinator_agent.py tests/test_web_scraper_agent.py tests/test_price_analyzer_agent.py tests/test_report_generator_agent.py -v
# Expected: 10 passed
```

### Shared Testing
- **Tool Unit Tests**: [tests/test_tools.py](tests/test_tools.py) - Validates scraping, analysis, file operations
- **End-to-End Smoke Test**: [tests/test_graph_smoke.py](tests/test_graph_smoke.py) - Full pipeline validation
- **Multi-Scenario Evaluation**: [evaluation.py](evaluation.py) - Coconut, rice, milk powder scenarios

### Master Reference
See [docs/TOOLS_AND_TESTING.md](docs/TOOLS_AND_TESTING.md) for comprehensive tool building and testing guide.

---

## Group-Level Notes
- **Unified architecture**: 4 agents in sequential LangGraph pipeline
- **Shared state**: TypedDict-based MASState ensures type safety
- **Observability**: JSONL trace files + JSON summaries in logs/
- **Offline mode**: All tests use deterministic mock data (MAS_OFFLINE_MODE=1)
- **Repository**: https://github.com/Tharushi-Nethmini/MAS
- **Architecture documentation**: [docs/architecture.md](docs/architecture.md)
- **Technical report**: [docs/technical_report_final.md](docs/technical_report_final.md)
