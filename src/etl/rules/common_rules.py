"""
Common Data Quality Rules
"""
import pandas as pd
from src.etl.models import ValidationFailure


def dq03_foreign_key(parent_df, child_df, dataset_name):
    """
    Validate foreign keys in child_df against parent_df.
    """
    failures = []
    if "company_id" not in child_df.columns or "id" not in parent_df.columns:
        return failures

    parent_ids = set(parent_df["id"].dropna().unique())
    orphans = child_df[~child_df["company_id"].isin(parent_ids)]

    for idx, row in orphans.iterrows():
        failures.append(
            ValidationFailure(
                rule_id="DQ-03",
                severity="CRITICAL",
                dataset=dataset_name,
                row_number=int(idx) + 2,
                company_id=str(row["company_id"]),
                year=str(row.get("year", "")),
                column_name="company_id",
                message="Orphan record: company_id not in master table",
                value=str(row["company_id"]),
            )
        )
    return failures


def dq07_year(df, dataset_name):
    """
    Year must be present and parseable.
    """
    failures = []
    col = "Year" if "Year" in df.columns else ("year" if "year" in df.columns else None)
    if not col:
        return failures

    missing = df[df[col].isna() | (df[col] == "PARSE_ERROR")]

    for idx, row in missing.iterrows():
        failures.append(
            ValidationFailure(
                rule_id="DQ-07",
                severity="WARNING",
                dataset=dataset_name,
                row_number=int(idx) + 2,
                company_id=str(row.get("company_id", "")),
                year=str(row.get(col, "")),
                column_name=col,
                message="Year is missing or unparseable",
                value=str(row.get(col, "NULL")),
            )
        )

    return failures


def dq16_minimum_years(df, dataset_name):
    """
    Dataset or company history should contain at least 3 years.
    """
    failures = []
    col = "Year" if "Year" in df.columns else ("year" if "year" in df.columns else None)
    if not col:
        return failures

    years = df[col].dropna().unique()

    if len(years) < 3:
        failures.append(
            ValidationFailure(
                rule_id="DQ-16",
                severity="WARNING",
                dataset=dataset_name,
                row_number=2,
                company_id=str(df["company_id"].iloc[0]) if "company_id" in df.columns else "",
                year="",
                column_name=col,
                message=f"Insufficient history: found {len(years)} years (min 3 required)",
                value=str(len(years)),
            )
        )

    return failures