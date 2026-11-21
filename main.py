"""Command-line entry point for the market research workflow."""
import argparse
from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR, PROJECT_ROOT
from crew.crew import build_market_research_crew
from report.pdf_generator import compile_market_report
from tools.financial_parser import analyse_financial_csv
from utils.benchmark import BenchmarkRecorder


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research & Report Generator"
    )
    parser.add_argument("--query", required=True, help='Research topic, e.g. "Tech Sector Q3 Analysis"')
    parser.add_argument(
        "--csv", default=str(DATA_DIR / "sample_financial_metrics.csv"),
        help="Path to a financial metrics CSV (defaults to the bundled sample).",
    )
    parser.add_argument(
        "--output", default=str(OUTPUT_DIR / "market_report.pdf"),
        help="Destination for the generated PDF.",
    )
    parser.add_argument(
        "--benchmarks", default=str(PROJECT_ROOT / "benchmarks.json"),
        help="JSON file used to store execution benchmarks.",
    )
    return parser.parse_args(argv)


def run_workflow(query: str, csv_path: str, output_path: str, benchmark_path=None):
    """Run the hierarchical crew, compile its report, and persist benchmark data."""
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("The research query must not be empty.")
    csv_file = Path(csv_path).expanduser()
    if not csv_file.is_file():
        raise FileNotFoundError(f"Financial CSV file not found: {csv_file}")

    recorder = BenchmarkRecorder(benchmark_path or PROJECT_ROOT / "benchmarks.json")
    recorder.start_run(clean_query, str(csv_file), str(output_path))
    try:
        print("[1/3] Initializing Gemini-powered hierarchical CrewAI manager...")
        crew = build_market_research_crew(
            clean_query, str(csv_file), verbose=True,
            task_callback=recorder.record_task_completion,
        )
        print("[2/3] Manager is coordinating specialist task delegation...")
        result = crew.kickoff()
        report_text = getattr(result, "raw", None) or str(result)
        if not str(report_text).strip():
            raise RuntimeError("The crew completed without producing report content.")

        print("[3/3] Compiling the final A4 PDF report...")
        metrics_markdown = analyse_financial_csv(csv_file)
        title = f"{clean_query} — Market Research Report"
        pdf_path = compile_market_report(
            title=title, query=clean_query, report_text=str(report_text),
            metrics_markdown=metrics_markdown, output_path=output_path,
        )
        if not Path(pdf_path).is_file():
            raise RuntimeError("PDF compiler returned, but the output file was not found.")
        recorder.finish_run("success")
        print(f"Report generated successfully: {pdf_path}")
        print(f"Benchmark history updated: {recorder.path.resolve()}")
        return pdf_path
    except Exception as exc:
        recorder.finish_run("failed", error=f"{type(exc).__name__}: {exc}")
        raise


def main(argv=None):
    args = parse_args(argv)
    try:
        run_workflow(args.query, args.csv, args.output, args.benchmarks)
    except Exception as exc:
        print(f"Workflow failed: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
