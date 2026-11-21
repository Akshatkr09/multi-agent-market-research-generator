# Multi-Agent Market Research & Report Generator

Python project using CrewAI, Gemini, Tavily, Pandas, and ReportLab.

**M2 adds a Tavily-powered web research and extraction tool.** Specialist agents, hierarchical orchestration, financial parsing, PDF generation, and benchmarking are planned for later milestones.

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

## Tests
```powershell
pytest -v
```
M2 tests mock Tavily responses; they do not make network requests or consume API credits.

## Milestone status
- [x] M1 — Project scaffold and configuration
- [x] M2 — Tavily web research and extraction tool
- [ ] M3 — Financial CSV parser and statistical summaries
- [ ] M4 — Three specialist agents and task definitions
- [ ] M5 — Hierarchical CrewAI orchestration and CLI execution
- [ ] M6 — A4 PDF report generation
- [ ] M7 — Benchmarks, routing history, and expanded tests
- [ ] M8 — Integration, documentation, sample outputs, and final validation

The original project brief remains the authoritative source for final acceptance criteria.
