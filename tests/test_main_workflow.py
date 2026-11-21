"""Offline tests for the end-to-end CLI workflow."""
from types import SimpleNamespace
import main


class FakeCrew:
    def __init__(self, result):
        self.result = result
        self.kickoff_called = False
    def kickoff(self):
        self.kickoff_called = True
        return SimpleNamespace(raw=self.result)


def test_parse_args_uses_default_csv_and_output():
    args = main.parse_args(["--query", "Tech Sector Q3 Analysis"])
    assert args.query == "Tech Sector Q3 Analysis"
    assert args.csv.endswith("sample_financial_metrics.csv")
    assert args.output.endswith("market_report.pdf")


def test_run_workflow_generates_pdf_and_returns_path(tmp_path, monkeypatch):
    csv_file = tmp_path / "metrics.csv"
    csv_file.write_text("revenue,profit\n10,2\n20,4\n", encoding="utf-8")
    output_file = tmp_path / "report.pdf"
    fake_crew = FakeCrew("# Executive Summary\nA grounded market report.")
    captured = {}
    def fake_builder(query, csv_path, verbose=True, task_callback=None):
        captured["crew_args"] = (query, csv_path, verbose, task_callback)
        return fake_crew
    def fake_metrics(path):
        captured["metrics_path"] = path
        return "| statistic | revenue |\n|---|---:|\n| mean | 15.00 |"
    def fake_pdf(**kwargs):
        captured["pdf_args"] = kwargs
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(b"%PDF-1.4\n% mocked test PDF\n")
        return str(output_file)
    monkeypatch.setattr(main, "build_market_research_crew", fake_builder)
    monkeypatch.setattr(main, "analyse_financial_csv", fake_metrics)
    monkeypatch.setattr(main, "compile_market_report", fake_pdf)
    result = main.run_workflow("  Tech Sector Q3 Analysis  ", str(csv_file), str(output_file), str(tmp_path / "bench.json"))
    assert result == str(output_file)
    assert fake_crew.kickoff_called
    assert captured["crew_args"][0] == "Tech Sector Q3 Analysis"
    assert callable(captured["crew_args"][3])
    assert captured["pdf_args"]["report_text"].startswith("# Executive Summary")
    assert "mean" in captured["pdf_args"]["metrics_markdown"]


def test_run_workflow_rejects_missing_csv(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError, match="Financial CSV file not found"):
        main.run_workflow("topic", str(tmp_path / "missing.csv"), str(tmp_path / "out.pdf"))


def test_run_workflow_rejects_blank_query(tmp_path):
    import pytest
    csv_file = tmp_path / "metrics.csv"
    csv_file.write_text("revenue\n10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="query"):
        main.run_workflow("   ", str(csv_file), str(tmp_path / "out.pdf"))
