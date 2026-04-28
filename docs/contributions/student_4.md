# Student 4: Report Generator Agent - Tool Building & Testing

## Agent Overview
**Report Generator Agent** (`src/mas/agents/risk_reporter.py`) - Transforms analysis results into human-readable reports. Generates Markdown documentation and PDF files with visualizations.

---

## Tool Implementation

### Primary Tools: Report Generation Toolkit

#### Tool 1: Markdown Report (`save_markdown_file`)
**Location**: `src/mas/tools/file_tools.py`  
**Function**: `save_markdown_file(file_path: str, content: str) -> str`

**Functionality**:
1. **Path Handling**: Creates parent directories if missing (mkdir -p behavior)
2. **Content Writing**: Writes formatted markdown to disk
3. **Validation**: Confirms file exists post-write
4. **Return**: Absolute path to created file

**Input Example**:
```python
file_path="reports/price_report_demo_123.md",
content="""# AI-Based Smart Price Comparison Report

## Product: Coconut
## Best Store: StoreC
## Best Price: LKR 420.00
"""
```

**Output**:
```
reports/price_report_demo_123.md (created)
```

---

#### Tool 2: PDF Report (`save_report_pdf`)
**Location**: `src/mas/tools/pdf_tools.py`  
**Function**: `save_report_pdf(path: str, title: str, content: str) -> str`

**Functionality**:
1. **PDF Creation**: Uses ReportLab to render markdown content as A4 PDF
2. **Styling**: Applies professional formatting with headers, tables, spacing
3. **Content Embedding**: Includes all analysis summary, store data, price ranges
4. **File Generation**: Saves to specified path

**Input Example**:
```python
file_path="reports/price_report_demo_123.pdf",
content="Same markdown content"
```

**Output**:
```
reports/price_report_demo_123.pdf (created)
```

---

#### Tool 3: Shell Execution (`run_safe_shell`)
**Location**: `src/mas/tools/shell_tools.py`  
**Function**: `run_safe_shell(command: str) -> str`

**Functionality**:
1. **Command Allowlisting**: Only allows safe commands (Get-ChildItem, dir, pwd, Get-Date, Get-Location)
2. **Injection Prevention**: Blocks dangerous commands (rm, del, curl, etc.)
3. **Output Capture**: Returns command stdout
4. **Trace Logging**: Records shell snapshot in trace file

**Allowed Commands**:
- `Get-ChildItem` - List files
- `dir` - List files (Windows)
- `pwd` / `Get-Location` - Show current directory
- `Get-Date` - Show timestamp

**Blocked Commands**:
- `rm`, `del`, `Remove-Item` - Deletion
- `curl`, `wget`, `Invoke-WebRequest` - Downloads
- `pip install`, `npm install` - Package managers

---

### Report Content Schema

Final report includes:
```markdown
# AI-Based Smart Price Comparison Report

## Executive Summary
- Product searched: {product_name}
- Best price available: LKR {best_price}
- Available at: {best_store}
- Price range: LKR {min_price} - {max_price}
- Average market price: LKR {average_price}

## Store Comparison
| Store | Price | Title |
|-------|-------|-------|
| StoreC | 420.00 | Fresh Coconut 2kg |
| StoreA | 450.00 | Premium Coconut |

## Analysis Summary
{analysis_summary}
```

---

## Testing & Evaluation

### Test File: `tests/test_report_generator_agent.py`

**Run command**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_report_generator_agent.py
```

**Test Cases**:

1. **test_report_generator_agent_writes_report_files** (PASS)
   - Scenario: Generate report with temporary directory
   - Input: Complete MASState with all analysis results
   - Expected: 
     - Markdown file created at reports/price_report_*.md
     - PDF file created at reports/price_report_*.pdf
     - Both files contain expected content
   - Validates: File creation and content accuracy
   - Assertions:
     - saved_report_path exists
     - saved_report_pdf_path exists
     - Markdown contains "AI-Based Smart Price Comparison Report"
     - Markdown contains best_store name
     - PDF file size > 1000 bytes (valid PDF)
     - Shell snapshot captured in trace

2. **test_report_generator_agent_handles_shell_tool_failure** (PASS)
   - Scenario: shell tool raises runtime error
   - Expected: report generation still completes and includes fallback shell error note
   - Validates: graceful degradation and reliability under tool failure

**Success Metrics**:
- PASS 2 passed
- Markdown file created
- PDF file created
- Report content contains all required sections
- Shell execution tracked
- File paths returned correctly

### Shared Evaluation Tests
Report generation also validated in:
- `tests/test_graph_smoke.py` - Full pipeline end-to-end
- `evaluation.py` - Multi-scenario report generation (coconut, rice, milk powder)

**Run all generator tests**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_report_generator_agent.py -v
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_graph_smoke.py -v
```

**Verify generated reports**:
```bash
Get-ChildItem reports/ -Filter "price_report_*.md"
Get-ChildItem reports/ -Filter "price_report_*.pdf"
```

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| PDF generation complexity | Used ReportLab library for professional A4 formatting |
| Markdown-to-PDF conversion fidelity | Implemented custom ReportLab builders to preserve content |
| Shell injection attacks | Implemented strict allowlist of safe commands; block all else |
| File path handling across OS | Used pathlib.Path for cross-platform compatibility |
| State serialization in output | TypedDict schema ensures all fields present in final report |
| Race conditions on file write | Use unique trace_id in filename; atomic write operations |

---

## Key Commits
- `22a8d59` - Report generator agent + Markdown generation
- `1ea4ff1` - PDF generation + file tools implementation

---

## Viva Talking Points
1. **What information goes into the final report?**  
   -> Product name, best store, best price, price range, average price, full store comparison table

2. **How do you ensure Markdown and PDF stay synchronized?**  
   -> Single content source; generate both from same markdown template

3. **Why allowlist shell commands instead of blacklist?**  
   -> Allowlist is more secure-only explicitly safe commands allowed; blacklist can be bypassed

4. **How do you handle file creation errors?**  
   -> Create parent dirs if missing; validate file exists post-write; return path or error

5. **How do you test report generation without manual inspection?**  
   -> Run: `pytest tests/test_report_generator_agent.py` -> Validates file existence + content assertions

6. **Where are reports saved?**  
   -> reports/ directory with naming: `price_report_{trace_id}.md` and `.pdf`
