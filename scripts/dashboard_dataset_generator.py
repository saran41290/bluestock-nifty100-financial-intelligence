"""
dashboard_dataset_generator.py

Generates Power BI ready dashboard datasets.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("db") / "nifty100.db"

OUTPUT_DIR = Path("output") / "dashboard"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def export_query(connection, query, filename):

    df = pd.read_sql_query(query, connection)

    output_file = OUTPUT_DIR / filename

    df.to_csv(output_file, index=False)

    print(f"{filename:<40} {len(df):>6} rows")


def main():

    
    print("---------------------------GENERATING POWER BI DATASETS---------------------------------")
   

    conn = sqlite3.connect(DB_PATH)

    # =====================================================
    # Dashboard 1-5
    # =====================================================
    export_query(
        conn,
        """
        SELECT *
        FROM vw_latest_company_metrics
        ORDER BY company_name;
        """,
        "dashboard_company_metrics.csv"
    )
    # =====================================================
    # Dashboard 6
    # Executive Summary
    # =====================================================

    export_query(

        conn,

        """
       SELECT

            COUNT(*) AS total_companies,

            ROUND(AVG(roe_percentage), 2) AS avg_roe,

            ROUND(AVG(roce_percentage), 2) AS avg_roce

        FROM vw_company_summary;

        """,

        "dashboard_summary.csv"

    )

    conn.close()

   
    print("-----------------------ALL DASHBOARD DATASETS GENERATED---------------------------")
    


if __name__ == "__main__":
    main()