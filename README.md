# Multi-Agent Market Research & Report Generator

A Python application built with CrewAI, Gemini, Tavily, Pandas, and ReportLab.

This repository is being developed in milestones. **M1 establishes the project scaffold and configuration only**; research tools, agents, orchestration, PDF generation, and full tests will be added in later milestones.

## Requirements

- Python 3.11 (64-bit recommended)
- Git
- Google Gemini API key
- Tavily API key

## Setup (Windows PowerShell)

1. Extract this ZIP into your project location.
2. Open the extracted folder in VS Code.
3. Create and activate a virtual environment:

   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and add your API keys:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` locally. Never commit it or share its contents.

## Configuration

`.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

The project will use Gemini through CrewAI's Google GenAI integration. API free-tier availability and limits are controlled by the providers and may change.

## Current milestone

**M1 — Project scaffold**

- Standard package layout
- Environment-variable template
- Dependency manifest
- CLI entry-point placeholder
- Initial test scaffold
- Git ignore rules

The application intentionally reports that the full workflow is not implemented yet. Do not treat M1 as the completed assignment.

## Planned execution command

The final project will support:

```powershell
python main.py --query "Tech Sector Q3 Analysis"
```

## Tests

```powershell
pytest
```

M1 includes only scaffold/configuration tests. The assignment's required Pandas and PDF tests will be added in their respective milestones.

## Evaluation requirements tracked

The original project brief requires:

1. Three specialist agents under CrewAI hierarchical orchestration with a manager LLM.
2. Custom web research/scraping and Pandas financial-statistics tools.
3. A formatted A4 PDF with header, tables, footer, and page numbering.
4. `benchmarks.json` with task durations and routing history, plus pytest tests.
5. Clean project structure, `.env.example`, at least eight meaningful Git commits, and README instructions.

See the original project brief for the authoritative acceptance criteria.
