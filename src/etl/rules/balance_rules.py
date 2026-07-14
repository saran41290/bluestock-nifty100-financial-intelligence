"""
balance_rules.py

Validation rules for balancesheet.xlsx

DQ-04 Balance Sheet Equation
DQ-10 Fixed Assets >= 0
DQ-15 Balance Sheet Information Check
"""

import pandas as pd

from src.etl.models import ValidationFailure
from src.utils.number_utils import _to_number



# -------------------------------------------------------
# DQ-04
# Assets should approximately equal Liabilities
# -------------------------------------------------------

def dq04_balance_sheet(df, dataset_name):

    failures = []

    required = {
        "total_assets",
        "total_liabilities"
    }

    if not required.issubset(df.columns):
        return failures

    for index, row in df.iterrows():

        assets = _to_number(row["total_assets"])
        liabilities = _to_number(row["total_liabilities"])

        if assets is None or liabilities is None:
            continue

        if assets == 0:
            continue

        difference = abs(assets - liabilities)

        percentage = (difference / assets) * 100

        if percentage > 1:

            failures.append(

                ValidationFailure(

                    rule_id="DQ-04",

                    severity="WARNING",

                    dataset=dataset_name,

                    row_number=index + 2,

                    company_id=str(row["company_id"]),

                    year=str(row["year"]),

                    column_name="total_assets,total_liabilities",

                    message=f"Balance Sheet mismatch ({percentage:.2f}% difference)",

                    value=f"Assets={assets}, Liabilities={liabilities}"

                )

            )

    return failures


# -------------------------------------------------------
# DQ-10
# Fixed Assets cannot be negative
# -------------------------------------------------------

def dq10_fixed_assets(df, dataset_name):

    failures = []

    if "fixed_assets" not in df.columns:
        return failures

    for index, row in df.iterrows():

        value = _to_number(row["fixed_assets"])

        if value is None:
            continue

        if value < 0:

            failures.append(

                ValidationFailure(

                    rule_id="DQ-10",

                    severity="WARNING",

                    dataset=dataset_name,

                    row_number=index + 2,

                    company_id=str(row["company_id"]),

                    year=str(row["year"]),

                    column_name="fixed_assets",

                    message="Fixed Assets cannot be negative",

                    value=str(value)

                )

            )

    return failures


# -------------------------------------------------------
# DQ-15
# Informational Balance Sheet Check
# -------------------------------------------------------

def dq15_balance_info(df, dataset_name):

    failures = []

    required = {
        "equity_capital",
        "reserves",
        "borrowings",
        "other_liabilities",
        "total_liabilities"
    }

    if not required.issubset(df.columns):
        return failures

    for index, row in df.iterrows():

        equity = _to_number(row["equity_capital"])
        reserves = _to_number(row["reserves"])
        borrowings = _to_number(row["borrowings"])
        other = _to_number(row["other_liabilities"])
        total = _to_number(row["total_liabilities"])

        if None in (
            equity,
            reserves,
            borrowings,
            other,
            total
        ):
            continue

        calculated = (
            equity +
            reserves +
            borrowings +
            other
        )

        difference = abs(calculated - total)

        if difference > 1:

            failures.append(

                ValidationFailure(

                    rule_id="DQ-15",

                    severity="INFO",

                    dataset=dataset_name,

                    row_number=index + 2,

                    company_id=str(row["company_id"]),

                    year=str(row["year"]),

                    column_name="total_liabilities",

                    message="Total liabilities do not match calculated value",

                    value=f"Expected={calculated}, Actual={total}"

                )

            )

    return failures