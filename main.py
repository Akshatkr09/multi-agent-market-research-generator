"""Command-line entry point for the market research workflow."""
import argparse
from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR
from crew.crew import build_market_research_crew
from report.pdf_generator import compile_market_report
from tools.financial_parser import analyse_financial_csv


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research & Report Generator"
    )
    parser.add_argument("--query", required=True, help='Research topic, e.g. "Tech Sector Q3 Analysis"')
    parser.add_argument(
        "--csv",
        default=str(DATA_DIR / "sample_financial_metrics.csv"),
        help="Path to a financial metrics CSV (defaults to the bundled sample).",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_DIR / "market_report.pdf"),
        help="Destination for the generated PDF.",
    )
    return parser.parse_args(argv)


def run_workflow(query: str, csv_path: str, output_path: str):
    """Run the hierarchical crew, compile its report, and return the PDF path."""
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("The research query must not be empty.")
    csv_file = Path(csv_path).expanduser()
    if not csv_file.is_file():
        raise FileNotFoundError(f"Financial CSV file not found: {csv_file}")

    print("[1/3] Initializing Gemini-powered hierarchical CrewAI manager...")
    crew = build_market_research_crew(clean_query, str(csv_file), verbose=True)

    print("[2/3] Manager is coordinating specialist task delegation...")
    result = crew.kickoff()
    report_text = getattr(result, "raw", None) or str(result)
    if not str(report_text).strip():
        raise RuntimeError("The crew completed without producing report content.")

    print("[3/3] Compiling the final A4 PDF report...")
    metrics_markdown = analyse_financial_csv(csv_file)
    title = f"{clean_query} — Market Research Report"
    pdf_path = compile_market_report(
        title=title,
        query=clean_query,
        report_text=str(report_text),
        metrics_markdown=metrics_markdown,
        output_path=output_path,
    )
    print(f"Report generated successfully: {pdf_path}")
    return pdf_path


def main(argv=None):
    args = parse_args(argv)
    try:
        run_workflow(args.query, args.csv, args.output)
    except Exception as exc:
        print(f"Workflow failed: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
