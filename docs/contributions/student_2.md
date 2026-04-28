# Student 2: Web Scraper Agent - Tool Building & Testing

## Agent Overview
**Web Scraper Agent** (`src/mas/agents/researcher.py`) - Collects product prices from multiple online sources. Orchestrates scraping tools and returns normalized price listings.

---

## Tool Implementation

### Primary Tool: Price Scraper (`scrape_prices`)

**Location**: `src/mas/tools/public_api.py`  
**Function**: `scrape_prices(product_name: str, source_urls: list[str] | None = None, offline_mode: bool = False, model: str | None = None) -> list[dict[str, Any]]`

**Tool Functionality**:
1. **Source Detection**: Identifies Shopify endpoints and standard e-commerce sites
2. **HTML Fetching**: Retrieves product pages via `requests.get()`
3. **Price Extraction**: Uses BeautifulSoup4 to parse HTML and extract:
   - Store name
   - Product title
   - Price (with regex: `r"\$(\d+(?:\.\d{2})?)"`)
   - Currency
4. **Normalization**: Converts prices to float, validates numeric ranges
5. **Offline Mode**: Returns deterministic mock data when `MAS_OFFLINE_MODE=1`

**Input Parameters**:
```python
product_name="coconut",
source_urls=[],
offline_mode=True,
model="llama3:8b"
```

**Output Data Structure**:
```python
[
  {
    "store": "StoreA",
    "title": "Fresh Coconut 2kg",
    "price": 450.00,
    "currency": "LKR",
    "url": "https://store.example.com/coconut"
  },
  {"store": "StoreB", "price": 480.00, ...},
  ...
]
```

**Error Handling**:
- Network timeout (offline mode) -> returns fallback profile
- Invalid HTML -> skips malformed entries
- Missing price fields -> filters out incomplete items
- Currency mismatch -> normalizes to detected currency

---

## Testing & Evaluation

### Test File: `tests/test_web_scraper_agent.py`

**Run command**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_web_scraper_agent.py
```

**Test Cases**:

1. **test_web_scraper_agent_collects_offline_items** (PASS)
   - Scenario: Offline mode enabled (MAS_OFFLINE_MODE=1)
   - Input: product_name="coconut"
   - Expected: >=3 scraped_items with valid prices (> 0)
   - Validates: Scraper returns populated item list with correct structure
   - Checks:
     - scraped_items.length >= 3
     - Each item has "store", "title", "price" fields
     - price > 0 for all items
     - research_notes starts with "Collected"

2. **test_web_scraper_agent_handles_unknown_product_in_offline_mode** (PASS)
   - Scenario: Unknown product string in offline mode
   - Expected: fallback/dataset still provides usable positive price records
   - Validates: resilience when query has no direct product match

**Success Metrics**:
- PASS 2 passed
- Minimum 3 price points collected
- All prices are positive numbers
- Store names populated
- Item structure consistent

### Shared Tool Tests
Scraping behavior also validated in:
- `tests/test_tools.py` - `test_scrape_prices_offline_mode()`
- `tests/test_tools.py` - `test_scrape_prices_returns_valid_structure()`
- `evaluation.py` - Multi-scenario scraping (coconut, rice, milk powder)

**Run all scraper tests**:
```bash
& ".\\.venv\Scripts\python.exe" -m pytest -q tests/test_tools.py -k scrape -v
```

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Inconsistent HTML structures across sites | Implemented flexible BeautifulSoup selectors + regex price extraction |
| Network timeouts during scraping | Added offline mode with deterministic fallback profiles (demo mode) |
| Duplicate entries from multiple sources | Applied set-based deduplication on (store, title, price) tuples |
| Missing or malformed prices | Filter invalid items before returning results |
| Currency inconsistency | Detect and normalize currency field on per-store basis |

---

## Key Commits
- `87f7a84` - Web scraper agent + public_api.py scraping logic
- `ca43650` - HTML parsing + BeautifulSoup4 integration

---

## Viva Talking Points
1. **How does the scraper handle different website structures?**  
   -> BeautifulSoup flexible selectors + regex price extraction handles variations

2. **What happens if a website is down?**  
   -> Offline mode returns deterministic mock data; in production, skips unreachable sites

3. **How do you validate scraped prices?**  
   -> Check that price is numeric, > 0, and has valid currency; filter invalid entries

4. **How many sources do you typically scrape?**  
   -> Minimum 3 sources per product for robust price comparison

5. **How do you test scraping without hitting live sites?**  
   -> Run with MAS_OFFLINE_MODE=1 to use deterministic offline data and fallback profiles
