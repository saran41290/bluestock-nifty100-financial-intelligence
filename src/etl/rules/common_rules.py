"""
Common Data Quality Rules
"""

from src.etl.models import ValidationFailure


def dq03_foreign_key(parent_df,child_df, dataset_name):
    """
    Placeholder for foreign key validation.
    """
    return []


def dq07_year(df, dataset_name):
    """
    Year must be present.
    """

    failures = []

    if "Year" not in df.columns:
        return failures

    missing = df["Year"].isna()

    for idx in df[missing].index:

        failures.append(

            ValidationFailure(
                dataset="Unknown",
                rule="DQ07",
                severity="WARNING",
                row=int(idx),
                column="Year",
                value="NULL",
                message="Year is missing",
            )

        )

    return failures


def dq16_minimum_years(df, dataset_name):
    """
    Dataset should contain at least 3 years.
    """

    failures = []

    if "Year" not in df.columns:
        return failures

    years = df["Year"].dropna().unique()

    if len(years) < 3:

        failures.append(

            ValidationFailure(
                dataset="Unknown",
                rule="DQ16",
                severity="WARNING",
                row=0,
                column="Year",
                value=len(years),
                message="Less than 3 years of data",
            )

        )

    return failures