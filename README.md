# Multi-Agent Market Research & Report Generator

Python project using CrewAI, Gemini, Tavily, Pandas, and ReportLab. The project is being built milestone by milestone.

## Requirements
- Python 3.11 (64-bit recommended)
- Git
- Tavily API key for live research
- Gemini API key for live agent orchestration

## Windows setup
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
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

## Running the workflow (M6)
Run a complete research workflow from the project root:
```powershell
python main.py --query "Tech Sector Q3 Analysis"
```
By default, the workflow uses `data/sample_financial_metrics.csv` and writes `output/market_report.pdf`.

Optional CSV and output paths:
```powershell
python main.py --query "Tech Sector Q3 Analysis" --csv "data/sample_financial_metrics.csv" --output "output/tech_q3_report.pdf"
```
The CLI validates the query and CSV path, initializes the Gemini-powered hierarchical crew, runs manager-coordinated specialist tasks, compiles the final report and Pandas statistics into an A4 PDF, and prints the output path. Live execution requires valid Gemini and Tavily API keys in `.env`; it can consume provider quota.

## M2: Web research tool
`tools/web_scraper.py` defines a CrewAI `@tool` that searches with Tavily, requests raw page content, returns source URLs and extracted text, and limits extracted text to 10,000 characters per source.

## M3: Financial CSV parser
`tools/financial_parser.py` loads CSV data with Pandas, selects numeric metric columns, calculates descriptive statistics, and returns a Markdown table. It reports clear errors for missing, empty, malformed, or non-numeric input files.

## M4: A4 PDF report compiler
`report/pdf_generator.py` uses ReportLab to compile a polished A4 PDF with a header banner, document metadata, styled headings and body text, formatted tables, footer notes, and automatic `Page X of Y` numbering.

## M5: Specialist agents and hierarchical orchestration
`crew/agents.py` defines the Lead Market Research Specialist, Financial Data Analyst, and Technical Market Research Report Writer. The researcher receives the Tavily tool, the analyst receives the Pandas parser, and the writer synthesizes their outputs. All agents use Gemini (`gemini/gemini-2.5-flash`).

`crew/tasks.py` defines three manager-assignable tasks without fixed agent assignments. `crew/crew.py` builds a `Process.hierarchical` crew with `manager_llm` configured.

## Tests
```powershell
pytest -v
```
Unit tests mock external workflow calls and do not consume API credits.

## Milestone status
- [x] M1 — Project scaffold and configuration
- [x] M2 — Tavily web research and extraction tool
- [x] M3 — Financial CSV parser and statistical summaries
- [x] M4 — A4 PDF report generation
- [x] M5 — Three specialist agents and hierarchical CrewAI architecture
- [x] M6 — End-to-end CLI execution and report integration
- [ ] M7 — Benchmarks, routing history, and expanded tests
- [ ] M8 — Integration, documentation, sample outputs, and final validation

The original project brief remains the authoritative source for final acceptance criteria.
