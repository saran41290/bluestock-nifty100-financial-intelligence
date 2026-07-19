"""
validator.py

Financial Statement Validation Engine

Responsibilities
----------------
1. Validate required financial fields
2. Validate numeric values
3. Validate business rules
4. Return validation errors
5. Never raise exceptions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import re
# ==========================================================
# VALIDATION RESULT
# ==========================================================

@dataclass
class ValidationResult:
    """
    Validation response.
    """

    is_valid: bool

    errors: list[str]


# ==========================================================
# FINANCIAL VALIDATOR
# ==========================================================

class FinancialValidator:
    """
    Validates one company-year financial statement.
    """

    # ------------------------------------------------------
    # Required Columns
    # ------------------------------------------------------

    REQUIRED_FIELDS = [

        "company_id",

        "year",

        "sales",

        "net_profit",

        "operating_profit",

        "borrowings",

        "interest",

        "equity_capital",

        "reserves",

        "total_assets",

        "operating_activity",

        "investing_activity",

        "financing_activity",

    ]

    # ------------------------------------------------------

    @staticmethod
    def validate(
        record: dict[str, Any],
    ) -> ValidationResult:
        """
        Validate one financial record.
        """

        errors: list[str] = []

        # ------------------------------------------
        # Required fields
        # ------------------------------------------

        for field in FinancialValidator.REQUIRED_FIELDS:

            if field not in record:

                errors.append(

                    f"{field} column missing"

                )

                continue

            value = record[field]

            if value is None:

                errors.append(

                    f"{field} is NULL"

                )

        # ------------------------------------------
        # Numeric validation
        # ------------------------------------------

        numeric_fields = [

            "sales",

            "net_profit",

            "operating_profit",

            "borrowings",

            "interest",

            "equity_capital",

            "reserves",

            "total_assets",

            "operating_activity",

            "investing_activity",

            "financing_activity",

        ]

        for field in numeric_fields:

            if field not in record:

                continue

            value = record[field]

            if value is None:

                continue

            try:

                float(value)

            except (TypeError, ValueError):

                errors.append(

                    f"{field} is not numeric"

                )

        # ------------------------------------------
        # Business Rules
        # ------------------------------------------

        sales = record.get("sales")

        if sales is not None:

            try:

                if float(sales) < 0:

                    errors.append(

                        "Sales cannot be negative"

                    )

            except Exception:

                pass

        assets = record.get("total_assets")

        if assets is not None:

            try:

                if float(assets) <= 0:

                    errors.append(

                        "Total Assets must be greater than zero"

                    )

            except Exception:

                pass

        year = record.get("year")

        if year is not None:
            match = re.search(r"\b(19|20)\d{2}\b", str(year))
            try:

                if match:
                    record["year"] = int(match.group())
                else:
                    errors.append("Invalid year")

            except Exception:

                errors.append(

                    "Invalid year"

                )

        # ------------------------------------------

        return ValidationResult(

            is_valid=len(errors) == 0,

            errors=errors,

        )