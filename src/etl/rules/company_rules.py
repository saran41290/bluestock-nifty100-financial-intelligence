"""
company_rules.py

Validation rules for companies.xlsx

DQ-01 Primary Key
DQ-08 Company ID Format
DQ-13 URL Validation
"""

import re
import pandas as pd

from src.etl.models import ValidationFailure

URL_PATTERN = re.compile(r"^https?://")


# -------------------------------------------------------
# DQ-01
# Company ID should be unique and not null
# -------------------------------------------------------

def dq01_company_pk(df: pd.DataFrame, dataset_name: str):

    failures = []

    if "id" not in df.columns:
        return failures

    # Missing IDs
    for index in df[df["id"].isna()].index:

        failures.append(
            ValidationFailure(
                rule_id="DQ-01",
                severity="CRITICAL",
                dataset=dataset_name,
                row_number=index + 2,
                company_id="",
                year="",
                column_name="id",
                message="Company ID is missing",
                value=""
            )
        )

    # Duplicate IDs
    duplicates = df[df.duplicated("id", keep=False)]

    for index, row in duplicates.iterrows():

        failures.append(
            ValidationFailure(
                rule_id="DQ-01",
                severity="CRITICAL",
                dataset=dataset_name,
                row_number=index + 2,
                company_id=str(row["id"]),
                year="",
                column_name="id",
                message="Duplicate Company ID",
                value=str(row["id"])
            )
        )

    return failures


# -------------------------------------------------------
# DQ-08
# Company ID format
# -------------------------------------------------------

def dq08_company_id(df: pd.DataFrame, dataset_name: str):

    failures = []

    if "id" not in df.columns:
        return failures

    for index, row in df.iterrows():

        company = str(row["id"]).strip()

        if company == "" or company.lower() == "nan":
            continue

        if not company.isupper():

            failures.append(
                ValidationFailure(
                    rule_id="DQ-08",
                    severity="WARNING",
                    dataset=dataset_name,
                    row_number=index + 2,
                    company_id=company,
                    year="",
                    column_name="id",
                    message="Company ID should be uppercase",
                    value=company
                )
            )

    return failures


# -------------------------------------------------------
# DQ-13
# Validate URL fields
# -------------------------------------------------------

def dq13_company_urls(df: pd.DataFrame, dataset_name: str):

    failures = []

    url_columns = [
        "website",
        "chart_link",
        "nse_profile",
        "bse_profile",
        "company_logo"
    ]

    for column in url_columns:

        if column not in df.columns:
            continue

        for index, row in df.iterrows():

            value = str(row[column]).strip()

            if value == "" or value.lower() == "nan":
                continue

            if not URL_PATTERN.match(value):

                failures.append(
                    ValidationFailure(
                        rule_id="DQ-13",
                        severity="WARNING",
                        dataset=dataset_name,
                        row_number=index + 2,
                        company_id=str(row["id"]),
                        year="",
                        column_name=column,
                        message="Invalid URL",
                        value=value
                    )
                )

    return failures