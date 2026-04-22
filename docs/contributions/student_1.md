# Student 1: Coordinator Agent - Tool Building & Testing

## Agent Overview
**Coordinator Agent** (`src/mas/agents/coordinator.py`) - Orchestrates the workflow initiation by extracting and normalizing the user's product query. Acts as the entry point of the multi-agent system.

---

## Tool Implementation

### Primary Tool: Request Normalization

**Location**: `src/mas/agents/coordinator.py`  
**Function**: `coordinator_agent(state: MASState) -> dict`

**Tool Functionality**:
1. **Regex Pattern Extraction**: Applies patterns like `r"(for|of)\s+([\w\s]+?)(?:\s+in|$)"` to extract product names
2. **Keyword Fallback**: If regex fails, uses keyword lists ("coconut", "rice", "milk powder") as fallback
3. **LLM Refinement**: Sends extracted names to Ollama for validation and normalization
4. **State Initialization**: Populates `product_name` and `normalized_product_query` fields in MASState

**Input State**:
```python
{
  "user_request": "Compare prices for coconut in Colombo",
  "trace_id": "abc123"
}
```

**Output State**:
```python
{
  "product_name": "coconut",
  "normalized_product_query": "coconut",
  "source_urls": [...]
}
```

**Error Handling**:
- Empty request → defaults to "coconut"
- LLM failure → uses keyword-based fallback
- Invalid regex match → applies keyword list

---

## Testing & Evaluation

### Test File: `tests/test_coordinator_agent.py`

**Run command**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_coordinator_agent.py
```

**Test Cases**:

1. **test_coordinator_agent_extracts_product_name** (PASS)
   - Input: "Compare prices for coconut"
   - Expected: product_name = "coconut", normalized_product_query = "coconut"
   - Validates: Regex extraction + LLM refinement pipeline
   - Checks:
     - product_name matches normalized_product_query
     - source_urls preserved

2. **test_coordinator_agent_uses_fallback_for_empty_request** (PASS)
   - Input: empty user_request=""
   - Expected: product_name = "coconut" (fallback)
   - Validates: Fallback mechanism when request is malformed

**Success Metrics**:
- ✅ 2 passed in 0.04s
- Normalized query matches product name
- Fallback activates for edge cases
- source_urls preserved in output state

### Shared Evaluation
Coordinator behavior also validated in:
- `evaluation.py` - Product extraction scenario
- `tests/test_graph_smoke.py` - End-to-end pipeline

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Vague user requests (e.g., "find me the best deals") | Implemented keyword fallback list + LLM-based validation |
| Uppercase/lowercase inconsistency | Normalized output to lowercase before LLM refinement |
| Missing product context | Default fallback to "coconut" ensures pipeline continuity |
| State mutation risks | Used TypedDict to enforce immutable state schema |

---

## Key Commits
- `ca43650` - Coordinator agent + request normalization logic
- `c940a18` - Fallback extraction patterns + LLM refinement integration

---

## Viva Talking Points
1. **How does request normalization work?**  
   → Uses regex patterns first, falls back to keyword list, then validates with LLM

2. **What happens if the user gives a vague request?**  
   → System extracts best-match keyword and refines via LLM; if still ambiguous, uses "coconut" fallback

3. **Where is the extracted product name used?**  
   → Passed to Web Scraper agent via `normalized_product_query` field to guide search

4. **How do you test request normalization?**  
   → Run: `pytest tests/test_coordinator_agent.py` → Validates extraction + fallback scenarios
