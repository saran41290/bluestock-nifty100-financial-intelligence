"""
validator.py

Central Validation Engine

Executes all Data Quality Rules and returns a consolidated
list of ValidationFailure objects.
"""

from typing import Dict, List

import pandas as pd

from src.etl.models import ValidationFailure

# Company Rules
from src.etl.rules.company_rules import (
    dq01_company_pk,
    dq08_company_id,
    dq13_company_urls,
)

# Profit & Loss Rules
from src.etl.rules.pnl_rules import (
    dq02_company_year,
    dq05_opm,
    dq06_sales,
    dq11_tax,
    dq12_dividend,
    dq14_eps,
)

# Balance Sheet Rules
from src.etl.rules.balance_rules import (
    dq04_balance_sheet,
    dq10_fixed_assets,
    dq15_balance_info,
)

# Cash Flow Rules
from src.etl.rules.cashflow_rules import (
    dq09_net_cash,
)

# Common Rules
from src.etl.rules.common_rules import (
    dq03_foreign_key,
    dq07_year,
    dq16_minimum_years,
)


class Validator:
    """
    Validation Engine

    Executes all DQ rules against all loaded datasets.

    Returns:
        List[ValidationFailure]
    """

    def validate_all(
        self,
        datasets: Dict[str, pd.DataFrame],
    ) -> List[ValidationFailure]:

        failures: List[ValidationFailure] = []

        # --------------------------------------------------
        # Required datasets
        # --------------------------------------------------

        companies = datasets.get("companies")
        pnl = datasets.get("profitandloss")
        balance = datasets.get("balancesheet")
        cashflow = datasets.get("cashflow")
        documents = datasets.get("documents")
        analysis = datasets.get("analysis")
        pros = datasets.get("prosandcons")

        # --------------------------------------------------
        # Companies
        # --------------------------------------------------

        if companies is not None:

            failures.extend(
                dq01_company_pk(
                    companies,
                    "companies",
                )
            )

            failures.extend(
                dq08_company_id(
                    companies,
                    "companies",
                )
            )

            failures.extend(
                dq13_company_urls(
                    companies,
                    "companies",
                )
            )

        # --------------------------------------------------
        # Profit & Loss
        # --------------------------------------------------

        if pnl is not None:

            failures.extend(
                dq02_company_year(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq05_opm(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq06_sales(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq11_tax(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq12_dividend(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq14_eps(
                    pnl,
                    "profitandloss",
                )
            )

            if companies is not None:

                failures.extend(
                    dq03_foreign_key(
                        companies,
                        pnl,
                        "profitandloss",
                    )
                )

            failures.extend(
                dq07_year(
                    pnl,
                    "profitandloss",
                )
            )

            failures.extend(
                dq16_minimum_years(
                    pnl,
                    "profitandloss",
                )
            )

        # --------------------------------------------------
        # Balance Sheet
        # --------------------------------------------------

        if balance is not None:

            failures.extend(
                dq04_balance_sheet(
                    balance,
                    "balancesheet",
                )
            )

            failures.extend(
                dq10_fixed_assets(
                    balance,
                    "balancesheet",
                )
            )

            failures.extend(
                dq15_balance_info(
                    balance,
                    "balancesheet",
                )
            )

            if companies is not None:

                failures.extend(
                    dq03_foreign_key(
                        companies,
                        balance,
                        "balancesheet",
                    )
                )

            failures.extend(
                dq07_year(
                    balance,
                    "balancesheet",
                )
            )

            failures.extend(
                dq16_minimum_years(
                    balance,
                    "balancesheet",
                )
            )

        # --------------------------------------------------
        # Cash Flow
        # --------------------------------------------------

        if cashflow is not None:

            failures.extend(
                dq09_net_cash(
                    cashflow,
                    "cashflow",
                )
            )

            if companies is not None:

                failures.extend(
                    dq03_foreign_key(
                        companies,
                        cashflow,
                        "cashflow",
                    )
                )

            failures.extend(
                dq07_year(
                    cashflow,
                    "cashflow",
                )
            )

            failures.extend(
                dq16_minimum_years(
                    cashflow,
                    "cashflow",
                )
            )

        # --------------------------------------------------
        # Documents
        # --------------------------------------------------

        if documents is not None and companies is not None:

            failures.extend(
                dq03_foreign_key(
                    companies,
                    documents,
                    "documents",
                )
            )

        # --------------------------------------------------
        # Analysis
        # --------------------------------------------------

        if analysis is not None and companies is not None:

            failures.extend(
                dq03_foreign_key(
                    companies,
                    analysis,
                    "analysis",
                )
            )

        # --------------------------------------------------
        # Pros & Cons
        # --------------------------------------------------

        if pros is not None and companies is not None:

            failures.extend(
                dq03_foreign_key(
                    companies,
                    pros,
                    "prosandcons",
                )
            )

        return failures