"""
load_database.py

Loads validated datasets into SQLite.

Usage
-----
python scripts/load_database.py
"""

from pathlib import Path
import pandas as pd

from src.etl.loader import load_excel, CORE_DATASETS
from src.etl.validator import Validator
from src.database.database import DatabaseManager
from src.database.sqlite_loader import SQLiteLoader
from src.etl.report_writer import ValidationReportWriter


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


LOAD_ORDER = [

    "companies",

    "analysis",

    "documents",

    "prosandcons",

    "profitandloss",

    "balancesheet",

    "cashflow",

]


def load_all_datasets():

    datasets = {}

    print("\nLoading Excel Files\n")

    for filename, header in CORE_DATASETS.items():

        dataset = filename.replace(".xlsx", "")

        print(f"Loading {filename}")

        datasets[dataset] = load_excel(

            filename,

            header

        )

    return datasets


def main():

    # Load Excel
    
    datasets = load_all_datasets()

    valid_company_ids = set(datasets["companies"]["id"])

    child_tables = [
        "analysis",
        "documents",
        "prosandcons",
        "profitandloss",
        "balancesheet",
        "cashflow",
    ]
    orphan_summary = []
    for table in child_tables:

        before = len(datasets[table])

        datasets[table] = datasets[table][
            datasets[table]["company_id"].isin(valid_company_ids)
        ]

        removed = before - len(datasets[table])

        if removed > 0:

            print(f"{table}: Removed {removed} orphan records")

            orphan_summary.append({
                "table": table,
                "original_rows": before,
                "removed_orphan_records": removed,
                "loaded_rows": len(datasets[table]),
                "status": "PASS"
            })


    if orphan_summary:

        orphan_df = pd.DataFrame(orphan_summary)

        orphan_file = OUTPUT_DIR / "orphan_records_summary.csv"

        orphan_df.to_csv(
            orphan_file,
            index=False
        )

        print(f"\nOrphan Summary Report: {orphan_file}")
    # Validate
    
    validator = Validator()

    failures = validator.validate_all(datasets)

    report = ValidationReportWriter()

    report.write_validation_failures(failures)

    report.write_summary(failures)

    critical = [ f for f in failures if f.severity == "CRITICAL"]

    print(f"Critical Issues : {len(critical)}")

    # Database
    
    db = DatabaseManager()

    connection = db.connect()

    db.create_tables()

    loader = SQLiteLoader(

        connection

    )

    audit = []

    print()

    print("-" * 60)

    print("Loading SQLite")

    print("-" * 60)

    for table in LOAD_ORDER:

        if table not in datasets:

            continue

        df = datasets[table]
        # Remove duplicate Profit & Loss records
        if table == "profitandloss":

            before_dedup = len(df)

            df = (
                df.sort_values("id")
                .drop_duplicates(
                    subset=["company_id", "year"],
                    keep="first"
                )
            )

            removed = before_dedup - len(df)

            print(f"Removed {removed} duplicate Profit & Loss rows")
        before = loader.count_rows(table)
        print(f"\nLoading table: {table}")

        loader.insert_dataframe(df, table)

        print(f"Finished loading: {table}")

        after = loader.count_rows(table)

        inserted = after - before

        print(

            f"{table:<20}"

            f"{inserted:>8} rows"

        )

        audit.append(

            {

                "table": table,

                "rows_loaded": inserted,

                "total_rows": after,

                "status": "PASS"

            }

        )

    loader.commit()

    loader.close()

    audit_df = pd.DataFrame(

        audit

    )

    audit_file = (

        OUTPUT_DIR /

        "load_audit.csv"

    )

    audit_df.to_csv(

        audit_file,

        index=False

    )

    print()

    
    print("-------------Database Load Complete-----------------------")

    print(f"Audit Report : {audit_file}")

    print()


if __name__ == "__main__":

    main()