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


# Generated Output Files


CAPITAL_ALLOCATION_CSV = OUTPUT_DIR / "capital_allocation.csv"

RATIO_EDGE_CASE_LOG = OUTPUT_DIR / "ratio_edge_cases.log"


# Logs


LOG_DIR = OUTPUT_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RATIO_ENGINE_LOG = LOG_DIR / "ratio_engine.log"

ERROR_LOG = LOG_DIR / "error.log"


# Processing


BATCH_SIZE = 500

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
