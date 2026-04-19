# Technical Report Template (4-8 Pages)

## 1. Problem Domain
- Domain selected:
- Why this problem matters:
- Why a MAS is better than a single agent:

## 2. System Architecture
- High-level architecture description
- Multi-agent orchestration model (sequential/delegation)
- Workflow diagram (insert figure)
- Agent roles and responsibilities

## 3. Agent Design
For each agent, include:
- Agent name
- System prompt
- Persona
- Constraints/safety rules
- Input schema
- Output schema
- Reasoning/interaction strategy

## 4. Tooling
For each custom tool, include:
- Tool name
- Purpose
- Type hints and signature
- Error handling strategy
- Example call and response

## 5. State Management
- Global state structure (`MASState`)
- Which fields are produced/consumed by each agent
- How context is preserved between handoffs

## 6. Observability (LLMOps/AgentOps)
- Logging/tracing strategy
- What events are recorded
- Sample trace log snippet

## 7. Testing and Evaluation
- Unified test harness design
- Individual test cases per student
- Evaluation metrics and pass criteria
- Reliability and failure analysis

## 8. Student Contributions
For each student:
- Agent developed
- Tool implemented
- Test cases written
- Challenges faced and resolution

## 9. Repository Link
- GitHub/GitLab:
