"""
verify_database.py

Verifies the SQLite database after loading.
"""

import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("db") / "nifty100.db"


TABLES = [

    "companies",
    "analysis",
    "documents",
    "prosandcons",
    "profitandloss",
    "balancesheet",
    "cashflow"

]


def main():

    
    print("--------------------DATABASE VERIFICATION----------------------------")
    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    print("\nTable Row Counts\n")
    summary = []
    for table in TABLES:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(f"{table:<20}{count:>8}")
        summary.append({
            "table": table,
            "rows": count
        })
    summary_df = pd.DataFrame(summary)

    summary_df.to_csv(
        "output/database_summary.csv",
        index=False
    )

    print("\nDatabase Summary saved to output/database_summary.csv")
    print("\nChecking Foreign Keys...\n")

    cursor.execute(
        "PRAGMA foreign_key_check;"
    )

    violations = cursor.fetchall()

    if len(violations) == 0:

        print("PASS : No foreign key violations found.")

    else:

        print(f"FAIL : {len(violations)} foreign key violations found.")

        for violation in violations:

            print(violation)

    conn.close()

    print("\nDatabase verification completed.")


if __name__ == "__main__":
    main()