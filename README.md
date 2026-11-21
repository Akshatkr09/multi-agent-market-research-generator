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

## Benchmarking
Each run appends a record to `benchmarks.json`, including query, timestamps, status, total workflow duration, task completion intervals, assigned agent names, and chronological task-completion routing history. CrewAI's task callback fires at completion, so the per-task field is an observed completion interval (from kickoff or the previous callback), not a separately instrumented model-only duration.
The benchmark file is generated locally and is intentionally gitignored.

## Tests
```powershell
pytest -v
```
The test suite mocks external workflow calls and does not consume API credits.

## Architecture
See `docs/ARCHITECTURE.md` for agent responsibilities, data flow, evidence rules, and benchmark semantics.

## Sample outputs
Illustrative Markdown and PDF examples are in `sample_outputs/`. They use synthetic sample financial data and are not live market research. Refresh them from a real API-backed run before presenting them as actual research.

## GitHub Actions
The workflow in `.github/workflows/tests.yml` runs pytest on pushes and pull requests to `main`.

## Milestones
- [x] M1 — Project scaffold and configuration
- [x] M2 — Tavily web research and extraction tool
- [x] M3 — Financial CSV parser and statistical summaries
- [x] M4 — A4 PDF report generation
- [x] M5 — Hierarchical CrewAI architecture
- [x] M6 — End-to-end CLI execution
- [x] M7 — Benchmarking and execution tracking
- [x] M8 — Final documentation, sample outputs, and CI workflow
