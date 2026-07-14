"""
pnl_rules.py

Validation rules for profitandloss.xlsx

DQ-02 Company + Year uniqueness
DQ-05 OPM cross check
DQ-06 Positive Sales
DQ-11 Tax Percentage
DQ-12 Dividend Payout
DQ-14 EPS Sign Consistency
"""

import pandas as pd

from src.etl.models import ValidationFailure
from src.utils.number_utils import _to_number





# -------------------------------------------------------
# DQ-02
# Company + Year should be unique
# -------------------------------------------------------

def dq02_company_year(df,dataset_name):

    failures = []

    required = {"company_id", "year"}

    if not required.issubset(df.columns):
        return failures

    duplicates = df[df.duplicated(["company_id", "year"], keep=False)]

    for index, row in duplicates.iterrows():

        failures.append(

            ValidationFailure(

                rule_id="DQ-02",

                severity="CRITICAL",

                dataset=dataset_name,

                row_number=index + 2,

                company_id=str(row["company_id"]),

                year=str(row["year"]),

                column_name="company_id,year",

                message="Duplicate Company-Year record",

                value=f'{row["company_id"]}-{row["year"]}'

            )

        )

    return failures


# -------------------------------------------------------
# DQ-05
# Verify OPM
# -------------------------------------------------------

def dq05_opm(df, dataset_name):

    failures = []

    cols = {

        "sales",

        "operating_profit",

        "opm_percentage"

    }

    if not cols.issubset(df.columns):
        return failures

    for index, row in df.iterrows():

        sales = _to_number(row["sales"])
        op = _to_number(row["operating_profit"])
        opm = _to_number(row["opm_percentage"])

        if sales in (None, 0):
            continue

        if op is None or opm is None:
            continue

        calculated = (op / sales) * 100

        if abs(calculated - opm) > 1:

            failures.append(

                ValidationFailure(

                    "DQ-05",

                    "WARNING",

                    "profitandloss",

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "opm_percentage",

                    "OPM mismatch",

                    f"Expected {calculated:.2f}"

                )

            )

    return failures


# -------------------------------------------------------
# DQ-06
# Sales must be positive
# -------------------------------------------------------

def dq06_sales(df, dataset_name):

    failures = []

    if "sales" not in df.columns:
        return failures

    for index, row in df.iterrows():

        sales = _to_number(row["sales"])

        if sales is None:
            continue

        if sales <= 0:

            failures.append(

                ValidationFailure(

                    "DQ-06",

                    "WARNING",

                    dataset_name,

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "sales",

                    "Sales should be positive",

                    str(sales)

                )

            )

    return failures


# -------------------------------------------------------
# DQ-11
# Tax percentage
# -------------------------------------------------------

def dq11_tax(df, dataset_name):

    failures = []

    if "tax_percentage" not in df.columns:
        return failures

    for index, row in df.iterrows():

        tax = _to_number(row["tax_percentage"])

        if tax is None:
            continue

        if tax < 0 or tax > 100:

            failures.append(

                ValidationFailure(

                    "DQ-11",

                    "WARNING",

                    dataset_name,

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "tax_percentage",

                    "Tax should be between 0 and 100",

                    str(tax)

                )

            )

    return failures


# -------------------------------------------------------
# DQ-12
# Dividend payout
# -------------------------------------------------------

def dq12_dividend(df, dataset_name):

    failures = []

    if "dividend_payout" not in df.columns:
        return failures

    for index, row in df.iterrows():

        dividend = _to_number(row["dividend_payout"])

        if dividend is None:
            continue

        if dividend < 0 or dividend > 100:

            failures.append(

                ValidationFailure(

                    "DQ-12",

                    "WARNING",

                    dataset_name,

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "dividend_payout",

                    "Dividend payout should be between 0 and 100",

                    str(dividend)

                )

            )

    return failures


# -------------------------------------------------------
# DQ-14
# EPS Sign Check
# -------------------------------------------------------

def dq14_eps(df, dataset_name):

    failures = []

    cols = {

        "net_profit",

        "eps"

    }

    if not cols.issubset(df.columns):
        return failures

    for index, row in df.iterrows():

        profit = _to_number(row["net_profit"])
        eps = _to_number(row["eps"])

        if profit is None or eps is None:
            continue

        if profit > 0 and eps < 0:

            failures.append(

                ValidationFailure(

                    "DQ-14",

                    "WARNING",

                    dataset_name,

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "eps",

                    "EPS sign inconsistent with Profit",

                    str(eps)

                )

            )

        if profit < 0 and eps > 0:

            failures.append(

                ValidationFailure(

                    "DQ-14",

                    "WARNING",

                    "profitandloss",

                    index + 2,

                    str(row["company_id"]),

                    str(row["year"]),

                    "eps",

                    "EPS sign inconsistent with Loss",

                    str(eps)

                )

            )

    return failures