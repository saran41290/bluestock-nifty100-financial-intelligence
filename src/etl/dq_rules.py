import re
from typing import List

import pandas as pd

from src.etl.models import ValidationFailure


YEAR_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def dq01_company_pk(df: pd.DataFrame, dataset: str) -> List[ValidationFailure]:
    """
    DQ-01
    Company Primary Key uniqueness.
    """

    failures = []

    if "company_id" not in df.columns:
        return failures

    duplicates = df[df["company_id"].duplicated(keep=False)]

    for index, row in duplicates.iterrows():
        failures.append(
            ValidationFailure(
                rule_id="DQ-01",
                severity="CRITICAL",
                dataset=dataset,
                row_number=index + 2,
                company_id=str(row["company_id"]),
                year="",
                column_name="company_id",
                message="Duplicate company_id found",
            )
        )

    return failures


def dq02_company_year_pk(df: pd.DataFrame, dataset: str) -> List[ValidationFailure]:
    """
    DQ-02
    Company + Year uniqueness.
    """

    failures = []

    if "company_id" not in df.columns:
        return failures

    if "year" not in df.columns:
        return failures

    duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

    for index, row in duplicates.iterrows():
        failures.append(
            ValidationFailure(
                "DQ-02",
                "CRITICAL",
                dataset,
                index + 2,
                str(row["company_id"]),
                str(row["year"]),
                "company_id,year",
                "Duplicate company/year",
            )
        )

    return failures


def dq07_year_format(df: pd.DataFrame, dataset: str) -> List[ValidationFailure]:
    """
    DQ-07
    Year format YYYY-MM
    """

    failures = []

    if "year" not in df.columns:
        return failures

    for index, row in df.iterrows():

        value = str(row["year"])

        if not YEAR_PATTERN.match(value):

            failures.append(
                ValidationFailure(
                    "DQ-07",
                    "CRITICAL",
                    dataset,
                    index + 2,
                    str(row.get("company_id", "")),
                    value,
                    "year",
                    "Invalid year format",
                )
            )

    return failures


def dq08_ticker_format(df: pd.DataFrame, dataset: str) -> List[ValidationFailure]:
    """
    DQ-08
    Ticker should already be uppercase.
    """

    failures = []

    if "company_id" not in df.columns:
        return failures

    for index, row in df.iterrows():

        ticker = str(row["company_id"])

        if ticker != ticker.strip().upper():

            failures.append(
                ValidationFailure(
                    "DQ-08",
                    "CRITICAL",
                    dataset,
                    index + 2,
                    ticker,
                    "",
                    "company_id",
                    "Ticker not normalized",
                )
            )

    return failures