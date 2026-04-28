# Student 3: Price Analyzer Agent - Tool Building & Testing

## Agent Overview
**Price Analyzer Agent** (`src/mas/agents/budgeter.py`) - Performs statistical analysis on collected price data. Identifies best deals, computes price ranges, and generates insights.

---

## Tool Implementation

### Primary Tool: Price Analysis (`analyze_prices`)

**Location**: `src/mas/tools/price_tools.py`  
**Function**: `analyze_prices(items: list[dict[str, Any]]) -> dict[str, Any]`

**Tool Functionality**:
1. **Data Validation**: Filters items with:
   - Valid numeric price (not None, not NaN)
   - Price > 0
   - Non-empty store name
2. **Best Price Detection**: Finds minimum price + associated store
3. **Statistical Computation**:
   - `min_price`: Lowest price across all sources
   - `max_price`: Highest price across all sources
   - `average_price`: Mean of all valid prices
   - `sample_size`: Count of valid items analyzed
4. **Result Packaging**: Returns normalized dict with all metrics

**Input Data Structure**:
```python
scraped_items=[
  {"store": "StoreA", "price": 450.00, "title": "Coconut 2kg"},
  {"store": "StoreB", "price": 480.00, "title": "Coconut 2kg"},
  {"store": "StoreC", "price": 420.00, "title": "Coconut 2kg"},
]
```

**Output Analysis Result**:
```python
{
  "best_store": "StoreC",
  "best_price": 420.00,
  "min_price": 420.00,
  "max_price": 480.00,
  "average_price": 450.00,
  "sample_size": 3,
  "price_range_valid": True  # min <= max
}
```

**Validation Rules**:
- `min_price <= max_price` (always true)
- `min_price <= average_price <= max_price` (statistical consistency)
- `sample_size >= 1` (at least one valid item)
- `best_price == min_price` (best = cheapest)

---

## Testing & Evaluation

### Test File: `tests/test_price_analyzer_agent.py`

**Run command**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_price_analyzer_agent.py
```

**Test Cases**:

1. **test_budget_agent_finds_best_price** (PASS)
   - Scenario: Multiple stores with varying prices
   - Input items: StoreA=200, StoreB=150, StoreC=175
   - Expected: best_store="StoreB", best_price=150
   - Validates: Correct minimum detection and store attribution
   - Assertions:
     - best_store == "StoreB"
     - best_price == 150
     - min_price == 150
     - max_price == 200
     - average_price ~= 175

2. **test_price_analyzer_agent_handles_invalid_items** (PASS)
   - Scenario: Mixed valid/invalid price data
   - Input items: StoreA=valid(111), StoreB=None, StoreC=valid(111), StoreD=0 (invalid)
   - Expected: Only StoreA and StoreC counted; StoreB and StoreD filtered
   - Validates: Invalid data exclusion before analysis
   - Assertions:
     - sample_size == 2 (not 4)
     - best_price == 111
     - average_price == 111

3. **test_price_analyzer_agent_handles_all_invalid_prices** (PASS)
   - Scenario: All records invalid (`None`, malformed string, zero)
   - Expected: agent returns safe fallback (`best_store="N/A"`, `best_price=0.0`)
   - Validates: secure fail-closed behavior for fully invalid inputs

**Success Metrics**:
- PASS 3 passed
- Correct min/max detection
- Invalid items filtered properly
- Price ranges consistent (min <= avg <= max)
- Store attribution correct

### Shared Tool Tests
Analysis behavior also validated in:
- `tests/test_tools.py` - `test_analyze_prices_returns_correct_structure()`
- `tests/test_tools.py` - `test_analyze_prices_filters_invalid_items()`
- `evaluation.py` - Multi-scenario analysis (coconut, rice, milk powder)

**Run all analyzer tests**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_tools.py -k analyze -v
```

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Invalid/missing price values | Filter items with None, NaN, or 0 prices before analysis |
| Store name inconsistency | Normalize store names; handle empty/whitespace values |
| Outlier prices skewing average | Implemented range validation to catch inconsistent data |
| Type coercion errors | Convert prices to float early; validate before computation |
| Empty item list | Return default error state or skip analysis gracefully |

---

## Key Commits
- `c940a18` - Price analyzer agent + analyze_prices() implementation
- `ca43650` - Data validation + filtering logic

---

## Viva Talking Points
1. **How do you identify the best price?**  
   -> Find minimum price across all valid items, return associated store name

2. **How do you handle invalid price data?**  
   -> Filter items with None, NaN, or <=0 prices before computation

3. **What validation do you apply to results?**  
   -> Ensure min <= average <= max; sample_size >= 1; all prices numeric

4. **How do you test price analysis?**  
   -> Run: `pytest tests/test_price_analyzer_agent.py` -> Validates best-price detection + filtering

5. **What if all prices are the same?**  
   -> All stats are identical; best_price = average_price; no concern
