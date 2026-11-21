# Architecture and Implementation Notes

## Workflow

1. The CLI accepts a research query and a financial CSV path.
2. `build_market_research_crew` creates three specialist agents and three manager-assignable tasks.
3. CrewAI runs the crew with `Process.hierarchical` and a Gemini manager LLM.
4. The Lead Market Research Specialist uses the Tavily-backed web research tool to collect source URLs and extracted page text.
5. The Financial Data Analyst uses the Pandas parser to calculate descriptive statistics from the supplied CSV.
6. The Technical Market Research Report Writer synthesizes the available research and metrics into a structured report.
7. ReportLab compiles the report and Pandas summary into an A4 PDF.
8. `BenchmarkRecorder` appends run-level duration, task completion observations, status, and routing history to `benchmarks.json`.

## Agent responsibilities

| Agent | Responsibility | Tool |
|---|---|---|
| Lead Market Research Specialist | Gather current market context and cite sources | Web Research and Extraction |
| Financial Data Analyst | Validate numeric columns and summarize financial metrics | Financial Data Parser |
| Technical Market Research Report Writer | Produce a balanced, structured Markdown report | No external tool |

## Data and evidence rules

- Cite source URLs and dates where available.
- Distinguish observed facts from estimates and interpretation.
- Do not invent missing financial values.
- State when a requested detail could not be verified.
- Keep the supplied CSV as the source of truth for the financial summary table.

## Benchmarking semantics

The workflow records total run duration directly. CrewAI's task callback is invoked when a task completes, so the recorded `completion_interval_seconds` is the elapsed interval since kickoff or the previous callback. It is an observed completion interval, **not** a precise isolated model execution duration. Routing history records the observed task completion order and assigned agent.

## Local validation

```powershell
pytest -v
python main.py --query "Tech Sector Q3 Analysis"
Get-Content .\benchmarks.json
```

The tests mock external calls and should not consume Gemini or Tavily API credits. The CLI run requires valid API keys and network access.
