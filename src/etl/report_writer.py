"""
report_writer.py

Generates CSV reports for ETL validation.

Current Reports
---------------
1. validation_failures.csv

Future Reports
--------------
2. load_audit.csv
3. validation_summary.csv
"""

from pathlib import Path
from typing import List

import pandas as pd

from src.etl.models import ValidationFailure


class ValidationReportWriter:
    """
    Writes validation failures into CSV reports.
    """

    def __init__(self, output_folder: str = "output"):

        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------
    # Validation Failures Report
    # ---------------------------------------------------

    def write_validation_failures(
        self,
        failures: List[ValidationFailure]
    ) -> Path:

        output_file = (
            self.output_folder /
            "validation_failures.csv"
        )

        rows = [

            failure.to_dict()

            for failure in failures

        ]

        df = pd.DataFrame(rows)

        if not df.empty:

            df = df.sort_values(

                by=[
                    "severity",
                    "rule_id",
                    "dataset",
                    "company_id",
                    "row_number"
                ]

            )

        df.to_csv(

            output_file,

            index=False,

            encoding="utf-8"

        )

        return output_file

    # ---------------------------------------------------
    # Validation Summary
    # ---------------------------------------------------

    def write_summary(
        self,
        failures: List[ValidationFailure]
    ) -> Path:

        output_file = (

            self.output_folder /

            "validation_summary.csv"

        )

        if len(failures) == 0:

            summary = pd.DataFrame(

                [

                    {

                        "severity": "PASS",

                        "count": 0

                    }

                ]

            )

        else:

            df = pd.DataFrame(

                [

                    f.to_dict()

                    for f in failures

                ]

            )

            summary = (

                df.groupby(

                    "severity"

                )

                .size()

                .reset_index(

                    name="count"

                )

            )

        summary.to_csv(

            output_file,

            index=False

        )

        return output_file

    # ---------------------------------------------------
    # Console Report
    # ---------------------------------------------------

    def print_summary(
        self,
        failures: List[ValidationFailure]
    ):

        print()

        print("=" * 60)

        print("DATA QUALITY VALIDATION SUMMARY")

        print("=" * 60)

        total = len(failures)

        critical = sum(

            1

            for f in failures

            if f.severity == "CRITICAL"

        )

        warning = sum(

            1

            for f in failures

            if f.severity == "WARNING"

        )

        info = sum(

            1

            for f in failures

            if f.severity == "INFO"

        )

        print(f"Total Failures : {total}")

        print(f"Critical       : {critical}")

        print(f"Warnings       : {warning}")

        print(f"Information    : {info}")

        if critical == 0:

            print()

            print("ETL Status : PASS")

        else:

            print()

            print("ETL Status : FAILED")

        print("=" * 60)