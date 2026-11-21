"""Tests for financial CSV loading and Pandas summary statistics."""
import pandas as pd
import pytest
from tools.financial_parser import analyse_financial_csv, calculate_summary, format_summary_markdown, load_financial_data


def test_parser_calculates_expected_statistics_from_mock_csv(tmp_path):
    f = tmp_path / "metrics.csv"
    f.write_text("company,revenue,profit\nA,10,2\nB,20,4\nC,30,6\n", encoding="utf-8")
    numeric = load_financial_data(f)
    summary = calculate_summary(numeric)
    assert list(numeric.columns) == ["revenue", "profit"] and summary.loc["mean", "revenue"] == 20.0
    assert summary.loc["min", "revenue"] == 10.0 and summary.loc["max", "revenue"] == 30.0
    assert summary.loc["std", "revenue"] == 10.0 and summary.loc["mean", "profit"] == 4.0


def test_analysis_returns_markdown_table(tmp_path):
    f = tmp_path / "metrics.csv"
    f.write_text("revenue\n100\n200\n", encoding="utf-8")
    result = analyse_financial_csv(f)
    assert "| mean" in result and "| min" in result and "| max" in result and "| std" in result and "150.00" in result


def test_non_numeric_columns_are_ignored(tmp_path):
    f = tmp_path / "mixed.csv"
    f.write_text("company,revenue\nA,10\nB,20\n", encoding="utf-8")
    assert list(load_financial_data(f).columns) == ["revenue"]


def test_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        load_financial_data(tmp_path / "missing.csv")


def test_empty_csv_raises_clear_error(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_financial_data(f)


def test_csv_without_numeric_columns_is_rejected(tmp_path):
    f = tmp_path / "text.csv"
    f.write_text("company,sector\nA,Tech\nB,Finance\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no numeric columns"):
        load_financial_data(f)


def test_markdown_formatter_outputs_a_table():
    summary = pd.DataFrame({"revenue": [2.0, 1.0, 3.0]}, index=["mean", "min", "max"])
    md = format_summary_markdown(summary)
    assert "| mean" in md and "revenue" in md


def test_all_null_numeric_column_is_rejected(tmp_path):
    f = tmp_path / "nulls.csv"
    f.write_text("revenue\nNaN\nNaN\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no usable numeric values"):
        load_financial_data(f)
