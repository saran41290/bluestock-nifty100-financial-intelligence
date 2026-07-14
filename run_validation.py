"""
run_validation.py

Entry point for ETL Validation.

Usage
-----
python run_validation.py
"""

from pathlib import Path

from src.etl.loader import load_excel
from src.etl.validator import Validator
from src.etl.report_writer import ValidationReportWriter
from src.etl.loader import (
    load_excel,
    CORE_DATASETS,
)

# ---------------------------------------------------------
# Dataset Locations
# ---------------------------------------------------------




def load_all_datasets():

    datasets = {}

    print()

    
    print("--------------------Loading Excel Files----------------------------")

    for filename, header in CORE_DATASETS.items():

        dataset_name = filename.replace(".xlsx", "")

        print(f"Loading {filename}")

        datasets[dataset_name] = load_excel(
            filename,
            header,
        )
    print()

    return datasets


def main():

    print()

    print("------------------Bluestock Nifty100 ETL Validation----------------------------")
    

    datasets = load_all_datasets()

    if not datasets:

        print("No datasets found.")

        return

    validator = Validator()

    failures = validator.validate_all(datasets)

    writer = ValidationReportWriter()

    validation_csv = writer.write_validation_failures(
        failures
    )

    summary_csv = writer.write_summary(
        failures
    )

    writer.print_summary(
        failures
    )

    print()

    print(f"Validation Report : {validation_csv}")

    print(f"Summary Report    : {summary_csv}")

    print()

    critical = sum(

        1

        for failure in failures

        if failure.severity == "CRITICAL"

    )

    if critical == 0:

        print("Validation PASSED")

    else:

        print("Validation FAILED")

        print(f"{critical} Critical Issues Found")

    print()


if __name__ == "__main__":

    main()