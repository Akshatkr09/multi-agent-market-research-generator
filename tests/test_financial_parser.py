"""Tests for financial CSV loading and Pandas summary statistics."""
import pandas as pd
import pytest

from tools.financial_parser import (
    analyse_financial_csv,
    calculate_summary,
    format_summary_markdown,
    load_financial_data,
)


def test_parser_calculates_expected_statistics_from_mock_csv(tmp_path):
    csv_file = tmp_path / "metrics.csv"
    csv_file.write_text(
        "company,revenue,profit\nA,10,2\nB,20,4\nC,30,6\n",
        encoding="utf-8",
    )

    numeric = load_financial_data(csv_file)
    summary = calculate_summary(numeric)

    assert list(numeric.columns) == ["revenue", "profit"]
    assert summary.loc["mean", "revenue"] == 20.0
    assert summary.loc["min", "revenue"] == 10.0
    assert summary.loc["max", "revenue"] == 30.0
    assert summary.loc["std", "revenue"] == 10.0
    assert summary.loc["mean", "profit"] == 4.0


def test_analysis_returns_markdown_table(tmp_path):
    csv_file = tmp_path / "metrics.csv"
    csv_file.write_text("revenue\n100\n200\n", encoding="utf-8")

    result = analyse_financial_csv(csv_file)

    assert "| mean" in result
    assert "| min" in result
    assert "| max" in result
    assert "| std" in result
    assert "150.00" in result


def test_non_numeric_columns_are_ignored(tmp_path):
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text("company,revenue\nA,10\nB,20\n", encoding="utf-8")

    numeric = load_financial_data(csv_file)

    assert list(numeric.columns) == ["revenue"]


def test_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        load_financial_data(tmp_path / "missing.csv")


def test_empty_csv_raises_clear_error(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_financial_data(csv_file)


def test_csv_without_numeric_columns_is_rejected(tmp_path):
    csv_file = tmp_path / "text_only.csv"
    csv_file.write_text("company,sector\nA,Tech\nB,Finance\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no numeric columns"):
        load_financial_data(csv_file)


def test_markdown_formatter_outputs_a_table():
    summary = pd.DataFrame(
        {"revenue": [2.0, 1.0, 3.0]},
        index=["mean", "min", "max"],
    )

    markdown = format_summary_markdown(summary)

    assert "| mean" in markdown
    assert "revenue" in markdown


def test_all_null_numeric_column_is_rejected(tmp_path):
    csv_file = tmp_path / "nulls.csv"
    csv_file.write_text("revenue\nNaN\nNaN\n", encoding="utf-8")

    with pytest.raises(ValueError, match="no usable numeric values"):
        load_financial_data(csv_file)
