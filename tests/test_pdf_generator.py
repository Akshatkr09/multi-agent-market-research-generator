"""Tests for the ReportLab market report compiler."""
from pathlib import Path
import pytest
from report.pdf_generator import compile_market_report


def test_pdf_compiler_creates_valid_pdf(tmp_path):
    output = tmp_path / "market_report.pdf"
    result = compile_market_report(
        title="Technology Sector Q3 Analysis", query="Tech Sector Q3 Analysis",
        report_text="# Executive Summary\nTechnology companies showed mixed performance during the quarter.\n## Key Findings\n- Revenue growth varied across companies.\n- Profitability remained an important differentiator.",
        metrics_markdown="| Statistic | Revenue |\n|---|---:|\n| mean | 120.50 |\n| min | 98.00 |\n| max | 145.20 |",
        output_path=str(output),
    )
    assert Path(result).exists()
    assert Path(result).stat().st_size > 500
    assert Path(result).read_bytes().startswith(b"%PDF")


def test_pdf_compiler_creates_parent_directory(tmp_path):
    output = tmp_path / "nested" / "reports" / "report.pdf"
    compile_market_report(title="Sample Report", report_text="A short report body.", output_path=str(output))
    assert output.exists()


def test_pdf_compiler_rejects_empty_content(tmp_path):
    with pytest.raises(ValueError, match="Provide report text or a metrics table"):
        compile_market_report(title="Empty Report", report_text="", metrics_markdown="", output_path=str(tmp_path / "empty.pdf"))


def test_pdf_compiler_rejects_empty_title(tmp_path):
    with pytest.raises(ValueError, match="title"):
        compile_market_report(title=" ", report_text="Some report text.", output_path=str(tmp_path / "no-title.pdf"))
