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

if __name__ == "__main__":

    for dataset, header in CORE_DATASETS.items():

        try:
            df = load_excel(dataset, header)

            print(f"----------------{dataset}----------------")
            print(df.shape)

        except Exception as e:

            print(e)