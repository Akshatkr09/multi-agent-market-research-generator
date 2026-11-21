"""Pandas-based financial CSV parser for the market research workflow."""
from pathlib import Path
from typing import Union
import pandas as pd
from crewai.tools import tool
PathLike = Union[str, Path]
def load_financial_data(csv_path: PathLike) -> pd.DataFrame:
    path = Path(csv_path).expanduser()
    if not path.exists(): raise FileNotFoundError(f"CSV file not found: {path}")
    if not path.is_file(): raise ValueError(f"CSV path is not a file: {path}")
    try: dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc: raise ValueError("The CSV file is empty.") from exc
    except pd.errors.ParserError as exc: raise ValueError(f"Could not parse the CSV file: {exc}") from exc
    if dataframe.empty: raise ValueError("The CSV file contains no data rows.")
    numeric_data = dataframe.select_dtypes(include="number")
    if numeric_data.empty: raise ValueError("The CSV file contains no numeric columns to analyse.")
    numeric_data = numeric_data.dropna(axis=1, how="all")
    if numeric_data.empty: raise ValueError("The CSV file contains no usable numeric values.")
    return numeric_data
def calculate_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty or dataframe.select_dtypes(include="number").empty: raise ValueError("At least one non-empty numeric column is required.")
    return dataframe.describe().round(2)
def format_summary_markdown(summary: pd.DataFrame) -> str:
    return summary.to_markdown(index=True, floatfmt=".2f")
def analyse_financial_csv(csv_path: PathLike) -> str:
    return format_summary_markdown(calculate_summary(load_financial_data(csv_path)))
@tool("Financial Data Parser")
def calculate_financial_metrics(csv_path: str) -> str:
    """Load financial metrics from a CSV and return Pandas descriptive statistics as Markdown."""
    try: return analyse_financial_csv(csv_path)
    except (FileNotFoundError, ValueError) as exc: return f"Financial data could not be analysed: {exc}"
    except Exception as exc: return f"Financial data analysis failed: {type(exc).__name__}: {exc}"
