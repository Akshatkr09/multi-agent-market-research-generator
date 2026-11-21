"""Pandas-based financial CSV parser for the market research workflow."""
from pathlib import Path
from typing import Union

import pandas as pd
from crewai.tools import tool

PathLike = Union[str, Path]


def load_financial_data(csv_path: PathLike) -> pd.DataFrame:
    """Load a CSV and validate that it contains usable numeric metrics."""
    path = Path(csv_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    if not path.is_file():
        raise ValueError(f"CSV path is not a file: {path}")

    try:
        dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The CSV file is empty.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse the CSV file: {exc}") from exc

    if dataframe.empty:
        raise ValueError("The CSV file contains no data rows.")

    numeric_data = dataframe.select_dtypes(include="number")
    if numeric_data.empty:
        raise ValueError("The CSV file contains no numeric columns to analyse.")

    # Ignore columns that contain no usable values; describe() would otherwise
    # produce mostly empty statistics for them.
    numeric_data = numeric_data.dropna(axis=1, how="all")
    if numeric_data.empty:
        raise ValueError("The CSV file contains no usable numeric values.")

    return numeric_data


def calculate_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate count, mean, standard deviation, min/max and quartiles."""
    if dataframe.empty or dataframe.select_dtypes(include="number").empty:
        raise ValueError("At least one non-empty numeric column is required.")
    return dataframe.describe().round(2)


def format_summary_markdown(summary: pd.DataFrame) -> str:
    """Render summary statistics as a clean Markdown table."""
    return summary.to_markdown(index=True, floatfmt=".2f")


def analyse_financial_csv(csv_path: PathLike) -> str:
    """Load a financial CSV and return its descriptive statistics as Markdown."""
    numeric_data = load_financial_data(csv_path)
    summary = calculate_summary(numeric_data)
    return format_summary_markdown(summary)


@tool("Financial Data Parser")
def calculate_financial_metrics(csv_path: str) -> str:
    """Load financial metrics from a CSV file and return Pandas summary statistics as a Markdown table.

    The CSV should contain column headers and one or more numeric metric columns.
    The output includes count, mean, standard deviation, minimum, quartiles and maximum.
    """
    try:
        return analyse_financial_csv(csv_path)
    except (FileNotFoundError, ValueError) as exc:
        return f"Financial data could not be analysed: {exc}"
    except Exception as exc:
        return f"Financial data analysis failed: {type(exc).__name__}: {exc}"
