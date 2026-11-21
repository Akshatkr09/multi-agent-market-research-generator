# Multi-Agent Market Research & Report Generator

Python project using CrewAI, Gemini, Tavily, Pandas, and ReportLab.

## Requirements
- Python 3.11 (64-bit recommended)
- Git
- Tavily API key for live research
- Gemini API key for live agent orchestration

## Windows setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Add `TAVILY_API_KEY` and `GOOGLE_API_KEY` to `.env`. Never commit `.env`.

## Run
```powershell
python main.py --query "Tech Sector Q3 Analysis"
```
Default CSV: `data/sample_financial_metrics.csv`; default PDF: `output/market_report.pdf`.
Use `--csv`, `--output`, and `--benchmarks` to override paths.

## Benchmarking (M7)
Each run appends a record to `benchmarks.json`, including query, timestamps, status, total workflow duration, task completion intervals, assigned agent names, and chronological task-completion routing history. Task callbacks occur at completion, so the per-task field is explicitly an observed completion interval (from kickoff or the previous callback), not a separately instrumented model-only duration.

The benchmark file is generated locally and is intentionally gitignored.

## Tests
```powershell
pytest -v
```
The test suite mocks external workflow calls and does not consume API credits.

## Milestones
- [x] M1 — Project scaffold and configuration
- [x] M2 — Tavily web research and extraction tool
- [x] M3 — Financial CSV parser and statistical summaries
- [x] M4 — A4 PDF report generation
- [x] M5 — Hierarchical CrewAI architecture
- [x] M6 — End-to-end CLI execution
- [x] M7 — Benchmarking and execution tracking
- [ ] M8 — Final integration, documentation, sample outputs, and validation
