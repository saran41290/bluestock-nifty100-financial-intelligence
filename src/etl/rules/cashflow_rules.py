"""
cashflow_rules.py

Validation rules for cashflow.xlsx

DQ-09 Net Cash Flow Validation
"""

import pandas as pd

from src.etl.models import ValidationFailure
from src.utils.number_utils import _to_number


# -------------------------------------------------------
# DQ-09
#
# Operating
# + Investing
# + Financing
# =
# Net Cash Flow
# -------------------------------------------------------

def dq09_net_cash(df, dataset_name):

    failures = []

    required_columns = {

        "cash_from_operating_activity",

        "cash_from_investing_activity",

        "cash_from_financing_activity",

        "net_cash_flow"

    }

    if not required_columns.issubset(df.columns):
        return failures

    for index, row in df.iterrows():

        operating = _to_number(
            row["cash_from_operating_activity"]
        )

        investing = _to_number(
            row["cash_from_investing_activity"]
        )

        financing = _to_number(
            row["cash_from_financing_activity"]
        )

        net_cash = _to_number(
            row["net_cash_flow"]
        )

        if None in (
            operating,
            investing,
            financing,
            net_cash
        ):
            continue

        calculated = (

            operating +

            investing +

            financing

        )

        difference = abs(

            calculated -

            net_cash

        )

        # Allow rounding tolerance

        if difference > 1:

            failures.append(

                ValidationFailure(

                    rule_id="DQ-09",

                    severity="WARNING",

                    dataset=dataset_name,

                    row_number=index + 2,

                    company_id=str(row["company_id"]),

                    year=str(row["year"]),

                    column_name="net_cash_flow",

                    message="Net Cash Flow mismatch",

                    value=f"Expected={calculated}, Actual={net_cash}"

                )

            )

    return failures