# Multi-Agent Market Research & Report Generator

Python project using CrewAI, Gemini, Tavily, Pandas, and ReportLab. The project is being built milestone by milestone.

## Requirements
- Python 3.11 (64-bit recommended)
- Git
- Tavily API key for live research
- Gemini API key for later agent milestones

## Windows setup
```powershell
py -3.11 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Add keys to `.env`:
```env
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_gemini_api_key
```
Never commit `.env` or share its contents.

## M2: Web research tool
`tools/web_scraper.py` defines a CrewAI `@tool` that:
- Searches with Tavily using basic search depth.
- Requests raw page content using `include_raw_content=True`.
- Returns titles, source URLs, summaries, and extracted text.
- Limits extracted text to 10,000 characters per source.
- Handles missing API configuration and provider errors clearly.

Manual live test (uses Tavily API quota):
```powershell
python -c "from tools.web_scraper import web_research_tool; print(web_research_tool.run('Tech Sector Q3 Analysis'))"
```


## M3: Financial CSV parser
`tools/financial_parser.py` provides a CrewAI `@tool` named `Financial Data Parser`. It:
- Loads a CSV file with Pandas and selects numeric metric columns.
- Calculates count, mean, sample standard deviation, minimum, quartiles, and maximum.
- Returns the statistics as a Markdown table.
- Reports clear messages for missing, empty, malformed, or non-numeric input files.

The reusable functions `load_financial_data`, `calculate_summary`, `format_summary_markdown`, and `analyse_financial_csv` are also tested independently. Unit tests use temporary mock CSV files and do not require API keys or network access.


## M4: A4 PDF report compiler
`report/pdf_generator.py` uses ReportLab to compile a polished A4 PDF from report copy and an optional Markdown metrics table. It includes a dark header banner, document metadata, styled headings and body text, formatted tables, footer notes, and automatic `Page X of Y` numbering.

Example:
```python
from report.pdf_generator import compile_market_report

compile_market_report(
    title="Technology Sector Q3 Analysis",
    query="Tech Sector Q3 Analysis",
    report_text="# Executive Summary\\nYour report copy...",
    metrics_markdown="| Metric | Value |\\n|---|---:|\\n| Revenue mean | 120.5 |",
    output_path="output/market_report.pdf",
)
```

Run the PDF tests with `pytest -v tests/test_pdf_generator.py`. These tests create temporary PDFs and do not require API keys or network access.



## M5: Specialist agents and hierarchical orchestration
`crew/agents.py` defines the Lead Market Research Specialist, Financial Data Analyst, and Technical Market Research Report Writer. The researcher receives the Tavily tool, the analyst receives the Pandas financial parser, and the writer synthesizes their outputs. All agents use Gemini (`gemini/gemini-2.5-flash`).

`crew/tasks.py` defines three manager-assignable tasks. Their `agent` fields are intentionally left unset so CrewAI can dynamically delegate them. `crew/crew.py` builds a `Process.hierarchical` crew with `manager_llm` configured. This milestone builds the architecture; the runnable end-to-end CLI workflow is added in the next milestone.

The crew expects a CSV path. By default, the project sample file is `data/sample_financial_metrics.csv`. Set `GOOGLE_API_KEY` in `.env` before building/running the live crew.

## Tests
```powershell
pytest -v
```
M2 tests mock Tavily responses; they do not make network requests or consume API credits.

## Milestone status
- [x] M1 — Project scaffold and configuration
- [x] M2 — Tavily web research and extraction tool
- [x] M3 — Financial CSV parser and statistical summaries
- [x] M4 — A4 PDF report generation
- [x] M5 — Three specialist agents and hierarchical CrewAI architecture
- [ ] M6 — End-to-end CLI execution and report integration
- [ ] M7 — Benchmarks, routing history, and expanded tests
- [ ] M8 — Integration, documentation, sample outputs, and final validation

The original project brief remains the authoritative source for final acceptance criteria.
