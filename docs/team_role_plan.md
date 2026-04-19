# Team Role Plan (4 Members)

## Member A
- Agent ownership: Coordinator Agent
- Tool ownership: input parsing and product normalization helper
- Required tests:
  - product extraction from standard request
  - fallback behavior for ambiguous request

## Member B
- Agent ownership: Web Scraper Agent
- Tool ownership: scrape_prices and HTML extraction routines
- Required tests:
  - offline catalog extraction
  - malformed HTML handling

## Member C
- Agent ownership: Price Analyzer Agent
- Tool ownership: analyze_prices
- Required tests:
  - valid statistics computation
  - no-valid-price error handling

## Member D
- Agent ownership: Report Generator Agent
- Tool ownership: save report and run summary observability artifact
- Required tests:
  - report file creation
  - summary JSON creation

## Shared Deliverables
- docs/technical_report_draft.md
- docs/video_script.md
- docs/architecture.md
- evaluation.py multi-case scoring
