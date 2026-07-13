"""
company_rules.py

Validation rules for companies.xlsx

DQ-01 Company PK uniqueness
DQ-08 Company ID format
DQ-13 Website URL validation
"""

from urllib.parse import urlparse

import pandas as pd

from src.etl.models import ValidationFailure


def _valid_url(url: str) -> bool:
    """
    Returns True if URL looks valid.
    """

    if pd.isna(url):
        return False

    url = str(url).strip()

    if url == "":
        return False

    parsed = urlparse(url)

    return parsed.scheme in ("http", "https") and parsed.netloc != ""


def dq01_company_pk(df: pd.DataFrame):

    failures = []

    if "id" not in df.columns:
        return failures

    duplicate_rows = df[df["id"].duplicated(keep=False)]

    for index, row in duplicate_rows.iterrows():

        failures.append(

            ValidationFailure(

                rule_id="DQ-01",

                severity="CRITICAL",

                dataset="companies",

                row_number=index + 2,

                company_id=str(row["id"]),

                column_name="id",

                message="Duplicate Company Primary Key",

                value=str(row["id"])

            )

        )

    return failures


def dq08_company_id(df: pd.DataFrame):

    failures = []

    if "id" not in df.columns:
        return failures

    for index, row in df.iterrows():

        company = str(row["id"]).strip()

        if company != company.upper():

            failures.append(

                ValidationFailure(

                    rule_id="DQ-08",

                    severity="CRITICAL",

                    dataset="companies",

                    row_number=index + 2,

                    company_id=company,

                    column_name="id",

                    message="Company ID should be uppercase",

                    value=company

                )

            )

    return failures


def dq13_company_urls(df: pd.DataFrame):

    failures = []

    url_columns = [

        "website",

        "nse_profile",

        "bse_profile"

    ]

    for column in url_columns:

        if column not in df.columns:
            continue

        for index, row in df.iterrows():

            value = row[column]

            if pd.isna(value):
                continue

            if not _valid_url(value):

                failures.append(

                    ValidationFailure(

                        rule_id="DQ-13",

                        severity="WARNING",

                        dataset="companies",

                        row_number=index + 2,

                        company_id=str(row["id"]),

                        column_name=column,

                        message="Invalid URL",

                        value=str(value)

                    )

                )

    return failures