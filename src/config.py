from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset folders
DATASETS_DIR = BASE_DIR / "datasets"
SUPPORTING_DATASETS_DIR = BASE_DIR / "supporting_datasets"

# Output
OUTPUT_DIR = BASE_DIR / "output"

# Database
DATABASE_PATH = BASE_DIR / "db" / "nifty100.db"
