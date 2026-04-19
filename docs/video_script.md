# Demo Video Script (Target: 4 minutes 30 seconds)

## 0:00 - 0:30 Opening
Speaker line:
"We are presenting our AI-Based Smart Price Comparison Multi-Agent System built fully on local resources for CTSE Assignment 2. Our system automates product price comparison across multiple sources using four collaborating agents."

On screen:
- Project title slide
- Team member names

## 0:30 - 1:15 Architecture
Speaker line:
"The system runs as a LangGraph pipeline with four agents: Coordinator, Web Scraper, Price Analyzer, and Report Generator. The user gives a product query, each agent updates shared global state, and the final report is generated automatically."

On screen:
- docs/architecture.md diagram
- Brief highlight of each agent responsibility

## 1:15 - 2:20 Live Execution
Speaker line:
"Now we run the complete workflow locally in offline mode for stable demonstration results."

Command:
- $env:MAS_OFFLINE_MODE="1"; python -m src.mas.main --request "Compare prices for coconut" --model llama3:8b

Explain while output appears:
- Trace ID generated
- Report file path returned
- Run summary file path returned

## 2:20 - 3:10 Generated Outputs
Speaker line:
"The Report Generator creates a structured markdown output containing product details, scraped entries, best price, and statistics."

On screen:
- reports/price_report_<trace_id>.md
- logs/trace_<trace_id>.jsonl
- logs/summary_<trace_id>.json

Key commentary:
- Show at least one tool_call log event
- Show agent_output transitions

## 3:10 - 4:00 Testing and Evaluation
Speaker line:
"We validate reliability with tool tests, graph smoke tests, and a multi-case evaluation harness for coconut, rice, and milk powder."

Commands:
- pytest -q
- python evaluation.py

Explain:
- Security check verifies unsafe shell commands are blocked
- Statistical checks verify best price is inside computed range

## 4:00 - 4:30 Contribution and Closing
Speaker line:
"Each team member implemented one agent, one tool, and related tests. Contribution evidence is documented in our repository. This demonstrates local, zero-cost, observable multi-agent automation for a practical real-world problem."

On screen:
- CONTRIBUTIONS.md
- docs/contributions/student_1.md ... student_4.md
