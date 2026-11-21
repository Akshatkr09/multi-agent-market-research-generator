"""Project configuration and environment loading."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
OUTPUT_DIR = PROJECT_ROOT / "output"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
for directory in (OUTPUT_DIR, DATA_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
