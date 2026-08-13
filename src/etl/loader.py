from pathlib import Path

import pandas as pd

from src.config import DATASETS_DIR

CORE_DATASETS = {
    "companies.xlsx": 1,
    "profitandloss.xlsx": 1,
    "balancesheet.xlsx": 1,
    "cashflow.xlsx": 1,
    "analysis.xlsx": 1,
    "documents.xlsx": 1,
    "prosandcons.xlsx": 1,
}
def load_excel(filename: str, header: int = 0) -> pd.DataFrame:
    """
    Generic Excel Loader.
    """

    file_path = DATASETS_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    return pd.read_excel(file_path, header=header)


def load_companies() -> pd.DataFrame:
    """Load master companies dataset."""
    return load_excel("companies.xlsx", header=1)


def load_profit_and_loss() -> pd.DataFrame:
    """Load annual profit & loss dataset."""
    return load_excel("profitandloss.xlsx", header=1)


def load_balance_sheet() -> pd.DataFrame:
    """Load annual balance sheet dataset."""
    return load_excel("balancesheet.xlsx", header=1)


def load_cash_flow() -> pd.DataFrame:
    """Load annual cash flow dataset."""
    return load_excel("cashflow.xlsx", header=1)


def load_analysis() -> pd.DataFrame:
    """Load pre-computed growth analysis dataset."""
    return load_excel("analysis.xlsx", header=1)


def load_documents() -> pd.DataFrame:
    """Load annual report links dataset."""
    return load_excel("documents.xlsx", header=1)


def load_pros_and_cons() -> pd.DataFrame:
    """Load qualitative pros & cons dataset."""
    return load_excel("prosandcons.xlsx", header=1)


if __name__ == "__main__":

    for dataset, header in CORE_DATASETS.items():

        try:
            df = load_excel(dataset, header)

            print(f"----------------{dataset}----------------")
            print(df.shape)

        except Exception as e:

            print(e)