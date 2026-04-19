# Individual Contribution Tracker

Each student should own one agent, one tool, and one test set.

## Student 1
- Agent: Coordinator Agent
- Tool: Query normalization helper in coordinator workflow
- Tests: Coordinator extraction and normalization checks
- Evidence: commit links and pull request ID
- Challenges faced: handling vague user queries

## Student 2
- Agent: Web Scraper Agent
- Tool: BeautifulSoup scraping tool in src/mas/tools/public_api.py
- Tests: offline scraping extraction checks
- Evidence: commit links and pull request ID
- Challenges faced: inconsistent HTML structures

## Student 3
- Agent: Price Analyzer Agent
- Tool: analyze_prices in src/mas/tools/price_tools.py
- Tests: min/max/avg and best-price consistency checks
- Evidence: commit links and pull request ID
- Challenges faced: filtering invalid numeric values

## Student 4
- Agent: Report Generator Agent
- Tool: report persistence and run summary generation
- Tests: report path creation and evaluation suite checks
- Evidence: commit links and pull request ID
- Challenges faced: preserving complete context in final output

## Group-Level Notes
- Unified test harness: tests/ and evaluation.py
- Shared architecture and observability evidence: docs/architecture.md and logs/
- Final report and demo responsibility: completed collaboratively
